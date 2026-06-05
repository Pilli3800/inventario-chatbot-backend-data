from __future__ import annotations

from typing import List

from pydantic import BaseModel


class CriterioAnalisisResponse(BaseModel):
    metodo: str
    diasPeriodo: int | None = None
    periodosHistorial: int | None = None
    zScoreThreshold: float | None = None
    diasHist: int | None = None
    diasFuturo: int | None = None
    metodoTendencia: str | None = None
    metodoEvento: str | None = None


class PeriodoAnalizadoResponse(BaseModel):
    fechaInicio: str
    fechaFin: str
    cuadrillaCodigo: str | None = None
    itemCodigo: str | None = None


class AnomaliaConsumoItemResponse(BaseModel):
    cuadrillaCodigo: str
    itemCodigo: str
    itemNombre: str
    consumoActual: float
    consumoPromedio: float
    desviacionStd: float
    zScore: float
    anomalyScore: float
    isAnomaly: bool
    explicacion: str


class AnomaliaConsumoResponse(BaseModel):
    criterio: CriterioAnalisisResponse
    periodoAnalizado: PeriodoAnalizadoResponse
    totalRegistros: int
    totalAnomalias: int
    resultados: List[AnomaliaConsumoItemResponse]
    explicacionGeneral: str


class EvolucionConsumoItemResponse(BaseModel):
    fecha: str
    consumoDiario: float
    tendencia: float
    zScore: float
    eventoDestacado: bool
    explicacion: str


class EvolucionResumenResponse(BaseModel):
    consumoTotal: float
    consumoPromedioDiario: float
    desviacionStdDiaria: float
    eventosDestacados: int


class EvolucionConsumoResponse(BaseModel):
    criterio: CriterioAnalisisResponse
    periodoAnalizado: PeriodoAnalizadoResponse
    resumen: EvolucionResumenResponse
    resultados: List[EvolucionConsumoItemResponse]
    explicacionGeneral: str


class ProyeccionConsumoItemResponse(BaseModel):
    fecha: str
    consumoEstimado: float
    metodo: str
    explicacion: str


class ProyeccionResumenResponse(BaseModel):
    consumoPromedioDiario: float
    desviacionStdDiaria: float


class ProyeccionConsumoResponse(BaseModel):
    criterio: CriterioAnalisisResponse
    periodoAnalizado: PeriodoAnalizadoResponse
    resumen: ProyeccionResumenResponse
    resultados: List[ProyeccionConsumoItemResponse]
    explicacionGeneral: str
