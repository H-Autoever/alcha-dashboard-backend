#!/usr/bin/env python3
"""
MongoDB vs TimescaleDB 저장 용량 비교 스크립트
동일한 데이터를 저장했을 때의 용량 차이를 확인합니다.
"""

import os
from pymongo import MongoClient
import psycopg2

# MongoDB 연결
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))
MONGO_DB = os.getenv("MONGO_DB", "alcha_events")

# TimescaleDB 연결
TIMESCALEDB_HOST = os.getenv("TIMESCALEDB_HOST", "localhost")
TIMESCALEDB_PORT = int(os.getenv("TIMESCALEDB_PORT", "5432"))
TIMESCALEDB_DB = os.getenv("TIMESCALEDB_DB", "alcha_events")
TIMESCALEDB_USER = os.getenv("TIMESCALEDB_USER", "alcha")
TIMESCALEDB_PASSWORD = os.getenv("TIMESCALEDB_PASSWORD", "alcha_password")

def format_bytes(bytes_size):
    """바이트를 읽기 쉬운 형식으로 변환"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"

def check_mongodb_size(db_mongo, collection_name):
    """MongoDB 컬렉션 용량 조회"""
    try:
        # PyMongo 최신 버전에서는 command() 메서드를 사용
        stats = db_mongo.command("collStats", collection_name)
        
        size_mb = stats.get('size', 0) / (1024 * 1024)
        storage_size_mb = stats.get('storageSize', 0) / (1024 * 1024)
        index_size_mb = stats.get('totalIndexSize', 0) / (1024 * 1024)
        count = stats.get('count', 0)
        
        return {
            'collection': collection_name,
            'size_mb': size_mb,
            'storage_size_mb': storage_size_mb,
            'index_size_mb': index_size_mb,
            'total_size_mb': size_mb + index_size_mb,
            'count': count,
            'avg_size_per_doc_bytes': (stats.get('size', 0) / count) if count > 0 else 0
        }
    except Exception as e:
        return {
            'collection': collection_name,
            'error': str(e)
        }

def check_timescaledb_size(conn_tsdb, table_name):
    """TimescaleDB 테이블 용량 조회 (하이퍼테이블 포함, chunk 합산)"""
    try:
        cursor = conn_tsdb.cursor()
        
        # 하이퍼테이블인지 확인하고 크기 조회
        # TimescaleDB 하이퍼테이블의 경우 timescaledb_information 뷰 사용
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 
                FROM timescaledb_information.hypertables 
                WHERE hypertable_name = %s
            )
        """, (table_name,))
        is_hypertable = cursor.fetchone()[0]
        
        chunk_details = []
        
        if is_hypertable:
            # 하이퍼테이블의 경우: chunk 직접 합산 (가장 정확한 방법)
            # timescaledb_information.hypertable_sizes 뷰는 부정확할 수 있으므로 chunk 직접 조회
            cursor.execute("""
                SELECT 
                    chunk_schema || '.' || chunk_name AS chunk_full_name,
                    pg_total_relation_size(chunk_schema || '.' || chunk_name) AS chunk_total_bytes,
                    pg_relation_size(chunk_schema || '.' || chunk_name) AS chunk_table_bytes,
                    pg_indexes_size(chunk_schema || '.' || chunk_name) AS chunk_index_bytes
                FROM timescaledb_information.chunks
                WHERE hypertable_name = %s
                ORDER BY chunk_name
            """, (table_name,))
            chunks = cursor.fetchall()
            
            total_bytes = 0
            table_bytes = 0
            index_bytes = 0
            num_chunks = len(chunks)
            
            for chunk in chunks:
                chunk_total = chunk[1] if chunk[1] else 0
                chunk_table = chunk[2] if chunk[2] else 0
                chunk_index = chunk[3] if chunk[3] else 0
                
                total_bytes += chunk_total
                table_bytes += chunk_table
                index_bytes += chunk_index
                
                chunk_details.append({
                    'name': chunk[0],
                    'size_pretty': format_bytes(chunk_total),
                    'total_bytes': chunk_total,
                    'table_bytes': chunk_table,
                    'index_bytes': chunk_index
                })
            
            toast_bytes = 0
        else:
            # 일반 테이블의 경우
            cursor.execute(f"""
                SELECT pg_total_relation_size('{table_name}') AS total_size,
                       pg_relation_size('{table_name}') AS table_size,
                       pg_indexes_size('{table_name}') AS index_size
            """)
            size_info = cursor.fetchone()
            total_bytes = size_info[0]
            table_bytes = size_info[1]
            index_bytes = size_info[2]
            toast_bytes = 0
            num_chunks = 0
        
        # 레코드 개수
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        
        total_size_mb = total_bytes / (1024 * 1024)
        table_size_mb = table_bytes / (1024 * 1024)
        index_size_mb = index_bytes / (1024 * 1024)
        
        conn_tsdb.commit()  # 트랜잭션 커밋
        cursor.close()
        
        return {
            'table': table_name,
            'size_mb': table_size_mb,
            'index_size_mb': index_size_mb,
            'total_size_mb': total_size_mb,
            'count': count,
            'avg_size_per_row_bytes': (table_bytes / count) if count > 0 else 0,
            'is_hypertable': is_hypertable,
            'num_chunks': num_chunks if is_hypertable else None,
            'chunk_details': chunk_details if is_hypertable and chunk_details else None
        }
    except Exception as e:
        # timescaledb_information 뷰가 없는 경우 (TimescaleDB 확장이 설치되지 않았거나 오류)
        try:
            conn_tsdb.rollback()  # 이전 트랜잭션 롤백
            # 일반 테이블 크기 조회로 폴백
            cursor = conn_tsdb.cursor()
            cursor.execute(f"""
                SELECT pg_total_relation_size('{table_name}') AS total_size,
                       pg_relation_size('{table_name}') AS table_size,
                       pg_indexes_size('{table_name}') AS index_size
            """)
            size_info = cursor.fetchone()
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            
            total_size_bytes = size_info[0]
            table_size_bytes = size_info[1]
            index_size_bytes = size_info[2]
            
            total_size_mb = total_size_bytes / (1024 * 1024)
            table_size_mb = table_size_bytes / (1024 * 1024)
            index_size_mb = index_size_bytes / (1024 * 1024)
            
            conn_tsdb.commit()  # 트랜잭션 커밋
            cursor.close()
            
            return {
                'table': table_name,
                'size_mb': table_size_mb,
                'index_size_mb': index_size_mb,
                'total_size_mb': total_size_mb,
                'count': count,
                'avg_size_per_row_bytes': (table_size_bytes / count) if count > 0 else 0,
                'is_hypertable': False,
                'num_chunks': None
            }
        except Exception as e2:
            return {
                'table': table_name,
                'error': str(e2)
            }

