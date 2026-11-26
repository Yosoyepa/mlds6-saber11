"""Acceso a las fuentes de datos del proyecto."""

from saber11.database.carga import (
    cargar_saber11,
    contar_registros,
    descargar_saber11,
    obtener_saber11,
    ruta_por_defecto,
)

__all__ = [
    "cargar_saber11",
    "contar_registros",
    "descargar_saber11",
    "obtener_saber11",
    "ruta_por_defecto",
]
