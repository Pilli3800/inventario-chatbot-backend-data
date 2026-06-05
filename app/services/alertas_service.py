from sqlalchemy.orm import Session
from sqlalchemy import text


def crear_alerta_si_no_existe(
    db: Session,
    tipo: str,
    descripcion: str,
    referencia_tipo: str,
    referencia_codigo: str,
) -> bool:
    # Evita duplicados del mismo evento reciente.
    existe = db.execute(
        text(
            """
            SELECT 1
            FROM data.alertas_ml
            WHERE tipo = :tipo
            AND referencia_tipo = :ref_tipo
            AND referencia_codigo = :ref_codigo
            AND fecha_alerta >= NOW() - INTERVAL '1 hour'
            LIMIT 1
            """
        ),
        {
            "tipo": tipo,
            "ref_tipo": referencia_tipo,
            "ref_codigo": referencia_codigo,
        },
    ).fetchone()

    if existe:
        return False

    db.execute(
        text(
            """
            INSERT INTO data.alertas_ml (
                tipo,
                descripcion,
                referencia_tipo,
                referencia_codigo
            ) VALUES (
                :tipo,
                :descripcion,
                :ref_tipo,
                :ref_codigo
            )
            """
        ),
        {
            "tipo": tipo,
            "descripcion": descripcion,
            "ref_tipo": referencia_tipo,
            "ref_codigo": referencia_codigo,
        },
    )

    db.commit()
    return True
