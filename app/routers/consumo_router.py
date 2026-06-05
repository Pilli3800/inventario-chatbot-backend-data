from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.consumo_schema import (
    AnomaliaConsumoResponse,
    EvolucionConsumoResponse,
    ProyeccionConsumoResponse,
)
from app.services.alerta_reglas_service import (
    guardar_alertas_anomalias_consumo,
    guardar_alertas_eventos_consumo,
)
from app.services.consumo_anomalias_service import detectar_anomalias_consumo
from app.services.consumo_evolucion_service import obtener_evolucion_consumo
from app.services.consumo_prediccion_service import proyectar_consumo_simple

router = APIRouter(prefix="/ml/consumo", tags=["consumo"])


@router.get("/anomalias", response_model=AnomaliaConsumoResponse)
def consumo_anomalias(
    dias: int = Query(7, ge=1, le=30),
    periodosHistorial: int = Query(4, ge=2, le=12),
    guardarAlertas: bool = Query(False),
    db: Session = Depends(get_db),
):
    respuesta = detectar_anomalias_consumo(
        db=db,
        dias=dias,
        periodos_historial=periodosHistorial,
    )

    if guardarAlertas:
        guardar_alertas_anomalias_consumo(db, respuesta["resultados"])

    return respuesta


@router.get("/evolucion", response_model=EvolucionConsumoResponse)
def consumo_evolucion(
    cuadrillaCodigo: str = Query(..., min_length=1),
    itemCodigo: str = Query(..., min_length=1),
    dias: int = Query(30, ge=7, le=120),
    guardarAlertas: bool = Query(False),
    db: Session = Depends(get_db),
):
    respuesta = obtener_evolucion_consumo(db, cuadrillaCodigo, itemCodigo, dias)

    if guardarAlertas:
        guardar_alertas_eventos_consumo(db, respuesta["resultados"], cuadrillaCodigo)

    return respuesta


@router.get("/proyeccion", response_model=ProyeccionConsumoResponse)
def consumo_proyeccion(
    itemCodigo: str = Query(..., min_length=1),
    diasHist: int = Query(60, ge=15, le=180),
    diasFuturo: int = Query(15, ge=1, le=60),
    db: Session = Depends(get_db),
):
    return proyectar_consumo_simple(
        db=db,
        codigo_item=itemCodigo,
        dias_hist=diasHist,
        dias_futuro=diasFuturo,
    )
