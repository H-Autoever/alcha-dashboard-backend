from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from ..db import get_db
from .. import models


router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.get("/", response_model=List[Dict[str, Any]])
def list_vehicles(db: Session = Depends(get_db)):
    rows = db.query(models.BasicInfo.vehicle_id, models.BasicInfo.model).all()
    return [{"vehicle_id": r[0], "model": r[1]} for r in rows]


@router.get("/summary", response_model=Dict[str, int])
def vehicles_summary(db: Session = Depends(get_db)):
    total = db.query(models.BasicInfo).count()
    return {"total_vehicles": total}


@router.get("/{vehicle_id}")
def get_vehicle_detail(vehicle_id: str, db: Session = Depends(get_db)):
    row = db.query(models.BasicInfo).filter(models.BasicInfo.vehicle_id == vehicle_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return {
        "vehicle_id": row.vehicle_id,
        "model": row.model,
        "year": row.year,
        "total_distance": row.total_distance,
        "average_speed": row.average_speed,
        "fuel_efficiency": row.fuel_efficiency,
        "collision_events": row.collision_events,
        "analysis_date": row.analysis_date.isoformat() if row.analysis_date else None,
    }


