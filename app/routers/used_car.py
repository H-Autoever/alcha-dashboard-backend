from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models


router = APIRouter(prefix="/used-car", tags=["used_car"])

@router.get("/")
def list_used_car(db: Session = Depends(get_db)):
    rows = db.query(models.UsedCar).all()
    return [
        {
            "vehicle_id": r.vehicle_id,
            "engine_score": r.engine_score,
            "battery_score": r.battery_score,
            "tire_score": r.tire_score,
            "brake_score": r.brake_score,
            "fuel_efficiency_score": r.fuel_efficiency_score,
            "overall_grade": r.overall_grade,
            "analysis_date": r.analysis_date.isoformat() if r.analysis_date else None,
        }
        for r in rows
    ]


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


