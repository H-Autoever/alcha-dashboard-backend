from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from datetime import datetime
from ..timescaledb import get_events_for_vehicle

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
async def get_events_for_vehicle_with_range(
    vehicle_id: str, 
    start_time: str = None, 
    end_time: str = None
):
    """특정 차량의 시간 범위별 이벤트 데이터 조회"""
    try:
        events = get_events_for_vehicle(vehicle_id, start_time, end_time)
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch events: {str(e)}")
