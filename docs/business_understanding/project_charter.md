# Project Charter - Entendimiento del Negocio

## Nombre del Proyecto

Alerta temprana de bajo desempeño en la prueba Saber 11 a partir de factores socioeconómicos e institucionales

## Objetivo del Proyecto

### Contexto y problema

El examen Saber 11, que aplica el ICFES a los estudiantes que terminan la educación media, es requisito para ingresar a la educación superior en Colombia y uno de los criterios con que se asignan cupos, becas y créditos educativos. Un puntaje bajo reduce de forma concreta las oportunidades de un joven al salir del colegio.

Ese resultado está fuertemente asociado a condiciones que se conocen **antes** del examen. En los datos de este proyecto (53.407 examinados del periodo 2022-4, puntaje global promedio de 250 sobre 500):

| Grupo | Puntaje global promedio | Estudiantes en el cuartil inferior nacional |
| --- | --- | --- |
| Colegio rural / urbano | 228 / 255 | 40,2 % / 21,9 % |
| Colegio oficial / no oficial | 243 / 272 | 27,6 % / 16,0 % |
| Hogar sin internet / con internet | 228 / 260 | 38,7 % / 18,5 % |
| Madre sin estudios / con posgrado | 211 / 306 | 55,8 % / 6,4 % |
| Jornada nocturna / jornada completa | 211 / 280 | 54,1 % / 11,6 % |

Las secretarías de educación y los colegios tienen recursos limitados para refuerzo académico (tutorías, cursos de preparación, acompañamiento) y hoy los asignan con criterios gruesos. Una regla simple como "priorizar a los estudiantes de estrato 1 o sin estrato" solo alcanza al 38 % de quienes terminan en el cuartil inferior, y apenas el 31 % de los priorizados pertenece realmente a ese grupo. Hace falta una forma más precisa de identificar a tiempo a quién apoyar.

### Objetivo general

Desarrollar y desplegar un modelo de *machine learning* que, con la información disponible al momento de la inscripción al examen (cuestionario socioeconómico del estudiante y características de su colegio), estime la probabilidad de que un estudiante obtenga un puntaje global en el cuartil inferior nacional, para que secretarías de educación y colegios prioricen sus programas de refuerzo antes de la prueba.

En términos de analítica, es un problema de **clasificación binaria supervisada**. La variable objetivo, `bajo_desempeno`, vale 1 cuando el puntaje global es igual o inferior al percentil 25 nacional del periodo (209 puntos en 2022-4) y 0 en caso contrario.

### Objetivos específicos

1. Construir un flujo reproducible de adquisición y carga de los resultados Saber 11 desde el portal de datos abiertos del Estado colombiano.
2. Caracterizar, mediante análisis exploratorio, la calidad de los datos y la relación de las variables socioeconómicas e institucionales con el desempeño.
3. Entrenar y comparar modelos de clasificación (una línea base interpretable frente a modelos de mayor capacidad) con un esquema de validación que evite la fuga de información.
4. Desplegar el mejor modelo como un servicio web que reciba las características de un estudiante y devuelva su probabilidad de bajo desempeño.
5. Evaluar el modelo en datos no vistos, incluyendo su comportamiento por subgrupos de población, y documentar resultados, limitaciones y recomendaciones de uso.

## Alcance del Proyecto

### Incluye:

