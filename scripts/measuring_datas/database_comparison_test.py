#!/usr/bin/env python3
"""
MongoDB vs TimescaleDB 실제 성능 검증 테스트
- 데이터에 기반한 실제 측정값만 표시
- 좋게 포장하지 않고 실제 결과만 제시
- Prometheus 메트릭 export 지원
"""

import sys
import os
import time
from pymongo import MongoClient
import psycopg2
from datetime import datetime, timedelta
import random
from prometheus_client import start_http_server, Gauge, Histogram

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

# Prometheus 메트릭 설정
METRICS_PORT = int(os.getenv("METRICS_PORT", "8000"))

# Prometheus 메트릭 정의
db_write_records_per_second = Gauge(
    'db_write_records_per_second',
    '초당 쓰기 처리 레코드 수',
    ['db', 'batch_size']
)

db_write_time_seconds = Histogram(
    'db_write_time_seconds',
    '쓰기 작업 소요 시간 (초)',
    ['db', 'batch_size'],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

db_read_query_time_seconds = Histogram(
    'db_read_query_time_seconds',
    '읽기 쿼리 소요 시간 (초)',
    ['db', 'query_type'],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

db_read_query_time_gauge = Gauge(
    'db_read_query_time_gauge_seconds',
    '읽기 쿼리 소요 시간 (초) - 게이지',
    ['db', 'query_type']
)

def connect_mongodb():
    """MongoDB 연결"""
    uri = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/"
    client = MongoClient(uri)
    return client[MONGO_DB]

def connect_timescaledb():
    """TimescaleDB 연결"""
    conn = psycopg2.connect(
        host=TIMESCALEDB_HOST,
        port=TIMESCALEDB_PORT,
        database=TIMESCALEDB_DB,
        user=TIMESCALEDB_USER,
        password=TIMESCALEDB_PASSWORD
    )
    return conn

def test_mongodb_write_performance(db_mongo):
    """테스트 1: MongoDB 쓰기 성능 검증"""
    print("\n" + "="*80)
    print("📝 테스트 1: MongoDB 쓰기 성능 검증")
    print("="*80)
    print("목적: MongoDB를 사용하는 핵심 이유인 빠른 쓰기 속도 검증")
    print("-"*80)
    
    # 기존 데이터 삭제
    test_collection = "write_performance_test"
    db_mongo[test_collection].drop()
    
    # 테스트 데이터 생성 (432,000개 레코드)
    test_data = []
    base_time = datetime(2025, 9, 23, 1, 54, 26)
    for i in range(432000):
        test_data.append({
            "vehicle_id": f"VHC-{random.randint(1, 10):03d}",
            "vehicle_speed": random.uniform(20, 120),
            "engine_rpm": random.randint(800, 6000),
            "throttle_position": random.uniform(0, 100),
            "timestamp": (base_time + timedelta(seconds=i)).strftime('%Y-%m-%dT%H:%M:%SZ'),
            "sensor_data": {
                "temperature": random.uniform(20, 100),
                "pressure": random.uniform(10, 50),
                "additional_field_1": f"value_{i}",
                "additional_field_2": random.randint(1, 1000),
                "nested_data": {
                    "x": random.uniform(-10, 10),
                    "y": random.uniform(-10, 10),
                    "z": random.uniform(8, 12)
                }
            }
        })
    
    # 배치 쓰기 테스트
    batch_sizes = [1000, 10000, 50000, 100000]
    
    print(f"\n테스트 데이터: {len(test_data)}개 레코드 준비 완료")
    print(f"배치 크기별 쓰기 성능 측정:\n")
    
    results = []
    for batch_size in batch_sizes:
        db_mongo[test_collection].drop()  # 초기화
        batches = [test_data[i:i+batch_size] for i in range(0, len(test_data), batch_size)]
        
        total_time = 0
        total_inserted = 0
        
        print(f"  배치 크기 {batch_size}:")
        print(f"    배치 개수: {len(batches)}개, 배치당 평균 레코드: {len(test_data) // len(batches)}개")
        
        for batch_idx, batch in enumerate(batches):
            start = time.time()
            result = db_mongo[test_collection].insert_many(batch)
            elapsed = time.time() - start
            total_time += elapsed
            total_inserted += len(result.inserted_ids)
            
            # 진행 상황 표시 (큰 배치의 경우)
            if batch_size >= 10000:
                if (batch_idx + 1) % max(1, len(batches) // 20) == 0 or (batch_idx + 1) == len(batches):
                    print(f"      진행: {batch_idx + 1}/{len(batches)} 배치 완료... ({batch_idx * batch_size}/{len(test_data)} 레코드)")
        
        records_per_second = total_inserted / total_time
        avg_time_per_batch = total_time / len(batches)
        
        results.append({
            'batch_size': batch_size,
            'total_records': total_inserted,
            'total_time': total_time,
            'records_per_second': records_per_second,
            'avg_time_per_batch': avg_time_per_batch
        })
        
        print(f"    결과:")
        print(f"      - 총 레코드: {total_inserted}개")
        print(f"      - 총 시간: {total_time:.2f}초 ({total_time*1000:.2f}ms)")
        print(f"      - 초당 처리: {records_per_second:.0f} 레코드/초")
        print(f"      - 배치당 평균: {avg_time_per_batch:.2f}초 ({avg_time_per_batch*1000:.2f}ms)")
        
        # Prometheus 메트릭 업데이트
        db_write_records_per_second.labels(db='mongodb', batch_size=str(batch_size)).set(records_per_second)
        db_write_time_seconds.labels(db='mongodb', batch_size=str(batch_size)).observe(total_time)
    
    # 최적 배치 크기
    best = max(results, key=lambda x: x['records_per_second'])
    print(f"\n최적 성능:")
    print(f"  배치 크기: {best['batch_size']}")
    print(f"  초당 처리: {best['records_per_second']:.0f} 레코드/초")
    
    return results

def test_timescaledb_write_performance(conn_tsdb):
    """테스트 2: TimescaleDB 쓰기 성능 검증"""
    print("\n" + "="*80)
    print("📝 테스트 2: TimescaleDB 쓰기 성능 검증")
    print("="*80)
    print("목적: TimescaleDB의 쓰기 성능 측정 및 MongoDB와 비교")
    print("-"*80)
    
    cursor = conn_tsdb.cursor()
    
    # 테스트 테이블 생성
    cursor.execute("""
        DROP TABLE IF EXISTS write_performance_test CASCADE;
    """)
    cursor.execute("""
        CREATE TABLE write_performance_test (
            vehicle_id VARCHAR(50) NOT NULL,
            vehicle_speed FLOAT,
            engine_rpm INTEGER,
            throttle_position FLOAT,
            timestamp TIMESTAMPTZ NOT NULL
        );
    """)
    cursor.execute("SELECT create_hypertable('write_performance_test', 'timestamp', if_not_exists => TRUE);")
    conn_tsdb.commit()
    
    # 테스트 데이터 생성 (432,000개 레코드)
    test_data = []
    base_time = datetime(2025, 9, 23, 1, 54, 26)
    for i in range(432000):
        test_data.append((
            f"VHC-{random.randint(1, 10):03d}",
            random.uniform(20, 120),
            random.randint(800, 6000),
            random.uniform(0, 100),
            (base_time + timedelta(seconds=i)).strftime('%Y-%m-%dT%H:%M:%SZ')
        ))
    
    # 배치 쓰기 테스트
    batch_sizes = [1000, 10000, 50000, 100000]
    
    print(f"\n테스트 데이터: {len(test_data)}개 레코드 준비 완료")
    print(f"배치 크기별 쓰기 성능 측정:\n")
    
    results = []
    for batch_size in batch_sizes:
        cursor.execute("DELETE FROM write_performance_test;")
        conn_tsdb.commit()
        
        batches = [test_data[i:i+batch_size] for i in range(0, len(test_data), batch_size)]
        
        total_time = 0
        total_inserted = 0
        
        print(f"  배치 크기 {batch_size}:")
        print(f"    배치 개수: {len(batches)}개, 배치당 평균 레코드: {len(test_data) // len(batches)}개")
        
        for batch_idx, batch in enumerate(batches):
            start = time.time()
            cursor.executemany("""
                INSERT INTO write_performance_test (vehicle_id, vehicle_speed, engine_rpm, throttle_position, timestamp)
                VALUES (%s, %s, %s, %s, %s)
            """, batch)
            conn_tsdb.commit()
            elapsed = time.time() - start
            total_time += elapsed
            total_inserted += len(batch)
            
            # 진행 상황 표시 (큰 배치의 경우)
            if batch_size >= 10000:
                if (batch_idx + 1) % max(1, len(batches) // 20) == 0 or (batch_idx + 1) == len(batches):
                    print(f"      진행: {batch_idx + 1}/{len(batches)} 배치 완료... ({batch_idx * batch_size}/{len(test_data)} 레코드)")
        
        records_per_second = total_inserted / total_time
        avg_time_per_batch = total_time / len(batches)
        
        results.append({
            'batch_size': batch_size,
            'total_records': total_inserted,
            'total_time': total_time,
            'records_per_second': records_per_second,
            'avg_time_per_batch': avg_time_per_batch
        })
        
        print(f"    결과:")
        print(f"      - 총 레코드: {total_inserted}개")
        print(f"      - 총 시간: {total_time:.2f}초 ({total_time*1000:.2f}ms)")
        print(f"      - 초당 처리: {records_per_second:.0f} 레코드/초")
        print(f"      - 배치당 평균: {avg_time_per_batch:.2f}초 ({avg_time_per_batch*1000:.2f}ms)")
        
        # Prometheus 메트릭 업데이트
        db_write_records_per_second.labels(db='timescaledb', batch_size=str(batch_size)).set(records_per_second)
        db_write_time_seconds.labels(db='timescaledb', batch_size=str(batch_size)).observe(total_time)
    
    # 최적 배치 크기
    best = max(results, key=lambda x: x['records_per_second'])
    print(f"\n최적 성능:")
    print(f"  배치 크기: {best['batch_size']}")
    print(f"  초당 처리: {best['records_per_second']:.0f} 레코드/초")
    
    cursor.close()
    return results

def test_timescaledb_time_series_query_performance(conn_tsdb):
    """테스트 3: TimescaleDB 시계열 데이터 처리 성능 검증"""
    print("\n" + "="*80)
    print("📊 테스트 3: TimescaleDB 시계열 데이터 처리 성능 검증")
    print("="*80)
    print("목적: TimescaleDB를 사용하는 핵심 이유인 시계열 쿼리 성능 검증")
    print("-"*80)
    
    cursor = conn_tsdb.cursor()
    
    # 실제 데이터 기준 테스트
    vehicle_ids = ["VHC-001", "VHC-002", "VHC-003"]
    
    tests = [
        {
            "name": "시간 범위 쿼리 (40시간 데이터)",
            "query": """
                SELECT vehicle_id, vehicle_speed, engine_rpm, throttle_position, timestamp
                FROM vehicle_telemetry
                WHERE vehicle_id = %s 
                  AND timestamp >= %s 
                  AND timestamp <= %s
                ORDER BY timestamp ASC
            """,
            "params": lambda vid: (vid, "2025-09-23T01:54:26Z", "2025-09-24T17:54:26Z")  # 40시간 범위
        },
        {
            "name": "집계 쿼리 (평균/최대/최소)",
            "query": """
                SELECT 
                    COUNT(*) as count,
                    AVG(vehicle_speed) as avg_speed,
                    MAX(vehicle_speed) as max_speed,
                    MIN(vehicle_speed) as min_speed,
                    AVG(engine_rpm) as avg_rpm,
                    MAX(engine_rpm) as max_rpm,
                    MIN(engine_rpm) as min_rpm
                FROM vehicle_telemetry
                WHERE vehicle_id = %s 
                  AND timestamp >= %s 
                  AND timestamp <= %s
            """,
            "params": lambda vid: (vid, "2025-09-23T01:54:26Z", "2025-09-24T17:54:26Z")  # 40시간 범위
        },
        {
            "name": "시간 기반 그룹화 (10분 단위)",
            "query": """
                SELECT 
                    time_bucket('10 minutes', timestamp) as bucket,
                    AVG(vehicle_speed) as avg_speed,
                    COUNT(*) as count
                FROM vehicle_telemetry
                WHERE vehicle_id = %s 
                  AND timestamp >= %s 
                  AND timestamp <= %s
                GROUP BY bucket
                ORDER BY bucket ASC
            """,
            "params": lambda vid: (vid, "2025-09-23T01:54:26Z", "2025-09-24T17:54:26Z")  # 40시간 범위
        },
        {
            "name": "시간 기반 그룹화 (1분 단위)",
            "query": """
                SELECT 
                    time_bucket('1 minute', timestamp) as bucket,
                    AVG(vehicle_speed) as avg_speed,
                    COUNT(*) as count
                FROM vehicle_telemetry
                WHERE vehicle_id = %s 
                  AND timestamp >= %s 
                  AND timestamp <= %s
                GROUP BY bucket
                ORDER BY bucket ASC
            """,
            "params": lambda vid: (vid, "2025-09-23T01:54:26Z", "2025-09-24T17:54:26Z")  # 40시간 범위
        },
        {
            "name": "복잡한 시간 범위 집계 (다중 차량)",
            "query": """
                SELECT 
                    vehicle_id,
                    time_bucket('5 minutes', timestamp) as bucket,
                    AVG(vehicle_speed) as avg_speed,
                    MAX(vehicle_speed) as max_speed,
                    COUNT(*) as count
                FROM vehicle_telemetry
                WHERE vehicle_id IN (%s, %s, %s)
                  AND timestamp >= %s 
                  AND timestamp <= %s
                GROUP BY vehicle_id, bucket
                ORDER BY vehicle_id, bucket ASC
            """,
            "params": lambda vid: ("VHC-001", "VHC-002", "VHC-003", "2025-09-23T01:54:26Z", "2025-09-24T17:54:26Z")  # 40시간 범위
        }
    ]
    
    print(f"\n시계열 쿼리 성능 측정 (각 테스트 10회 반복, 평균값 사용):\n")
    
    results = []
    for test in tests:
        times = []
        for _ in range(10):
            start = time.time()
            if "vehicle_id IN" in test["query"]:
                cursor.execute(test["query"], test["params"](None))
            else:
                cursor.execute(test["query"], test["params"]("VHC-001"))
            cursor.fetchall()
            times.append(time.time() - start)
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        # 결과 개수 확인 (한 번만 실행)
        if "vehicle_id IN" in test["query"]:
            cursor.execute(test["query"], test["params"](None))
        else:
            cursor.execute(test["query"], test["params"]("VHC-001"))
        result_count = len(cursor.fetchall())
        
        results.append({
            'name': test['name'],
            'avg_time': avg_time,
            'min_time': min_time,
            'max_time': max_time,
            'result_count': result_count
        })
        
        print(f"  {test['name']}:")
        print(f"    - 평균 시간: {avg_time*1000:.2f}ms")
        print(f"    - 최소 시간: {min_time*1000:.2f}ms")
        print(f"    - 최대 시간: {max_time*1000:.2f}ms")
        print(f"    - 결과 개수: {result_count}개")
        
        # Prometheus 메트릭 업데이트
        query_type_map = {
            '시간 범위 쿼리 (40시간 데이터)': 'time_range',
            '집계 쿼리 (평균/최대/최소)': 'aggregation',
            '시간 기반 그룹화 (10분 단위)': 'time_grouping_10min',
            '시간 기반 그룹화 (1분 단위)': 'time_grouping_1min',
            '복잡한 시간 범위 집계 (다중 차량)': 'multi_vehicle_aggregation'
        }
        query_type = query_type_map.get(test['name'], 'unknown')
        
        for time_val in times:
            db_read_query_time_seconds.labels(db='timescaledb', query_type=query_type).observe(time_val)
        db_read_query_time_gauge.labels(db='timescaledb', query_type=query_type).set(avg_time)
    
    cursor.close()
    return results

def test_mongodb_time_series_query_performance(db_mongo):
    """테스트 4: MongoDB 시계열 데이터 처리 성능 검증 (비교용)"""
    print("\n" + "="*80)
    print("📊 테스트 4: MongoDB 시계열 데이터 처리 성능 검증 (비교용)")
    print("="*80)
    print("목적: MongoDB의 시계열 쿼리 성능 측정 및 TimescaleDB와 비교")
    print("-"*80)
    
    vehicle_id = "VHC-001"
    start_time = "2025-09-23T01:54:26Z"
    end_time = "2025-09-24T17:54:26Z"  # 40시간 후
    
    tests = [
        {
            "name": "시간 범위 쿼리 (40시간 데이터)",
            "operation": lambda: list(db_mongo["realtime-storage-data"].find({
                "vehicle_id": vehicle_id,
                "timestamp": {"$gte": start_time, "$lte": end_time}
            }).sort("timestamp", 1))
        },
        {
            "name": "집계 쿼리 (평균/최대/최소)",
            "operation": lambda: list(db_mongo["realtime-storage-data"].aggregate([
                {"$match": {
                    "vehicle_id": vehicle_id,
                    "timestamp": {"$gte": start_time, "$lte": end_time}
                }},
                {"$group": {
                    "_id": None,
                    "avg_speed": {"$avg": "$vehicle_speed"},
                    "max_speed": {"$max": "$vehicle_speed"},
                    "min_speed": {"$min": "$vehicle_speed"},
                    "avg_rpm": {"$avg": "$engine_rpm"},
                    "max_rpm": {"$max": "$engine_rpm"},
                    "min_rpm": {"$min": "$engine_rpm"},
                    "count": {"$sum": 1}
                }}
            ]))
        },
        {
            "name": "시간 기반 그룹화 (10분 단위)",
            "operation": lambda: list(db_mongo["realtime-storage-data"].aggregate([
                {"$match": {
                    "vehicle_id": vehicle_id,
                    "timestamp": {"$gte": start_time, "$lte": end_time}
                }},
                {"$addFields": {
                    "timestamp_iso": {"$dateFromString": {"dateString": "$timestamp"}}
                }},
                {"$group": {
                    "_id": {
                        "$dateTrunc": {
                            "date": "$timestamp_iso",
                            "unit": "minute",
                            "binSize": 10
                        }
                    },
                    "avg_speed": {"$avg": "$vehicle_speed"},
                    "count": {"$sum": 1}
                }},
                {"$sort": {"_id": 1}}
            ]))
        }
    ]
    
    print(f"\n시계열 쿼리 성능 측정 (각 테스트 10회 반복, 평균값 사용):\n")
    
    results = []
    for test in tests:
        times = []
        for _ in range(10):
            start = time.time()
            result = test["operation"]()
            times.append(time.time() - start)
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        result_count = len(result)
        
        results.append({
            'name': test['name'],
            'avg_time': avg_time,
            'min_time': min_time,
            'max_time': max_time,
            'result_count': result_count
        })
        
        print(f"  {test['name']}:")
        print(f"    - 평균 시간: {avg_time*1000:.2f}ms")
        print(f"    - 최소 시간: {min_time*1000:.2f}ms")
        print(f"    - 최대 시간: {max_time*1000:.2f}ms")
        print(f"    - 결과 개수: {result_count}개")
        
        # Prometheus 메트릭 업데이트
        query_type_map = {
            '시간 범위 쿼리 (40시간 데이터)': 'time_range',
            '집계 쿼리 (평균/최대/최소)': 'aggregation',
            '시간 기반 그룹화 (10분 단위)': 'time_grouping_10min'
        }
        query_type = query_type_map.get(test['name'], 'unknown')
        
        for time_val in times:
            db_read_query_time_seconds.labels(db='mongodb', query_type=query_type).observe(time_val)
        db_read_query_time_gauge.labels(db='mongodb', query_type=query_type).set(avg_time)
    
    return results

def print_comparison_summary(mongo_write, tsdb_write, tsdb_read, mongo_read):
    """비교 요약 출력"""
    print("\n" + "="*80)
    print("📊 종합 비교 요약")
    print("="*80)
    
    # 쓰기 성능 비교
    mongo_best = max(mongo_write, key=lambda x: x['records_per_second'])
    tsdb_best = max(tsdb_write, key=lambda x: x['records_per_second'])
    
    print(f"\n1. 쓰기 성능 (최적 배치 크기 기준):")
    print(f"   MongoDB:")
    print(f"     - 초당 처리: {mongo_best['records_per_second']:.0f} 레코드/초")
    print(f"     - 배치 크기: {mongo_best['batch_size']}")
    print(f"   TimescaleDB:")
    print(f"     - 초당 처리: {tsdb_best['records_per_second']:.0f} 레코드/초")
    print(f"     - 배치 크기: {tsdb_best['batch_size']}")
    
    if mongo_best['records_per_second'] > tsdb_best['records_per_second']:
        diff = (mongo_best['records_per_second'] / tsdb_best['records_per_second'] - 1) * 100
        print(f"   → MongoDB가 {diff:.1f}% 빠름")
    else:
        diff = (tsdb_best['records_per_second'] / mongo_best['records_per_second'] - 1) * 100
        print(f"   → TimescaleDB가 {diff:.1f}% 빠름")
    
    # 읽기 성능 비교 (동일한 쿼리만 비교)
    print(f"\n2. 시계열 읽기 성능 (평균값 기준):")
    
    common_tests = [
        ("시간 범위 쿼리", "시간 범위 쿼리 (40시간 데이터)"),
        ("집계 쿼리", "집계 쿼리 (평균/최대/최소)"),
        ("시간 기반 그룹화", "시간 기반 그룹화 (10분 단위)")
    ]
    
    for test_name, mongo_key in common_tests:
        mongo_test = next((t for t in mongo_read if mongo_key in t['name']), None)
        tsdb_test = next((t for t in tsdb_read if test_name in t['name'] or mongo_key in t['name']), None)
        
        if mongo_test and tsdb_test:
            print(f"\n   {test_name}:")
            print(f"     - MongoDB: {mongo_test['avg_time']*1000:.2f}ms")
            print(f"     - TimescaleDB: {tsdb_test['avg_time']*1000:.2f}ms")
            if mongo_test['avg_time'] > tsdb_test['avg_time']:
                diff = (mongo_test['avg_time'] / tsdb_test['avg_time'] - 1) * 100
                print(f"     → TimescaleDB가 {diff:.1f}% 빠름")
            else:
                diff = (tsdb_test['avg_time'] / mongo_test['avg_time'] - 1) * 100
                print(f"     → MongoDB가 {diff:.1f}% 빠름")
    
    print(f"\n3. 결론:")
    print(f"   - MongoDB 쓰기: {mongo_best['records_per_second']:.0f} 레코드/초")
    print(f"   - TimescaleDB 쓰기: {tsdb_best['records_per_second']:.0f} 레코드/초")
    print(f"   - 시계열 쿼리: 실제 측정값 기준으로 판단")

def main():
    """메인 테스트 함수"""
    print("\n" + "="*80)
    print("🔬 MongoDB vs TimescaleDB 실제 성능 검증 테스트")
    print("="*80)
    print("주의: 실제 데이터 기반 측정값만 표시")
    print("="*80)
    
    # Prometheus 메트릭 서버 시작
    print(f"\n📊 Prometheus 메트릭 서버 시작 (포트 {METRICS_PORT})...")
    start_http_server(METRICS_PORT)
    print(f"✅ 메트릭 서버 시작 완료: http://localhost:{METRICS_PORT}/metrics")
    
    # 연결
    print("\n📡 데이터베이스 연결 중...")
    db_mongo = connect_mongodb()
    conn_tsdb = connect_timescaledb()
    print("✅ 연결 완료")
    
    try:
        # 테스트 실행
        print("\n" + "="*80)
        print("테스트 시작")
        print("="*80)
        
        mongo_write_results = test_mongodb_write_performance(db_mongo)
        tsdb_write_results = test_timescaledb_write_performance(conn_tsdb)
        tsdb_read_results = test_timescaledb_time_series_query_performance(conn_tsdb)
        mongo_read_results = test_mongodb_time_series_query_performance(db_mongo)
        
        # 비교 요약
        print_comparison_summary(mongo_write_results, tsdb_write_results, tsdb_read_results, mongo_read_results)
        
        print("\n" + "="*80)
        print("✅ 모든 테스트 완료")
        print("="*80)
        print(f"\n📊 Prometheus 메트릭 서버가 계속 실행 중입니다.")
        print(f"   메트릭 엔드포인트: http://localhost:{METRICS_PORT}/metrics")
        print(f"   Grafana 대시보드: http://localhost:3000")
        print(f"   Prometheus UI: http://localhost:9090")
        print(f"\n⚠️  메트릭 서버를 종료하려면 Ctrl+C를 누르세요.\n")
        
        # 메트릭 서버를 계속 실행하도록 대기
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n✅ 메트릭 서버 종료")
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn_tsdb.close()

if __name__ == "__main__":
    main()
