#!/usr/bin/env python3
"""
MongoDB 데이터 생성 스크립트
- 1시간치 실시간 텔레메트리 데이터 (3600개 × 3차량 = 10,800개)
- 주기적 데이터 (위치, 온도, 배터리 등)
- 다양한 이벤트 타입들
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient
from datetime import datetime, timedelta
import random
import math

# MongoDB 연결 설정
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))
MONGO_DB = os.getenv("MONGO_DB", "alcha_events")
MONGO_USER = os.getenv("MONGO_USER", "admin")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "adminpassword")

# 기준 시간: 2025-09-23 01:54:26 UTC
BASE_TIMESTAMP = datetime(2025, 9, 23, 1, 54, 26)
VEHICLE_IDS = ["VHC-001", "VHC-002", "VHC-003"]

def connect_mongodb():
    """MongoDB 연결"""
    try:
        # 인증 없이 연결 시도
        uri = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/"
        client = MongoClient(uri)
        db = client[MONGO_DB]
        
        # 연결 테스트
        client.admin.command('ping')
        print("✅ MongoDB 연결 성공")
        return client, db
    except Exception as e:
        print(f"❌ MongoDB 연결 실패: {e}")
        # 인증이 필요한 경우 다시 시도
        try:
            uri = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}?authSource=admin"
            client = MongoClient(uri)
            db = client[MONGO_DB]
            client.admin.command('ping')
            print("✅ MongoDB 연결 성공 (인증 사용)")
            return client, db
        except Exception as e2:
            print(f"❌ MongoDB 인증 연결도 실패: {e2}")
            return None, None

def clear_existing_data(db):
    """기존 데이터 초기화"""
    print("🗑️  기존 데이터 초기화 중...")
    collections = [
        "realtime-storage-data",
        "periodic-storage-data", 
        "event-collision",
        "event-sudden-acceleration",
        "event-engine-status",
        "event-warning-light"
    ]
    
    for collection_name in collections:
        try:
            db[collection_name].drop()
            print(f"  - {collection_name} 컬렉션 삭제 완료")
        except Exception as e:
            print(f"  - {collection_name} 삭제 실패: {e}")

def generate_realtime_data():
    """실시간 텔레메트리 데이터 생성 (40시간 × 3차량 = 432,000개)"""
    print("📊 실시간 텔레메트리 데이터 생성 중...")
    
    realtime_data = []
    total_records = 0
    
    for vehicle_id in VEHICLE_IDS:
        print(f"  - {vehicle_id} 데이터 생성 중...")
        vehicle_data = []
        
        for i in range(144000):  # 40시간 = 144,000초
            current_time = BASE_TIMESTAMP + timedelta(seconds=i)
            
            # 기본 차량 상태 시뮬레이션
            base_speed = random.uniform(20, 80)  # 20-80 km/h
            speed_variation = random.uniform(-5, 5)
            vehicle_speed = max(0, base_speed + speed_variation)
            
            # 엔진 RPM (속도에 비례)
            engine_rpm = int(800 + (vehicle_speed * 30) + random.uniform(-200, 200))
            engine_rpm = max(600, min(6000, engine_rpm))
            
            # 스로틀 위치 (속도 변화에 따라)
            throttle_position = random.uniform(10, 80)
            
            # 기어 상태
            gear_modes = ["P", "R", "N", "D"]
            gear_position_mode = random.choice(gear_modes)
            gear_position_current_gear = random.randint(1, 6) if gear_position_mode == "D" else 0
            
            # 자이로 센서 (차량 움직임 시뮬레이션)
            gyro_yaw_rate = random.uniform(-2, 2)
            gyro_pitch_rate = random.uniform(-1, 1)
            gyro_roll_rate = random.uniform(-1, 1)
            
            # 온도 (엔진 가동에 따라)
            engine_temp = random.uniform(75, 95)
            coolant_temp = random.uniform(78, 88)
            
            # 브레이크 상태
            side_brake_status = "ON" if vehicle_speed < 1 else "OFF"
            brake_pressure = random.uniform(5, 15)
            
            record = {
                "vehicle_id": vehicle_id,
                "vehicle_speed": round(vehicle_speed, 6),
                "engine_rpm": engine_rpm,
                "engine_status_ignition": "ON",
                "throttle_position": round(throttle_position, 6),
                "wheel_speed_front_left": round(vehicle_speed + random.uniform(-0.5, 0.5), 6),
                "wheel_speed_front_right": round(vehicle_speed + random.uniform(-0.5, 0.5), 6),
                "wheel_speed_rear_left": round(vehicle_speed + random.uniform(-0.5, 0.5), 6),
                "wheel_speed_rear_right": round(vehicle_speed + random.uniform(-0.5, 0.5), 6),
                "gear_position_mode": gear_position_mode,
                "gear_position_current_gear": gear_position_current_gear,
                "gyro_yaw_rate": round(gyro_yaw_rate, 6),
                "gyro_pitch_rate": round(gyro_pitch_rate, 6),
                "gyro_roll_rate": round(gyro_roll_rate, 6),
                "engine_temp": round(engine_temp, 6),
                "coolant_temp": round(coolant_temp, 6),
                "side_brake_status": side_brake_status,
                "brake_pressure": round(brake_pressure, 1),
                "timestamp": current_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            }
            
            vehicle_data.append(record)
        
        realtime_data.extend(vehicle_data)
        total_records += len(vehicle_data)
        print(f"    ✅ {len(vehicle_data)}개 레코드 생성 완료")
    
    print(f"✅ 총 {total_records}개 실시간 텔레메트리 데이터 생성 완료")
    return realtime_data

def generate_periodic_data():
    """주기적 데이터 생성 (위치, 온도, 배터리 등)"""
    print("📍 주기적 데이터 생성 중...")
    
    periodic_data = []
    
    # 각 차량별로 10분마다 주기적 데이터 생성 (40시간 = 240개)
    for vehicle_id in VEHICLE_IDS:
        for i in range(0, 144000, 600):  # 10분마다 (40시간 = 144,000초)
            current_time = BASE_TIMESTAMP + timedelta(seconds=i)
            
            # 서울 지역 좌표 (약간의 변동)
            base_lat = 37.5666
            base_lon = 126.9781
            latitude = base_lat + random.uniform(-0.01, 0.01)
            longitude = base_lon + random.uniform(-0.01, 0.01)
            
            record = {
                "vehicle_id": vehicle_id,
                "location_latitude": round(latitude, 4),
                "location_longitude": round(longitude, 4),
                "location_altitude": round(random.uniform(30, 50), 1),
                "temperature_cabin": round(random.uniform(20, 30), 6),
                "temperature_ambient": round(random.uniform(15, 25), 1),
                "battery_voltage": round(random.uniform(12.0, 14.0), 6),
                "tpms_front_left": round(random.uniform(230, 240), 6),
                "tpms_front_right": round(random.uniform(230, 240), 6),
                "tpms_rear_left": round(random.uniform(230, 240), 6),
                "tpms_rear_right": round(random.uniform(230, 240), 6),
                "accelerometer_x": round(random.uniform(-2, 2), 6),
                "accelerometer_y": round(random.uniform(-2, 2), 6),
                "accelerometer_z": round(random.uniform(8, 12), 6),
                "fuel_level": round(random.uniform(80, 100), 2),
                "engine_coolant_temp": round(random.uniform(20, 30), 1),
                "transmission_oil_temp": round(random.uniform(20, 30), 1),
                "timestamp": current_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            }
            
            periodic_data.append(record)
    
    print(f"✅ {len(periodic_data)}개 주기적 데이터 생성 완료")
    return periodic_data

def generate_collision_events():
    """충돌 이벤트 생성"""
    print("💥 충돌 이벤트 생성 중...")
    
    collision_events = []
    
    # VHC-001: 3개 충돌 이벤트
    for i, minute in enumerate([10, 25, 45]):
        event_time = BASE_TIMESTAMP + timedelta(minutes=minute)
        collision_events.append({
            "vehicle_id": "VHC-001",
            "damage": round(random.uniform(20, 80), 2),
            "timestamp": event_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        })
    
    # VHC-002: 2개 충돌 이벤트
    for i, minute in enumerate([20, 40]):
        event_time = BASE_TIMESTAMP + timedelta(minutes=minute)
        collision_events.append({
            "vehicle_id": "VHC-002", 
            "damage": round(random.uniform(30, 90), 2),
            "timestamp": event_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        })
    
    # VHC-003: 2개 충돌 이벤트
    for i, minute in enumerate([15, 35]):
        event_time = BASE_TIMESTAMP + timedelta(minutes=minute)
        collision_events.append({
            "vehicle_id": "VHC-003",
            "damage": round(random.uniform(15, 70), 2),
            "timestamp": event_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        })
    
    print(f"✅ {len(collision_events)}개 충돌 이벤트 생성 완료")
    return collision_events

def generate_sudden_acceleration_events():
    """급가속 이벤트 생성"""
    print("🚀 급가속 이벤트 생성 중...")
    
    sudden_accel_events = []
    
    # 각 차량별로 1-2개씩 급가속 이벤트
    for vehicle_id in VEHICLE_IDS:
        num_events = random.randint(1, 2)
        for i in range(num_events):
            minute = random.randint(5, 55)
            event_time = BASE_TIMESTAMP + timedelta(minutes=minute)
            
            sudden_accel_events.append({
                "vehicle_id": vehicle_id,
                "vehicle_speed": round(random.uniform(60, 120), 2),
                "throttle_position": round(random.uniform(70, 95), 2),
                "gear_position_mode": "D",
                "timestamp": event_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            })
    
    print(f"✅ {len(sudden_accel_events)}개 급가속 이벤트 생성 완료")
    return sudden_accel_events

def generate_engine_status_events():
    """엔진 상태 이벤트 생성"""
    print("🔧 엔진 상태 이벤트 생성 중...")
    
    engine_events = []
    
    # VHC-001: 2개 엔진 오프 이벤트
    for minute in [15, 50]:
        event_time = BASE_TIMESTAMP + timedelta(minutes=minute)
        engine_events.append({
            "vehicle_id": "VHC-001",
            "vehicle_speed": 0,
            "gear_position_mode": "P",
            "gyro_yaw_rate": round(random.uniform(-1, 1), 6),
            "gyro_pitch_rate": round(random.uniform(-1, 1), 6),
            "gyro_roll_rate": round(random.uniform(-1, 1), 6),
            "side_brake_status": "ON",
            "engine_status_ignition": "OFF",
            "timestamp": event_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            "dct_count": random.randint(3, 8),
            "transmission_gear_position": random.randint(3, 6),
            "abs_activation": random.randint(2, 7),
            "suspension_count": random.randint(3, 8),
            "adas_sensor_fault": random.randint(1, 5),
            "aeb_activation": random.randint(2, 6),
            "total_distance": random.randint(800, 1200)
        })
    
    # VHC-002: 3개 엔진 오프 이벤트
    for minute in [5, 30, 55]:
        event_time = BASE_TIMESTAMP + timedelta(minutes=minute)
        engine_events.append({
            "vehicle_id": "VHC-002",
            "vehicle_speed": 0,
            "gear_position_mode": "P",
            "gyro_yaw_rate": round(random.uniform(-1, 1), 6),
            "gyro_pitch_rate": round(random.uniform(-1, 1), 6),
            "gyro_roll_rate": round(random.uniform(-1, 1), 6),
            "side_brake_status": "ON",
            "engine_status_ignition": "OFF",
            "timestamp": event_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            "dct_count": random.randint(3, 8),
            "transmission_gear_position": random.randint(3, 6),
            "abs_activation": random.randint(2, 7),
            "suspension_count": random.randint(3, 8),
            "adas_sensor_fault": random.randint(1, 5),
            "aeb_activation": random.randint(2, 6),
            "total_distance": random.randint(800, 1200)
        })
    
    # VHC-003: 2개 엔진 오프 이벤트
    for minute in [12, 48]:
        event_time = BASE_TIMESTAMP + timedelta(minutes=minute)
        engine_events.append({
            "vehicle_id": "VHC-003",
            "vehicle_speed": 0,
            "gear_position_mode": "P",
            "gyro_yaw_rate": round(random.uniform(-1, 1), 6),
            "gyro_pitch_rate": round(random.uniform(-1, 1), 6),
            "gyro_roll_rate": round(random.uniform(-1, 1), 6),
            "side_brake_status": "ON",
            "engine_status_ignition": "OFF",
            "timestamp": event_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            "dct_count": random.randint(3, 8),
            "transmission_gear_position": random.randint(3, 6),
            "abs_activation": random.randint(2, 7),
            "suspension_count": random.randint(3, 8),
            "adas_sensor_fault": random.randint(1, 5),
            "aeb_activation": random.randint(2, 6),
            "total_distance": random.randint(800, 1200)
        })
    
    print(f"✅ {len(engine_events)}개 엔진 상태 이벤트 생성 완료")
    return engine_events

def generate_warning_light_events():
    """경고등 이벤트 생성"""
    print("⚠️  경고등 이벤트 생성 중...")
    
    warning_events = []
    warning_types = ["engine_oil_check", "engine_check", "airbag_check", "coolant_check"]
    
    # 각 차량별로 1-2개씩 경고등 이벤트
    for vehicle_id in VEHICLE_IDS:
        num_events = random.randint(1, 2)
        for i in range(num_events):
            minute = random.randint(10, 50)
            event_time = BASE_TIMESTAMP + timedelta(minutes=minute)
            
            warning_events.append({
                "vehicle_id": vehicle_id,
                "type": random.choice(warning_types),
                "timestamp": event_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            })
    
    print(f"✅ {len(warning_events)}개 경고등 이벤트 생성 완료")
    return warning_events

def insert_data_to_mongodb(db, all_data):
    """MongoDB에 데이터 삽입"""
    print("💾 MongoDB에 데이터 삽입 중...")
    
    total_inserted = 0
    
    for collection_name, data in all_data.items():
        if data:
            try:
                result = db[collection_name].insert_many(data)
                inserted_count = len(result.inserted_ids)
                total_inserted += inserted_count
                print(f"  ✅ {collection_name}: {inserted_count}개 삽입 완료")
            except Exception as e:
                print(f"  ❌ {collection_name} 삽입 실패: {e}")
    
    print(f"✅ 총 {total_inserted}개 레코드 삽입 완료")
    return total_inserted

def main():
    """메인 실행 함수"""
    print("🚀 MongoDB 데이터 생성 시작...")
    print(f"📅 기준 시간: {BASE_TIMESTAMP.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"🚗 대상 차량: {', '.join(VEHICLE_IDS)}")
    
    # MongoDB 연결
    client, db = connect_mongodb()
    if client is None or db is None:
        return False
    
    try:
        # 기존 데이터 초기화
        clear_existing_data(db)
        
        # 데이터 생성
        all_data = {
            "realtime-storage-data": generate_realtime_data(),
            "periodic-storage-data": generate_periodic_data(),
            "event-collision": generate_collision_events(),
            "event-sudden-acceleration": generate_sudden_acceleration_events(),
            "event-engine-status": generate_engine_status_events(),
            "event-warning-light": generate_warning_light_events()
        }
        
        # MongoDB에 삽입
        total_inserted = insert_data_to_mongodb(db, all_data)
        
        # 완료 메시지
        print(f"\n🎉 MongoDB 데이터 생성 완료!")
        print(f"  📊 총 삽입된 레코드: {total_inserted}개")
        print(f"  ⏰ 데이터 시간 범위: {BASE_TIMESTAMP.strftime('%Y-%m-%d %H:%M:%S')} ~ {(BASE_TIMESTAMP + timedelta(hours=40)).strftime('%Y-%m-%d %H:%M:%S')} UTC")
        
        # 컬렉션별 통계
        print(f"\n📈 컬렉션별 통계:")
        for collection_name in all_data.keys():
            count = db[collection_name].count_documents({})
            print(f"  - {collection_name}: {count}개")
        
        return True
        
    except Exception as e:
        print(f"❌ 데이터 생성 실패: {e}")
        return False
    finally:
        client.close()

if __name__ == "__main__":
    main()
