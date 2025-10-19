#!/usr/bin/env python3
"""
TimescaleDB로 이벤트 데이터 마이그레이션 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.timescaledb import init_timescaledb, write_engine_off_event, write_collision_event
from datetime import datetime

# 마이그레이션할 데이터 (기존 MongoDB 데이터)
MOCK_EVENTS_DATA = {
    "engine_off_events": [
        # VHC-001 엔진 오프 이벤트
        {"vehicle_id": "VHC-001", "speed": 0, "gear_status": "P", "gyro": 12.5, "side": "front", "ignition": False, "timestamp": "2024-10-01T08:30:00"},
        {"vehicle_id": "VHC-001", "speed": 0, "gear_status": "P", "gyro": 15.2, "side": "rear", "ignition": False, "timestamp": "2024-10-02T18:45:00"},
        {"vehicle_id": "VHC-001", "speed": 0, "gear_status": "N", "gyro": 8.7, "side": "left", "ignition": False, "timestamp": "2024-10-03T12:15:00"},
        {"vehicle_id": "VHC-001", "speed": 0, "gear_status": "P", "gyro": 20.1, "side": "right", "ignition": False, "timestamp": "2024-10-05T09:20:00"},
        {"vehicle_id": "VHC-001", "speed": 0, "gear_status": "P", "gyro": 11.3, "side": "front", "ignition": False, "timestamp": "2024-10-07T16:30:00"},
        {"vehicle_id": "VHC-001", "speed": 0, "gear_status": "N", "gyro": 14.8, "side": "rear", "ignition": False, "timestamp": "2024-10-10T11:45:00"},
        {"vehicle_id": "VHC-001", "speed": 0, "gear_status": "P", "gyro": 9.2, "side": "left", "ignition": False, "timestamp": "2024-10-12T14:20:00"},
        {"vehicle_id": "VHC-001", "speed": 0, "gear_status": "P", "gyro": 16.7, "side": "right", "ignition": False, "timestamp": "2024-10-15T07:10:00"},
        {"vehicle_id": "VHC-001", "speed": 0, "gear_status": "N", "gyro": 13.4, "side": "front", "ignition": False, "timestamp": "2024-10-18T19:25:00"},
        {"vehicle_id": "VHC-001", "speed": 0, "gear_status": "P", "gyro": 18.9, "side": "rear", "ignition": False, "timestamp": "2024-10-20T13:40:00"},
        
        # VHC-002 엔진 오프 이벤트
        {"vehicle_id": "VHC-002", "speed": 0, "gear_status": "P", "gyro": 10.5, "side": "front", "ignition": False, "timestamp": "2024-10-01T10:15:00"},
        {"vehicle_id": "VHC-002", "speed": 0, "gear_status": "P", "gyro": 14.2, "side": "rear", "ignition": False, "timestamp": "2024-10-03T17:30:00"},
        {"vehicle_id": "VHC-002", "speed": 0, "gear_status": "N", "gyro": 7.8, "side": "left", "ignition": False, "timestamp": "2024-10-06T09:45:00"},
        {"vehicle_id": "VHC-002", "speed": 0, "gear_status": "P", "gyro": 19.3, "side": "right", "ignition": False, "timestamp": "2024-10-08T15:20:00"},
        {"vehicle_id": "VHC-002", "speed": 0, "gear_status": "P", "gyro": 12.1, "side": "front", "ignition": False, "timestamp": "2024-10-11T11:10:00"},
        {"vehicle_id": "VHC-002", "speed": 0, "gear_status": "N", "gyro": 15.6, "side": "rear", "ignition": False, "timestamp": "2024-10-14T18:35:00"},
        {"vehicle_id": "VHC-002", "speed": 0, "gear_status": "P", "gyro": 8.9, "side": "left", "ignition": False, "timestamp": "2024-10-17T12:50:00"},
        {"vehicle_id": "VHC-002", "speed": 0, "gear_status": "P", "gyro": 17.4, "side": "right", "ignition": False, "timestamp": "2024-10-19T08:25:00"},
        
        # VHC-003 엔진 오프 이벤트
        {"vehicle_id": "VHC-003", "speed": 0, "gear_status": "P", "gyro": 11.8, "side": "front", "ignition": False, "timestamp": "2024-10-02T14:20:00"},
        {"vehicle_id": "VHC-003", "speed": 0, "gear_status": "P", "gyro": 13.7, "side": "rear", "ignition": False, "timestamp": "2024-10-04T16:45:00"},
        {"vehicle_id": "VHC-003", "speed": 0, "gear_status": "N", "gyro": 9.4, "side": "left", "ignition": False, "timestamp": "2024-10-07T10:30:00"},
        {"vehicle_id": "VHC-003", "speed": 0, "gear_status": "P", "gyro": 16.2, "side": "right", "ignition": False, "timestamp": "2024-10-09T13:15:00"},
        {"vehicle_id": "VHC-003", "speed": 0, "gear_status": "P", "gyro": 10.7, "side": "front", "ignition": False, "timestamp": "2024-10-12T19:40:00"},
        {"vehicle_id": "VHC-003", "speed": 0, "gear_status": "N", "gyro": 14.9, "side": "rear", "ignition": False, "timestamp": "2024-10-15T07:55:00"},
        {"vehicle_id": "VHC-003", "speed": 0, "gear_status": "P", "gyro": 12.3, "side": "left", "ignition": False, "timestamp": "2024-10-18T15:20:00"},
        {"vehicle_id": "VHC-003", "speed": 0, "gear_status": "P", "gyro": 18.1, "side": "right", "ignition": False, "timestamp": "2024-10-21T11:35:00"},
        
        # VHC-005 엔진 오프 이벤트
        {"vehicle_id": "VHC-005", "speed": 0, "gear_status": "P", "gyro": 10.5, "side": "right", "ignition": False, "timestamp": "2024-10-01T10:00:00"},
        
        # VHC-006 엔진 오프 이벤트
        {"vehicle_id": "VHC-006", "speed": 0, "gear_status": "N", "gyro": 8.1, "side": "front", "ignition": False, "timestamp": "2024-10-03T09:00:00"},
        {"vehicle_id": "VHC-006", "speed": 0, "gear_status": "P", "gyro": 11.3, "side": "rear", "ignition": False, "timestamp": "2024-10-05T17:00:00"},
        
        # VHC-007 엔진 오프 이벤트
        {"vehicle_id": "VHC-007", "speed": 0, "gear_status": "P", "gyro": 13.7, "side": "left", "ignition": False, "timestamp": "2024-10-01T14:00:00"},
        
        # VHC-008 엔진 오프 이벤트
        {"vehicle_id": "VHC-008", "speed": 0, "gear_status": "P", "gyro": 9.8, "side": "right", "ignition": False, "timestamp": "2024-10-02T16:00:00"},
        {"vehicle_id": "VHC-008", "speed": 0, "gear_status": "N", "gyro": 10.1, "side": "front", "ignition": False, "timestamp": "2024-10-04T10:00:00"},
        
        # VHC-009 엔진 오프 이벤트
        {"vehicle_id": "VHC-009", "speed": 0, "gear_status": "P", "gyro": 16.0, "side": "rear", "ignition": False, "timestamp": "2024-10-03T12:00:00"},
        
        # VHC-010 엔진 오프 이벤트
        {"vehicle_id": "VHC-010", "speed": 0, "gear_status": "P", "gyro": 20.3, "side": "right", "ignition": False, "timestamp": "2024-10-02T11:20:00"},
        {"vehicle_id": "VHC-010", "speed": 0, "gear_status": "P", "gyro": 18.7, "side": "left", "ignition": False, "timestamp": "2024-10-05T09:40:00"},
    ],
    
    "collision_events": [
        # VHC-001 충돌 이벤트
        {"vehicle_id": "VHC-001", "damage": 3, "timestamp": "2024-10-01T14:30:00"},
        {"vehicle_id": "VHC-001", "damage": 2, "timestamp": "2024-10-01T14:35:00"},  # 같은 날 두 번째 충돌
        {"vehicle_id": "VHC-001", "damage": 4, "timestamp": "2024-10-05T11:20:00"},
        {"vehicle_id": "VHC-001", "damage": 1, "timestamp": "2024-10-08T16:45:00"},
        {"vehicle_id": "VHC-001", "damage": 5, "timestamp": "2024-10-12T09:15:00"},
        {"vehicle_id": "VHC-001", "damage": 2, "timestamp": "2024-10-15T13:30:00"},
        {"vehicle_id": "VHC-001", "damage": 3, "timestamp": "2024-10-18T17:20:00"},
        {"vehicle_id": "VHC-001", "damage": 1, "timestamp": "2024-10-22T10:40:00"},
        
        # VHC-002 충돌 이벤트
        {"vehicle_id": "VHC-002", "damage": 2, "timestamp": "2024-10-02T15:45:00"},
        {"vehicle_id": "VHC-002", "damage": 4, "timestamp": "2024-10-06T12:10:00"},
        {"vehicle_id": "VHC-002", "damage": 1, "timestamp": "2024-10-09T18:25:00"},
        {"vehicle_id": "VHC-002", "damage": 3, "timestamp": "2024-10-13T14:50:00"},
        {"vehicle_id": "VHC-002", "damage": 2, "timestamp": "2024-10-16T11:35:00"},
        {"vehicle_id": "VHC-002", "damage": 4, "timestamp": "2024-10-20T16:15:00"},
        
        # VHC-003 충돌 이벤트
        {"vehicle_id": "VHC-003", "damage": 1, "timestamp": "2024-10-03T13:20:00"},
        {"vehicle_id": "VHC-003", "damage": 3, "timestamp": "2024-10-07T10:45:00"},
        {"vehicle_id": "VHC-003", "damage": 2, "timestamp": "2024-10-10T15:30:00"},
        {"vehicle_id": "VHC-003", "damage": 4, "timestamp": "2024-10-14T12:20:00"},
        {"vehicle_id": "VHC-003", "damage": 1, "timestamp": "2024-10-17T09:55:00"},
        {"vehicle_id": "VHC-003", "damage": 3, "timestamp": "2024-10-21T14:40:00"},
        
        # VHC-005 충돌 이벤트
        {"vehicle_id": "VHC-005", "damage": 2, "timestamp": "2024-10-02T15:30:00"},
        {"vehicle_id": "VHC-005", "damage": 4, "timestamp": "2024-10-02T18:00:00"},  # 같은 날 두 번째 충돌
        
        # VHC-007 충돌 이벤트
        {"vehicle_id": "VHC-007", "damage": 3, "timestamp": "2024-10-04T11:00:00"},
        
        # VHC-009 충돌 이벤트
        {"vehicle_id": "VHC-009", "damage": 1, "timestamp": "2024-10-05T08:00:00"},
        
        # VHC-010 충돌 이벤트
        {"vehicle_id": "VHC-010", "damage": 5, "timestamp": "2024-10-04T13:50:00"},
    ]
}

def migrate_data():
    """데이터 마이그레이션 실행"""
    print("🚀 TimescaleDB 데이터 마이그레이션 시작...")
    
    # TimescaleDB 초기화
    if not init_timescaledb():
        print("❌ TimescaleDB 초기화 실패")
        return False
    
    print("✅ TimescaleDB 초기화 성공")
    
    # 엔진 오프 이벤트 마이그레이션
    print("📝 엔진 오프 이벤트 마이그레이션 중...")
    engine_off_count = 0
    for event in MOCK_EVENTS_DATA["engine_off_events"]:
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
    
    print(f"✅ 엔진 오프 이벤트 {engine_off_count}개 마이그레이션 완료")
    
    # 충돌 이벤트 마이그레이션
    print("📝 충돌 이벤트 마이그레이션 중...")
    collision_count = 0
    for event in MOCK_EVENTS_DATA["collision_events"]:
        if write_collision_event(
            event["vehicle_id"],
            event["damage"],
            event["timestamp"]
        ):
            collision_count += 1
    
    print(f"✅ 충돌 이벤트 {collision_count}개 마이그레이션 완료")
    
    print(f"🎉 마이그레이션 완료! 총 {engine_off_count + collision_count}개 이벤트")
    return True

if __name__ == "__main__":
    migrate_data()
