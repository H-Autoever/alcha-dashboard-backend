from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models


router = APIRouter(prefix="/insurance", tags=["insurance"])

@router.get("/")
def list_insurance(db: Session = Depends(get_db)):
    rows = db.query(models.Insurance).all()
    return [
        {
            "vehicle_id": r.vehicle_id,
            "over_speed_risk": r.over_speed_risk,
            "sudden_accel_risk": r.sudden_accel_risk,
            "sudden_turn_risk": r.sudden_turn_risk,
            "night_drive_risk": r.night_drive_risk,
            "overall_grade": r.overall_grade,
            "analysis_date": r.analysis_date.isoformat() if r.analysis_date else None,
        }
        for r in rows
    ]


@router.get("/{vehicle_id}")
def get_insurance(vehicle_id: str, db: Session = Depends(get_db)):
    row = db.query(models.Insurance).filter(models.Insurance.vehicle_id == vehicle_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Insurance risk not found")
    return {
        "vehicle_id": row.vehicle_id,
        "over_speed_risk": row.over_speed_risk,
        "sudden_accel_risk": row.sudden_accel_risk,
        "sudden_turn_risk": row.sudden_turn_risk,
        "night_drive_risk": row.night_drive_risk,
        "overall_grade": row.overall_grade,
        "analysis_date": row.analysis_date.isoformat() if row.analysis_date else None,
    }


