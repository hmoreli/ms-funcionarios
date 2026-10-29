"""Reglas de fechas del legajo, compartidas por el alta y la modificación."""

import os
from datetime import date, datetime
from zoneinfo import ZoneInfo


def hoy() -> date:
    """La fecha de hoy en Paraguay (el servidor puede estar en UTC)."""
    return datetime.now(ZoneInfo(os.environ.get("ZONA_HORARIA", "America/Asuncion"))).date()


def errores_de_fechas(
    fecha_ingreso: date | None,
    fecha_ingreso_seguro_social: date | None,
    fecha_egreso: date | None,
) -> list[tuple[str, str]]:
    """Devuelve (campo, mensaje) por cada regla que no se cumple."""
    errores = []
    limite = hoy()
    if fecha_ingreso and fecha_ingreso > limite:
        errores.append(("fecha_ingreso", "La fecha de ingreso no puede ser posterior a hoy"))
    if fecha_ingreso_seguro_social:
        if fecha_ingreso_seguro_social > limite:
            errores.append(
                ("fecha_ingreso_seguro_social", "El ingreso a IPS no puede ser posterior a hoy")
            )
        if fecha_ingreso and fecha_ingreso_seguro_social < fecha_ingreso:
            errores.append(
                (
                    "fecha_ingreso_seguro_social",
                    "El ingreso a IPS no puede ser anterior a la fecha de ingreso",
                )
            )
    if fecha_egreso and fecha_ingreso and fecha_egreso < fecha_ingreso:
        errores.append(("fecha_egreso", "La fecha de egreso no puede ser anterior al ingreso"))
    return errores
