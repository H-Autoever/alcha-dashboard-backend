from datetime import date
from typing import Optional
from pydantic import BaseModel


class BasicInfoBase(BaseModel):
    vehicle_id: str
    model: str
    year: Optional[int] = None
    total_distance: Optional[float] = None
    average_speed: Optional[float] = None
    fuel_efficiency: Optional[float] = None
    collision_events: Optional[str] = None
    analysis_date: Optional[date] = None


class UsedCarBase(BaseModel):
    vehicle_id: str
    engine_score: Optional[int] = None
    battery_score: Optional[int] = None
    tire_score: Optional[int] = None
    brake_score: Optional[int] = None
    fuel_efficiency_score: Optional[int] = None
    overall_grade: Optional[int] = None
    analysis_date: Optional[date] = None


class InsuranceBase(BaseModel):
    vehicle_id: str
    over_speed_risk: Optional[int] = None
    sudden_accel_risk: Optional[int] = None
    sudden_turn_risk: Optional[int] = None
    night_drive_risk: Optional[int] = None
    overall_grade: Optional[int] = None
    analysis_date: Optional[date] = None


