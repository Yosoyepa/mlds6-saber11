"""Carga de datos del proyecto: resultados de la prueba Saber 11 (ICFES).

Descarga desde datos.gov.co el recorte de datos del proyecto, lo guarda en
``data/raw`` y muestra un resumen de lo cargado.

Uso (desde la raíz del repositorio)::

    python scripts/data_acquisition/main.py                 # muestra del proyecto
    python scripts/data_acquisition/main.py --forzar        # vuelve a descargar
    python scripts/data_acquisition/main.py --digitos 0,5   # muestra del 20 %
    python scripts/data_acquisition/main.py --digitos todos # periodo completo
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

try:
    from saber11.database import carga
except ModuleNotFoundError:
    # Permite ejecutar el script sin haber instalado el paquete (pip install -e .).
    sys.path.insert(0, str(RAIZ / "src"))
    from saber11.database import carga


def leer_argumentos() -> argparse.Namespace:
    analizador = argparse.ArgumentParser(description="Descarga y carga los resultados Saber 11 del proyecto.")
    analizador.add_argument(
        "--periodo",
        default=carga.PERIODO_POR_DEFECTO,
        help="Periodo del examen en formato AAAAP (por defecto: %(default)s).",
    )
    analizador.add_argument(
        "--digitos",
        default=",".join(carga.DIGITOS_POR_DEFECTO),
        help=(
            "Dígitos terminales de estu_consecutivo que definen la muestra, separados por coma. "
            "Cada dígito aporta cerca del 10 %% del periodo. Use 'todos' para el periodo completo "
            "(por defecto: %(default)s)."
        ),
    )
    analizador.add_argument(
        "--directorio",
        default=str(RAIZ / "data" / "raw"),
        help="Carpeta donde se guardan los datos crudos (por defecto: data/raw).",
    )
    analizador.add_argument(
        "--tam-pagina",
        type=int,
        default=carga.TAM_PAGINA,
        help="Filas por solicitud a la API (por defecto: %(default)s).",
    )
    analizador.add_argument(
        "--forzar",
        action="store_true",
        help="Descarga de nuevo aunque el archivo ya exista.",
    )
    return analizador.parse_args()


def resumir(datos, ruta: Path) -> None:
    """Imprime un resumen de los datos cargados."""
    nulos = (datos.isna().mean() * 100).sort_values(ascending=False).head(5).round(2)

    print()
    print("=" * 70)
    print("RESUMEN DE LA CARGA")
    print("=" * 70)
    print(f"Archivo crudo        : {ruta}")
    print(f"Filas (examinados)   : {len(datos):,}")
    print(f"Columnas             : {datos.shape[1]}")
    print(f"Consecutivos únicos  : {datos[carga.LLAVE].nunique():,}")
    print(f"Periodos             : {sorted(datos['periodo'].unique())}")
    print()
    print("Columnas con más valores faltantes (%):")
    print(nulos.to_string())
    print()
    print("Puntajes:")
    print(datos[carga.COLUMNAS_PUNTAJE].describe().T[["count", "mean", "std", "min", "max"]].round(2).to_string())
    print("=" * 70)


def main() -> int:
    argumentos = leer_argumentos()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s", datefmt="%H:%M:%S")

    digitos = None if argumentos.digitos.strip().lower() == "todos" else argumentos.digitos.split(",")

    datos = carga.obtener_saber11(
        directorio=argumentos.directorio,
        periodo=argumentos.periodo,
        digitos=digitos,
        forzar_descarga=argumentos.forzar,
        tam_pagina=argumentos.tam_pagina,
    )
    resumir(datos, carga.ruta_por_defecto(argumentos.directorio, argumentos.periodo, digitos))
    return 0


if __name__ == "__main__":
    sys.exit(main())
