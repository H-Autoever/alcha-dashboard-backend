from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import vehicles, used_car, insurance

app = FastAPI(title="Alcha Dashboard API")

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


@app.get("/health")
def health():
    return {"status": "ok"}