def print_comparison(mongo_result, tsdb_result):
    """비교 결과 출력"""
    print("\n" + "="*80)
    print("📊 저장 용량 비교 결과")
    print("="*80)
    
    if 'error' in mongo_result:
        print(f"\n❌ MongoDB 오류: {mongo_result['error']}")
        return
    if 'error' in tsdb_result:
        print(f"\n❌ TimescaleDB 오류: {tsdb_result['error']}")
        return
    
    print(f"\n📁 MongoDB: {mongo_result['collection']}")
    print(f"   - 문서 수: {mongo_result['count']:,}개")
    print(f"   - 데이터 크기: {mongo_result['size_mb']:.2f} MB ({format_bytes(mongo_result['size_mb'] * 1024 * 1024)})")
    print(f"   - 저장 공간: {mongo_result['storage_size_mb']:.2f} MB ({format_bytes(mongo_result['storage_size_mb'] * 1024 * 1024)})")
    print(f"   - 인덱스 크기: {mongo_result['index_size_mb']:.2f} MB ({format_bytes(mongo_result['index_size_mb'] * 1024 * 1024)})")
    print(f"   - 총 크기 (데이터+인덱스): {mongo_result['total_size_mb']:.2f} MB ({format_bytes(mongo_result['total_size_mb'] * 1024 * 1024)})")
    print(f"   - 문서당 평균 크기: {mongo_result['avg_size_per_doc_bytes']:.2f} bytes")
    
    print(f"\n📁 TimescaleDB: {tsdb_result['table']}")
    print(f"   - 레코드 수: {tsdb_result['count']:,}개")
    print(f"   - 테이블 크기: {tsdb_result['size_mb']:.2f} MB ({format_bytes(tsdb_result['size_mb'] * 1024 * 1024)})")
    print(f"   - 인덱스 크기: {tsdb_result['index_size_mb']:.2f} MB ({format_bytes(tsdb_result['index_size_mb'] * 1024 * 1024)})")
    print(f"   - 총 크기 (테이블+인덱스): {tsdb_result['total_size_mb']:.2f} MB ({format_bytes(tsdb_result['total_size_mb'] * 1024 * 1024)})")
    print(f"   - 레코드당 평균 크기: {tsdb_result['avg_size_per_row_bytes']:.2f} bytes")
    if tsdb_result.get('is_hypertable'):
        print(f"   - 하이퍼테이블: 예 ({tsdb_result.get('num_chunks', 0)} chunks)")
        if tsdb_result.get('chunk_details') and len(tsdb_result['chunk_details']) > 0:
            print(f"   - Chunk 상세 정보 ({len(tsdb_result['chunk_details'])}개):")
            for chunk in tsdb_result['chunk_details']:
                print(f"     * {chunk['name']}: {chunk.get('size_pretty', format_bytes(chunk['total_bytes']))} (테이블: {format_bytes(chunk['table_bytes'])}, 인덱스: {format_bytes(chunk['index_bytes'])})")
        elif tsdb_result.get('num_chunks', 0) > 0:
            print(f"   ⚠️  Chunk 정보를 조회할 수 없습니다 (하이퍼테이블이지만 chunk가 조회되지 않음)")
    else:
        print(f"   - 하이퍼테이블: 아니오 (일반 테이블)")
    
    print("\n" + "-"*80)
    print("📈 비교 결과:")
    
    if mongo_result['total_size_mb'] > tsdb_result['total_size_mb']:
        diff = ((mongo_result['total_size_mb'] / tsdb_result['total_size_mb']) - 1) * 100
        print(f"   MongoDB가 TimescaleDB보다 {diff:.1f}% 큽니다")
        print(f"   절약 공간: {mongo_result['total_size_mb'] - tsdb_result['total_size_mb']:.2f} MB")
    else:
        diff = ((tsdb_result['total_size_mb'] / mongo_result['total_size_mb']) - 1) * 100
        print(f"   TimescaleDB가 MongoDB보다 {diff:.1f}% 큽니다")
        print(f"   절약 공간: {tsdb_result['total_size_mb'] - mongo_result['total_size_mb']:.2f} MB")
    
    if mongo_result['count'] == tsdb_result['count']:
        print(f"   ✅ 레코드 수가 동일합니다 ({mongo_result['count']:,}개)")
    else:
        print(f"   ⚠️  레코드 수가 다릅니다 (MongoDB: {mongo_result['count']:,}, TimescaleDB: {tsdb_result['count']:,})")

