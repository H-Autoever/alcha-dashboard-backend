from motor.motor_asyncio import AsyncIOMotorClient
import os
from typing import Optional

class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    database = None

mongodb = MongoDB()

async def get_mongodb() -> AsyncIOMotorClient:
    return mongodb.client

async def connect_to_mongo():
    """MongoDB 연결"""
    mongodb.client = AsyncIOMotorClient(
        f"mongodb://admin:adminpassword@alcha-mongodb:27017/?authSource=admin"
    )
    mongodb.database = mongodb.client.alcha_events
    print("MongoDB 연결 성공!")

async def close_mongo_connection():
    """MongoDB 연결 종료"""
    if mongodb.client:
        mongodb.client.close()
        print("MongoDB 연결 종료!")
