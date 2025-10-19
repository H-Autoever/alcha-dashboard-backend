from sqlalchemy import Column, String, Integer, Float, Date, Text, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    vehicle_id = Column(String(50), primary_key=True)
    model = Column(String(100), nullable=False)
    year = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 관계 설정
    daily_metrics = relationship("DailyMetrics", back_populates="vehicle", cascade="all, delete-orphan")
    used_car = relationship("UsedCar", back_populates="vehicle", cascade="all, delete-orphan")
    insurance = relationship("Insurance", back_populates="vehicle", cascade="all, delete-orphan")


class DailyMetrics(Base):
    __tablename__ = "daily_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(String(50), ForeignKey('vehicles.vehicle_id'), nullable=False)
    total_distance = Column(Float)
    average_speed = Column(Float)
    fuel_efficiency = Column(Float)
    analysis_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 관계 설정
    vehicle = relationship("Vehicle", back_populates="daily_metrics")


class UsedCar(Base):
    __tablename__ = "used_car"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(String(50), ForeignKey("vehicles.vehicle_id", ondelete="CASCADE"), nullable=False)
    market_value = Column(Numeric(10, 2))
    depreciation_rate = Column(Float)
    condition_score = Column(Integer)
    mileage_impact = Column(Float)
    analysis_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 관계 설정
    vehicle = relationship("Vehicle", back_populates="used_car")


class Insurance(Base):
    __tablename__ = "insurance"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(String(50), ForeignKey("vehicles.vehicle_id", ondelete="CASCADE"), nullable=False)
    risk_score = Column(Float)
    premium_estimate = Column(Numeric(10, 2))
    accident_history = Column(Integer)
    driver_age_factor = Column(Float)
    analysis_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 관계 설정
    vehicle = relationship("Vehicle", back_populates="insurance")


