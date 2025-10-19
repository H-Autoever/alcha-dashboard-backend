from sqlalchemy import Column, String, Integer, Float, Date, Text, ForeignKey
from .db import Base


class BasicInfo(Base):
    __tablename__ = "basic_info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(String(50), nullable=False)
    model = Column(String(100), nullable=False)
    year = Column(Integer)
    total_distance = Column(Float)
    average_speed = Column(Float)
    fuel_efficiency = Column(Float)
    analysis_date = Column(Date)


class UsedCar(Base):
    __tablename__ = "used_car"

    vehicle_id = Column(String(50), ForeignKey("basic_info.vehicle_id", ondelete="CASCADE"), primary_key=True)
    engine_score = Column(Integer)
    battery_score = Column(Integer)
    tire_score = Column(Integer)
    brake_score = Column(Integer)
    fuel_efficiency_score = Column(Integer)
    overall_grade = Column(Integer)
    analysis_date = Column(Date)


class Insurance(Base):
    __tablename__ = "insurance"

    vehicle_id = Column(String(50), ForeignKey("basic_info.vehicle_id", ondelete="CASCADE"), primary_key=True)
    over_speed_risk = Column(Integer)
    sudden_accel_risk = Column(Integer)
    sudden_turn_risk = Column(Integer)
    night_drive_risk = Column(Integer)
    overall_grade = Column(Integer)
    analysis_date = Column(Date)


