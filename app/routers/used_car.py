from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models


router = APIRouter(prefix="/used-car", tags=["used_car"])


@router.get("/{vehicle_id}")
def get_used_car(vehicle_id: str, db: Session = Depends(get_db)):
    row = db.query(models.UsedCar).filter(models.UsedCar.vehicle_id == vehicle_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Used car evaluation not found")
    return {
        "vehicle_id": row.vehicle_id,
        "engine_score": row.engine_score,
        "battery_score": row.battery_score,
        "tire_score": row.tire_score,
        "brake_score": row.brake_score,
        "fuel_efficiency_score": row.fuel_efficiency_score,
        "overall_grade": row.overall_grade,
        "analysis_date": row.analysis_date.isoformat() if row.analysis_date else None,
    }


