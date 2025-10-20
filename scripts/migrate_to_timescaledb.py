#!/usr/bin/env python3
"""
TimescaleDB 초기 데이터 생성 스크립트
- 텔레메트리 데이터: 2025-09-23 01:54:26 ~ 02:54:26 (1시간)
- 이벤트 데이터: 텔레메트리 시간 범위 내에서 일관성 있게 생성
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.timescaledb import (
    init_timescaledb, 
    write_engine_off_event, 
    write_collision_event,
    batch_write_telemetry_data,
    get_timescaledb_connection
)
from datetime import datetime, timedelta
import random

# 기준 시간: 2025-09-23 01:54:26 UTC
BASE_TIMESTAMP = datetime(2025, 9, 23, 1, 54, 26)

def clear_existing_data():
    """기존 데이터 초기화"""
    print("🗑️  기존 데이터 초기화 중...")
    conn = get_timescaledb_connection()
    if not conn:
        print("❌ 데이터베이스 연결 실패")
        return False
    
    try:
        cursor = conn.cursor()
        
        # 기존 테이블 삭제
        cursor.execute("DROP TABLE IF EXISTS engine_off_events CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS collision_events CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS vehicle_telemetry CASCADE;")
        
        conn.commit()
        print("✅ 기존 데이터 초기화 완료")
        return True
    except Exception as e:
        print(f"❌ 데이터 초기화 실패: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def generate_telemetry_data():
    """1시간치 텔레메트리 데이터 생성 (VHC-001, VHC-002, VHC-003)"""
    print("📊 텔레메트리 데이터 생성 중...")
    
    # 시작 시간: 2025-09-23 01:54:26 (1시간 동안)
    start_time = BASE_TIMESTAMP
    vehicle_ids = ['VHC-001', 'VHC-002', 'VHC-003']
    
    telemetry_data = []
    
    for vehicle_id in vehicle_ids:
        print(f"  - {vehicle_id} 데이터 생성 중...")
        
        # 각 차량마다 다른 기본 패턴 설정
        base_speed = 60.0 if vehicle_id == 'VHC-001' else (55.0 if vehicle_id == 'VHC-002' else 65.0)
        base_rpm = 2000 if vehicle_id == 'VHC-001' else (1800 if vehicle_id == 'VHC-002' else 2200)
        
        for second in range(3600):  # 1시간 = 3600초
            timestamp = start_time + timedelta(seconds=second)
            
            # 속도 변화 (정현파 + 랜덤)
            speed_variation = random.uniform(-5, 5) + 10 * (0.5 + 0.5 * (second % 600) / 600)
            vehicle_speed = base_speed + speed_variation
            vehicle_speed = max(0, min(120, vehicle_speed))  # 0-120 km/h
            
            # RPM은 속도에 비례 + 랜덤 변동
            engine_rpm = int(base_rpm + (vehicle_speed - base_speed) * 30 + random.uniform(-100, 100))
            engine_rpm = max(800, min(6000, engine_rpm))  # 800-6000 RPM
            
            # 스로틀 위치 (0-100%)
            throttle_position = (vehicle_speed / 120) * 100 + random.uniform(-5, 5)
            throttle_position = max(0, min(100, throttle_position))
            
            telemetry_data.append({
                'vehicle_id': vehicle_id,
                'vehicle_speed': round(vehicle_speed, 2),
                'engine_rpm': engine_rpm,
                'throttle_position': round(throttle_position, 2),
                'timestamp': timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            })
    
    print(f"✅ 총 {len(telemetry_data)}개 텔레메트리 레코드 생성 완료")
    return telemetry_data

def generate_events():
    """텔레메트리 시간 범위 내에서 일관성 있는 이벤트 생성"""
    print("📝 이벤트 데이터 생성 중...")
    
    # 텔레메트리 시간 범위: 2025-09-23 01:54:26 ~ 02:54:26
    start_time = BASE_TIMESTAMP
    end_time = start_time + timedelta(hours=1)
    
    engine_off_events = []
    collision_events = []
    
    # VHC-001 이벤트 (텔레메트리 시간 범위 내)
    print("  - VHC-001 이벤트 생성...")
    # 충돌 이벤트 3개 (10분, 25분, 45분)
    collision_events.extend([
        {"vehicle_id": "VHC-001", "damage": 2, "timestamp": (start_time + timedelta(minutes=10)).strftime('%Y-%m-%dT%H:%M:%SZ')},
        {"vehicle_id": "VHC-001", "damage": 3, "timestamp": (start_time + timedelta(minutes=25)).strftime('%Y-%m-%dT%H:%M:%SZ')},
        {"vehicle_id": "VHC-001", "damage": 1, "timestamp": (start_time + timedelta(minutes=45)).strftime('%Y-%m-%dT%H:%M:%SZ')},
    ])
    # 엔진 오프 이벤트 2개 (15분, 50분)
    engine_off_events.extend([
        {"vehicle_id": "VHC-001", "speed": 0, "gear_status": "P", "gyro": 12.5, "side": "front", "ignition": False, 
         "timestamp": (start_time + timedelta(minutes=15)).strftime('%Y-%m-%dT%H:%M:%SZ')},
        {"vehicle_id": "VHC-001", "speed": 0, "gear_status": "N", "gyro": 15.2, "side": "rear", "ignition": False, 
         "timestamp": (start_time + timedelta(minutes=50)).strftime('%Y-%m-%dT%H:%M:%SZ')},
    ])
    
    # VHC-002 이벤트 (텔레메트리 시간 범위 내)
    print("  - VHC-002 이벤트 생성...")
    # 충돌 이벤트 2개 (20분, 40분)
    collision_events.extend([
        {"vehicle_id": "VHC-002", "damage": 4, "timestamp": (start_time + timedelta(minutes=20)).strftime('%Y-%m-%dT%H:%M:%SZ')},
        {"vehicle_id": "VHC-002", "damage": 2, "timestamp": (start_time + timedelta(minutes=40)).strftime('%Y-%m-%dT%H:%M:%SZ')},
    ])
    # 엔진 오프 이벤트 3개 (5분, 30분, 55분)
    engine_off_events.extend([
        {"vehicle_id": "VHC-002", "speed": 0, "gear_status": "P", "gyro": 10.5, "side": "left", "ignition": False, 
         "timestamp": (start_time + timedelta(minutes=5)).strftime('%Y-%m-%dT%H:%M:%SZ')},
        {"vehicle_id": "VHC-002", "speed": 0, "gear_status": "P", "gyro": 14.2, "side": "right", "ignition": False, 
         "timestamp": (start_time + timedelta(minutes=30)).strftime('%Y-%m-%dT%H:%M:%SZ')},
        {"vehicle_id": "VHC-002", "speed": 0, "gear_status": "N", "gyro": 7.8, "side": "front", "ignition": False, 
         "timestamp": (start_time + timedelta(minutes=55)).strftime('%Y-%m-%dT%H:%M:%SZ')},
    ])
    
    # VHC-003 이벤트 (텔레메트리 시간 범위 내)
    print("  - VHC-003 이벤트 생성...")
    # 충돌 이벤트 2개 (12분, 35분)
    collision_events.extend([
        {"vehicle_id": "VHC-003", "damage": 3, "timestamp": (start_time + timedelta(minutes=12)).strftime('%Y-%m-%dT%H:%M:%SZ')},
        {"vehicle_id": "VHC-003", "damage": 1, "timestamp": (start_time + timedelta(minutes=35)).strftime('%Y-%m-%dT%H:%M:%SZ')},
    ])
    # 엔진 오프 이벤트 2개 (22분, 48분)
    engine_off_events.extend([
        {"vehicle_id": "VHC-003", "speed": 0, "gear_status": "P", "gyro": 11.8, "side": "rear", "ignition": False, 
         "timestamp": (start_time + timedelta(minutes=22)).strftime('%Y-%m-%dT%H:%M:%SZ')},
        {"vehicle_id": "VHC-003", "speed": 0, "gear_status": "P", "gyro": 13.7, "side": "left", "ignition": False, 
         "timestamp": (start_time + timedelta(minutes=48)).strftime('%Y-%m-%dT%H:%M:%SZ')},
    ])
    
    # VHC-004는 이벤트 없음 (의도적)
    
    # VHC-005 ~ VHC-010 이벤트 (텔레메트리 범위 밖, 일별 타임라인용)
    print("  - VHC-005~010 이벤트 생성...")
    # 다양한 날짜에 분산
    base_date = datetime(2025, 9, 1, 10, 0, 0)
    
    # VHC-005
    collision_events.append({"vehicle_id": "VHC-005", "damage": 2, "timestamp": (base_date + timedelta(days=5)).strftime('%Y-%m-%dT%H:%M:%SZ')})
    engine_off_events.append({"vehicle_id": "VHC-005", "speed": 0, "gear_status": "P", "gyro": 10.5, "side": "right", "ignition": False, 
                              "timestamp": (base_date + timedelta(days=3)).strftime('%Y-%m-%dT%H:%M:%SZ')})
    
    # VHC-006
    collision_events.append({"vehicle_id": "VHC-006", "damage": 3, "timestamp": (base_date + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ')})
    engine_off_events.extend([
        {"vehicle_id": "VHC-006", "speed": 0, "gear_status": "N", "gyro": 8.1, "side": "front", "ignition": False, 
         "timestamp": (base_date + timedelta(days=2)).strftime('%Y-%m-%dT%H:%M:%SZ')},
        {"vehicle_id": "VHC-006", "speed": 0, "gear_status": "P", "gyro": 11.3, "side": "rear", "ignition": False, 
         "timestamp": (base_date + timedelta(days=10)).strftime('%Y-%m-%dT%H:%M:%SZ')},
    ])
    
    # VHC-007
    collision_events.append({"vehicle_id": "VHC-007", "damage": 4, "timestamp": (base_date + timedelta(days=6)).strftime('%Y-%m-%dT%H:%M:%SZ')})
    engine_off_events.append({"vehicle_id": "VHC-007", "speed": 0, "gear_status": "P", "gyro": 13.7, "side": "left", "ignition": False, 
                              "timestamp": (base_date + timedelta(days=4)).strftime('%Y-%m-%dT%H:%M:%SZ')})
    
    # VHC-008
    collision_events.append({"vehicle_id": "VHC-008", "damage": 1, "timestamp": (base_date + timedelta(days=8)).strftime('%Y-%m-%dT%H:%M:%SZ')})
    engine_off_events.extend([
        {"vehicle_id": "VHC-008", "speed": 0, "gear_status": "P", "gyro": 9.8, "side": "right", "ignition": False, 
         "timestamp": (base_date + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')},
        {"vehicle_id": "VHC-008", "speed": 0, "gear_status": "N", "gyro": 10.1, "side": "front", "ignition": False, 
         "timestamp": (base_date + timedelta(days=9)).strftime('%Y-%m-%dT%H:%M:%SZ')},
    ])
    
    # VHC-009
    collision_events.append({"vehicle_id": "VHC-009", "damage": 2, "timestamp": (base_date + timedelta(days=11)).strftime('%Y-%m-%dT%H:%M:%SZ')})
    engine_off_events.append({"vehicle_id": "VHC-009", "speed": 0, "gear_status": "P", "gyro": 16.0, "side": "rear", "ignition": False, 
                              "timestamp": (base_date + timedelta(days=6)).strftime('%Y-%m-%dT%H:%M:%SZ')})
    
    # VHC-010
    collision_events.append({"vehicle_id": "VHC-010", "damage": 5, "timestamp": (base_date + timedelta(days=12)).strftime('%Y-%m-%dT%H:%M:%SZ')})
    engine_off_events.extend([
        {"vehicle_id": "VHC-010", "speed": 0, "gear_status": "P", "gyro": 20.3, "side": "right", "ignition": False, 
         "timestamp": (base_date + timedelta(days=8)).strftime('%Y-%m-%dT%H:%M:%SZ')},
        {"vehicle_id": "VHC-010", "speed": 0, "gear_status": "P", "gyro": 18.7, "side": "left", "ignition": False, 
         "timestamp": (base_date + timedelta(days=14)).strftime('%Y-%m-%dT%H:%M:%SZ')},
    ])
    
    print(f"✅ 충돌 이벤트 {len(collision_events)}개, 엔진 오프 이벤트 {len(engine_off_events)}개 생성 완료")
    return engine_off_events, collision_events

def initialize_database(clear_data=True):
    """데이터베이스 초기화 및 데이터 생성"""
    print("🚀 TimescaleDB 초기 데이터 생성 시작...")
    print(f"📅 기준 시간: {BASE_TIMESTAMP.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    
    # 1. 기존 데이터 초기화
    if clear_data:
        print("\n기존 데이터를 초기화합니다...")
        if not clear_existing_data():
            return False
    
    # 2. TimescaleDB 초기화 (테이블 생성 및 하이퍼테이블 설정)
    print("\n🔧 TimescaleDB 초기화 중...")
    if not init_timescaledb():
        print("❌ TimescaleDB 초기화 실패")
        return False
    
    print("✅ TimescaleDB 초기화 성공")
    
    # 3. 이벤트 데이터 생성 및 삽입
    print("\n📝 이벤트 데이터 생성 및 삽입 중...")
    engine_off_events, collision_events = generate_events()
    
    # 엔진 오프 이벤트 삽입
    engine_off_count = 0
    for event in engine_off_events:
        if write_engine_off_event(
            event["vehicle_id"],
            event["speed"],
            event["gear_status"],
            event["gyro"],
            event["side"],
            event["ignition"],
            event["timestamp"]
        ):
            engine_off_count += 1
    
    print(f"✅ 엔진 오프 이벤트 {engine_off_count}개 삽입 완료")
    
    # 충돌 이벤트 삽입
    collision_count = 0
    for event in collision_events:
        if write_collision_event(
            event["vehicle_id"],
            event["damage"],
            event["timestamp"]
        ):
            collision_count += 1
    
    print(f"✅ 충돌 이벤트 {collision_count}개 삽입 완료")
    
    # 4. 텔레메트리 데이터 생성 및 삽입
    print("\n📊 텔레메트리 데이터 생성 및 삽입 중...")
    telemetry_data = generate_telemetry_data()
    
    # 배치 단위로 삽입 (성능 최적화)
    batch_size = 1000
    total_batches = (len(telemetry_data) + batch_size - 1) // batch_size
    
    for i in range(0, len(telemetry_data), batch_size):
        batch = telemetry_data[i:i+batch_size]
        batch_num = (i // batch_size) + 1
        print(f"  배치 {batch_num}/{total_batches} 처리 중...")
        if not batch_write_telemetry_data(batch):
            print(f"❌ 배치 {batch_num} 삽입 실패")
            return False
    
    print(f"✅ 텔레메트리 데이터 {len(telemetry_data)}개 삽입 완료")
    
    # 5. 완료 메시지
    print(f"\n🎉 초기 데이터 생성 완료!")
    print(f"  ⏰ 텔레메트리 시간 범위: {BASE_TIMESTAMP.strftime('%Y-%m-%d %H:%M:%S')} ~ {(BASE_TIMESTAMP + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"  📊 텔레메트리 데이터: {len(telemetry_data)}개 (VHC-001, 002, 003)")
    print(f"  🚨 충돌 이벤트: {collision_count}개")
    print(f"  🔧 엔진 오프 이벤트: {engine_off_count}개")
    print(f"  💾 총 레코드: {len(telemetry_data) + collision_count + engine_off_count}개")
    return True

if __name__ == "__main__":
    initialize_database()
