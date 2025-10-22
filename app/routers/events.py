from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any
from datetime import datetime
from ..timescaledb import get_events_for_vehicle, get_timescaledb_connection

router = APIRouter(prefix="/events", tags=["events"])

@router.get("/{vehicle_id}", response_model=Dict[str, List[Dict[str, Any]]])
async def get_events_for_vehicle_endpoint(vehicle_id: str):
    """특정 차량의 이벤트 데이터 조회 (TimescaleDB)"""
    try:
        events = get_events_for_vehicle(vehicle_id)
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch events: {str(e)}")

@router.get("/{vehicle_id}/range", response_model=Dict[str, List[Dict[str, Any]]])
async def get_events_for_vehicle_range(
    vehicle_id: str,
    start_time: str = Query(None, description="시작 시간 (ISO 8601 format)"),
    end_time: str = Query(None, description="종료 시간 (ISO 8601 format)")
):
    """특정 차량의 시간 범위 이벤트 데이터 조회 (TimescaleDB)"""
    try:
        events = get_events_for_vehicle(vehicle_id, start_time, end_time)
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch events: {str(e)}")

@router.get("/{vehicle_id}/sudden-acceleration", response_model=List[Dict[str, Any]])
async def get_sudden_acceleration_events(
    vehicle_id: str,
    start_time: str = Query(None, description="시작 시간"),
    end_time: str = Query(None, description="종료 시간")
):
    """급가속 이벤트 조회"""
    try:
        conn = get_timescaledb_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        cursor = conn.cursor()
        
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
            SELECT vehicle_id, vehicle_speed, throttle_position, gear_position_mode, timestamp
            FROM sudden_acceleration_events
            WHERE vehicle_id = %s {time_condition}
            ORDER BY timestamp ASC
        """
        
        cursor.execute(query, params)
        events = []
        for row in cursor.fetchall():
            events.append({
                "vehicle_id": row[0],
                "vehicle_speed": row[1],
                "throttle_position": row[2],
                "gear_position_mode": row[3],
                "timestamp": row[4].isoformat()
            })
        
        return events
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch sudden acceleration events: {str(e)}")
    finally:
        if conn:
            conn.close()

@router.get("/{vehicle_id}/warning-lights", response_model=List[Dict[str, Any]])
async def get_warning_light_events(
    vehicle_id: str,
    start_time: str = Query(None, description="시작 시간"),
    end_time: str = Query(None, description="종료 시간")
):
    """경고등 이벤트 조회"""
    try:
        conn = get_timescaledb_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        cursor = conn.cursor()
        
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
            SELECT vehicle_id, warning_type, timestamp
            FROM warning_light_events
            WHERE vehicle_id = %s {time_condition}
            ORDER BY timestamp ASC
        """
        
        cursor.execute(query, params)
        events = []
        for row in cursor.fetchall():
            events.append({
                "vehicle_id": row[0],
                "warning_type": row[1],
                "timestamp": row[2].isoformat()
            })
        
        return events
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch warning light events: {str(e)}")
    finally:
        if conn:
            conn.close()

@router.get("/{vehicle_id}/periodic-data", response_model=List[Dict[str, Any]])
async def get_periodic_data(
    vehicle_id: str,
    start_time: str = Query(None, description="시작 시간"),
    end_time: str = Query(None, description="종료 시간")
):
    """주기적 데이터 조회 (위치, 온도, 배터리 등)"""
    try:
        conn = get_timescaledb_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        cursor = conn.cursor()
        
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
            SELECT vehicle_id, location_latitude, location_longitude, location_altitude,
                   temperature_cabin, temperature_ambient, battery_voltage,
                   tpms_front_left, tpms_front_right, tpms_rear_left, tpms_rear_right,
                   accelerometer_x, accelerometer_y, accelerometer_z, fuel_level,
                   engine_coolant_temp, transmission_oil_temp, timestamp
            FROM periodic_data
            WHERE vehicle_id = %s {time_condition}
            ORDER BY timestamp ASC
        """
        
        cursor.execute(query, params)
        data = []
        for row in cursor.fetchall():
            data.append({
                "vehicle_id": row[0],
                "location_latitude": row[1],
                "location_longitude": row[2],
                "location_altitude": row[3],
                "temperature_cabin": row[4],
                "temperature_ambient": row[5],
                "battery_voltage": row[6],
                "tpms_front_left": row[7],
                "tpms_front_right": row[8],
                "tpms_rear_left": row[9],
                "tpms_rear_right": row[10],
                "accelerometer_x": row[11],
                "accelerometer_y": row[12],
                "accelerometer_z": row[13],
                "fuel_level": row[14],
                "engine_coolant_temp": row[15],
                "transmission_oil_temp": row[16],
                "timestamp": row[17].isoformat()
            })
        
        return data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch periodic data: {str(e)}")
    finally:
        if conn:
            conn.close()
