from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .routers import vehicles, used_car, insurance, events
from .timescaledb import init_timescaledb

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시 TimescaleDB 초기화
    init_timescaledb()
    yield
    # 종료 시 정리 작업 (필요시)

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

