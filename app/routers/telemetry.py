from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any
from datetime import datetime
from ..timescaledb import get_telemetry_data

router = APIRouter(prefix="/telemetry", tags=["telemetry"])

@router.get("/{vehicle_id}", response_model=List[Dict[str, Any]])
async def get_vehicle_telemetry(
    vehicle_id: str,
    start_time: str = Query(None, description="시작 시간 (ISO 8601 format)"),
    end_time: str = Query(None, description="종료 시간 (ISO 8601 format)")
):
    """
    특정 차량의 텔레메트리 데이터 조회 (TimescaleDB)
    
    - **vehicle_id**: 차량 ID (예: VHC-001)
    - **start_time**: 시작 시간 (선택, 예: 2024-10-20T11:00:00)
    - **end_time**: 종료 시간 (선택, 예: 2024-10-20T12:00:00)
    
    반환: 시계열 텔레메트리 데이터 리스트
    - vehicle_speed: 차량 속도 (km/h)
    - engine_rpm: 엔진 회전수 (RPM)
    - throttle_position: 스로틀 위치 (%)
    - timestamp: 타임스탬프
    """
    try:
        telemetry = get_telemetry_data(vehicle_id, start_time, end_time)
        return telemetry
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch telemetry data: {str(e)}")

@router.get("/{vehicle_id}/summary", response_model=Dict[str, Any])
async def get_telemetry_summary(
    vehicle_id: str,
    start_time: str = Query(None, description="시작 시간"),
    end_time: str = Query(None, description="종료 시간")
):
    """
    특정 차량의 텔레메트리 데이터 요약 통계
    
    반환: 통계 정보
    - count: 총 데이터 포인트 수
    - avg_speed: 평균 속도
    - max_speed: 최고 속도
    - min_speed: 최저 속도
    - avg_rpm: 평균 RPM
    """
    try:
        telemetry = get_telemetry_data(vehicle_id, start_time, end_time)
        
        if not telemetry:
            return {
                "count": 0,
                "avg_speed": 0,
                "max_speed": 0,
                "min_speed": 0,
                "avg_rpm": 0,
                "max_rpm": 0,
                "min_rpm": 0
            }
        
        speeds = [d['vehicle_speed'] for d in telemetry]
        rpms = [d['engine_rpm'] for d in telemetry]
        
        return {
            "count": len(telemetry),
            "avg_speed": round(sum(speeds) / len(speeds), 2),
            "max_speed": max(speeds),
            "min_speed": min(speeds),
            "avg_rpm": round(sum(rpms) / len(rpms), 2),
            "max_rpm": max(rpms),
            "min_rpm": min(rpms)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate summary: {str(e)}")
