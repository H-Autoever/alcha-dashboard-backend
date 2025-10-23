import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
from typing import List, Dict, Any
from datetime import datetime

load_dotenv()

# TimescaleDB 설정
TIMESCALEDB_HOST = os.getenv("TIMESCALEDB_HOST", "localhost")
TIMESCALEDB_PORT = os.getenv("TIMESCALEDB_PORT", "5432")
TIMESCALEDB_DB = os.getenv("TIMESCALEDB_DB", "alcha_events")
TIMESCALEDB_USER = os.getenv("TIMESCALEDB_USER", "alcha")
TIMESCALEDB_PASSWORD = os.getenv("TIMESCALEDB_PASSWORD", "alcha_password")

def get_timescaledb_connection():
    """TimescaleDB 연결 반환"""
    try:
        conn = psycopg2.connect(
            host=TIMESCALEDB_HOST,
            port=TIMESCALEDB_PORT,
            database=TIMESCALEDB_DB,
            user=TIMESCALEDB_USER,
            password=TIMESCALEDB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"Failed to connect to TimescaleDB: {e}")
        return None

def init_timescaledb():
    """TimescaleDB 초기화 및 테이블 생성"""
    conn = get_timescaledb_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # TimescaleDB 확장 활성화
        cursor.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")
        
        # 엔진 오프 이벤트 테이블 생성
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS engine_off_events (
                id SERIAL,
                vehicle_id VARCHAR(50) NOT NULL,
                speed FLOAT,
                gear_status VARCHAR(10),
                gyro FLOAT,
                side VARCHAR(20),
                ignition BOOLEAN,
                timestamp TIMESTAMPTZ NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                PRIMARY KEY (id, timestamp)
            );
        """)
        
        # 충돌 이벤트 테이블 생성
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS collision_events (
                id SERIAL,
                vehicle_id VARCHAR(50) NOT NULL,
                damage INTEGER,
                timestamp TIMESTAMPTZ NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                PRIMARY KEY (id, timestamp)
            );
        """)
        
        # 차량 텔레메트리 테이블 생성 (1초 단위 시계열 데이터)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vehicle_telemetry (
                id SERIAL,
                vehicle_id VARCHAR(50) NOT NULL,
                vehicle_speed FLOAT,
                engine_rpm INTEGER,
                throttle_position FLOAT,
                timestamp TIMESTAMPTZ NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                PRIMARY KEY (id, timestamp)
            );
        """)
        
        # 주기적 데이터 테이블 생성 (위치, 온도, 배터리 등)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS periodic_data (
                id SERIAL,
                vehicle_id VARCHAR(50) NOT NULL,
                location_latitude FLOAT,
                location_longitude FLOAT,
                location_altitude FLOAT,
                temperature_cabin FLOAT,
                temperature_ambient FLOAT,
                battery_voltage FLOAT,
                tpms_front_left FLOAT,
                tpms_front_right FLOAT,
                tpms_rear_left FLOAT,
                tpms_rear_right FLOAT,
                accelerometer_x FLOAT,
                accelerometer_y FLOAT,
                accelerometer_z FLOAT,
                fuel_level FLOAT,
                engine_coolant_temp FLOAT,
                transmission_oil_temp FLOAT,
                timestamp TIMESTAMPTZ NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                PRIMARY KEY (id, timestamp)
            );
        """)
        
        # 급가속 이벤트 테이블 생성
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sudden_acceleration_events (
                id SERIAL,
                vehicle_id VARCHAR(50) NOT NULL,
                vehicle_speed FLOAT,
                throttle_position FLOAT,
                gear_position_mode VARCHAR(10),
                timestamp TIMESTAMPTZ NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                PRIMARY KEY (id, timestamp)
            );
        """)
        
        # 경고등 이벤트 테이블 생성
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS warning_light_events (
                id SERIAL,
                vehicle_id VARCHAR(50) NOT NULL,
                warning_type VARCHAR(50) NOT NULL,
                timestamp TIMESTAMPTZ NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                PRIMARY KEY (id, timestamp)
            );
        """)
        
        # TimescaleDB 하이퍼테이블로 변환
        cursor.execute("SELECT create_hypertable('engine_off_events', 'timestamp', if_not_exists => TRUE);")
        cursor.execute("SELECT create_hypertable('collision_events', 'timestamp', if_not_exists => TRUE);")
        cursor.execute("SELECT create_hypertable('vehicle_telemetry', 'timestamp', if_not_exists => TRUE);")
        cursor.execute("SELECT create_hypertable('periodic_data', 'timestamp', if_not_exists => TRUE);")
        cursor.execute("SELECT create_hypertable('sudden_acceleration_events', 'timestamp', if_not_exists => TRUE);")
        cursor.execute("SELECT create_hypertable('warning_light_events', 'timestamp', if_not_exists => TRUE);")
        
        # 인덱스 생성
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_engine_off_vehicle_id ON engine_off_events(vehicle_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_engine_off_timestamp ON engine_off_events(timestamp);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_collision_vehicle_id ON collision_events(vehicle_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_collision_timestamp ON collision_events(timestamp);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_vehicle_id ON vehicle_telemetry(vehicle_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_timestamp ON vehicle_telemetry(timestamp);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_vehicle_time ON vehicle_telemetry(vehicle_id, timestamp DESC);")
        
        # 새로운 테이블 인덱스
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_periodic_vehicle_id ON periodic_data(vehicle_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_periodic_timestamp ON periodic_data(timestamp);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sudden_accel_vehicle_id ON sudden_acceleration_events(vehicle_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sudden_accel_timestamp ON sudden_acceleration_events(timestamp);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_warning_vehicle_id ON warning_light_events(vehicle_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_warning_timestamp ON warning_light_events(timestamp);")
        
        conn.commit()
        print("TimescaleDB 초기화 완료")
        return True
        
    except Exception as e:
        print(f"Failed to initialize TimescaleDB: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def write_engine_off_event(vehicle_id: str, speed: float, gear_status: str, 
                          gyro: float, side: str, ignition: bool, timestamp: str):
    """엔진 오프 이벤트를 TimescaleDB에 기록"""
    conn = get_timescaledb_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO engine_off_events (vehicle_id, speed, gear_status, gyro, side, ignition, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (vehicle_id, speed, gear_status, gyro, side, ignition, timestamp))
        
        conn.commit()
        print(f"Successfully wrote engine off event for {vehicle_id}")
        return True
    except Exception as e:
        print(f"Failed to write engine off event: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def write_collision_event(vehicle_id: str, damage: int, timestamp: str):
    """충돌 이벤트를 TimescaleDB에 기록"""
    conn = get_timescaledb_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO collision_events (vehicle_id, damage, timestamp)
            VALUES (%s, %s, %s)
        """, (vehicle_id, damage, timestamp))
        
        conn.commit()
        print(f"Successfully wrote collision event for {vehicle_id}")
        return True
    except Exception as e:
        print(f"Failed to write collision event: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def write_telemetry_data(vehicle_id: str, vehicle_speed: float, engine_rpm: int, 
                        throttle_position: float, timestamp: str):
    """차량 텔레메트리 데이터를 TimescaleDB에 기록"""
    conn = get_timescaledb_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO vehicle_telemetry (vehicle_id, vehicle_speed, engine_rpm, throttle_position, timestamp)
            VALUES (%s, %s, %s, %s, %s)
        """, (vehicle_id, vehicle_speed, engine_rpm, throttle_position, timestamp))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Failed to write telemetry data: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def batch_write_telemetry_data(data_list: List[Dict[str, Any]]):
    """배치로 텔레메트리 데이터 기록 (성능 최적화)"""
    conn = get_timescaledb_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # 배치 삽입
        args = [(
            d['vehicle_id'],
            d['vehicle_speed'],
            d['engine_rpm'],
            d['throttle_position'],
            d['timestamp']
        ) for d in data_list]
        
        cursor.executemany("""
            INSERT INTO vehicle_telemetry (vehicle_id, vehicle_speed, engine_rpm, throttle_position, timestamp)
            VALUES (%s, %s, %s, %s, %s)
        """, args)
        
        conn.commit()
        print(f"Successfully wrote {len(data_list)} telemetry records")
        return True
    except Exception as e:
        print(f"Failed to batch write telemetry data: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def get_telemetry_data(vehicle_id: str, start_time: str = None, end_time: str = None) -> List[Dict[str, Any]]:
    """특정 차량의 텔레메트리 데이터 조회"""
    conn = get_timescaledb_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 시간 범위 조건 설정
        time_condition = ""
        params = [vehicle_id]
        
        if start_time and end_time:
            time_condition = "AND timestamp BETWEEN %s AND %s"
            params.extend([start_time, end_time])
        elif start_time:
            time_condition = "AND timestamp >= %s"
            params.append(start_time)
        elif end_time:
            time_condition = "AND timestamp <= %s"
            params.append(end_time)
        
        query = f"""
            SELECT vehicle_id, vehicle_speed, engine_rpm, throttle_position, timestamp
            FROM vehicle_telemetry
            WHERE vehicle_id = %s {time_condition}
            ORDER BY timestamp ASC
        """
        
        cursor.execute(query, params)
        telemetry_data = []
        for row in cursor.fetchall():
            telemetry_data.append({
                "vehicle_id": row["vehicle_id"],
                "vehicle_speed": row["vehicle_speed"],
                "engine_rpm": row["engine_rpm"],
                "throttle_position": row["throttle_position"],
                "timestamp": row["timestamp"].isoformat()
            })
        
        return telemetry_data
        
    except Exception as e:
        print(f"Failed to query telemetry data: {e}")
        return []
    finally:
        conn.close()

def get_events_for_vehicle(vehicle_id: str, start_time: str = None, end_time: str = None) -> Dict[str, List[Dict[str, Any]]]:
    """특정 차량의 이벤트 데이터 조회"""
    conn = get_timescaledb_connection()
    if not conn:
        return {
            "engine_off_events": [], 
            "collision_events": [],
            "sudden_acceleration_events": [],
            "warning_light_events": []
        }
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 시간 범위 조건 설정
        time_condition = ""
        params = [vehicle_id]
        
        if start_time and end_time:
            time_condition = "AND timestamp BETWEEN %s AND %s"
            params.extend([start_time, end_time])
        elif start_time:
            time_condition = "AND timestamp >= %s"
            params.append(start_time)
        elif end_time:
            time_condition = "AND timestamp <= %s"
            params.append(end_time)
        
        # 엔진 오프 이벤트 조회
        engine_off_query = f"""
            SELECT vehicle_id, speed, gear_status, gyro, side, ignition, timestamp
            FROM engine_off_events
            WHERE vehicle_id = %s {time_condition}
            ORDER BY timestamp ASC
        """
        
        cursor.execute(engine_off_query, params)
        engine_off_events = []
        for row in cursor.fetchall():
            engine_off_events.append({
                "vehicle_id": row["vehicle_id"],
                "speed": row["speed"],
                "gear_status": row["gear_status"],
                "gyro": row["gyro"],
                "side": row["side"],
                "ignition": row["ignition"],
                "timestamp": row["timestamp"].isoformat()
            })
        
        # 충돌 이벤트 조회
        collision_query = f"""
            SELECT vehicle_id, damage, timestamp
            FROM collision_events
            WHERE vehicle_id = %s {time_condition}
            ORDER BY timestamp ASC
        """
        
        cursor.execute(collision_query, params)
        collision_events = []
        for row in cursor.fetchall():
            collision_events.append({
                "vehicle_id": row["vehicle_id"],
                "damage": row["damage"],
                "timestamp": row["timestamp"].isoformat()
            })
        
        # 급가속 이벤트 조회
        sudden_accel_query = f"""
            SELECT vehicle_id, vehicle_speed, throttle_position, gear_position_mode, timestamp
            FROM sudden_acceleration_events
            WHERE vehicle_id = %s {time_condition}
            ORDER BY timestamp ASC
        """
        
        cursor.execute(sudden_accel_query, params)
        sudden_acceleration_events = []
        for row in cursor.fetchall():
            sudden_acceleration_events.append({
                "vehicle_id": row["vehicle_id"],
                "vehicle_speed": row["vehicle_speed"],
                "throttle_position": row["throttle_position"],
                "gear_position_mode": row["gear_position_mode"],
                "timestamp": row["timestamp"].isoformat()
            })
        
        # 경고등 이벤트 조회
        warning_light_query = f"""
            SELECT vehicle_id, warning_type, timestamp
            FROM warning_light_events
            WHERE vehicle_id = %s {time_condition}
            ORDER BY timestamp ASC
        """
        
        cursor.execute(warning_light_query, params)
        warning_light_events = []
        for row in cursor.fetchall():
            warning_light_events.append({
                "vehicle_id": row["vehicle_id"],
                "warning_type": row["warning_type"],
                "timestamp": row["timestamp"].isoformat()
            })
        
        return {
            "engine_off_events": engine_off_events,
            "collision_events": collision_events,
            "sudden_acceleration_events": sudden_acceleration_events,
            "warning_light_events": warning_light_events
        }
        
    except Exception as e:
        print(f"Failed to query events: {e}")
        return {
            "engine_off_events": [], 
            "collision_events": [],
            "sudden_acceleration_events": [],
            "warning_light_events": []
        }
    finally:
        conn.close()

def write_periodic_data(vehicle_id: str, location_latitude: float, location_longitude: float, 
                       location_altitude: float, temperature_cabin: float, temperature_ambient: float,
                       battery_voltage: float, tpms_front_left: float, tpms_front_right: float,
                       tpms_rear_left: float, tpms_rear_right: float, accelerometer_x: float,
                       accelerometer_y: float, accelerometer_z: float, fuel_level: float,
                       engine_coolant_temp: float, transmission_oil_temp: float, timestamp: str):
    """주기적 데이터를 TimescaleDB에 기록"""
    conn = get_timescaledb_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO periodic_data (vehicle_id, location_latitude, location_longitude, location_altitude,
                                     temperature_cabin, temperature_ambient, battery_voltage,
                                     tpms_front_left, tpms_front_right, tpms_rear_left, tpms_rear_right,
                                     accelerometer_x, accelerometer_y, accelerometer_z, fuel_level,
                                     engine_coolant_temp, transmission_oil_temp, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (vehicle_id, location_latitude, location_longitude, location_altitude,
              temperature_cabin, temperature_ambient, battery_voltage,
              tpms_front_left, tpms_front_right, tpms_rear_left, tpms_rear_right,
              accelerometer_x, accelerometer_y, accelerometer_z, fuel_level,
              engine_coolant_temp, transmission_oil_temp, timestamp))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Failed to write periodic data: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def write_sudden_acceleration_event(vehicle_id: str, vehicle_speed: float, throttle_position: float,
                                   gear_position_mode: str, timestamp: str):
    """급가속 이벤트를 TimescaleDB에 기록"""
    conn = get_timescaledb_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sudden_acceleration_events (vehicle_id, vehicle_speed, throttle_position, gear_position_mode, timestamp)
            VALUES (%s, %s, %s, %s, %s)
        """, (vehicle_id, vehicle_speed, throttle_position, gear_position_mode, timestamp))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Failed to write sudden acceleration event: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def write_warning_light_event(vehicle_id: str, warning_type: str, timestamp: str):
    """경고등 이벤트를 TimescaleDB에 기록"""
    conn = get_timescaledb_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO warning_light_events (vehicle_id, warning_type, timestamp)
            VALUES (%s, %s, %s)
        """, (vehicle_id, warning_type, timestamp))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Failed to write warning light event: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
