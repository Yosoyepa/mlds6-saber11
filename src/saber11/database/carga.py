"""Adquisición y carga de los resultados de la prueba Saber 11 (ICFES).

Fuente
------
Portal de Datos Abiertos de Colombia (https://www.datos.gov.co), recurso
"Resultados únicos Saber 11" (identificador ``kgxf-xxbe``), publicado por el
Instituto Colombiano para la Evaluación de la Educación (ICFES) bajo licencia
Creative Commons Attribution-ShareAlike 4.0. La consulta se hace contra la API
SODA de Socrata, que no exige credenciales.

Flujo
-----
1. ``descargar_saber11`` consulta la API por páginas y devuelve los registros
   tal como los entrega la fuente (todas las columnas como texto).
2. ``guardar_crudo`` escribe esos registros en ``data/raw`` junto con un
   archivo de metadatos (consulta, fecha de descarga y huella SHA-256).
3. ``cargar_saber11`` lee el archivo crudo, elimina las filas duplicadas
   exactas que trae la fuente y asigna los tipos de dato.

``obtener_saber11`` encadena los tres pasos y es el punto de entrada que usan
los scripts y notebooks del proyecto.
"""

from __future__ import annotations

import hashlib
import io
import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Sequence, Union

import pandas as pd
import requests

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------
# Parámetros de la fuente
# --------------------------------------------------------------------------
ID_RECURSO = "kgxf-xxbe"
URL_PORTAL = "https://www.datos.gov.co"
URL_RECURSO = f"{URL_PORTAL}/resource/{ID_RECURSO}"
URL_FICHA = f"{URL_PORTAL}/d/{ID_RECURSO}"
LICENCIA = "Creative Commons Attribution-ShareAlike 4.0 International"

# Recorte de datos que usa el proyecto (ver docs/data/data_definition.md).
PERIODO_POR_DEFECTO = "20224"
DIGITOS_POR_DEFECTO = ("7",)
TAM_PAGINA = 50_000

LLAVE = "estu_consecutivo"
COLUMNA_FECHA = "estu_fechanacimiento"
FORMATO_FECHA = "%d/%m/%Y"
FECHA_MINIMA_VALIDA = pd.Timestamp("1900-01-01")

COLUMNAS_PUNTAJE = [
    "punt_ingles",
    "punt_matematicas",
    "punt_sociales_ciudadanas",
    "punt_c_naturales",
    "punt_lectura_critica",
    "punt_global",
]

# Esquema del recurso, en el orden en que lo publica la fuente.
COLUMNAS = [
    "periodo",
    "estu_tipodocumento",
    "estu_consecutivo",
    "cole_area_ubicacion",
    "cole_bilingue",
    "cole_calendario",
    "cole_caracter",
    "cole_cod_dane_establecimiento",
    "cole_cod_dane_sede",
    "cole_cod_depto_ubicacion",
    "cole_cod_mcpio_ubicacion",
    "cole_codigo_icfes",
    "cole_depto_ubicacion",
    "cole_genero",
    "cole_jornada",
    "cole_mcpio_ubicacion",
    "cole_naturaleza",
    "cole_nombre_establecimiento",
    "cole_nombre_sede",
    "cole_sede_principal",
    "estu_cod_depto_presentacion",
    "estu_cod_mcpio_presentacion",
    "estu_cod_reside_depto",
    "estu_cod_reside_mcpio",
    "estu_depto_presentacion",
    "estu_depto_reside",
    "estu_estadoinvestigacion",
    "estu_estudiante",
    "estu_fechanacimiento",
    "estu_genero",
    "estu_mcpio_presentacion",
    "estu_mcpio_reside",
    "estu_nacionalidad",
    "estu_pais_reside",
    "estu_privado_libertad",
    "fami_cuartoshogar",
    "fami_educacionmadre",
    "fami_educacionpadre",
    "fami_estratovivienda",
    "fami_personashogar",
    "fami_tieneautomovil",
    "fami_tienecomputador",
    "fami_tieneinternet",
    "fami_tienelavadora",
    "desemp_ingles",
    "punt_ingles",
    "punt_matematicas",
    "punt_sociales_ciudadanas",
    "punt_c_naturales",
    "punt_lectura_critica",
    "punt_global",
]