- **Datos disponibles.** El conjunto *Resultados únicos Saber 11*, publicado por el ICFES en el portal de Datos Abiertos de Colombia ([datos.gov.co](https://www.datos.gov.co/d/kgxf-xxbe)) bajo licencia CC BY-SA 4.0. El recurso completo tiene 7,1 millones de registros (2010 a 2022) y 51 variables. El proyecto usa el periodo **2022-4**, el más reciente, con una muestra sistemática de 1 de cada 10 examinados: **53.407 estudiantes**. Las variables se agrupan en identificación y control (4), estudiante (14), hogar (9), colegio (17) y resultados (7). El detalle está en el [diccionario de datos](../data/data_dictionary.md) y en la [definición de los datos](../data/data_definition.md).
- **Resultados esperados.**
  - Código reproducible de carga, preprocesamiento, entrenamiento y evaluación, organizado según la plantilla TDSP.
  - Reporte de análisis exploratorio y de calidad de datos.
  - Un modelo de clasificación entrenado, comparado contra una línea base, con su reporte de métricas (ROC-AUC, PR-AUC, *recall*, precisión y F1) y de las variables que más pesan en la predicción.
  - Un servicio web (API) que expone el modelo.
  - Documentación de cada fase y un informe final con conclusiones y limitaciones.
- **Criterios de éxito.** Se miden sobre un conjunto de prueba que el modelo no ve durante el entrenamiento:

  | Criterio | Métrica | Meta |
  | --- | --- | --- |
  | Capacidad de discriminación | ROC-AUC | ≥ 0,75 |
  | Cobertura de los estudiantes en riesgo | *Recall* de la clase `bajo_desempeno` | ≥ 0,70 |
  | Eficiencia de la focalización | Precisión de la clase `bajo_desempeno` en el umbral elegido | ≥ 0,40 (1,6 veces la tasa base de 25 %) |
  | Valor frente a la práctica actual | Comparación con la regla "estrato 1 o sin estrato" (*recall* 0,38; precisión 0,31) y con la línea base | Supera a ambas en *recall* y precisión |
  | Equidad | Diferencia de *recall* entre subgrupos (sexo, zona, naturaleza del colegio) | Reportada; una brecha mayor de 0,10 obliga a revisar el umbral de decisión |
  | Reproducibilidad | Ejecución desde un clon limpio del repositorio | Cada etapa corre con un comando y sin credenciales |
  | Despliegue | Tiempo de respuesta del servicio por solicitud | Menor de 1 segundo |

  Estas metas son preliminares y se revisarán al cierre del análisis exploratorio.

### Excluye:

- **Explicaciones causales.** El modelo identifica asociaciones útiles para priorizar; no demuestra que una variable cause el bajo desempeño ni evalúa el efecto de ninguna intervención.
- **Variables de resultado como predictoras.** Los puntajes por prueba y el nivel de inglés se conocen después del examen; usarlos sería fuga de información.
- **Predicción del puntaje exacto** o del puntaje por área. La regresión sobre el puntaje global solo se considera como análisis complementario.
- **Otros periodos y otras pruebas.** No se usan los periodos 2010 a 2022-1 ni las pruebas Saber 3°, 5°, 9°, Saber Pro o Saber TyT. El recurso termina en 2022, así que no se valida el desempeño del modelo en cohortes posteriores.
- **Población fuera del recurso.** Los datos solo contienen examinados inscritos como estudiantes de un colegio; quedan por fuera quienes se presentan como individuales.
- **Operación real.** No se integra con sistemas de matrícula, no se pone en producción con usuarios reales y no se usa información personal distinta de los datos abiertos y anonimizados del ICFES.
- **Decisiones individuales de alto impacto.** El resultado es un insumo para priorizar apoyo; no se propone para admitir, clasificar, sancionar ni etiquetar estudiantes.

## Metodología

El proyecto sigue **CRISP-DM** (*Cross Industry Standard Process for Data Mining*) y se organiza con la plantilla **TDSP** del programa. Se prefiere CRISP-DM sobre KDD y SEMMA porque estos dos parten de los datos (selección o muestreo) y terminan en la evaluación, mientras que este proyecto necesita dos etapas que solo CRISP-DM hace explícitas: el entendimiento del negocio, que fija para quién y para qué sirve la predicción, y el despliegue, que entrega el modelo como servicio.

| Fase CRISP-DM | Actividades en este proyecto | Entregable en el repositorio |
| --- | --- | --- |
| Entendimiento del negocio | Definir el problema, los usuarios, la variable objetivo y los criterios de éxito | `docs/business_understanding/project_charter.md` |
| Entendimiento de los datos | Seleccionar la fuente, cargar los datos, describir cada variable y explorar su calidad y distribución | `scripts/data_acquisition/`, `docs/data/`, `scripts/eda/` |
| Preparación de los datos | Tratar faltantes y valores inválidos, construir la variable objetivo, codificar variables categóricas, derivar variables (edad, agregados por colegio) | `scripts/preprocessing/`, `src/saber11/preprocessing/` |
| Modelamiento | Línea base con regresión logística; modelos de ensamble de árboles; ajuste de hiperparámetros con validación cruzada y registro de experimentos | `scripts/training/`, `docs/modeling/` |
| Evaluación | Métricas en el conjunto de prueba, elección del umbral de decisión, análisis por subgrupos y contraste con los criterios de éxito | `scripts/evaluation/`, `docs/modeling/model_report.md` |
| Despliegue | Empaquetar el modelo y exponerlo como API | `docs/deployment/`, `docs/acceptance/` |

Decisiones de método que se adoptan desde ya:

- **Trabajo iterativo.** Cada semana es una iteración que termina con un entregable verificable y un *commit* en el repositorio. Los hallazgos de una fase pueden devolver el trabajo a la anterior, como prevé CRISP-DM.
- **Sin fuga de información.** Solo entran al modelo variables conocidas en la inscripción. La partición de los datos se hace por colegio, de modo que el conjunto de prueba contenga colegios que el modelo no vio; así la evaluación refleja el uso real en instituciones nuevas.
- **Reproducibilidad.** Los datos no se guardan en Git: se obtienen con un script parametrizado que registra la consulta y la huella del archivo descargado. El versionamiento de datos y modelos se hará con DVC y el registro de experimentos con MLflow.
- **Herramientas.** Python, pandas y scikit-learn; plotnine y matplotlib para visualización; Git y GitHub para control de versiones; FastAPI para el servicio web.

## Cronograma

| Etapa | Duración Estimada | Fechas |
|------|---------|-------|
| Entendimiento del negocio y carga de datos | 1 semana | del 23 al 29 de noviembre de 2026 |
| Preprocesamiento, análisis exploratorio | 1 semana | del 30 de noviembre al 6 de diciembre de 2026 |
| Modelamiento y extracción de características | 1 semana | del 7 al 13 de diciembre de 2026 |
| Despliegue | 1 semana | del 14 al 20 de diciembre de 2026 |
| Evaluación y entrega final | 1 semana | del 21 al 27 de diciembre de 2026 |

Las fechas siguen el ritmo de una entrega por semana del módulo y se ajustarán si el calendario del curso cambia.

## Equipo del Proyecto

El proyecto lo desarrolla una sola persona, que asume todos los roles:

- **Juan Carlos Andrade Unigarro** - Líder del proyecto
- **Juan Carlos Andrade Unigarro** - Ingeniero de datos (adquisición, carga y versionamiento de los datos)
- **Juan Carlos Andrade Unigarro** - Científico de datos (análisis exploratorio, modelamiento y evaluación)
- **Juan Carlos Andrade Unigarro** - Ingeniero de *machine learning* (empaquetado y despliegue del modelo)

## Presupuesto

Es un proyecto académico sin financiación externa. El único costo real es el tiempo de trabajo; se valora a una tarifa de referencia para dimensionar el esfuerzo, pero no implica desembolso.

| Categoría | Descripción | Costo estimado (COP) | Notas |
| --- | --- | --- | --- |
| Personal | 60 horas de trabajo (12 horas por semana durante 5 semanas) | $3.000.000 | Tarifa de referencia de $50.000 por hora. Costo de oportunidad, sin desembolso |
| Datos | Resultados Saber 11 en datos.gov.co | $0 | Datos abiertos con licencia CC BY-SA 4.0 |
| Cómputo | Computador personal y Google Colab (plan gratuito) | $0 | Los datos son tabulares (53.407 filas); no se requiere GPU |
| Software | Python, pandas, scikit-learn, DVC, MLflow, FastAPI, Git | $0 | Herramientas de código abierto |
| Repositorio y despliegue | GitHub y un servicio de alojamiento en su plan gratuito | $0 | Suficiente para un prototipo |
| Contingencia | 10 % del total | $300.000 | Horas adicionales por reprocesos |
| **Total estimado** | | **$3.300.000** | **Desembolso efectivo: $0** |

## Stakeholders

Al ser un ejercicio académico no existe un vínculo formal con las entidades que usarían la solución. Se identifican como usuarios y beneficiarios objetivo, y sus necesidades orientan el diseño.

| Stakeholder | Relación con el proyecto | Expectativas |
| --- | --- | --- |
| Secretarías de educación departamentales y municipales | Usuario objetivo. Deciden a qué colegios y estudiantes dirigir los programas de refuerzo | Una lista priorizada y confiable de estudiantes en riesgo, con criterios que se puedan explicar y defender |
| Rectores, coordinadores académicos y docentes de grado 11 | Usuario final de las alertas dentro del colegio | Saber a quién acompañar con tiempo suficiente antes del examen, mediante una herramienta sencilla de consultar |
| Estudiantes de grado 11 y sus familias | Beneficiarios | Recibir apoyo oportuno sin ser estigmatizados y con sus datos protegidos |
| ICFES | Proveedor de los datos | Uso de los datos conforme a la licencia, con la atribución debida y sin intentos de reidentificar personas |
| Equipo docente del programa MLDS, Universidad Nacional de Colombia | Evaluador y patrocinador académico | Entregas completas y a tiempo en cada fase, según la rúbrica del proyecto aplicado |
| Juan Carlos Andrade Unigarro | Responsable del proyecto | Aplicar el ciclo completo de un proyecto de *machine learning* y obtener un prototipo funcional |

## Riesgos y consideraciones éticas

| Riesgo | Efecto | Mitigación |
| --- | --- | --- |
| El modelo reproduce desigualdades y sirve para etiquetar estudiantes | Estigmatización de poblaciones vulnerables | Uso limitado a priorizar apoyo; reporte de métricas por subgrupo; documentación explícita de los usos no permitidos |
| Las variables del hogar son autorreportadas y tienen faltantes (4 % a 7 %) y respuestas "No sabe" | Ruido en las predicciones | Tratamiento explícito de faltantes en el preprocesamiento y análisis de su relación con el objetivo |
| La fuente publica filas duplicadas y fechas de nacimiento imposibles | Conteos inflados y variables derivadas erróneas | Eliminación de duplicados exactos en la carga y validación de rangos en el preprocesamiento |
| Los datos terminan en 2022 | El modelo puede perder vigencia en cohortes recientes | Se declara como limitación; el flujo de carga está parametrizado por periodo para reentrenar cuando haya datos nuevos |
| Cambios o caídas de la API de datos.gov.co | La carga deja de funcionar | Reintentos automáticos, verificación de esquema y de número de filas, y huella SHA-256 del archivo descargado |

## Aprobaciones

- **Aprobador:** Juan Carlos Andrade Unigarro - Líder del proyecto
- **Firma:** Juan Carlos Andrade Unigarro
- **Fecha de aprobación:** 26 de noviembre de 2026

La aprobación del equipo docente del programa MLDS se da con la evaluación de esta entrega.
