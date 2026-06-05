from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
from sqlalchemy.orm import Session

from app.services.consumo_data_service import obtener_consumo_diario_por_cuadrilla_item


def obtener_evolucion_consumo(
    db: Session,
    codigo_cuadrilla: str,
    codigo_item: str,
    dias: int = 30,
):
    df = obtener_consumo_diario_por_cuadrilla_item(db, codigo_cuadrilla, codigo_item, dias)
    fecha_fin = date.today()
    fecha_inicio = fecha_fin - timedelta(days=max(dias - 1, 0))
    fechas = pd.date_range(start=fecha_inicio, end=fecha_fin, freq="D")

    if df.empty:
        serie = pd.Series(0.0, index=fechas, dtype=float)
    else:
        df["fecha"] = pd.to_datetime(df["fecha"])
        serie = (
            df.groupby("fecha", as_index=True)["consumo_diario"]
            .sum()
            .reindex(fechas, fill_value=0.0)
            .astype(float)
        )

    tendencia = serie.rolling(window=7, min_periods=1).mean()
    promedio = float(serie.mean())
    desviacion = float(serie.std(ddof=0))
    if desviacion > 0:
        z_scores = (serie - promedio) / desviacion
    else:
        z_scores = pd.Series(0.0, index=serie.index, dtype=float)

    resultados = []
    for fecha in serie.index:
        consumo_diario = float(serie.loc[fecha])
        tendencia_dia = float(tendencia.loc[fecha])
        z_score = float(z_scores.loc[fecha])
        evento_destacado = bool(abs(z_score) >= 2.0 and consumo_diario > 0)

        if evento_destacado:
            explicacion = (
                f"Evento destacado: consumo diario {consumo_diario:.2f} con z-score {z_score:.2f}, "
                "por encima del patron normal del periodo."
            )
        elif consumo_diario > tendencia_dia:
            explicacion = (
                f"Consumo diario {consumo_diario:.2f} por encima de la tendencia movil "
                f"de 7 dias ({tendencia_dia:.2f})."
            )
        else:
            explicacion = (
                f"Consumo diario alineado con la tendencia reciente ({tendencia_dia:.2f})."
            )

        resultados.append(
            {
                "fecha": fecha.strftime("%Y-%m-%d"),
                "consumoDiario": round(consumo_diario, 2),
                "tendencia": round(tendencia_dia, 2),
                "zScore": round(z_score, 2),
                "eventoDestacado": evento_destacado,
                "explicacion": explicacion,
            }
        )

    return {
        "criterio": {
            "metodo": "serie_diaria_consumo",
            "metodoTendencia": "promedio_movil_7_dias",
            "metodoEvento": "z_score_diario",
            "zScoreThreshold": 2.0,
        },
        "periodoAnalizado": {
            "fechaInicio": fecha_inicio.isoformat(),
            "fechaFin": fecha_fin.isoformat(),
            "cuadrillaCodigo": codigo_cuadrilla,
            "itemCodigo": codigo_item,
        },
        "resumen": {
            "consumoTotal": round(float(serie.sum()), 2),
            "consumoPromedioDiario": round(promedio, 2),
            "desviacionStdDiaria": round(desviacion, 2),
            "eventosDestacados": sum(1 for item in resultados if item["eventoDestacado"]),
        },
        "resultados": resultados,
        "explicacionGeneral": (
            "La evolucion se calcula con consumo diario neto, una tendencia simple de promedio movil "
            "y eventos destacados basados en z-score."
        ),
    }
