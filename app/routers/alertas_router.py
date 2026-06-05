from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

router = APIRouter(prefix="/ml/alertas")

@router.get("")
def listar_alertas(
    tipo: str | None = Query(None),
    referencia_tipo: str | None = Query(None),
    referencia_codigo: str | None = Query(None),
    fechaInicio: str | None = Query(None),
    fechaFin: str | None = Query(None),
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = """
        SELECT
            id,
            tipo,
            descripcion,
            referencia_tipo,
            referencia_codigo,
            fecha_alerta
        FROM data.alertas_ml
        WHERE 1=1
    """
    params = {}

    if tipo:
        query += " AND tipo = :tipo"
        params["tipo"] = tipo

    if referencia_tipo:
        query += " AND referencia_tipo = :referencia_tipo"
        params["referencia_tipo"] = referencia_tipo

    if referencia_codigo:
        query += " AND referencia_codigo = :referencia_codigo"
        params["referencia_codigo"] = referencia_codigo

    if fechaInicio:
        query += " AND fecha_alerta >= :fecha_inicio"
        params["fecha_inicio"] = fechaInicio

    if fechaFin:
        query += " AND fecha_alerta <= :fecha_fin"
        params["fecha_fin"] = fechaFin

    query += " ORDER BY fecha_alerta DESC LIMIT :limit"
    params["limit"] = limit

    result = db.execute(text(query), params)
    return [dict(row) for row in result.mappings()]