# Respuestas HTTP ante las que vale la pena reintentar la consulta.
CODIGOS_REINTENTO = {429, 500, 502, 503, 504}

Ruta = Union[str, Path]


# --------------------------------------------------------------------------
# Consulta a la API
# --------------------------------------------------------------------------
def crear_sesion() -> requests.Session:
    """Crea la sesión HTTP con la que se consulta la API.

    La API funciona sin credenciales. Si existe la variable de entorno
    ``SOCRATA_APP_TOKEN`` se envía como ``X-App-Token``, lo que únicamente
    amplía el límite de solicitudes permitido por el portal.
    """
    sesion = requests.Session()
    token = os.environ.get("SOCRATA_APP_TOKEN")
    if token:
        sesion.headers["X-App-Token"] = token
    return sesion


def normalizar_digitos(digitos: Optional[Sequence[str]]) -> tuple:
    """Valida y ordena los dígitos terminales que definen la muestra.

    Devuelve una tupla vacía cuando no hay muestreo (se pide ``None``, una
    secuencia vacía o los diez dígitos), es decir, el periodo completo.
    """
    if not digitos:
        return ()
    unicos = sorted({str(d).strip() for d in digitos})
    if any(len(d) != 1 or not d.isdigit() for d in unicos):
        raise ValueError(
            f"Los dígitos de muestreo deben ser caracteres entre 0 y 9; se recibió {digitos!r}."
        )
    return () if len(unicos) == 10 else tuple(unicos)


def construir_filtro(
    periodo: str = PERIODO_POR_DEFECTO,
    digitos: Optional[Sequence[str]] = DIGITOS_POR_DEFECTO,
) -> str:
    """Construye la cláusula ``$where`` (SoQL) que delimita los datos.

    Parameters
    ----------
    periodo:
        Periodo de aplicación del examen con el formato del ICFES ``AAAAP``
        (por ejemplo ``"20224"``: año 2022, aplicación 4, calendario A).
    digitos:
        Dígitos terminales de ``estu_consecutivo`` que se conservan. Como el
        consecutivo se asigna de forma secuencial, quedarse con un dígito
        terminal equivale a un muestreo sistemático de 1 de cada 10
        examinados, reproducible y sin semilla aleatoria. ``None`` descarga el
        periodo completo.
    """
    periodo = str(periodo).strip()
    if len(periodo) != 5 or not periodo.isdigit():
        raise ValueError(f"El periodo debe tener el formato AAAAP (p. ej. '20224'); se recibió {periodo!r}.")

    filtro = f"periodo = '{periodo}'"
    digitos = normalizar_digitos(digitos)
    if digitos:
        condiciones = " OR ".join(f"{LLAVE} like '%{d}'" for d in digitos)
        filtro += f" AND ({condiciones})"
    return filtro


def _solicitar(
    sesion: requests.Session,
    url: str,
    parametros: dict,
    *,
    reintentos: int = 4,
    tiempo_limite: int = 180,
) -> requests.Response:
    """Hace una solicitud GET con reintentos y espera exponencial."""
    ultimo_error: Optional[Exception] = None
    for intento in range(1, reintentos + 1):
        try:
            respuesta = sesion.get(url, params=parametros, timeout=tiempo_limite)
        except (requests.ConnectionError, requests.Timeout) as error:
            ultimo_error = error
        else:
            if respuesta.status_code not in CODIGOS_REINTENTO:
                # Un 4xx distinto de 429 es un error de la consulta: no se reintenta.
                respuesta.raise_for_status()
                return respuesta
            ultimo_error = requests.HTTPError(f"HTTP {respuesta.status_code}", response=respuesta)

        if intento < reintentos:
            espera = 2**intento
            logger.warning(
                "Intento %d/%d fallido (%s); se reintenta en %d s.", intento, reintentos, ultimo_error, espera
            )
            time.sleep(espera)

    raise ConnectionError(f"No fue posible consultar {url} tras {reintentos} intentos.") from ultimo_error


