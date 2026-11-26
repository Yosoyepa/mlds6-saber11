# Diccionario de datos

## Base de datos 1: Resultados únicos Saber 11 (ICFES), periodo 2022-4

Resultados individuales del examen de Estado Saber 11, que presentan los estudiantes al terminar la educación media en Colombia. Cada fila es un examinado y reúne cuatro tipos de información: datos del estudiante, respuestas del cuestionario socioeconómico sobre su hogar, características del colegio y puntajes obtenidos.

| | |
| --- | --- |
| **Fuente** | Recurso `kgxf-xxbe` del portal de Datos Abiertos de Colombia: <https://www.datos.gov.co/d/kgxf-xxbe> |
| **Publicador** | Instituto Colombiano para la Evaluación de la Educación (ICFES) |
| **Licencia** | Creative Commons Attribution-ShareAlike 4.0 |
| **Recorte del proyecto** | Periodo 2022-4, muestra sistemática de 1 de cada 10 examinados (`estu_consecutivo` terminado en 7) |
| **Tamaño** | 53.407 filas (una por examinado) y 51 columnas |
| **Llave** | `estu_consecutivo` |
| **Archivo local** | `data/raw/saber11_20224_d7.csv` |

Cómo leer las tablas:

- **Tipo de dato** es el tipo con que queda la variable después de la carga (`cargar_saber11`). Los códigos se conservan como texto porque son identificadores y pueden empezar por cero.
- **Rango/Valores posibles** describe lo observado en la muestra del proyecto. Cuando la variable tiene valores faltantes se indica su porcentaje; si no se menciona, está completa.
- **Fuente de datos** indica quién origina el dato dentro del proceso del ICFES. Todas las variables llegan por el mismo recurso de datos.gov.co.

### 1.1 Identificación y control (4 variables)

Identifican el registro y la aplicación. No se usan como predictoras.

| Variable | Descripción | Tipo de dato | Rango/Valores posibles | Fuente de datos |
| --- | --- | --- | --- | --- |
| periodo | Periodo de aplicación del examen: año seguido del número de aplicación | Texto (código) | `20224` en todo el recorte. En el recurso completo va de `20101` a `20224` | ICFES, registro de la aplicación |
| estu_consecutivo | Identificador anónimo del examinado. Es la llave de la tabla | Texto (identificador) | 16 caracteres: prefijo `SB11`, periodo y número secuencial. Ejemplo: `SB11202240478157`. 53.407 valores únicos | ICFES, registro de la aplicación |
| estu_estadoinvestigacion | Estado de validez del resultado para su publicación | Texto (categórica) | `PUBLICAR` (99,9 %), `VALIDEZ OFICINA JURÍDICA` (27 casos). En otros periodos aparecen más estados | ICFES, registro de la aplicación |
| estu_estudiante | Indica si el examinado se inscribió como estudiante de un colegio | Texto (categórica) | `ESTUDIANTE` en todas las filas: el recurso no incluye examinados individuales | ICFES, registro de la aplicación |

### 1.2 Estudiante (14 variables)

Datos personales y de ubicación del examinado. El estudiante los suministra al inscribirse, antes del examen, por lo que son candidatos a predictoras.

