import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.routers.alertas_router import router as alertas_router
from app.routers.consumo_router import router as consumo_router

load_dotenv()

app = FastAPI(
    title="Analisis de Consumo",
    description="Servicio para analisis simple y explicable de consumo de inventario.",
    version="1.0",
)

cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:8080").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=os.getenv("CORS_ALLOW_CREDENTIALS", "false").lower() == "true",
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(consumo_router)
app.include_router(alertas_router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "analisis-consumo",
        "version": "1.0",
    }


@app.get("/")
def root():
    return {
        "service": "Analisis de Consumo",
        "docs": "/docs",
        "version": "1.0",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=os.getenv("APP_HOST", "0.0.0.0"),
        port=int(os.getenv("APP_PORT", "8081")),
    )
