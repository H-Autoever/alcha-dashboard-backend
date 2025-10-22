from datetime import datetime

from sqlalchemy import Column, String, Integer, Float, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from .db import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    vehicle_id = Column(String(50), primary_key=True)
    model = Column(String(100), nullable=False)
    year = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    daily_metrics = relationship("DailyMetrics", back_populates="vehicle", cascade="all, delete-orphan")
    score_daily = relationship("VehicleScoreDaily", back_populates="vehicle", cascade="all, delete-orphan")
    driving_habits = relationship("DrivingHabitMonthly", back_populates="vehicle", cascade="all, delete-orphan")


class DailyMetrics(Base):
    __tablename__ = "daily_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(String(50), ForeignKey("vehicles.vehicle_id"), nullable=False)
    total_distance = Column(Float)
    average_speed = Column(Float)
    fuel_efficiency = Column(Float)
    analysis_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    vehicle = relationship("Vehicle", back_populates="daily_metrics")


class VehicleScoreDaily(Base):
    __tablename__ = "vehicle_score_daily"

    vehicle_id = Column(String(50), ForeignKey("vehicles.vehicle_id", ondelete="CASCADE"), primary_key=True)
    analysis_date = Column(Date, primary_key=True)
    final_score = Column(Integer)
    engine_powertrain_score = Column(Integer)
    transmission_drivetrain_score = Column(Integer)
    brake_suspension_score = Column(Integer)
    adas_safety_score = Column(Integer)
    electrical_battery_score = Column(Integer)
    other_score = Column(Integer)
    engine_rpm_avg = Column(Integer)
    engine_coolant_temp_avg = Column(Float)
    transmission_oil_temp_avg = Column(Float)
    battery_voltage_avg = Column(Float)
    alternator_output_avg = Column(Float)
    temperature_ambient_avg = Column(Float)
    dtc_count = Column(Integer)
    gear_change_count = Column(Integer)
    abs_activation_count = Column(Integer)
    suspension_shock_count = Column(Integer)
    adas_sensor_fault_count = Column(Integer)
    aeb_activation_count = Column(Integer)
    engine_start_count = Column(Integer)
    suddenacc_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    vehicle = relationship("Vehicle", back_populates="score_daily")


class DrivingHabitMonthly(Base):
    __tablename__ = "driving_habit_monthly"

    vehicle_id = Column(String(50), ForeignKey("vehicles.vehicle_id", ondelete="CASCADE"), primary_key=True)
    analysis_month = Column(Date, primary_key=True)
    acceleration_events = Column(Integer)
    lane_departure_events = Column(Integer)
    night_drive_ratio = Column(Float)
    avg_drive_duration_minutes = Column(Float)
    avg_speed = Column(Float)
    avg_distance = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    vehicle = relationship("Vehicle", back_populates="driving_habits")