| Variable | Descripción | Tipo de dato | Rango/Valores posibles | Fuente de datos |
| --- | --- | --- | --- | --- |
| estu_tipodocumento | Tipo de documento de identidad | Texto (categórica) | 10 valores. `TI` tarjeta de identidad (84 %), `CC` cédula de ciudadanía (14 %), `CR` contraseña de la Registraduría, `NES` número establecido por la secretaría de educación, `CE` cédula de extranjería, `PEP` permiso especial de permanencia, `PPT` permiso por protección temporal; poco frecuentes: `PE`, `NUIP`, `PET` | Formulario de inscripción |
| estu_genero | Sexo del examinado | Texto (categórica) | `F` (54,3 %), `M` (45,7 %) | Formulario de inscripción |
| estu_fechanacimiento | Fecha de nacimiento | Fecha (datetime64) | De 1900-01-01 a 2022-05-16; el 63 % de los examinados nació en 2004 o 2005. En la fuente viene como texto `dd/mm/aaaa`. Hay fechas inverosímiles en ambos extremos. Faltantes: 0,01 % (7 filas) | Formulario de inscripción |
| estu_nacionalidad | País de nacionalidad | Texto (categórica) | 15 países. `COLOMBIA` (98,7 %), `VENEZUELA` (1,2 %), otros (0,1 %) | Formulario de inscripción |
| estu_pais_reside | País de residencia | Texto (categórica) | 15 países. En el recorte coincide con `estu_nacionalidad` en todas las filas | Formulario de inscripción |
| estu_privado_libertad | Indica si el examinado está privado de la libertad | Texto (categórica) | `N` (99,9 %), `S` (35 casos) | Formulario de inscripción |
| estu_cod_reside_depto | Código DIVIPOLA del departamento de residencia | Texto (código) | 2 dígitos, 33 valores (32 departamentos y Bogotá D.C.), de `05` a `99` | Formulario de inscripción |
| estu_depto_reside | Nombre del departamento de residencia | Texto (categórica) | 33 valores en mayúscula, por ejemplo `BOGOTÁ`, `ANTIOQUIA`, `VALLE`, `NARIÑO` | Formulario de inscripción |
| estu_cod_reside_mcpio | Código DIVIPOLA del municipio de residencia | Texto (código) | 5 dígitos (departamento y municipio), 1.105 valores, de `05001` a `99773` | Formulario de inscripción |
| estu_mcpio_reside | Nombre del municipio de residencia | Texto (categórica) | 1.025 nombres. Un mismo nombre se repite en varios departamentos; para identificar el municipio se usa el código | Formulario de inscripción |
| estu_cod_depto_presentacion | Código DIVIPOLA del departamento donde presentó el examen | Texto (código) | 2 dígitos, 33 valores | ICFES, citación al examen |
| estu_depto_presentacion | Nombre del departamento donde presentó el examen | Texto (categórica) | 33 valores en mayúscula | ICFES, citación al examen |
| estu_cod_mcpio_presentacion | Código DIVIPOLA del municipio donde presentó el examen | Texto (código) | 5 dígitos, 517 valores (el examen se aplica en menos municipios de los que tienen colegios) | ICFES, citación al examen |
| estu_mcpio_presentacion | Nombre del municipio donde presentó el examen | Texto (categórica) | 501 nombres | ICFES, citación al examen |

### 1.3 Hogar: cuestionario socioeconómico (9 variables)

Respuestas del estudiante sobre su hogar al momento de inscribirse. Son autorreportadas y concentran la mayor parte de los valores faltantes. Son las principales candidatas a predictoras.

