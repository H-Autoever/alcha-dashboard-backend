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
        
        # TimescaleDB 하이퍼테이블로 변환
        cursor.execute("SELECT create_hypertable('engine_off_events', 'timestamp', if_not_exists => TRUE);")
        cursor.execute("SELECT create_hypertable('collision_events', 'timestamp', if_not_exists => TRUE);")
        
        # 인덱스 생성
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_engine_off_vehicle_id ON engine_off_events(vehicle_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_engine_off_timestamp ON engine_off_events(timestamp);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_collision_vehicle_id ON collision_events(vehicle_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_collision_timestamp ON collision_events(timestamp);")
        
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

def get_events_for_vehicle(vehicle_id: str, start_time: str = None, end_time: str = None) -> Dict[str, List[Dict[str, Any]]]:
    """특정 차량의 이벤트 데이터 조회"""
    conn = get_timescaledb_connection()
    if not conn:
        return {"engine_off_events": [], "collision_events": []}
    
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
        
        return {
            "engine_off_events": engine_off_events,
            "collision_events": collision_events
        }
        
    except Exception as e:
        print(f"Failed to query events: {e}")
        return {"engine_off_events": [], "collision_events": []}
    finally:
        conn.close()
