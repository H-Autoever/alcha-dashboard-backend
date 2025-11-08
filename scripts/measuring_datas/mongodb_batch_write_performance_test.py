#!/usr/bin/env python3
"""
MongoDB 배치 쓰기 성능 테스트
- 배치 크기별 쓰기 성능 측정
- Prometheus 메트릭 export 지원
- Grafana로 시각화
"""

import sys
import os
import time
from pymongo import MongoClient
from datetime import datetime, timedelta
import random
from prometheus_client import start_http_server, Gauge, Histogram, Summary

# MongoDB 연결
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))
MONGO_DB = os.getenv("MONGO_DB", "alcha_events")

# Prometheus 메트릭 설정
METRICS_PORT = int(os.getenv("METRICS_PORT", "8001"))

# Prometheus 메트릭 정의
mongodb_batch_write_records_per_second = Gauge(
    'mongodb_batch_write_records_per_second',
    '초당 쓰기 처리 레코드 수',
    ['batch_size']
)

mongodb_batch_write_time_seconds = Histogram(
    'mongodb_batch_write_time_seconds',
    '배치 쓰기 작업 소요 시간 (초)',
    ['batch_size'],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

mongodb_batch_write_time_summary = Summary(
    'mongodb_batch_write_time_summary_seconds',
    '배치 쓰기 작업 소요 시간 요약 (초)',
    ['batch_size']
)

mongodb_batch_size_gauge = Gauge(
    'mongodb_batch_size',
    '테스트된 배치 크기',
    ['batch_size']
)

mongodb_total_records_gauge = Gauge(
    'mongodb_total_records_inserted',
    '총 삽입된 레코드 수',
    ['batch_size']
)

mongodb_avg_batch_time_gauge = Gauge(
    'mongodb_avg_batch_time_seconds',
    '배치당 평균 쓰기 시간 (초)',
    ['batch_size']
)

def connect_mongodb():
    """MongoDB 연결"""
    uri = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/"
    client = MongoClient(uri)
    return client[MONGO_DB]

def generate_test_data(num_records):
    """테스트 데이터 생성"""
    test_data = []
    base_time = datetime(2025, 9, 23, 1, 54, 26)
    for i in range(num_records):
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
    return test_data

def test_mongodb_batch_write_performance(db_mongo):
    """MongoDB 배치 쓰기 성능 테스트"""
    print("\n" + "="*80)
    print("📝 MongoDB 배치 쓰기 성능 테스트")
    print("="*80)
    print("목적: 배치 크기별 MongoDB 쓰기 성능 측정")
    print("-"*80)
    
    # 테스트 컬렉션
    test_collection = "batch_write_performance_test"
    
    # 배치 크기 설정 (10000부터 100000까지 10000씩 증가)
    batch_sizes = [10000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000]
    
    # 총 테스트 데이터 개수 (각 배치 크기별로 동일한 총 데이터량)
    total_test_records = 1000000  # 100만 개 레코드
    
    print(f"\n테스트 설정:")
    print(f"  - 총 테스트 레코드: {total_test_records:,}개")
    print(f"  - 배치 크기: {batch_sizes}")
    print(f"  - 각 배치 크기별로 동일한 양의 데이터를 여러 배치로 나누어 테스트\n")
    
    results = []
    
    for batch_size in batch_sizes:
        print(f"\n{'='*80}")
        print(f"배치 크기: {batch_size:,}개 레코드/배치")
        print(f"{'='*80}")
        
        # 기존 데이터 삭제
        db_mongo[test_collection].drop()
        
        # 테스트 데이터 생성
        print(f"  테스트 데이터 생성 중... ({total_test_records:,}개 레코드)")
        test_data = generate_test_data(total_test_records)
        
        # 배치로 나누기
        batches = [test_data[i:i+batch_size] for i in range(0, len(test_data), batch_size)]
        num_batches = len(batches)
        
        print(f"  총 {num_batches}개의 배치로 나뉨")
        print(f"  배치당 평균 레코드: {len(test_data) // num_batches}개\n")
        
        # 배치 쓰기 테스트 시작
        print(f"  배치 쓰기 시작...")
        total_time = 0
        total_inserted = 0
        batch_times = []
        
        for batch_idx, batch in enumerate(batches):
            start = time.time()
            try:
                result = db_mongo[test_collection].insert_many(batch, ordered=False)
                elapsed = time.time() - start
                total_time += elapsed
                total_inserted += len(result.inserted_ids)
                batch_times.append(elapsed)
                
                # 진행 상황 표시
                if (batch_idx + 1) % max(1, num_batches // 10) == 0 or (batch_idx + 1) == num_batches:
                    progress = (batch_idx + 1) / num_batches * 100
                    records_inserted = (batch_idx + 1) * batch_size
                    if records_inserted > total_test_records:
                        records_inserted = total_test_records
                    print(f"    진행: {batch_idx + 1}/{num_batches} 배치 완료 ({progress:.1f}%) - {records_inserted:,}/{total_test_records:,} 레코드")
            except Exception as e:
                print(f"    ❌ 배치 {batch_idx + 1} 실패: {e}")
                elapsed = time.time() - start
                total_time += elapsed
        
        # 결과 계산
        records_per_second = total_inserted / total_time if total_time > 0 else 0
        avg_time_per_batch = total_time / num_batches if num_batches > 0 else 0
        min_batch_time = min(batch_times) if batch_times else 0
        max_batch_time = max(batch_times) if batch_times else 0
        
        result = {
            'batch_size': batch_size,
            'num_batches': num_batches,
            'total_records': total_inserted,
            'total_time': total_time,
            'records_per_second': records_per_second,
            'avg_time_per_batch': avg_time_per_batch,
            'min_batch_time': min_batch_time,
            'max_batch_time': max_batch_time,
            'batch_times': batch_times
        }
        results.append(result)
        
        # 결과 출력
        print(f"\n  ✅ 결과:")
        print(f"    - 총 레코드: {total_inserted:,}개")
        print(f"    - 총 시간: {total_time:.2f}초 ({total_time*1000:.2f}ms)")
        print(f"    - 초당 처리: {records_per_second:,.0f} 레코드/초")
        print(f"    - 배치당 평균: {avg_time_per_batch:.3f}초 ({avg_time_per_batch*1000:.2f}ms)")
        print(f"    - 배치당 최소: {min_batch_time:.3f}초 ({min_batch_time*1000:.2f}ms)")
        print(f"    - 배치당 최대: {max_batch_time:.3f}초 ({max_batch_time*1000:.2f}ms)")
        
        # Prometheus 메트릭 업데이트
        batch_size_label = str(batch_size)
        mongodb_batch_write_records_per_second.labels(batch_size=batch_size_label).set(records_per_second)
        mongodb_batch_size_gauge.labels(batch_size=batch_size_label).set(batch_size)
        mongodb_total_records_gauge.labels(batch_size=batch_size_label).set(total_inserted)
        mongodb_avg_batch_time_gauge.labels(batch_size=batch_size_label).set(avg_time_per_batch)
        
        # 각 배치 시간을 히스토그램에 기록
        for batch_time in batch_times:
            mongodb_batch_write_time_seconds.labels(batch_size=batch_size_label).observe(batch_time)
            mongodb_batch_write_time_summary.labels(batch_size=batch_size_label).observe(batch_time)
        
        # 약간의 대기 시간 (메트릭 수집을 위해)
        time.sleep(2)
    
    # 최종 요약
    print(f"\n{'='*80}")
    print("📊 최종 성능 요약")
    print(f"{'='*80}\n")
    
    print(f"{'배치 크기':<12} {'초당 처리 (레코드)':<20} {'배치당 평균 시간 (ms)':<25} {'총 시간 (초)':<15}")
    print(f"{'-'*80}")
    
    for result in results:
        print(f"{result['batch_size']:>10,}  {result['records_per_second']:>18,.0f}  {result['avg_time_per_batch']*1000:>23.2f}  {result['total_time']:>13.2f}")
    
    # 최적 배치 크기 찾기
    best = max(results, key=lambda x: x['records_per_second'])
    print(f"\n🏆 최적 성능:")
    print(f"  배치 크기: {best['batch_size']:,}개")
    print(f"  초당 처리: {best['records_per_second']:,.0f} 레코드/초")
    print(f"  배치당 평균 시간: {best['avg_time_per_batch']*1000:.2f}ms")
    
    return results

def main():
    """메인 테스트 함수"""
    print("\n" + "="*80)
    print("🔬 MongoDB 배치 쓰기 성능 테스트")
    print("="*80)
    print("배치 크기별 MongoDB 쓰기 성능을 측정합니다")
    print("="*80)
    
    # Prometheus 메트릭 서버 시작
    print(f"\n📊 Prometheus 메트릭 서버 시작 (포트 {METRICS_PORT})...")
    start_http_server(METRICS_PORT, addr='0.0.0.0')
    print(f"✅ 메트릭 서버 시작 완료: http://0.0.0.0:{METRICS_PORT}/metrics")
    print(f"   로컬 접속: http://localhost:{METRICS_PORT}/metrics")
    
    # MongoDB 연결
    print("\n📡 MongoDB 연결 중...")
    db_mongo = connect_mongodb()
    print("✅ MongoDB 연결 완료")
    
    try:
        # 테스트 실행
        print("\n" + "="*80)
        print("테스트 시작")
        print("="*80)
        
        results = test_mongodb_batch_write_performance(db_mongo)
        
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

if __name__ == "__main__":
    main()