| Variable | Descripción | Tipo de dato | Rango/Valores posibles | Fuente de datos |
| --- | --- | --- | --- | --- |
| fami_estratovivienda | Estrato socioeconómico de la vivienda según el recibo de servicios públicos | Texto (categórica ordinal) | `Estrato 1` a `Estrato 6` y `Sin Estrato`. Los estratos 1 a 3 suman 82 %. Faltantes: 6,71 % | Cuestionario socioeconómico (autorreporte) |
| fami_educacionmadre | Máximo nivel educativo alcanzado por la madre | Texto (categórica ordinal) | 12 valores: `Ninguno`, `Primaria incompleta`, `Primaria completa`, `Secundaria (Bachillerato) incompleta`, `Secundaria (Bachillerato) completa`, `Técnica o tecnológica incompleta`, `Técnica o tecnológica completa`, `Educación profesional incompleta`, `Educación profesional completa`, `Postgrado`, `No sabe`, `No Aplica`. Faltantes: 5,86 % | Cuestionario socioeconómico (autorreporte) |
| fami_educacionpadre | Máximo nivel educativo alcanzado por el padre | Texto (categórica ordinal) | Los mismos 12 valores de `fami_educacionmadre`. Faltantes: 5,81 % | Cuestionario socioeconómico (autorreporte) |
| fami_personashogar | Número de personas que viven en el hogar | Texto (categórica ordinal) | `1 a 2`, `3 a 4`, `5 a 6`, `7 a 8`, `9 o más`. Faltantes: 4,28 % | Cuestionario socioeconómico (autorreporte) |
| fami_cuartoshogar | Número de cuartos del hogar en los que duermen las personas | Texto (categórica ordinal) | `Uno`, `Dos`, `Tres`, `Cuatro`, `Cinco`, `Seis o mas`. Faltantes: 4,45 % | Cuestionario socioeconómico (autorreporte) |
| fami_tieneinternet | El hogar tiene servicio de internet | Texto (binaria) | `Si` (68,2 %), `No` (25,8 %). Faltantes: 5,95 % | Cuestionario socioeconómico (autorreporte) |
| fami_tienecomputador | El hogar tiene computador | Texto (binaria) | `Si` (51,1 %), `No` (44,5 %). Faltantes: 4,39 % | Cuestionario socioeconómico (autorreporte) |
| fami_tienelavadora | El hogar tiene lavadora | Texto (binaria) | `Si` (74,1 %), `No` (21,5 %). Faltantes: 4,38 % | Cuestionario socioeconómico (autorreporte) |
| fami_tieneautomovil | El hogar tiene automóvil | Texto (binaria) | `No` (71,1 %), `Si` (24,3 %). Faltantes: 4,58 % | Cuestionario socioeconómico (autorreporte) |

### 1.4 Colegio (17 variables)

Características del establecimiento educativo y de la sede donde estudia el examinado. Se conocen antes del examen. Las variables descriptivas son candidatas a predictoras; los códigos sirven para agrupar por colegio (partición de los datos y variables agregadas) y los nombres no se usan en el modelo.

| Variable | Descripción | Tipo de dato | Rango/Valores posibles | Fuente de datos |
| --- | --- | --- | --- | --- |
| cole_codigo_icfes | Código que el ICFES asigna al establecimiento. Un mismo establecimiento puede tener varios | Texto (código) | 6 dígitos, 11.474 valores | ICFES, directorio de establecimientos |
| cole_cod_dane_establecimiento | Código DANE del establecimiento educativo | Texto (código) | 12 dígitos, 9.159 valores | ICFES, directorio de establecimientos |
| cole_nombre_establecimiento | Nombre del establecimiento educativo | Texto libre | 8.343 nombres, de 4 a 100 caracteres | ICFES, directorio de establecimientos |
| cole_cod_dane_sede | Código DANE de la sede | Texto (código) | 12 dígitos, 9.726 valores | ICFES, directorio de establecimientos |
| cole_nombre_sede | Nombre de la sede | Texto libre | 9.159 nombres, de 4 a 100 caracteres | ICFES, directorio de establecimientos |
| cole_sede_principal | Indica si la sede es la principal del establecimiento | Texto (binaria) | `S` (94,6 %), `N` (5,4 %) | ICFES, directorio de establecimientos |
| cole_naturaleza | Sector del establecimiento | Texto (binaria) | `OFICIAL` (77,3 %), `NO OFICIAL` (22,7 %) | ICFES, directorio de establecimientos |
| cole_area_ubicacion | Zona donde está ubicada la sede | Texto (binaria) | `URBANO` (82,9 %), `RURAL` (17,1 %) | ICFES, directorio de establecimientos |
| cole_calendario | Calendario académico del establecimiento | Texto (categórica) | `A` (99,5 %), `B`, `OTRO` | ICFES, directorio de establecimientos |
| cole_caracter | Carácter o modalidad de la formación | Texto (categórica) | `ACADÉMICO`, `TÉCNICO`, `TÉCNICO/ACADÉMICO`, `NO APLICA`. Faltantes: 3,96 % | ICFES, directorio de establecimientos |
| cole_genero | Población que atiende el establecimiento según sexo | Texto (categórica) | `MIXTO` (97,1 %), `FEMENINO`, `MASCULINO` | ICFES, directorio de establecimientos |
| cole_jornada | Jornada de la sede | Texto (categórica) | `MAÑANA`, `UNICA`, `COMPLETA`, `TARDE`, `SABATINA`, `NOCHE` | ICFES, directorio de establecimientos |
| cole_bilingue | Indica si el establecimiento es bilingüe | Texto (binaria) | `N` (80,9 %), `S` (1,1 %). Faltantes: 18,10 %, el mayor de la tabla | ICFES, directorio de establecimientos |
| cole_cod_depto_ubicacion | Código DIVIPOLA del departamento de la sede | Texto (código) | 2 dígitos, 33 valores. Coincide con los dos primeros dígitos de `cole_cod_mcpio_ubicacion` | ICFES, directorio de establecimientos |
| cole_depto_ubicacion | Nombre del departamento de la sede | Texto (categórica) | 33 valores en mayúscula. Mayor participación: `BOGOTÁ` (14,7 %), `ANTIOQUIA` (13,5 %), `VALLE` (7,4 %) | ICFES, directorio de establecimientos |
| cole_cod_mcpio_ubicacion | Código DIVIPOLA del municipio de la sede | Texto (código) | 5 dígitos, 1.104 valores | ICFES, directorio de establecimientos |
| cole_mcpio_ubicacion | Nombre del municipio de la sede | Texto (categórica) | 1.023 nombres | ICFES, directorio de establecimientos |