def main():
    """메인 함수"""
    print("\n" + "="*80)
    print("🔍 MongoDB vs TimescaleDB 저장 용량 비교")
    print("="*80)
    
    # 연결
    print("\n📡 데이터베이스 연결 중...")
    try:
        uri = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/"
        client = MongoClient(uri)
        db_mongo = client[MONGO_DB]
        print("✅ MongoDB 연결 완료")
    except Exception as e:
        print(f"❌ MongoDB 연결 실패: {e}")
        return
    
    try:
        conn_tsdb = psycopg2.connect(
            host=TIMESCALEDB_HOST,
            port=TIMESCALEDB_PORT,
            database=TIMESCALEDB_DB,
            user=TIMESCALEDB_USER,
            password=TIMESCALEDB_PASSWORD
        )
        print("✅ TimescaleDB 연결 완료")
    except Exception as e:
        print(f"❌ TimescaleDB 연결 실패: {e}")
        return
    
    # 테스트 데이터 비교 (write_performance_test)
    print("\n" + "-"*80)
    print("📊 테스트 데이터 비교 (write_performance_test)")
    print("-"*80)
    
    mongo_test_result = check_mongodb_size(db_mongo, "write_performance_test")
    tsdb_test_result = check_timescaledb_size(conn_tsdb, "write_performance_test")
    
    if 'error' not in mongo_test_result and 'error' not in tsdb_test_result:
        print_comparison(mongo_test_result, tsdb_test_result)
    
    # 실제 데이터 비교 (realtime-storage-data vs vehicle_telemetry)
    print("\n" + "-"*80)
    print("📊 실제 운영 데이터 비교")
    print("-"*80)
    
    mongo_real_result = check_mongodb_size(db_mongo, "realtime-storage-data")
    tsdb_real_result = check_timescaledb_size(conn_tsdb, "vehicle_telemetry")
    
    if 'error' not in mongo_real_result and 'error' not in tsdb_real_result:
        print_comparison(mongo_real_result, tsdb_real_result)
    else:
        if 'error' in mongo_real_result:
            print(f"⚠️  MongoDB realtime-storage-data: {mongo_real_result['error']}")
        if 'error' in tsdb_real_result:
            print(f"⚠️  TimescaleDB vehicle_telemetry: {tsdb_real_result['error']}")
    
    # 모든 컬렉션/테이블 용량 요약
    print("\n" + "="*80)
    print("📋 전체 컬렉션/테이블 용량 요약")
    print("="*80)
    
    print("\n📁 MongoDB 컬렉션:")
    try:
        collections = db_mongo.list_collection_names()
        for collection in collections:
            result = check_mongodb_size(db_mongo, collection)
            if 'error' not in result:
                print(f"   - {collection}: {result['total_size_mb']:.2f} MB ({result['count']:,}개 문서)")
    except Exception as e:
        print(f"   ⚠️  컬렉션 목록 조회 실패: {e}")
    
    print("\n📁 TimescaleDB 테이블:")
    cursor = conn_tsdb.cursor()
    cursor.execute("""
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public'
        ORDER BY tablename
    """)
    tables = [row[0] for row in cursor.fetchall()]
    cursor.close()
    
    for table in tables:
        result = check_timescaledb_size(conn_tsdb, table)
        if 'error' not in result:
            print(f"   - {table}: {result['total_size_mb']:.2f} MB ({result['count']:,}개 레코드)")
    
    print("\n" + "="*80)
    print("✅ 용량 비교 완료")
    print("="*80)

if __name__ == "__main__":
    main()

