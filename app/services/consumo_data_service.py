from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session


def obtener_consumo_diario_por_cuadrilla_item(
    db: Session,
    codigo_cuadrilla: str,
    codigo_item: str,
    dias: int,
) -> pd.DataFrame:
    fecha_fin = date.today()
    fecha_inicio = fecha_fin - timedelta(days=max(dias - 1, 0))

    query = text(
        """
        SELECT
            c.id_cuadrilla,
            c.codigo_cuadrilla,
            i.id_item,
            i.codigo_item,
            DATE(m.fecha_movimiento) AS fecha,
            SUM(
                CASE
                    WHEN m.tipo_movimiento IN ('SALIDA', 'SALIDA_CUADRILLA') THEN m.cantidad
                    WHEN m.tipo_movimiento IN ('DEVOLUCION', 'RETORNO_A_SEDE') THEN -m.cantidad
                    ELSE 0
                END
            ) AS consumo_diario
        FROM core.movimientos_inventario m
        JOIN core.cuadrillas c
            ON c.id_cuadrilla = m.cuadrilla_id
        LEFT JOIN core.inventario_sedes inv
            ON inv.id_inventario_sede = m.inventario_origen_id
        LEFT JOIN core.inventarios_servicio inv_serv
            ON inv_serv.id = m.inventario_servicio_origen_id
        JOIN core.items i
            ON i.id_item = COALESCE(inv.item_id, inv_serv.item_id)
        WHERE c.codigo_cuadrilla = :codigo_cuadrilla
          AND i.codigo_item = :codigo_item
          AND DATE(m.fecha_movimiento) BETWEEN :fecha_inicio AND :fecha_fin
          AND m.tipo_movimiento IN ('SALIDA', 'SALIDA_CUADRILLA', 'DEVOLUCION', 'RETORNO_A_SEDE')
        GROUP BY
            c.id_cuadrilla,
            c.codigo_cuadrilla,
            i.id_item,
            i.codigo_item,
            DATE(m.fecha_movimiento)
        ORDER BY DATE(m.fecha_movimiento)
        """
    )

    return pd.read_sql(
        query,
        db.bind,
        params={
            "codigo_cuadrilla": codigo_cuadrilla,
            "codigo_item": codigo_item,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
        },
    )


def obtener_consumo_diario_para_anomalias(
    db: Session,
    dias_periodo: int,
    periodos_historial: int,
) -> pd.DataFrame:
    total_dias = dias_periodo * (periodos_historial + 1)
    fecha_fin = date.today()
    fecha_inicio = fecha_fin - timedelta(days=max(total_dias - 1, 0))

    query = text(
        """
        SELECT
            c.id_cuadrilla,
            c.codigo_cuadrilla,
            i.id_item,
            i.codigo_item,
            i.nombre AS nombre_item,
            DATE(m.fecha_movimiento) AS fecha,
            SUM(
                CASE
                    WHEN m.tipo_movimiento IN ('SALIDA', 'SALIDA_CUADRILLA') THEN m.cantidad
                    WHEN m.tipo_movimiento IN ('DEVOLUCION', 'RETORNO_A_SEDE') THEN -m.cantidad
                    ELSE 0
                END
            ) AS consumo_diario
        FROM core.movimientos_inventario m
        JOIN core.cuadrillas c
            ON c.id_cuadrilla = m.cuadrilla_id
        LEFT JOIN core.inventario_sedes inv
            ON inv.id_inventario_sede = m.inventario_origen_id
        LEFT JOIN core.inventarios_servicio inv_serv
            ON inv_serv.id = m.inventario_servicio_origen_id
        JOIN core.items i
            ON i.id_item = COALESCE(inv.item_id, inv_serv.item_id)
        WHERE DATE(m.fecha_movimiento) BETWEEN :fecha_inicio AND :fecha_fin
          AND m.tipo_movimiento IN ('SALIDA', 'SALIDA_CUADRILLA', 'DEVOLUCION', 'RETORNO_A_SEDE')
          AND m.cuadrilla_id IS NOT NULL
        GROUP BY
            c.id_cuadrilla,
            c.codigo_cuadrilla,
            i.id_item,
            i.codigo_item,
            i.nombre,
            DATE(m.fecha_movimiento)
        ORDER BY DATE(m.fecha_movimiento), c.id_cuadrilla, i.id_item
        """
    )

    return pd.read_sql(
        query,
        db.bind,
        params={
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
        },
    )


def obtener_item_desde_movimientos(db: Session, codigo_item: str, dias_hist: int) -> pd.DataFrame:
    fecha_fin = date.today()
    fecha_inicio = fecha_fin - timedelta(days=max(dias_hist - 1, 0))

    query = text(
        """
        SELECT
            i.id_item,
            i.codigo_item,
            i.nombre AS nombre_item,
            DATE(m.fecha_movimiento) AS fecha,
            SUM(
                CASE
                    WHEN m.tipo_movimiento IN ('SALIDA', 'SALIDA_CUADRILLA') THEN m.cantidad
                    WHEN m.tipo_movimiento IN ('DEVOLUCION', 'RETORNO_A_SEDE') THEN -m.cantidad
                    ELSE 0
                END
            ) AS consumo_diario
        FROM core.movimientos_inventario m
        LEFT JOIN core.inventario_sedes inv
            ON inv.id_inventario_sede = m.inventario_origen_id
        LEFT JOIN core.inventarios_servicio inv_serv
            ON inv_serv.id = m.inventario_servicio_origen_id
        JOIN core.items i
            ON i.id_item = COALESCE(inv.item_id, inv_serv.item_id)
        WHERE i.codigo_item = :codigo_item
          AND DATE(m.fecha_movimiento) BETWEEN :fecha_inicio AND :fecha_fin
          AND m.tipo_movimiento IN ('SALIDA', 'SALIDA_CUADRILLA', 'DEVOLUCION', 'RETORNO_A_SEDE')
        GROUP BY
            i.id_item,
            i.codigo_item,
            i.nombre,
            DATE(m.fecha_movimiento)
        ORDER BY DATE(m.fecha_movimiento)
        """
    )

    return pd.read_sql(
        query,
        db.bind,
        params={
            "codigo_item": codigo_item,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
        },
    )
