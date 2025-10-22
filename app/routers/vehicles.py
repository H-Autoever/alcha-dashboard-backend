from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any

from ..db import get_db
from .. import models


router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.get("/", response_model=List[Dict[str, Any]])
def list_vehicles(db: Session = Depends(get_db)):
    # vehicles 테이블에서 모든 차량 정보 반환 (메인 페이지용)
    vehicles = db.query(models.Vehicle).all()
    return [{"vehicle_id": v.vehicle_id, "model": v.model} for v in vehicles]


@router.get("/summary", response_model=Dict[str, int])
def vehicles_summary(db: Session = Depends(get_db)):
    total = db.query(models.Vehicle).count()
    return {"total_vehicles": total}


@router.get("/{vehicle_id}")
def get_vehicle_detail(vehicle_id: str, db: Session = Depends(get_db)):
    # vehicles 테이블에서 차량 기본 정보 조회
    vehicle = db.query(models.Vehicle).filter(
        models.Vehicle.vehicle_id == vehicle_id
    ).first()
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    # daily_metrics 테이블에서 해당 차량의 모든 일별 데이터 조회
    daily_metrics = db.query(models.DailyMetrics).filter(
        models.DailyMetrics.vehicle_id == vehicle_id
    ).order_by(models.DailyMetrics.analysis_date.desc()).all()
    
    print(f"DEBUG: Found {len(daily_metrics)} daily metrics for vehicle_id {vehicle_id}")
    
    # 응답 데이터 구성
    vehicle_info = {
        "vehicle_id": vehicle.vehicle_id,
        "model": vehicle.model,
        "year": vehicle.year,
        "daily_data": []
    }
    
    # 모든 날짜별 데이터 추가
    for metric in daily_metrics:
        vehicle_info["daily_data"].append({
            "analysis_date": metric.analysis_date.isoformat() if metric.analysis_date else None,
            "total_distance": metric.total_distance,
            "average_speed": metric.average_speed,
            "fuel_efficiency": metric.fuel_efficiency,
            "collision_events": None,  # 이제 별도 테이블에서 관리
        })
    
    return vehicle_info


