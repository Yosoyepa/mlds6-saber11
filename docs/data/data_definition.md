# Definición de los datos

## Origen de los datos

- **Fuente.** Conjunto *Resultados únicos Saber 11*, publicado por el Instituto Colombiano para la Evaluación de la Educación (ICFES) en el portal de Datos Abiertos de Colombia: <https://www.datos.gov.co/d/kgxf-xxbe> (identificador del recurso: `kgxf-xxbe`).
- **Contenido.** Resultados individuales y anonimizados del examen Saber 11 de 2010 a 2022: 7.109.704 filas y 51 columnas con datos del estudiante, de su hogar, de su colegio y sus puntajes.
- **Licencia.** Creative Commons Attribution-ShareAlike 4.0. Permite usar y transformar los datos citando la fuente y compartiendo lo derivado bajo la misma licencia.
- **Forma de obtención.** Consulta programática a la API SODA del portal (plataforma Socrata). Es pública y no exige credenciales ni registro. Los datos no se copian a mano ni se guardan en el repositorio: se descargan con el script del proyecto.
- **Recorte que usa el proyecto.**
  - *Periodo 2022-4.* Es la aplicación más reciente del recurso y corresponde casi por completo a colegios de calendario A (99,5 % de la muestra). Usar un solo periodo evita mezclar cohortes y cambios en el cuestionario. Los periodos anteriores a 2014-2 quedan descartados de entrada porque no tienen puntaje global.
  - *Muestra sistemática de 1 de cada 10 examinados.* Se conservan los registros cuyo `estu_consecutivo` termina en el dígito 7. Como el consecutivo se asigna de forma secuencial, el filtro es reproducible sin semilla aleatoria y se aplica en el servidor. El resultado, 53.407 estudiantes, es suficiente para un problema tabular y mantiene la descarga por debajo de un minuto.
- **Calidad de la fuente.** El recurso publica dos veces cada registro de los periodos 2019-4 y 2022-4 (1.065.888 filas para 532.792 examinados en 2022-4). El proceso de carga elimina esas copias.

## Especificación de los scripts para la carga de datos

| Archivo | Función |
| --- | --- |
| `src/saber11/database/carga.py` | Módulo con toda la lógica de la carga. Lo usan el script y el notebook |
| `scripts/data_acquisition/main.py` | Script de línea de comandos: descarga, guarda, carga y muestra un resumen |
| `scripts/data_acquisition/carga_de_datos.ipynb` | Notebook ejecutado que documenta la carga paso a paso y sus verificaciones |

Funciones principales de `carga.py`:

| Función | Qué hace |
| --- | --- |
| `construir_filtro(periodo, digitos)` | Arma la condición de consulta (SoQL) y valida los parámetros |
| `contar_registros(periodo, digitos)` | Pregunta a la API cuántas filas tiene el recorte |
| `descargar_saber11(periodo, digitos)` | Descarga por páginas, con reintentos, y verifica número de filas y esquema |
| `guardar_crudo(datos, ruta, filtro)` | Escribe el CSV crudo y su archivo de metadatos |
| `cargar_saber11(ruta)` | Lee el CSV crudo, elimina duplicados exactos y asigna tipos de dato |
| `obtener_saber11()` | Punto de entrada: descarga solo si el archivo no existe y devuelve los datos listos |

Ejecución desde la raíz del repositorio:

```bash
pip install -e .                                          # instala el paquete y sus dependencias (pandas, requests)
python scripts/data_acquisition/main.py                   # recorte del proyecto: periodo 20224, dígito 7
python scripts/data_acquisition/main.py --forzar          # descarga de nuevo aunque el archivo exista
python scripts/data_acquisition/main.py --digitos 0,5     # muestra del 20 %
python scripts/data_acquisition/main.py --digitos todos   # periodo completo
python scripts/data_acquisition/main.py --periodo 20194   # otro periodo
```

Desde Python, en cualquier fase posterior:

```python
from saber11.database import obtener_saber11

datos = obtener_saber11()   # DataFrame de 53.407 filas y 51 columnas
```

## Referencias a rutas o bases de datos origen y destino

| | Origen | Destino |
| --- | --- | --- |
| Ubicación | `https://www.datos.gov.co/resource/kgxf-xxbe.csv` | `data/raw/saber11_20224_d7.csv` |
| Tipo | API REST pública (SODA) | Archivo CSV local |
| Filas | 106.850 (con duplicados) | 106.850 en el archivo; 53.407 al cargarlo |
| Columnas | 51 | 51 |

