#!/usr/bin/env python3
"""
MongoDB 샤딩 성능 비교 테스트
- 샤딩 전후 쓰기/읽기 성능 비교
- 실제 데이터 기반 측정
"""

import sys
import os
import time
from pymongo import MongoClient
from datetime import datetime, timedelta
import random

# MongoDB 연결 (샤딩 클러스터)
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))
MONGO_DB = os.getenv("MONGO_DB", "alcha_events")

def connect_mongodb_sharded():
    """샤딩된 MongoDB 연결"""
    uri = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/"
    client = MongoClient(uri)
    return client[MONGO_DB]

def test_sharded_write_performance(db):
    """테스트 1: 샤딩된 MongoDB 쓰기 성능"""
    print("\n" + "="*80)
    print("📝 테스트 1: 샤딩된 MongoDB 쓰기 성능 검증")
    print("="*80)
    print("목적: 샤딩을 통한 수평 확장으로 쓰기 성능 향상 측정")
    print("-"*80)
    
    # 기존 데이터 삭제
    test_collection = "sharded_write_test"
    
    # 샤딩이 활성화되지 않은 경우 샤딩 활성화
    try:
        db.command("shardingState")
        print("✅ 샤딩 클러스터 연결 확인")
    except:
        print("⚠️  샤딩 클러스터가 아닙니다. 일반 MongoDB로 테스트합니다.")
    
    # 테스트 데이터 생성 (50,000개 레코드 - 대량 데이터)
    print(f"\n대량 데이터 생성 중... (50,000개 레코드)")
    test_data = []
    base_time = datetime(2025, 9, 23, 1, 54, 26)
    for i in range(50000):
        vehicle_id = f"VHC-{random.randint(1, 100):03d}"  # 100개 차량으로 확장
        test_data.append({
            "vehicle_id": vehicle_id,
            "vehicle_speed": random.uniform(20, 120),
            "engine_rpm": random.randint(800, 6000),
            "throttle_position": random.uniform(0, 100),
            "timestamp": (base_time + timedelta(seconds=i)).strftime('%Y-%m-%dT%H:%M:%SZ'),
            "sensor_data": {
                "temperature": random.uniform(20, 100),
                "pressure": random.uniform(10, 50)
            }
        })
    
    # 배치 쓰기 테스트
    batch_sizes = [1000, 5000, 10000]
    
    print(f"배치 크기별 쓰기 성능 측정:\n")
    
    results = []
    for batch_size in batch_sizes:
        # 기존 데이터 삭제
        db[test_collection].drop()
        
        batches = [test_data[i:i+batch_size] for i in range(0, len(test_data), batch_size)]
        
        total_time = 0
        total_inserted = 0
        
        for batch in batches:
            start = time.time()
            result = db[test_collection].insert_many(batch)
            elapsed = time.time() - start
            total_time += elapsed
            total_inserted += len(result.inserted_ids)
        
        records_per_second = total_inserted / total_time
        avg_time_per_batch = total_time / len(batches)
        
        results.append({
            'batch_size': batch_size,
            'total_records': total_inserted,
            'total_time': total_time,
            'records_per_second': records_per_second,
            'avg_time_per_batch': avg_time_per_batch
        })
        
        print(f"  배치 크기 {batch_size}:")
        print(f"    - 총 레코드: {total_inserted}개")
        print(f"    - 총 시간: {total_time*1000:.2f}ms")
        print(f"    - 초당 처리: {records_per_second:.0f} 레코드/초")
        print(f"    - 배치당 평균: {avg_time_per_batch*1000:.2f}ms")
    
    # 최적 배치 크기
    best = max(results, key=lambda x: x['records_per_second'])
    print(f"\n최적 성능:")
    print(f"  배치 크기: {best['batch_size']}")
    print(f"  초당 처리: {best['records_per_second']:.0f} 레코드/초")
    
    return results