def contar_registros(
    periodo: str = PERIODO_POR_DEFECTO,
    digitos: Optional[Sequence[str]] = DIGITOS_POR_DEFECTO,
    sesion: Optional[requests.Session] = None,
) -> int:
    """Devuelve el número de filas que la fuente tiene para el recorte pedido."""
    sesion = sesion or crear_sesion()
    parametros = {"$select": "count(*) as n", "$where": construir_filtro(periodo, digitos)}
    respuesta = _solicitar(sesion, f"{URL_RECURSO}.json", parametros)
    return int(respuesta.json()[0]["n"])


def descargar_saber11(
    periodo: str = PERIODO_POR_DEFECTO,
    digitos: Optional[Sequence[str]] = DIGITOS_POR_DEFECTO,
    tam_pagina: int = TAM_PAGINA,
    sesion: Optional[requests.Session] = None,
) -> pd.DataFrame:
    """Descarga los registros del recorte pedido tal como los entrega la fuente.

    La descarga se hace por páginas ordenadas por el identificador interno de
    fila (``:id``), que es estable entre solicitudes. Todas las columnas se
    leen como texto para no alterar códigos con ceros a la izquierda (DANE,
    departamento, municipio). Al final se comprueba que el número de filas
    recibidas coincida con el conteo que reporta la propia API.
    """
    if tam_pagina <= 0:
        raise ValueError("El tamaño de página debe ser un entero positivo.")

    sesion = sesion or crear_sesion()
    filtro = construir_filtro(periodo, digitos)
    total = contar_registros(periodo, digitos, sesion)
    if total == 0:
        raise ValueError(f"La fuente no tiene registros para el filtro: {filtro}")
    logger.info("La fuente reporta %d filas para el filtro: %s", total, filtro)

    paginas = []
    for desplazamiento in range(0, total, tam_pagina):
        parametros = {
            "$where": filtro,
            "$order": ":id",
            "$limit": tam_pagina,
            "$offset": desplazamiento,
        }
        respuesta = _solicitar(sesion, f"{URL_RECURSO}.csv", parametros)
        pagina = pd.read_csv(
            io.BytesIO(respuesta.content),
            dtype=str,
            encoding="utf-8",
            keep_default_na=False,
            na_values=[""],
        )
        paginas.append(pagina)
        logger.info("Descargadas %d de %d filas.", min(desplazamiento + len(pagina), total), total)

    datos = pd.concat(paginas, ignore_index=True)

    if len(datos) != total:
        raise RuntimeError(f"Descarga incompleta: se esperaban {total} filas y llegaron {len(datos)}.")
    faltantes = [columna for columna in COLUMNAS if columna not in datos.columns]
    if faltantes:
        raise RuntimeError(f"La fuente cambió de esquema; faltan las columnas: {faltantes}")

    return datos[COLUMNAS]


# --------------------------------------------------------------------------
# Almacenamiento local
# --------------------------------------------------------------------------
def ruta_por_defecto(
    directorio: Ruta = "data/raw",
    periodo: str = PERIODO_POR_DEFECTO,
    digitos: Optional[Sequence[str]] = DIGITOS_POR_DEFECTO,
) -> Path:
    """Ruta del archivo crudo que corresponde a un periodo y una muestra."""
    digitos = normalizar_digitos(digitos)
    sufijo = f"d{''.join(digitos)}" if digitos else "completo"
    return Path(directorio) / f"saber11_{periodo}_{sufijo}.csv"


def _huella_sha256(ruta: Path) -> str:
    huella = hashlib.sha256()
    with open(ruta, "rb") as archivo:
        for bloque in iter(lambda: archivo.read(1 << 20), b""):
            huella.update(bloque)
    return huella.hexdigest()