### Rutas de origen de datos

- **Ubicación de los archivos de origen.** Los datos no están en archivos sino en una API. La consulta que define el recorte es:

  ```text
  GET https://www.datos.gov.co/resource/kgxf-xxbe.csv
      ?$where=periodo = '20224' AND (estu_consecutivo like '%7')
      &$order=:id
      &$limit=50000
      &$offset=0, 50000, 100000
  ```

  El conteo previo se obtiene del mismo recurso en formato JSON con `$select=count(*)`. Si se define la variable de entorno `SOCRATA_APP_TOKEN`, se envía como encabezado `X-App-Token`; es opcional y solo amplía el límite de solicitudes.

- **Estructura de los archivos de origen.** Respuesta en CSV con codificación UTF-8, una fila de encabezados y 51 columnas con nombres en minúscula. Todas las columnas están declaradas como texto en el portal, incluidos los puntajes. Los valores faltantes llegan como cadenas vacías. La descripción de cada columna está en el [diccionario de datos](data_dictionary.md).

- **Procedimientos de transformación y limpieza.** La carga se limita a lo necesario para que los datos sean fieles a la fuente y utilizables:

  1. *Lectura sin interpretación.* Todas las columnas se leen como texto y solo la cadena vacía se toma como faltante. Así se conservan los ceros a la izquierda de los códigos (por ejemplo, el departamento `05`).
  2. *Verificación de integridad.* Se comprueba que las filas recibidas coincidan con el conteo de la API y que estén las 51 columnas esperadas; si no, la carga se detiene con un error.
  3. *Eliminación de duplicados exactos.* Se quitan las filas idénticas en las 51 columnas (53.443 en el recorte). Si quedaran filas con el mismo `estu_consecutivo` pero contenido distinto, no se eliminan: se registra una advertencia para revisarlas.
  4. *Asignación de tipos.* Los seis puntajes pasan a numéricos (`float64`) y `estu_fechanacimiento` a fecha. Las fechas imposibles de representar o anteriores a 1900 quedan como faltantes.

  La imputación de faltantes, la recodificación de categorías, la validación de edades y la construcción de la variable objetivo corresponden a la fase de preprocesamiento.

### Base de datos de destino

- **Base de datos de destino.** El proyecto no usa un motor de base de datos: con 53.407 filas, un archivo plano es suficiente y más fácil de reproducir. El destino es la carpeta `data/raw/` del repositorio, que está excluida de Git (`.gitignore`) para no versionar datos en el control de código.

- **Estructura del destino.**

  | Archivo | Contenido |
  | --- | --- |
  | `data/raw/saber11_<periodo>_d<dígitos>.csv` | Datos crudos tal como los entrega la API: CSV en UTF-8, 51 columnas de texto. Para el recorte del proyecto, `saber11_20224_d7.csv` (45,5 MB) |
  | `data/raw/saber11_<periodo>_d<dígitos>.meta.json` | Metadatos de la descarga: fuente, licencia, consulta, fecha y hora (UTC), número de filas y columnas y huella SHA-256 del CSV |

  Si se descarga el periodo completo, el sufijo es `_completo` en lugar de `_d<dígitos>`.

  Al cargar el archivo se obtiene una tabla con una fila por examinado y llave `estu_consecutivo`: 44 columnas de texto, 6 numéricas y 1 de fecha.

- **Procedimientos de carga y transformación en el destino.** El archivo crudo se guarda sin modificar, de modo que siempre se pueda volver a lo que entregó la fuente. La eliminación de duplicados y la asignación de tipos se aplican al leerlo con `cargar_saber11`, no sobre el archivo. `obtener_saber11` reutiliza el archivo local si existe y solo consulta la API cuando falta o cuando se pide forzar la descarga.

- **Reproducibilidad.** Dos descargas independientes del recorte produjeron archivos idénticos, con huella SHA-256 `2581985d3ca86af07a7e0f02bc2fbdd1bbe86c16f79960084685b350e781a588`. Comparar esa huella con la del archivo `.meta.json` permite confirmar que se trabaja con los mismos datos. A partir de la siguiente fase los datos se versionarán con DVC.