def test_sharded_read_performance(db):
    """테스트 2: 샤딩된 MongoDB 읽기 성능"""
    print("\n" + "="*80)
    print("📊 테스트 2: 샤딩된 MongoDB 읽기 성능 검증")
    print("="*80)
    print("목적: 샤딩을 통한 분산 읽기 성능 향상 측정")
    print("-"*80)
    
    # 실제 데이터가 있는지 확인
    collection = "realtime-storage-data"
    count = db[collection].count_documents({})
    
    if count == 0:
        print(f"⚠️  {collection} 컬렉션에 데이터가 없습니다.")
        print("   먼저 데이터를 생성해주세요.")
        return None
    
    print(f"\n{collection} 컬렉션: {count:,}개 레코드")
    
    # 다양한 읽기 패턴 테스트
    tests = [
        {
            "name": "단일 차량 시간 범위 쿼리 (샤드 키 사용)",
            "operation": lambda: list(db[collection].find({
                "vehicle_id": "VHC-001",
                "timestamp": {"$gte": "2025-09-23T01:54:26Z", "$lte": "2025-09-23T02:54:26Z"}
            }).sort("timestamp", 1).limit(3600))
        },
        {
            "name": "다중 차량 시간 범위 쿼리",
            "operation": lambda: list(db[collection].find({
                "vehicle_id": {"$in": ["VHC-001", "VHC-002", "VHC-003"]},
                "timestamp": {"$gte": "2025-09-23T01:54:26Z", "$lte": "2025-09-23T02:54:26Z"}
            }).sort("timestamp", 1).limit(10800))
        },
        {
            "name": "집계 쿼리 (평균/최대/최소)",
            "operation": lambda: list(db[collection].aggregate([
                {"$match": {
                    "vehicle_id": "VHC-001",
                    "timestamp": {"$gte": "2025-09-23T01:54:26Z", "$lte": "2025-09-23T02:54:26Z"}
                }},
                {"$group": {
                    "_id": None,
                    "avg_speed": {"$avg": "$vehicle_speed"},
                    "max_speed": {"$max": "$vehicle_speed"},
                    "min_speed": {"$min": "$vehicle_speed"},
                    "avg_rpm": {"$avg": "$engine_rpm"},
                    "count": {"$sum": 1}
                }}
            ]))
        },
        {
            "name": "전체 컬렉션 스캔 (샤딩 이점)",
            "operation": lambda: list(db[collection].find({}).limit(10000))
        }
    ]
    
    print(f"\n읽기 성능 측정 (각 테스트 10회 반복, 평균값 사용):\n")
    
    results = []
    for test in tests:
        times = []
        result_count = 0
        
        for _ in range(10):
            start = time.time()
            result = test["operation"]()
            times.append(time.time() - start)
            if not result_count:
                result_count = len(result)
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
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
    
    return results

def test_sharding_status(db):
    """테스트 3: 샤딩 상태 확인"""
    print("\n" + "="*80)
    print("📊 테스트 3: 샤딩 상태 확인")
    print("="*80)
    
    try:
        # 샤딩 상태 확인
        sharding_state = db.command("shardingState")
        print(f"✅ 샤딩 클러스터에 연결됨")
        
        # 샤드 분포 확인
        collection = "realtime-storage-data"
        if collection in db.list_collection_names():
            stats = db.command("collStats", collection)
            print(f"\n{collection} 컬렉션 샤딩 통계:")
            print(f"  - 샤드 수: {len(stats.get('shards', {}))}")
            print(f"  - 총 데이터 크기: {stats.get('size', 0):,} bytes")
            
            for shard_name, shard_stats in stats.get('shards', {}).items():
                print(f"  - {shard_name}:")
                print(f"      데이터 크기: {shard_stats.get('size', 0):,} bytes")
                print(f"      문서 수: {shard_stats.get('count', 0):,}개")
        
        return True
        
    except Exception as e:
        print(f"⚠️  샤딩 상태 확인 실패: {e}")
        print("   일반 MongoDB로 실행 중입니다.")
        return False

def compare_with_previous_results():
    """이전 테스트 결과와 비교"""
    print("\n" + "="*80)
    print("📊 샤딩 전후 성능 비교")
    print("="*80)
    
    print("\n이전 테스트 결과 (일반 MongoDB):")
    print("  - 최적 쓰기 성능: 168,501 레코드/초 (배치 크기 10,000)")
    print("  - 시간 범위 쿼리: 20.44ms (평균)")
    print("  - 집계 쿼리: 5.59ms (평균)")
    
    print("\n샤딩 클러스터 테스트 결과:")
    print("  (위 테스트 결과 참조)")

def main():
    """메인 테스트 함수"""
    print("\n" + "="*80)
    print("🔬 MongoDB 샤딩 성능 검증 테스트")
    print("="*80)
    print("목적: 샤딩을 통한 수평 확장으로 성능 최적화 검증")
    print("="*80)
    
    # 연결
    print("\n📡 샤딩된 MongoDB 연결 중...")
    db = connect_mongodb_sharded()
    print("✅ 연결 완료")
    
    try:
        # 샤딩 상태 확인
        is_sharded = test_sharding_status(db)
        
        # 테스트 실행
        print("\n" + "="*80)
        print("테스트 시작")
        print("="*80)
        
        write_results = test_sharded_write_performance(db)
        read_results = test_sharded_read_performance(db)
        
        # 비교
        if write_results:
            compare_with_previous_results()
        
        print("\n" + "="*80)
        print("✅ 모든 테스트 완료")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

