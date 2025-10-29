#!/usr/bin/env python3
"""
MongoDB → TimescaleDB 마이그레이션 스크립트
- MongoDB의 모든 컬렉션 데이터를 TimescaleDB로 변환
- 데이터 타입 매핑 및 변환
- 배치 처리로 성능 최적화
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient
from timescaledb import (
    init_timescaledb,
    write_telemetry_data,
    write_collision_event,
    write_engine_off_event,
    write_periodic_data,
    write_sudden_acceleration_event,
    write_warning_light_event,
    batch_write_telemetry_data
)
from datetime import datetime
import time

def convert_vehicle_id(vehicle_id):
    """vehicle_id를 VHC-XXX 형식으로 변환"""
    if vehicle_id.startswith('vehicle'):
        # vehicle1 -> VHC-001, vehicle2 -> VHC-002 등
        vehicle_num = vehicle_id.replace('vehicle', '')
        return f"VHC-{vehicle_num.zfill(3)}"
    return vehicle_id

# MongoDB 연결 설정
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))
MONGO_DB = os.getenv("MONGO_DB", "alcha_events")
MONGO_USER = os.getenv("MONGO_USER", "")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "")
MONGO_AUTH_DB = os.getenv("MONGO_AUTH_DB", "admin")

def connect_mongodb():
    """MongoDB 연결"""
    try:
        if MONGO_USER and MONGO_PASSWORD:
            uri = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}?authSource={MONGO_AUTH_DB}"
        else:
            uri = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/"
        client = MongoClient(uri)
        db = client[MONGO_DB]
        
        # 연결 테스트
        client.admin.command('ping')
        print("✅ MongoDB 연결 성공")
        return client, db
    except Exception as e:
        print(f"❌ MongoDB 연결 실패: {e}")
        return None, None

def migrate_realtime_data(db):
    """실시간 텔레메트리 데이터 마이그레이션"""
    print("📊 실시간 텔레메트리 데이터 마이그레이션 중...")
    
    try:
        collection = db["realtime_data"]
        total_count = collection.count_documents({})
        print(f"  - 총 {total_count}개 레코드 처리 예정")
        
        # 배치 단위로 처리 (1000개씩)
        batch_size = 1000
        processed = 0
        batch_data = []
        
        for doc in collection.find().sort("timestamp", 1):
            # MongoDB 문서를 TimescaleDB 형식으로 변환
            telemetry_record = {
                "vehicle_id": convert_vehicle_id(doc["vehicle_id"]),
                "vehicle_speed": doc["vehicle_speed"],
                "engine_rpm": doc["engine_rpm"],
                "throttle_position": doc["throttle_position"],
                "timestamp": doc["timestamp"]
            }
            
            batch_data.append(telemetry_record)
            processed += 1
            
            # 배치가 가득 찼거나 마지막 레코드인 경우 삽입
            if len(batch_data) >= batch_size or processed == total_count:
                if batch_write_telemetry_data(batch_data):
                    print(f"  ✅ 배치 {processed}/{total_count} 처리 완료")
                else:
                    print(f"  ❌ 배치 {processed}/{total_count} 처리 실패")
                    return False
                batch_data = []
        
        print(f"✅ 실시간 텔레메트리 데이터 마이그레이션 완료 ({processed}개)")
        return True
        
    except Exception as e:
        print(f"❌ 실시간 텔레메트리 데이터 마이그레이션 실패: {e}")
        return False

def migrate_periodic_data(db):
    """주기적 데이터 마이그레이션"""
    print("📍 주기적 데이터 마이그레이션 중...")
    
    try:
        collection = db["periodic_data"]
        total_count = collection.count_documents({})
        print(f"  - 총 {total_count}개 레코드 처리 예정")
        
        processed = 0
        for doc in collection.find().sort("timestamp", 1):
            if write_periodic_data(
                vehicle_id=convert_vehicle_id(doc["vehicle_id"]),
                location_latitude=doc["location_latitude"],
                location_longitude=doc["location_longitude"],
                location_altitude=doc["location_altitude"],
                temperature_cabin=doc["temperature_cabin"],
                temperature_ambient=doc["temperature_ambient"],
                battery_voltage=doc["battery_voltage"],
                tpms_front_left=doc["tpms_front_left"],
                tpms_front_right=doc["tpms_front_right"],
                tpms_rear_left=doc["tpms_rear_left"],
                tpms_rear_right=doc["tpms_rear_right"],
                accelerometer_x=doc["accelerometer_x"],
                accelerometer_y=doc["accelerometer_y"],
                accelerometer_z=doc["accelerometer_z"],
                fuel_level=doc["fuel_level"],
                engine_coolant_temp=doc["engine_coolant_temp"],
                transmission_oil_temp=doc["transmission_oil_temp"],
                timestamp=doc["timestamp"]
            ):
                processed += 1
            else:
                print(f"  ❌ 레코드 {processed + 1} 삽입 실패")
                return False
        
        print(f"✅ 주기적 데이터 마이그레이션 완료 ({processed}개)")
        return True
        
    except Exception as e:
        print(f"❌ 주기적 데이터 마이그레이션 실패: {e}")
        return False

def migrate_collision_events(db):
    """충돌 이벤트 마이그레이션"""
    print("💥 충돌 이벤트 마이그레이션 중...")
    
    try:
        collection = db["event_collision"]
        total_count = collection.count_documents({})
        print(f"  - 총 {total_count}개 레코드 처리 예정")
        
        processed = 0
        for doc in collection.find().sort("timestamp", 1):
            if write_collision_event(
                vehicle_id=convert_vehicle_id(doc["vehicle_id"]),
                damage=int(doc["damage"]),  # FLOAT을 INTEGER로 변환
                timestamp=doc["timestamp"]
            ):
                processed += 1
            else:
                print(f"  ❌ 레코드 {processed + 1} 삽입 실패")
                return False
        
        print(f"✅ 충돌 이벤트 마이그레이션 완료 ({processed}개)")
        return True
        
    except Exception as e:
        print(f"❌ 충돌 이벤트 마이그레이션 실패: {e}")
        return False

def migrate_sudden_acceleration_events(db):
    """급가속 이벤트 마이그레이션"""
    print("🚀 급가속 이벤트 마이그레이션 중...")
    
    try:
        collection = db["event_suddenacc"]
        total_count = collection.count_documents({})
        print(f"  - 총 {total_count}개 레코드 처리 예정")
        
        processed = 0
        for doc in collection.find().sort("timestamp", 1):
            if write_sudden_acceleration_event(
                vehicle_id=convert_vehicle_id(doc["vehicle_id"]),
                vehicle_speed=doc["vehicle_speed"],
                throttle_position=doc["throttle_position"],
                gear_position_mode=doc["gear_position_mode"],
                timestamp=doc["timestamp"]
            ):
                processed += 1
            else:
                print(f"  ❌ 레코드 {processed + 1} 삽입 실패")
                return False
        
        print(f"✅ 급가속 이벤트 마이그레이션 완료 ({processed}개)")
        return True
        
    except Exception as e:
        print(f"❌ 급가속 이벤트 마이그레이션 실패: {e}")
        return False

def migrate_engine_status_events(db):
    """엔진 상태 이벤트 마이그레이션"""
    print("🔧 엔진 상태 이벤트 마이그레이션 중...")
    
    try:
        collection = db["event_engine_status"]
        total_count = collection.count_documents({})
        print(f"  - 총 {total_count}개 레코드 처리 예정")
        
        processed = 0
        for doc in collection.find().sort("timestamp", 1):
            # MongoDB의 event-engine-status를 기존 engine_off_events 형식으로 변환
            if write_engine_off_event(
                vehicle_id=convert_vehicle_id(doc["vehicle_id"]),
                speed=doc["vehicle_speed"],
                gear_status=doc["gear_position_mode"],
                gyro=doc["inclination_sensor"],  # inclination_sensor 값 사용
                side="front",  # 기본값 설정
                ignition=doc["engine_status_ignition"] == "ON",
                timestamp=doc["timestamp"]
            ):
                processed += 1
            else:
                print(f"  ❌ 레코드 {processed + 1} 삽입 실패")
                return False
        
        print(f"✅ 엔진 상태 이벤트 마이그레이션 완료 ({processed}개)")
        return True
        
    except Exception as e:
        print(f"❌ 엔진 상태 이벤트 마이그레이션 실패: {e}")
        return False

def migrate_warning_light_events(db):
    """경고등 이벤트 마이그레이션"""
    print("⚠️  경고등 이벤트 마이그레이션 중...")
    
    try:
        collection = db["event_warning_light"]
        total_count = collection.count_documents({})
        print(f"  - 총 {total_count}개 레코드 처리 예정")
        
        processed = 0
        for doc in collection.find().sort("timestamp", 1):
            if write_warning_light_event(
                vehicle_id=convert_vehicle_id(doc["vehicle_id"]),
                warning_type=doc["type"],
                timestamp=doc["timestamp"]
            ):
                processed += 1
            else:
                print(f"  ❌ 레코드 {processed + 1} 삽입 실패")
                return False
        
        print(f"✅ 경고등 이벤트 마이그레이션 완료 ({processed}개)")
        return True
        
    except Exception as e:
        print(f"❌ 경고등 이벤트 마이그레이션 실패: {e}")
        return False

def clear_timescaledb_data():
    """TimescaleDB 기존 데이터 초기화"""
    print("🗑️  TimescaleDB 기존 데이터 초기화 중...")
    
    try:
        from timescaledb import get_timescaledb_connection
        conn = get_timescaledb_connection()
        if not conn:
            print("❌ TimescaleDB 연결 실패")
            return False
        
        cursor = conn.cursor()
        
        # 기존 테이블 데이터 삭제
        tables = [
            "warning_light_events",
            "sudden_acceleration_events", 
            "periodic_data",
            "engine_off_events",
            "collision_events",
            "vehicle_telemetry"
        ]
        
        for table in tables:
            cursor.execute(f"DELETE FROM {table};")
            print(f"  - {table} 데이터 삭제 완료")
        
        conn.commit()
        print("✅ TimescaleDB 데이터 초기화 완료")
        return True
        
    except Exception as e:
        print(f"❌ TimescaleDB 데이터 초기화 실패: {e}")
        return False
    finally:
        if conn:
            conn.close()

def main():
    """메인 마이그레이션 함수"""
    print("🚀 MongoDB → TimescaleDB 마이그레이션 시작...")
    start_time = time.time()
    
    # MongoDB 연결
    client, db = connect_mongodb()
    if client is None or db is None:
        return False
    
    try:
        # 1. TimescaleDB 초기화
        print("\n🔧 TimescaleDB 초기화 중...")
        if not init_timescaledb():
            print("❌ TimescaleDB 초기화 실패")
            return False
        print("✅ TimescaleDB 초기화 완료")
        
        # 2. 기존 데이터 초기화
        print("\n🗑️  기존 데이터 초기화 중...")
        if not clear_timescaledb_data():
            print("❌ 기존 데이터 초기화 실패")
            return False
        
        # 3. 데이터 마이그레이션
        print("\n📊 데이터 마이그레이션 시작...")
        
        migration_functions = [
            ("실시간 텔레메트리", migrate_realtime_data),
            ("주기적 데이터", migrate_periodic_data),
            ("충돌 이벤트", migrate_collision_events),
            ("급가속 이벤트", migrate_sudden_acceleration_events),
            ("엔진 상태 이벤트", migrate_engine_status_events),
            ("경고등 이벤트", migrate_warning_light_events)
        ]
        
        success_count = 0
        for name, func in migration_functions:
            print(f"\n--- {name} 마이그레이션 ---")
            if func(db):
                success_count += 1
                print(f"✅ {name} 마이그레이션 성공")
            else:
                print(f"❌ {name} 마이그레이션 실패")
        
        # 4. 완료 메시지
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n🎉 마이그레이션 완료!")
        print(f"  ⏱️  소요 시간: {duration:.2f}초")
        print(f"  ✅ 성공한 마이그레이션: {success_count}/{len(migration_functions)}")
        
        if success_count == len(migration_functions):
            print("🎊 모든 데이터가 성공적으로 마이그레이션되었습니다!")
            return True
        else:
            print("⚠️  일부 데이터 마이그레이션이 실패했습니다.")
            return False
        
    except Exception as e:
        print(f"❌ 마이그레이션 실패: {e}")
        return False
    finally:
        client.close()

if __name__ == "__main__":
    main()
