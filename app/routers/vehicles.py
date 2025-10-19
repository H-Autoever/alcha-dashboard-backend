from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any

from ..db import get_db
from .. import models


router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.get("/", response_model=List[Dict[str, Any]])
def list_vehicles(db: Session = Depends(get_db)):
    # 각 차량의 최신 데이터만 반환 (메인 페이지용)
    subquery = db.query(
        models.BasicInfo.vehicle_id,
        models.BasicInfo.model,
        func.max(models.BasicInfo.analysis_date).label('latest_date')
    ).group_by(models.BasicInfo.vehicle_id, models.BasicInfo.model).subquery()
    
    rows = db.query(subquery.c.vehicle_id, subquery.c.model).all()
    return [{"vehicle_id": r[0], "model": r[1]} for r in rows]


@router.get("/summary", response_model=Dict[str, int])
def vehicles_summary(db: Session = Depends(get_db)):
    total = db.query(models.BasicInfo).count()
    return {"total_vehicles": total}


@router.get("/{vehicle_id}")
def get_vehicle_detail(vehicle_id: str, db: Session = Depends(get_db)):
    # 특정 차량의 모든 날짜별 데이터를 반환 (상세페이지용)
    rows = db.query(models.BasicInfo).filter(
        models.BasicInfo.vehicle_id == vehicle_id
    ).order_by(models.BasicInfo.analysis_date.desc()).all()
    
    print(f"DEBUG: Found {len(rows)} rows for vehicle_id {vehicle_id}")
    
    if not rows:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    # 첫 번째 행에서 기본 정보 추출
    first_row = rows[0]
    vehicle_info = {
        "vehicle_id": first_row.vehicle_id,
        "model": first_row.model,
        "year": first_row.year,
        "daily_data": []
    }
    
    # 모든 날짜별 데이터 추가
    for row in rows:
        vehicle_info["daily_data"].append({
            "analysis_date": row.analysis_date.isoformat() if row.analysis_date else None,
            "total_distance": row.total_distance,
            "average_speed": row.average_speed,
            "fuel_efficiency": row.fuel_efficiency,
        })
    
    return vehicle_info


