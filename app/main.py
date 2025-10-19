from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .routers import vehicles, used_car, insurance, events
from .mongodb import connect_to_mongo, close_mongo_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시 MongoDB 연결
    await connect_to_mongo()
    yield
    # 종료 시 MongoDB 연결 해제
    await close_mongo_connection()

app = FastAPI(title="Alcha Dashboard API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vehicles.router, prefix="/api")
app.include_router(used_car.router, prefix="/api")
app.include_router(insurance.router, prefix="/api")
app.include_router(events.router, prefix="/api")

@app.get("/health")
def health():
    return {"status": "ok"}

# deploy test !!!

