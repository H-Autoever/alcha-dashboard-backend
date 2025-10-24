from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..db import get_db


router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.get("/", response_model=List[Dict[str, Any]])
def list_vehicles(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    vehicles = db.query(models.Vehicle).order_by(models.Vehicle.vehicle_id).all()
    return [
        {"vehicle_id": v.vehicle_id, "model": v.model, "year": v.year}
        for v in vehicles
    ]


@router.get("/summary", response_model=Dict[str, int])
def vehicles_summary(db: Session = Depends(get_db)) -> Dict[str, int]:
    total = db.query(models.Vehicle).count()
    return {"total_vehicles": total}


@router.get("/{vehicle_id}")
def get_vehicle_detail(vehicle_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    vehicle = (
        db.query(models.Vehicle)
        .filter(models.Vehicle.vehicle_id == vehicle_id)
        .first()
    )

    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    recent_metrics = (
        db.query(models.DailyMetrics)
        .filter(models.DailyMetrics.vehicle_id == vehicle_id)
        .order_by(models.DailyMetrics.analysis_date.desc())
        .limit(30)
        .all()
    )

    latest_metric = recent_metrics[0] if recent_metrics else None

    def serialize_metric(metric: Optional[models.DailyMetrics]) -> Optional[schemas.DailyMetric]:
        if not metric:
            return None
        return schemas.DailyMetric(
            analysis_date=metric.analysis_date,
            total_distance=metric.total_distance,
            average_speed=metric.average_speed,
            fuel_efficiency=metric.fuel_efficiency,
        )

    recent_serialized = [
        schemas.DailyMetric(
            analysis_date=metric.analysis_date,
            total_distance=metric.total_distance,
            average_speed=metric.average_speed,
            fuel_efficiency=metric.fuel_efficiency,
        )
        for metric in recent_metrics
    ]

    response = schemas.VehicleDetailResponse(
        vehicle_id=vehicle.vehicle_id,
        model=vehicle.model,
        year=vehicle.year,
        latest_metrics=serialize_metric(latest_metric),
        recent_metrics=recent_serialized,
    )

    return {
        "vehicle_id": response.vehicle_id,
        "model": response.model,
        "year": response.year,
        "latest_metrics": response.latest_metrics.dict() if response.latest_metrics else None,
        "recent_metrics": [metric.dict() for metric in response.recent_metrics],
    }


@router.get("/{vehicle_id}/scores")
def get_vehicle_scores(vehicle_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    vehicle = (
        db.query(models.Vehicle)
        .filter(models.Vehicle.vehicle_id == vehicle_id)
        .first()
    )
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    scores = (
        db.query(models.VehicleScoreDaily)
        .filter(models.VehicleScoreDaily.vehicle_id == vehicle_id)
        .order_by(models.VehicleScoreDaily.analysis_date.desc())
        .all()
    )

    return {
        "vehicle_id": vehicle_id,
        "records": [
            schemas.VehicleScoreDailyItem(
                analysis_date=score.analysis_date,
                final_score=score.final_score,
                engine_powertrain_score=score.engine_powertrain_score,
                transmission_drivetrain_score=score.transmission_drivetrain_score,
                brake_suspension_score=score.brake_suspension_score,
                adas_safety_score=score.adas_safety_score,
                electrical_battery_score=score.electrical_battery_score,
                other_score=score.other_score,
                engine_rpm_avg=score.engine_rpm_avg,
                engine_coolant_temp_avg=score.engine_coolant_temp_avg,
                transmission_oil_temp_avg=score.transmission_oil_temp_avg,
                battery_voltage_avg=score.battery_voltage_avg,
                alternator_output_avg=score.alternator_output_avg,
                temperature_ambient_avg=score.temperature_ambient_avg,
                dtc_count=score.dtc_count,
                gear_change_count=score.gear_change_count,
                abs_activation_count=score.abs_activation_count,
                suspension_shock_count=score.suspension_shock_count,
                adas_sensor_fault_count=score.adas_sensor_fault_count,
                aeb_activation_count=score.aeb_activation_count,
                engine_start_count=score.engine_start_count,
                suddenacc_count=score.suddenacc_count,
            ).dict()
            for score in scores
        ],
    }


@router.get("/{vehicle_id}/score/{analysis_date}")
def get_vehicle_score_by_date(vehicle_id: str, analysis_date: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """특정 날짜의 차량 점수 데이터 조회"""
    vehicle = (
        db.query(models.Vehicle)
        .filter(models.Vehicle.vehicle_id == vehicle_id)
        .first()
    )
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    # 날짜 문자열을 date 객체로 변환
    from datetime import datetime
    try:
        date_obj = datetime.strptime(analysis_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    score = (
        db.query(models.VehicleScoreDaily)
        .filter(
            models.VehicleScoreDaily.vehicle_id == vehicle_id,
            models.VehicleScoreDaily.analysis_date == date_obj
        )
        .first()
    )

    if not score:
        raise HTTPException(status_code=404, detail=f"No score data found for {analysis_date}")

    return {
        "vehicle_id": vehicle_id,
        "analysis_date": analysis_date,
        "scores": {
            "final_score": score.final_score,
            "engine_powertrain_score": score.engine_powertrain_score,
            "transmission_drivetrain_score": score.transmission_drivetrain_score,
            "brake_suspension_score": score.brake_suspension_score,
            "adas_safety_score": score.adas_safety_score,
            "electrical_battery_score": score.electrical_battery_score,
            "other_score": score.other_score,
        },
        "metrics": {
            "engine_rpm_avg": score.engine_rpm_avg,
            "engine_coolant_temp_avg": score.engine_coolant_temp_avg,
            "transmission_oil_temp_avg": score.transmission_oil_temp_avg,
            "battery_voltage_avg": score.battery_voltage_avg,
            "alternator_output_avg": score.alternator_output_avg,
            "temperature_ambient_avg": score.temperature_ambient_avg,
            "dtc_count": score.dtc_count,
            "gear_change_count": score.gear_change_count,
            "abs_activation_count": score.abs_activation_count,
            "suspension_shock_count": score.suspension_shock_count,
            "adas_sensor_fault_count": score.adas_sensor_fault_count,
            "aeb_activation_count": score.aeb_activation_count,
            "engine_start_count": score.engine_start_count,
            "suddenacc_count": score.suddenacc_count,
        }
    }


@router.get("/{vehicle_id}/score-history")
def get_vehicle_score_history(
    vehicle_id: str,
    days: int = 14,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """차량 점수 히스토리 조회 (기본 14일)"""
    if days <= 0:
        raise HTTPException(status_code=400, detail="days must be greater than 0")

    vehicle = (
        db.query(models.Vehicle)
        .filter(models.Vehicle.vehicle_id == vehicle_id)
        .first()
    )
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    def parse_date(value: Optional[str]) -> Optional[date]:
        if value is None:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    start_dt = parse_date(start_date)
    end_dt = parse_date(end_date)

    base_query = db.query(models.VehicleScoreDaily).filter(models.VehicleScoreDaily.vehicle_id == vehicle_id)

    latest_score = base_query.order_by(models.VehicleScoreDaily.analysis_date.desc()).first()
    if not latest_score:
        return {
            "vehicle_id": vehicle_id,
            "start_date": start_dt.isoformat() if start_dt else None,
            "end_date": end_dt.isoformat() if end_dt else None,
            "records": [],
        }

    if start_dt and end_dt and start_dt > end_dt:
        raise HTTPException(status_code=400, detail="start_date must be before or equal to end_date")

    if not start_dt and not end_dt:
        end_dt = latest_score.analysis_date
        start_dt = end_dt - timedelta(days=days - 1)
    elif start_dt and not end_dt:
        end_dt = start_dt + timedelta(days=days - 1)
    elif end_dt and not start_dt:
        start_dt = end_dt - timedelta(days=days - 1)

    history_query = db.query(models.VehicleScoreDaily).filter(
        models.VehicleScoreDaily.vehicle_id == vehicle_id,
        models.VehicleScoreDaily.analysis_date >= start_dt,
        models.VehicleScoreDaily.analysis_date <= end_dt,
    )

    scores = history_query.order_by(models.VehicleScoreDaily.analysis_date.asc()).all()

    records = [
        schemas.VehicleScoreHistoryItem(
            analysis_date=score.analysis_date,
            final_score=score.final_score,
            engine_powertrain_score=score.engine_powertrain_score,
            transmission_drivetrain_score=score.transmission_drivetrain_score,
            brake_suspension_score=score.brake_suspension_score,
            adas_safety_score=score.adas_safety_score,
            electrical_battery_score=score.electrical_battery_score,
            other_score=score.other_score,
        ).dict()
        for score in scores
    ]

    return {
        "vehicle_id": vehicle_id,
        "start_date": start_dt.isoformat() if start_dt else None,
        "end_date": end_dt.isoformat() if end_dt else None,
        "records": records,
    }


@router.get("/{vehicle_id}/driving-habits")
def get_driving_habits(vehicle_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    vehicle = (
        db.query(models.Vehicle)
        .filter(models.Vehicle.vehicle_id == vehicle_id)
        .first()
    )
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    habits = (
        db.query(models.DrivingHabitMonthly)
        .filter(models.DrivingHabitMonthly.vehicle_id == vehicle_id)
        .order_by(models.DrivingHabitMonthly.analysis_month.desc())
        .all()
    )

    records = [
        schemas.DrivingHabitMonthlyItem(
            analysis_month=habit.analysis_month,
            acceleration_events=habit.acceleration_events,
            lane_departure_events=habit.lane_departure_events,
            night_drive_ratio=habit.night_drive_ratio,
            avg_drive_duration_minutes=habit.avg_drive_duration_minutes,
            avg_speed=habit.avg_speed,
            avg_distance=habit.avg_distance,
        )
        for habit in habits
    ]

    latest = records[0] if records else None
    previous = records[1] if len(records) > 1 else None

    def to_dict(item: Optional[schemas.DrivingHabitMonthlyItem]) -> Optional[Dict[str, Any]]:
        return item.dict() if item else None

    def diff(
        latest_item: Optional[schemas.DrivingHabitMonthlyItem],
        previous_item: Optional[schemas.DrivingHabitMonthlyItem],
    ) -> Optional[Dict[str, Optional[float]]]:
        if not latest_item or not previous_item:
            return None
        return {
            "acceleration_events": (latest_item.acceleration_events or 0) - (previous_item.acceleration_events or 0),
            "lane_departure_events": (latest_item.lane_departure_events or 0) - (previous_item.lane_departure_events or 0),
            "night_drive_ratio": (latest_item.night_drive_ratio or 0.0) - (previous_item.night_drive_ratio or 0.0),
            "avg_drive_duration_minutes": (latest_item.avg_drive_duration_minutes or 0.0) - (previous_item.avg_drive_duration_minutes or 0.0),
            "avg_speed": (latest_item.avg_speed or 0.0) - (previous_item.avg_speed or 0.0),
            "avg_distance": (latest_item.avg_distance or 0.0) - (previous_item.avg_distance or 0.0),
        }

    return {
        "vehicle_id": vehicle_id,
        "latest": to_dict(latest),
        "previous": to_dict(previous),
        "delta": diff(latest, previous),
        "history": [item.dict() for item in records],
    }


@router.get("/{vehicle_id}/habit-monthly")
def get_vehicle_habit_monthly(
    vehicle_id: str,
    month: Optional[str] = None,
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    """차량의 월별 운전 습관 데이터 조회"""
    vehicle = (
        db.query(models.Vehicle)
        .filter(models.Vehicle.vehicle_id == vehicle_id)
        .first()
    )
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    query = (
        db.query(models.DrivingHabitMonthly)
        .filter(models.DrivingHabitMonthly.vehicle_id == vehicle_id)
    )

    if month:
        # 월 필터링 (YYYY-MM 형식) - LIKE 연산자 사용
        try:
            # 2025-09 -> 2025-09% 패턴으로 검색
            month_pattern = f"{month}%"
            query = query.filter(models.DrivingHabitMonthly.analysis_month.like(month_pattern))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid month format. Use YYYY-MM")

    records = query.order_by(models.DrivingHabitMonthly.analysis_month.desc()).all()

    if not records:
        raise HTTPException(status_code=404, detail=f"No habit data found for vehicle {vehicle_id}")

    # 각 월별로 운전 일수 계산
    result = []
    for record in records:
        # 해당 월의 운전 일수 계산 (engine_start_count > 0인 날짜 수)
        # analysis_month는 이미 Date 타입이므로 직접 사용
        year = record.analysis_month.year
        month_num = record.analysis_month.month
        
        # 해당 월의 첫째 날과 마지막 날
        from datetime import datetime
        import calendar
        first_day = datetime(year, month_num, 1).date()
        last_day = calendar.monthrange(year, month_num)[1]
        last_day_date = datetime(year, month_num, last_day).date()
        
        # 해당 월의 운전 일수 계산
        driving_days = (
            db.query(models.VehicleScoreDaily)
            .filter(
                models.VehicleScoreDaily.vehicle_id == vehicle_id,
                models.VehicleScoreDaily.analysis_date >= first_day,
                models.VehicleScoreDaily.analysis_date <= last_day_date,
                models.VehicleScoreDaily.engine_start_count > 0
            )
            .count()
        )
        
        result.append({
            "vehicle_id": record.vehicle_id,
            "analysis_month": record.analysis_month.isoformat(),
            "acceleration_events": record.acceleration_events,
            "deceleration_events": record.deceleration_events,
            "lane_departure_events": record.lane_departure_events,
            "night_drive_ratio": record.night_drive_ratio,
            "avg_drive_duration_minutes": record.avg_drive_duration_minutes,
            "avg_speed": record.avg_speed,
            "avg_distance": record.avg_distance,
            "driving_days": driving_days,
            "created_at": record.created_at.isoformat() if record.created_at else None,
        })
    
    return result