### 1.5 Resultados del examen (7 variables)

Puntajes obtenidos. Solo se conocen después del examen: **no se usan como predictoras** porque sería fuga de información. De `punt_global` se deriva la variable objetivo.

| Variable | Descripción | Tipo de dato | Rango/Valores posibles | Fuente de datos |
| --- | --- | --- | --- | --- |
| punt_global | Puntaje global del examen. Es el promedio ponderado de las cinco pruebas, con peso 3 para matemáticas, lectura crítica, sociales y ciencias naturales y peso 1 para inglés, llevado a escala de 500 | Numérico (float64) | Escala de 0 a 500, valores enteros. Observado: 88 a 450; media 250,0; mediana 247; percentil 25 = 209; percentil 75 = 287,5 | ICFES, calificación del examen |
| punt_matematicas | Puntaje en la prueba de matemáticas | Numérico (float64) | Escala de 0 a 100, valores enteros. Observado: 15 a 100; media 50,6 | ICFES, calificación del examen |
| punt_lectura_critica | Puntaje en la prueba de lectura crítica | Numérico (float64) | Escala de 0 a 100, valores enteros. Observado: 0 a 100; media 52,8 | ICFES, calificación del examen |
| punt_sociales_ciudadanas | Puntaje en la prueba de sociales y ciudadanas | Numérico (float64) | Escala de 0 a 100, valores enteros. Observado: 0 a 100; media 47,7 | ICFES, calificación del examen |
| punt_c_naturales | Puntaje en la prueba de ciencias naturales | Numérico (float64) | Escala de 0 a 100, valores enteros. Observado: 0 a 100; media 49,1 | ICFES, calificación del examen |
| punt_ingles | Puntaje en la prueba de inglés | Numérico (float64) | Escala de 0 a 100, valores enteros. Observado: 0 a 100; media 49,8. Faltantes: 0,34 % | ICFES, calificación del examen |
| desemp_ingles | Nivel de desempeño en inglés según el Marco Común Europeo de Referencia | Texto (categórica ordinal) | `A-` (puntaje de 0 a 47), `A1` (48 a 57), `A2` (58 a 67), `B1` (68 a 78), `B+` (79 a 100). Faltantes: 0,34 % | ICFES, calificación del examen |

- **Variable**: nombre de la variable.
- **Descripción**: breve descripción de la variable.
- **Tipo de dato**: tipo de dato que contiene la variable.
- **Rango/Valores posibles**: rango o valores que puede tomar la variable.
- **Fuente de datos**: fuente de los datos de la variable.

## Base de datos 2: variables derivadas

