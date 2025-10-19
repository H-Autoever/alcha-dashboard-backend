from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict, Any
from datetime import datetime
import json

from ..mongodb import get_mongodb

router = APIRouter(prefix="/events", tags=["events"])

@router.get("/{vehicle_id}")
async def get_vehicle_events(vehicle_id: str, db: AsyncIOMotorClient = Depends(get_mongodb)):
    """특정 차량의 모든 이벤트 조회"""
    try:
        # Engine Off Events 조회
        engine_off_cursor = db.alcha_events.engine_off_events.find(
            {"vehicle_id": vehicle_id}
        ).sort("timestamp", 1)
        engine_off_events = await engine_off_cursor.to_list(length=None)
        
        # Collision Events 조회
        collision_cursor = db.alcha_events.collision_events.find(
            {"vehicle_id": vehicle_id}
        ).sort("timestamp", 1)
        collision_events = await collision_cursor.to_list(length=None)
        
        # ObjectId를 문자열로 변환
        for event in engine_off_events:
            if "_id" in event:
                event["_id"] = str(event["_id"])
            if "timestamp" in event:
                event["timestamp"] = event["timestamp"].isoformat()
            if "created_at" in event:
                event["created_at"] = event["created_at"].isoformat()
        
        for event in collision_events:
            if "_id" in event:
                event["_id"] = str(event["_id"])
            if "timestamp" in event:
                event["timestamp"] = event["timestamp"].isoformat()
            if "created_at" in event:
                event["created_at"] = event["created_at"].isoformat()
        
        return {
            "vehicle_id": vehicle_id,
            "engine_off_events": engine_off_events,
            "collision_events": collision_events
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이벤트 조회 중 오류 발생: {str(e)}")

@router.get("/{vehicle_id}/summary")
async def get_vehicle_events_summary(vehicle_id: str, db: AsyncIOMotorClient = Depends(get_mongodb)):
    """특정 차량의 이벤트 요약 정보"""
    try:
        # Engine Off Events 개수
        engine_off_count = await db.alcha_events.engine_off_events.count_documents(
            {"vehicle_id": vehicle_id}
        )
        
        # Collision Events 개수
        collision_count = await db.alcha_events.collision_events.count_documents(
            {"vehicle_id": vehicle_id}
        )
        
        return {
            "vehicle_id": vehicle_id,
            "total_engine_off_events": engine_off_count,
            "total_collision_events": collision_count,
            "total_events": engine_off_count + collision_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이벤트 요약 조회 중 오류 발생: {str(e)}")
