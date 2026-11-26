# Alerta temprana de bajo desempeño en la prueba Saber 11

Proyecto aplicado del módulo 6, *Metodologías Ágiles para el Desarrollo de Proyectos de Machine Learning*, del Programa de Formación en Machine Learning y Data Science (MLDS) de la Universidad Nacional de Colombia.

**Autor:** Juan Carlos Andrade Unigarro

## De qué trata

El puntaje del examen Saber 11 condiciona el acceso a la educación superior en Colombia y está muy asociado a condiciones que se conocen antes de la prueba: en los datos de 2022, el 40 % de los estudiantes de colegios rurales quedó en el cuartil inferior nacional, frente al 22 % de los urbanos.

El proyecto construye un modelo de clasificación que estima, con la información disponible al inscribirse al examen (cuestionario socioeconómico y características del colegio), la probabilidad de que un estudiante obtenga un puntaje global bajo, para que secretarías de educación y colegios prioricen sus programas de refuerzo.

- **Datos:** [Resultados únicos Saber 11](https://www.datos.gov.co/d/kgxf-xxbe), ICFES, portal de Datos Abiertos de Colombia (licencia CC BY-SA 4.0). Periodo 2022-4, muestra de 53.407 estudiantes y 51 variables.
- **Metodología:** CRISP-DM, organizado con la plantilla [TDSP](https://github.com/mindlab-unal/tdsp_template) del programa.

## Estado del proyecto

| Fase | Entregables | Estado |
| --- | --- | --- |
| 1. Entendimiento del negocio y carga de datos | [Marco de proyecto](docs/business_understanding/project_charter.md) · [Diccionario de datos](docs/data/data_dictionary.md) · [Definición de los datos](docs/data/data_definition.md) · [Código de carga](scripts/data_acquisition/) | Entregada |
| 2. Preprocesamiento y análisis exploratorio | `docs/data/data_summary.md`, `scripts/eda/`, `scripts/preprocessing/` | Pendiente |
| 3. Modelamiento y extracción de características | `docs/modeling/`, `scripts/training/` | Pendiente |
| 4. Despliegue | `docs/deployment/` | Pendiente |
| 5. Evaluación y entrega final | `docs/acceptance/`, `scripts/evaluation/` | Pendiente |

## Cómo reproducir la carga de datos

Requiere Python 3.9 o superior y conexión a internet. No se necesitan credenciales.

```bash
git clone https://github.com/Yosoyepa/mlds6-saber11.git
cd mlds6-saber11
pip install -e .
python scripts/data_acquisition/main.py
```

El script descarga el recorte de datos del proyecto desde datos.gov.co (cerca de un minuto), lo guarda en `data/raw/` y muestra un resumen: 53.407 filas y 51 columnas. El mismo proceso está documentado paso a paso, con sus salidas, en el notebook [`scripts/data_acquisition/carga_de_datos.ipynb`](scripts/data_acquisition/carga_de_datos.ipynb).

Para usar los datos desde Python:

```python
from saber11.database import obtener_saber11

datos = obtener_saber11()
```

## Estructura del repositorio

* `src`: código del proyecto en Python, como el paquete instalable `saber11`.
  * `src/saber11/database`: adquisición y carga de datos.
* `docs`: documentos definidos en la metodología, uno por fase.
* `scripts`: scripts y notebooks que se ejecutan en cada fase.
* `data`: datos descargados. No se versiona en Git; se regenera con el script de carga.
* `pyproject.toml`: definición del paquete y sus dependencias.

## Licencia de los datos

Los datos pertenecen al ICFES y se distribuyen bajo licencia [Creative Commons Attribution-ShareAlike 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Este repositorio no redistribuye los datos: contiene el código que los descarga de la fuente oficial.