Variables que no vienen en la fuente y que el proyecto construye a partir de la base de datos 1. Se definen aquí para dejar fijada la variable objetivo; se calculan en la fase de preprocesamiento.

| Variable | Descripción | Tipo de dato | Rango/Valores posibles | Fuente de datos |
| --- | --- | --- | --- | --- |
| bajo_desempeno | **Variable objetivo.** Indica si el estudiante quedó en el cuartil inferior nacional del puntaje global | Entero (binaria) | `1` si `punt_global` ≤ 209 (percentil 25 del periodo 2022-4); `0` en caso contrario. Proporción esperada de la clase 1: 25,0 % | Derivada de `punt_global` |
| edad | Edad del estudiante en años cumplidos a la fecha del examen | Numérico | Se espera entre 14 y 25 años para la mayoría; las edades fuera de un rango verosímil se tratan como faltantes | Derivada de `estu_fechanacimiento` |

- **Variable**: nombre de la variable.
- **Descripción**: breve descripción de la variable.
- **Tipo de dato**: tipo de dato que contiene la variable.
- **Rango/Valores posibles**: rango o valores que puede tomar la variable.
- **Fuente de datos**: fuente de los datos de la variable.

## Uso previsto de las variables

| Rol | Variables |
| --- | --- |
| Objetivo | `bajo_desempeno`, derivada de `punt_global` |
| Predictoras candidatas | Las 9 variables del hogar (`fami_*`); del estudiante: `estu_genero`, `estu_tipodocumento`, `estu_privado_libertad`, `estu_nacionalidad`, la edad y el departamento y municipio de residencia; del colegio: `cole_naturaleza`, `cole_area_ubicacion`, `cole_calendario`, `cole_caracter`, `cole_genero`, `cole_jornada`, `cole_bilingue`, `cole_sede_principal` y la ubicación |
| Agrupación | `cole_cod_dane_establecimiento`, `cole_cod_dane_sede` y `cole_codigo_icfes`: para partir los datos por colegio y calcular variables agregadas |
| Excluidas por fuga de información | `punt_matematicas`, `punt_lectura_critica`, `punt_sociales_ciudadanas`, `punt_c_naturales`, `punt_ingles`, `desemp_ingles` |
| Excluidas por no aportar información | `periodo` y `estu_estudiante` (constantes), `estu_consecutivo` (llave), `estu_estadoinvestigacion`, `estu_pais_reside` (duplica a `estu_nacionalidad`), nombres de colegio y sede, y el lugar de presentación del examen |

Esta asignación es preliminar y se confirma en el análisis exploratorio.

## Observaciones de calidad detectadas en la carga

Hallazgos que se registran para tratarlos en las fases de exploración y preprocesamiento:

1. **Filas duplicadas en la fuente.** El recurso publica dos veces cada registro de los periodos 2019-4 y 2022-4. En el recorte llegan 106.850 filas para 53.407 examinados. Son copias exactas y la función de carga las elimina.
2. **Fechas de nacimiento inverosímiles.** Hay valores entre 1900 y 2022, que equivalen a edades de 0 a 122 años al presentar el examen.
3. **Categorías que equivalen a dato faltante.** `No sabe` y `No Aplica` en la educación de los padres, `Sin Estrato` en el estrato y `NO APLICA` en el carácter del colegio.
4. **Estratos altos con comportamiento atípico.** El puntaje promedio de los estratos 5 y 6 (260 y 244) es inferior al del estrato 4 (268), lo que sugiere errores de autorreporte.
5. **Variables redundantes.** `estu_pais_reside` es idéntica a `estu_nacionalidad`, y cada nombre de departamento o municipio tiene su código equivalente.
6. **Nombres de municipio repetidos.** Hay más códigos de municipio que nombres porque un mismo nombre existe en varios departamentos; la identificación debe hacerse por código.
7. **Faltantes concentrados.** `cole_bilingue` (18,1 %) y el cuestionario socioeconómico (4 % a 7 %) reúnen casi todos los valores faltantes.