def guardar_crudo(datos: pd.DataFrame, ruta: Ruta, filtro: str) -> Path:
    """Guarda los datos crudos en CSV (UTF-8) y un archivo de metadatos.

    El archivo ``<nombre>.meta.json`` deja constancia de la consulta, la fecha
    de descarga y la huella SHA-256 del CSV, de modo que se pueda verificar
    después con qué datos exactos se trabajó.
    """
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    datos.to_csv(ruta, index=False, encoding="utf-8")

    metadatos = {
        "fuente": "Resultados únicos Saber 11 - ICFES",
        "ficha": URL_FICHA,
        "api": f"{URL_RECURSO}.csv",
        "licencia": LICENCIA,
        "filtro_soql": filtro,
        "fecha_descarga_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "filas": int(len(datos)),
        "columnas": int(datos.shape[1]),
        "sha256": _huella_sha256(ruta),
    }
    ruta_meta = ruta.with_suffix(".meta.json")
    ruta_meta.write_text(json.dumps(metadatos, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Datos crudos guardados en %s (%d filas).", ruta, len(datos))
    return ruta


def leer_crudo(ruta: Ruta) -> pd.DataFrame:
    """Lee el archivo crudo sin transformarlo (todas las columnas como texto)."""
    return pd.read_csv(ruta, dtype=str, encoding="utf-8", keep_default_na=False, na_values=[""])


# --------------------------------------------------------------------------
# Carga para análisis
# --------------------------------------------------------------------------
def eliminar_duplicados_exactos(datos: pd.DataFrame) -> pd.DataFrame:
    """Elimina filas idénticas en todas sus columnas.

    El recurso publica dos veces cada registro de los periodos 20194 y 20224.
    Son copias exactas, así que quitarlas no descarta información.
    """
    sin_duplicados = datos.drop_duplicates(ignore_index=True)
    eliminadas = len(datos) - len(sin_duplicados)
    if eliminadas:
        logger.info("Se eliminaron %d filas duplicadas exactas de %d.", eliminadas, len(datos))
    return sin_duplicados


def tipificar(datos: pd.DataFrame) -> pd.DataFrame:
    """Asigna tipos de dato a las columnas que no son texto.

    * Puntajes: numéricos (``float64``); lo que no sea un número queda nulo.
    * Fecha de nacimiento: ``datetime``; las fechas imposibles que trae la
      fuente (p. ej. ``01/01/0001``) quedan nulas.
    * Códigos (DANE, ICFES, departamento, municipio, periodo): se conservan
      como texto porque son identificadores y pueden empezar por cero.
    """
    datos = datos.copy()
    for columna in COLUMNAS_PUNTAJE:
        datos[columna] = pd.to_numeric(datos[columna], errors="coerce").astype("float64")

    fechas = pd.to_datetime(datos[COLUMNA_FECHA], format=FORMATO_FECHA, errors="coerce")
    datos[COLUMNA_FECHA] = fechas.where(fechas >= FECHA_MINIMA_VALIDA)
    return datos


def cargar_saber11(ruta: Ruta, quitar_duplicados: bool = True) -> pd.DataFrame:
    """Carga el archivo crudo listo para analizar.

    Parameters
    ----------
    ruta:
        Archivo CSV escrito por ``guardar_crudo``.
    quitar_duplicados:
        Si es ``True`` (por defecto) elimina las filas duplicadas exactas.

    Returns
    -------
    pandas.DataFrame
        Una fila por examinado, con los puntajes numéricos y la fecha de
        nacimiento como fecha.
    """
    datos = leer_crudo(ruta)
    if quitar_duplicados:
        datos = eliminar_duplicados_exactos(datos)
        repetidos = int(datos[LLAVE].duplicated().sum())
        if repetidos:
            logger.warning(
                "%d filas comparten %s con otra fila sin ser copias exactas; se conservan para revisarlas en el EDA.",
                repetidos,
                LLAVE,
            )
    return tipificar(datos)


def obtener_saber11(
    directorio: Ruta = "data/raw",
    periodo: str = PERIODO_POR_DEFECTO,
    digitos: Optional[Sequence[str]] = DIGITOS_POR_DEFECTO,
    forzar_descarga: bool = False,
    tam_pagina: int = TAM_PAGINA,
) -> pd.DataFrame:
    """Devuelve los datos del proyecto, descargándolos solo si hace falta.

    Si el archivo crudo ya existe en ``directorio`` se reutiliza; de lo
    contrario (o si ``forzar_descarga`` es ``True``) se consulta la API y se
    guarda. En ambos casos se devuelve el resultado de ``cargar_saber11``.
    """
    ruta = ruta_por_defecto(directorio, periodo, digitos)
    if forzar_descarga or not ruta.exists():
        crudo = descargar_saber11(periodo, digitos, tam_pagina)
        guardar_crudo(crudo, ruta, construir_filtro(periodo, digitos))
    else:
        logger.info("Se reutiliza el archivo local %s.", ruta)
    return cargar_saber11(ruta)
