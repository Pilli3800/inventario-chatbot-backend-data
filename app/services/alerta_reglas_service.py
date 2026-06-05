from __future__ import annotations

from sqlalchemy.orm import Session

from app.services.alertas_service import crear_alerta_si_no_existe


def guardar_alertas_anomalias_consumo(db: Session, resultados: list[dict]) -> int:
    total_alertas = 0
    for item in resultados:
        if not item.get("isAnomaly"):
            continue

        alerta_creada = crear_alerta_si_no_existe(
            db,
            tipo="CONSUMO_ANOMALO",
            descripcion=(
                f"Consumo anomalo en cuadrilla {item['cuadrillaCodigo']} "
                f"para item {item['itemNombre']}."
            ),
            referencia_tipo="CUADRILLA_ITEM",
            referencia_codigo=f"{item['cuadrillaCodigo']}|{item['itemCodigo']}",
        )
        if alerta_creada:
            total_alertas += 1

    return total_alertas


def guardar_alertas_eventos_consumo(db: Session, resultados: list[dict], codigo_cuadrilla: str) -> int:
    total_alertas = 0
    for item in resultados:
        if not item.get("eventoDestacado"):
            continue

        alerta_creada = crear_alerta_si_no_existe(
            db,
            tipo="EVENTO_CONSUMO",
            descripcion=(
                f"Evento destacado de consumo en cuadrilla {codigo_cuadrilla} "
                f"el dia {item['fecha']}."
            ),
            referencia_tipo="CUADRILLA_FECHA",
            referencia_codigo=f"{codigo_cuadrilla}|{item['fecha']}",
        )
        if alerta_creada:
            total_alertas += 1

    return total_alertas
