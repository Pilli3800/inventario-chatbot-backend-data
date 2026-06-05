from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
from sqlalchemy.orm import Session

from app.services.consumo_data_service import obtener_item_desde_movimientos


def proyectar_consumo_simple(
    db: Session,
    codigo_item: str,
    dias_hist: int = 60,
    dias_futuro: int = 15,
):
    df = obtener_item_desde_movimientos(db, codigo_item, dias_hist)
    fecha_fin = date.today()
    fecha_inicio = fecha_fin - timedelta(days=max(dias_hist - 1, 0))

    if df.empty:
        return {
            "criterio": {
                "metodo": "promedio_historico_diario",
                "diasHist": dias_hist,
                "diasFuturo": dias_futuro,
            },
            "periodoAnalizado": {
                "fechaInicio": fecha_inicio.isoformat(),
                "fechaFin": fecha_fin.isoformat(),
                "itemCodigo": codigo_item,
            },
            "resumen": {
                "consumoPromedioDiario": 0.0,
                "desviacionStdDiaria": 0.0,
            },
            "resultados": [],
            "explicacionGeneral": "No hay historial suficiente para proyectar consumo.",
        }

    df["fecha"] = pd.to_datetime(df["fecha"])
    fechas_hist = pd.date_range(start=fecha_inicio, end=fecha_fin, freq="D")
    serie = (
        df.groupby("fecha", as_index=True)["consumo_diario"]
        .sum()
        .reindex(fechas_hist, fill_value=0.0)
        .astype(float)
    )

    promedio = float(serie.mean())
    desviacion = float(serie.std(ddof=0))
    fechas_futuras = pd.date_range(start=fecha_fin + timedelta(days=1), periods=dias_futuro, freq="D")

    resultados = []
    for fecha in fechas_futuras:
        resultados.append(
            {
                "fecha": fecha.strftime("%Y-%m-%d"),
                "consumoEstimado": round(promedio, 2),
                "metodo": "promedio_historico_diario",
                "explicacion": (
                    f"Proyeccion simple basada en el promedio diario de los ultimos {dias_hist} dias."
                ),
            }
        )

    return {
        "criterio": {
            "metodo": "promedio_historico_diario",
            "diasHist": dias_hist,
            "diasFuturo": dias_futuro,
        },
        "periodoAnalizado": {
            "fechaInicio": fecha_inicio.isoformat(),
            "fechaFin": fecha_fin.isoformat(),
            "itemCodigo": codigo_item,
        },
        "resumen": {
            "consumoPromedioDiario": round(promedio, 2),
            "desviacionStdDiaria": round(desviacion, 2),
        },
        "resultados": resultados,
        "explicacionGeneral": (
            "Esta proyeccion no usa un modelo avanzado; solo extiende el promedio historico diario "
            "como una primera aproximacion explicable."
        ),
    }
