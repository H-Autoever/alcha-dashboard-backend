from datetime import date
from typing import Optional, List

from pydantic import BaseModel


class VehicleListItem(BaseModel):
    vehicle_id: str
    model: str
    year: Optional[int] = None


class DailyMetric(BaseModel):
    analysis_date: date
    total_distance: Optional[float] = None
    average_speed: Optional[float] = None
    fuel_efficiency: Optional[float] = None


class VehicleScoreDailyItem(BaseModel):
    analysis_date: date
    final_score: Optional[int] = None
    engine_powertrain_score: Optional[int] = None
    transmission_drivetrain_score: Optional[int] = None
    brake_suspension_score: Optional[int] = None
    adas_safety_score: Optional[int] = None
    electrical_battery_score: Optional[int] = None
    other_score: Optional[int] = None
    engine_rpm_avg: Optional[int] = None
    engine_coolant_temp_avg: Optional[float] = None
    transmission_oil_temp_avg: Optional[float] = None
    battery_voltage_avg: Optional[float] = None
    alternator_output_avg: Optional[float] = None
    temperature_ambient_avg: Optional[float] = None
    dtc_count: Optional[int] = None
    gear_change_count: Optional[int] = None
    abs_activation_count: Optional[int] = None
    suspension_shock_count: Optional[int] = None
    adas_sensor_fault_count: Optional[int] = None
    aeb_activation_count: Optional[int] = None
    engine_start_count: Optional[int] = None
    suddenacc_count: Optional[int] = None


class DrivingHabitMonthlyItem(BaseModel):
    analysis_month: date
    acceleration_events: Optional[int] = None
    lane_departure_events: Optional[int] = None
    night_drive_ratio: Optional[float] = None
    avg_drive_duration_minutes: Optional[float] = None
    avg_speed: Optional[float] = None
    avg_distance: Optional[float] = None


class VehicleDetailResponse(BaseModel):
    vehicle_id: str
    model: str
    year: Optional[int] = None
    latest_metrics: Optional[DailyMetric] = None
    recent_metrics: List[DailyMetric] = []
