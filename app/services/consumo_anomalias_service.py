from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
from sqlalchemy.orm import Session

from app.services.consumo_data_service import obtener_consumo_diario_para_anomalias


def detectar_anomalias_consumo(
    db: Session,
    dias: int = 7,
    periodos_historial: int = 4,
    z_score_threshold: float = 2.0,
):
    df = obtener_consumo_diario_para_anomalias(db, dias, periodos_historial)
    fecha_fin = date.today()
    fecha_inicio = fecha_fin - timedelta(days=(dias * (periodos_historial + 1)) - 1)

    if df.empty:
        return {
            "criterio": {
                "metodo": "z_score_periodos",
                "diasPeriodo": dias,
                "periodosHistorial": periodos_historial,
                "zScoreThreshold": z_score_threshold,
            },
            "periodoAnalizado": {
                "fechaInicio": fecha_inicio.isoformat(),
                "fechaFin": fecha_fin.isoformat(),
            },
            "totalRegistros": 0,
            "totalAnomalias": 0,
            "resultados": [],
            "explicacionGeneral": "No se encontraron movimientos de consumo en el periodo analizado.",
        }

    df["fecha"] = pd.to_datetime(df["fecha"])
    resultados = []
    fecha_referencia = pd.Timestamp(fecha_fin)
    cantidad_dias = dias * (periodos_historial + 1)

    for claves, grupo in df.groupby(["codigo_cuadrilla", "codigo_item", "nombre_item"]):
        serie = grupo.groupby("fecha", as_index=True)["consumo_diario"].sum().sort_index()
        fechas = pd.date_range(end=fecha_referencia, periods=cantidad_dias, freq="D")
        serie = serie.reindex(fechas, fill_value=0.0).astype(float)

        periodos = []
        for indice in range(periodos_historial + 1):
            fin = len(serie) - (indice * dias)
            inicio = fin - dias
            if inicio < 0:
                continue
            periodos.append(float(serie.iloc[inicio:fin].sum()))

        if len(periodos) < 2:
            continue

        consumo_actual = periodos[0]
        historial = periodos[1:]
        consumo_promedio = float(pd.Series(historial).mean())
        desviacion_std = float(pd.Series(historial).std(ddof=0))
        z_score = 0.0
        if desviacion_std > 0:
            z_score = (consumo_actual - consumo_promedio) / desviacion_std

        ratio = consumo_actual / consumo_promedio if consumo_promedio > 0 else 0.0
        is_anomaly = bool(
            (desviacion_std > 0 and z_score >= z_score_threshold)
            or (desviacion_std == 0 and consumo_promedio > 0 and ratio >= 1.5)
        )

        explicacion = _explicar_anomalia(
            consumo_actual=consumo_actual,
            consumo_promedio=consumo_promedio,
            desviacion_std=desviacion_std,
            z_score=z_score,
            is_anomaly=is_anomaly,
            dias=dias,
        )

        codigo_cuadrilla, codigo_item, nombre_item = claves

        resultados.append(
            {
                "cuadrillaCodigo": codigo_cuadrilla,
                "itemCodigo": codigo_item,
                "itemNombre": nombre_item,
                "consumoActual": round(consumo_actual, 2),
                "consumoPromedio": round(consumo_promedio, 2),
                "desviacionStd": round(desviacion_std, 2),
                "zScore": round(z_score, 2),
                "anomalyScore": round(abs(z_score), 4),
                "isAnomaly": is_anomaly,
                "explicacion": explicacion,
            }
        )

    resultados.sort(
        key=lambda item: (
            not item["isAnomaly"],
            -item["anomalyScore"],
            -item["consumoActual"],
        )
    )

    return {
        "criterio": {
            "metodo": "z_score_periodos",
            "diasPeriodo": dias,
            "periodosHistorial": periodos_historial,
            "zScoreThreshold": z_score_threshold,
        },
        "periodoAnalizado": {
            "fechaInicio": fecha_inicio.isoformat(),
            "fechaFin": fecha_fin.isoformat(),
        },
        "totalRegistros": len(resultados),
        "totalAnomalias": sum(1 for item in resultados if item["isAnomaly"]),
        "resultados": resultados,
        "explicacionGeneral": (
            "Se compara el consumo del periodo actual contra periodos historicos equivalentes "
            "usando promedio, desviacion estandar y z-score."
        ),
    }


def _explicar_anomalia(
    consumo_actual: float,
    consumo_promedio: float,
    desviacion_std: float,
    z_score: float,
    is_anomaly: bool,
    dias: int,
) -> str:
    if consumo_promedio == 0 and consumo_actual == 0:
        return f"Sin consumo en la ventana actual de {dias} dias ni en el historial comparable."

    if desviacion_std == 0 and consumo_promedio > 0:
        if is_anomaly:
            return (
                f"El consumo actual ({consumo_actual:.2f}) supera claramente un historial estable "
                f"de {consumo_promedio:.2f} en ventanas de {dias} dias."
            )
        return (
            f"El historial es estable en {consumo_promedio:.2f} y el consumo actual "
            f"({consumo_actual:.2f}) no rompe ese patron."
        )

    if is_anomaly:
        return (
            f"Consumo anomalo: {consumo_actual:.2f} frente a un promedio historico "
            f"de {consumo_promedio:.2f}, con z-score {z_score:.2f}."
        )

    return (
        f"Consumo dentro de rango esperado: {consumo_actual:.2f} en la ventana actual, "
        f"promedio historico {consumo_promedio:.2f}, z-score {z_score:.2f}."
    )
