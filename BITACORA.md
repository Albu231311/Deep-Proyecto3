# Bitácora — Proyecto 3: Text-to-SQL con LoRA

**Curso:** Deep Learning 2026 — Universidad del Valle de Guatemala  
**Integrantes:**  
- **Carlos Alburez:** Albu231311 (Área: Datos + Validación y Errores)  
- **Erick Guerra:** Erick (Área: Entrenamiento e Inferencia)  

---

## Entrada 1 — Carlos Alburez — Miércoles 14 de octubre de 2026

**Tareas realizadas:**
- Configuración del entorno de contenedor con Docker para MySQL 8.4.10 (`docker-compose.yml`).
- Definición del usuario administrador (`root`) y del usuario no privilegiado de solo lectura (`evaluador`) conforme al contrato de evaluación del docente.
- Implementación de `src/mysql_utils.py`:
  - Manejo robusto de conexiones (`get_connection`, `get_readonly_connection`).
  - Funciones auxiliares `cargar_esquema(schema_file, db_name)` y `obtener_esquema(db_name)`.
  - Función de ejecución segura `ejecutar(sql, database)` con cursor buffered para evitar excepciones por resultados no leídos en MySQL Connector C-Extension.
  - Generador `hacer_ejecutar(database)`.
- Pruebas unitarias de conexión y verificación de permisos en `tests/test_mysql_utils.py` (100% aprobadas).
- Estructuración inicial de `BITACORA.md` y `CONTRIBUCIONES.md`.

**Decisiones tomadas:**
- Se restringen estrictamente los privilegios del usuario `evaluador` únicamente a `SELECT` para simular con precisión el entorno del evaluador oculto.
- Se selecciona `mysql-connector-python` con manejo buffered para máxima compatibilidad multiplataforma (Apple Silicon y Colab T4).

---

## Entrada 2 — Carlos Alburez — Jueves 15 de octubre de 2026

**Tareas realizadas:**
- Adquisición del dataset Spider y versión traducida al español (`MultiSpider`).
- Implementación del pipeline de extracción de bases SQLite contenidas en `spider_data.zip`.
- Conversión y transpilación automática de dialecto SQL (SQLite a MySQL 8.4) utilizando `sqlglot`.
- Normalización de nombres de tablas a minúsculas en DDL para solventar discrepancias de case-sensitivity del sistema de archivos Linux en Docker.
- Carga automatizada de bases en MySQL otorgando permisos de lectura al usuario evaluador.

**Decisiones tomadas:**
- Mantener las consultas originales en SQLite como referencia y almacenar la versión transpilada para validación directa en el motor.

---

## Entrada 3 — Carlos Alburez — Viernes 16 de octubre de 2026

**Tareas realizadas:**
- Diseño e implementación completa de los 2 esquemas independientes de validación propia:
  - `sistema_academico.sql`: 5 tablas (departamentos, profesores, estudiantes, cursos, inscripciones), comentarios DDL detallados y datos semilla.
  - `clinica_salud.sql`: 6 tablas (departamentos médicos, médicos, pacientes, citas, medicamentos, recetas), comentarios DDL y datos de prueba.
- Redacción de las **40 preguntas propias de validación** en `datos/validacion/val.jsonl`:
  - 15 Fáciles (peso 1)
  - 15 Medias (peso 2)
  - 10 Difíciles (peso 3: CTEs `WITH`, funciones de ventana `DENSE_RANK`, subconsultas correlacionadas, `TIMESTAMPDIFF`).
- Creación de `tests/test_validation_set.py`: verificación de ejecución al 100% de las 40 consultas en MySQL 8.4.10 Docker sin ningún fallo.
- Implementación de `src/evaluador.py`:
  - Comparación multiconjunto y con orden requerido.
  - Tolerancia de redondeo numérico a 2 decimales y columnas adicionales.
  - Ponderación de Exactitud por Ejecución (EX) y clasificación de fallos en 6 categorías canónicas.

---

## Entrada 4 — Carlos Alburez — Sábado 17 de octubre de 2026

**Tareas realizadas:**
- Ejecución completa del pipeline de generación y filtrado por ejecución en `src/preparar_datos.py`.
- Generación de `datos/entrenamiento/train.jsonl` con **2,429 pares válidos** (superando la meta de ≥2,000 pares). Cada par incluye esquema `SHOW CREATE TABLE`, pregunta en español, SQL validado en MySQL 8.4 y nivel de dificultad.
- Clasificación de 4,672 pares descartados en `datos/descartes/descartes.jsonl`.
- Redacción del reporte exhaustivo `datos/descartes/resumen_descartes.md`, detallando el impacto del modo estricto `ONLY_FULL_GROUP_BY` (causante principal de descartes) y funciones de fecha no equivalentes.
- Implementación y ejecución de `src/chequeo_fuga.py`:
  - Verificación formal de solapamiento de esquemas.
  - Resultado: **0% de fuga detectada**. Los esquemas de validación son completamente ajenos a los 272 esquemas únicos de entrenamiento.

---

## Entrada 5 — Carlos Alburez — Domingo 18 de octubre de 2026

**Tareas realizadas:**
- Elaboración y documentación del notebook interactivo `notebooks/01_datos.ipynb`.
- Inclusión de celdas explicativas paso a paso: descarga, transpilación con `sqlglot`, filtrado por ejecución en Docker, distribución por dificultad y chequeo de fuga programático.
- Validación de reproducibilidad local de las celdas del notebook.

---

## Entrada 6 — Carlos Alburez — Lunes 19 de octubre de 2026

**Tareas realizadas:**
- Creación de la estructura base del notebook `notebooks/03_evaluacion.ipynb`.
- Integración de la evaluación con simulación de baseline perfecto sobre `val.jsonl` obteniendo EX ponderado = 1.0 (100%).
- Redacción completa del `README.md` del repositorio: guía de despliegue en Docker, reproducibilidad del pipeline de datos, licencias (Spider CC BY-SA 4.0, Qwen Apache 2.0) y declaración ética de uso de IA.
- Actualización de `CONTRIBUCIONES.md` reflejando todas las entregas de Carlos Alburez completadas y listas para la fase de entrenamiento de Erick Guerra.

---

## Entrada 7 — Erick Guerra — Sábado 24 de octubre de 2026

**Tareas realizadas:**
- Creación de `config.json` con la forma exigida (`Qwen/Qwen2.5-Coder-1.5B-Instruct`, `adapter/`, `usar_adapter`, semilla 2026).
- Implementación de `src/prompt.py`: prompt único (system + esquema + pregunta) usado igual en entrenamiento, inferencia con adapter y baseline. `limpiar_esquema()` quita `ENGINE`, `CHARSET`, `COLLATE` y `AUTO_INCREMENT` de la salida de `SHOW CREATE TABLE` (~25 % menos caracteres) sin perder columnas, llaves ni `COMMENT`.
- Implementación de `src/filtro.py`: `es_solo_lectura()` (solo un `SELECT` o `WITH ... SELECT`, sin palabras de modificación fuera de strings/comentarios, sin múltiples sentencias ni `/*! */`) y `limpiar_salida()` (quita markdown, explicaciones y `;` final). `tests/test_filtro.py` con 40 casos aprobados; además, el filtro acepta las 2,469 consultas de referencia de entrenamiento y validación (0 falsos rechazos).
- Implementación de `solucion.py` con `generar_sql(esquema, pregunta, ejecutar=None)`: carga al importar, `float16` en GPU, generación greedy (`do_sample=False`), adapter LoRA fusionado con `merge_and_unload()`, autocorrección con `ejecutar` (máx. 3 llamadas, corte de seguridad a los 20 s) y respaldo `SELECT 1` si la salida no es de solo lectura.
- Creación de `notebooks/02_entrenamiento.ipynb` (enmascarado del prompt en la loss, curvas y métricas en `resultados/curvas_loss/`).

**Hipótesis (escritas antes de entrenar). Factor que varía: rango `r` (8 vs 32, `alpha = 2r`):**
- **H1:** `r = 32` (4× parámetros entrenables) bajará más rápido la loss de entrenamiento.
- **H2:** con ~2.4k pares y esquemas de evaluación distintos, la diferencia de EX en la validación propia será pequeña (≤ 5 puntos); si la loss de validación de `r = 32` se estanca o sube, `r = 8` generalizará igual o mejor.
- **H3:** si `r = 32` gana, la ganancia estará en preguntas difíciles (subconsultas, `WITH`, ventanas).
- **H4:** el tiempo de entrenamiento de `r = 32` será solo ≈ 10–20 % mayor.

**Decisiones tomadas:**
- La loss se calcula solo sobre la consulta SQL (+ `<|im_end|>`), con los tokens del prompt enmascarados (`-100`).
- Para graficar la loss de validación se retiene ~5 % de las bases de entrenamiento (partición por `db_id`); la validación propia de 40 preguntas solo se usa para medir EX.

---

## Entrada 8 — Erick Guerra — Sábado 24 de octubre de 2026

**Tareas realizadas:**
- Primer entrenamiento de `r = 8` en Colab T4 (desde la extensión de VS Code). Se resolvieron tres problemas de entorno:
  - `peft 0.21` lanza `ImportError` con el `torchao 0.10` preinstalado en Colab, aunque no se use cuantización. Se creó `src/compat.py` (`parchear_torchao()`), que también protege a `solucion.py` en el Colab del docente.
  - `transformers 5.x` eliminó `warmup_ratio` y renombró `group_by_length` → `train_sampling_strategy`; el notebook detecta la versión.
  - `CUDA out of memory`: con batch 4 los logits (4 × 2048 tokens × 151,936 de vocabulario, fp32) ocupaban ~4.6 GB. Se pasó a batch 2 × 8 de acumulación (**batch efectivo 16 sin cambios**).
- La corrida de `r = 8` terminó (67.7 min) pero **se perdió**: se agotaron las unidades de cómputo de Colab antes de guardar el adapter. Quedó registrada la curva: loss de validación mínima en el paso 100 (0.111) y luego subiendo hasta 0.142, con la de entrenamiento bajando a 0.045 → sobreajuste en la segunda época.
- Se migró el entrenamiento a **Kaggle (T4)** con "Save & Run All" (corre en segundo plano). El notebook 02 entrena `r = 8` y `r = 32` en una sola corrida y **sube a GitHub cada adapter apenas termina**, para no volver a perder trabajo.
- Adapters guardados en `float16`: `r = 32` en `float32` pesaría ~148 MB (> 100 MB permitidos); en `float16` pesa 73.9 MB.

**Decisiones tomadas:**
- Mismo hardware (una sola T4, también en Kaggle que ofrece dos) para que los tiempos de ambas configuraciones sean comparables.

---

## Entrada 9 — Erick Guerra — Sábado 24 de octubre de 2026

**Tareas realizadas:**
- Entorno local de evaluación con la RTX 4060 (PyTorch CUDA en `.venv`) y MySQL 8.4.10 en Docker. `solucion.py` probado con el modelo real: carga en 7–13 s (límite 300 s) y 2–6 s por pregunta (límite 30 s). **Determinismo verificado**: dos generaciones de las mismas preguntas son idénticas.
- **Corrección del evaluador:** `ejecutar()` devuelve máximo 10 filas (contrato del docente) y el evaluador comparaba solo esas 10. 9 de las 40 preguntas devuelven más de 10 filas, y sin `ORDER BY` dos consultas equivalentes pueden devolver subconjuntos distintos. Se agregó `max_filas` a `ejecutar()` y el evaluador ahora compara el resultado completo.
- Baseline (modelo sin adapter): **EX = 0.387**. El análisis de errores mostró que **18 de los 23 errores** eran consultas razonables que no devolvían las columnas esperadas (p. ej. "¿Qué profesores tienen grado de Doctorado?" esperaba `nombre, email`), porque **nuestras preguntas no indicaban qué columnas devolver**, a diferencia de la evaluación oculta ("cada pregunta indica qué columnas devolver").
- Se reescribió el texto de las 40 preguntas para que indiquen las columnas ("Devuelve las columnas: nombre, email."), **sin modificar las consultas de referencia ni las columnas esperadas**. En `val_33` y `val_36` además se aclaró en el texto un filtro que la referencia ya aplicaba (solo citas Completadas). Baseline con las preguntas corregidas: **EX = 0.747** (fácil 1.00, media 0.87, difícil 0.50).

**Decisiones tomadas:**
- Se reportan ambos valores del baseline (0.387 con las preguntas originales y 0.747 con las corregidas) para dejar transparente el cambio, hecho después de ver el primer resultado.

---

## Entrada 10 — Erick Guerra — Sábado 24 de octubre de 2026

**Resultados del experimento LoRA (dataset v1, Kaggle T4):**

| Config | Parámetros entrenables | Tiempo | Loss train final | Loss val (mín / final) | EX validación propia |
|---|---|---|---|---|---|
| Baseline (sin adapter) | — | — | — | — | **0.747** |
| r = 8, alpha = 16 | 9,232,384 (0.59 %) | 58.3 min | 0.045 | 0.111 / 0.143 | 0.467 |
| r = 32, alpha = 64 | 36,929,536 (2.34 %) | 58.8 min | 0.027 | 0.123 / 0.153 | 0.467 |

**Contraste con las hipótesis (Entrada 7):**
- **H1 confirmada:** `r = 32` llega a una loss de entrenamiento más baja (0.027 vs 0.045).
- **H2 confirmada:** el EX es idéntico (0.467); `r = 32` sobreajusta más (loss de validación final 0.153 vs 0.143). En ambas la loss de validación toca su mínimo en el paso 100 (~0.7 épocas) y sube después.
- **H3 no aplica:** `r = 32` no gana en ningún nivel.
- **H4 refutada (a favor):** `r = 32` tarda solo +1 % (58.8 vs 58.3 min), menos que el 10–20 % previsto.

**Experimento de inferencia (autocorrección con `ejecutar`, sobre r = 8):** no cambió el EX (0.467). En las 6 preguntas cuya consulta fallaba se usaron las 3 llamadas, pero el modelo repitió la misma consulta en cada intento.

**Análisis:** ambos adapters quedan **0.28 por debajo del baseline**. 10–11 de sus 16 errores son de columnas: aprendieron el estilo de Spider (alias `T1`/`T2`, expresiones sin nombre como `AVG(x)`) e **ignoran la indicación de columnas**, que nunca aparece en las preguntas de Spider. Con el dataset v1 el rango no importa: el cuello de botella son los datos, no la capacidad del adapter.

**Decisión: dataset v2** (`src/aumentar_columnas.py` → `datos/entrenamiento/train_v2.jsonl`, sin modificar `train.jsonl`):
- A cada pregunta se le agrega qué columnas devolver, con 5 redacciones distintas para no depender de una sola frase.
- A las expresiones sin nombre del SELECT exterior se les pone alias (`COUNT(*) AS cantidad`, `AVG(hours) AS promedio_hours`) y las columnas repetidas se renombran con su tabla. 761 de 2,429 consultas cambiaron; **cada una se volvió a ejecutar en MySQL 8.4.10** sobre bases creadas con su `SHOW CREATE TABLE`, y los nombres de columna se tomaron de lo que devuelve MySQL.
- Se reentrenan `r = 8` y `r = 32` con v2 (notebook 02b, mismos hiperparámetros) guardando también el adapter de la época 1, para decidir con EX si conviene 1 o 2 épocas.

---

## Entrada 11 — Erick Guerra — Sábado 24 de octubre de 2026

**Resultados del dataset v2 (notebook 02b, Kaggle T4, 2,357 ejemplos de entrenamiento y 70 de loss de validación):**

| Config | Tiempo | Loss train final | Loss val (mín / final) | EX época 1 | EX época 2 |
|---|---|---|---|---|---|
| Baseline (sin adapter) | — | — | — | — | **0.747** |
| r = 8, alpha = 16 | 59.7 min | 0.037 | 0.100 / 0.108 | 0.480 | 0.520 |
| r = 32, alpha = 64 | 60.3 min | 0.024 | 0.107 / 0.110 | 0.467 | 0.520 |

- La indicación de columnas ayudó (+5 puntos frente a v1, medias 0.47 → 0.60), pero ambos adapters siguen **0.23 por debajo del baseline**. La segunda época mejora el EX aunque la loss de validación suba un poco.
- Autocorrección con `ejecutar` sobre r8_v2: EX igual (0.520), 0 preguntas arregladas y 0 empeoradas; 34 preguntas usaron 1 llamada, 1 usó 2 y 5 usaron 3 (tiempo máximo 10.3 s, dentro del límite de 30 s).

**Diagnóstico pregunta por pregunta (r8_v2 frente al baseline):** el adapter **rompe 8 preguntas que el modelo base acertaba y arregla solo 1** (val_37):
- Alias `T1`/`T2`/`T3` de Spider que confunden las tablas: val_14, val_16, val_29 y val_38.
- Sin funciones de fecha (Spider no las tiene): calcula `2026 - fecha_nac` en vez de `TIMESTAMPDIFF` en val_20 y val_40.
- JOIN y GROUP BY más pobres: val_12 y val_34.

Conclusión: el fine-tuning le está quitando al modelo cosas que ya sabía, porque Spider tiene un estilo (alias opacos, SQL simple, sin fechas) muy distinto de la evaluación (MySQL, fechas, `WITH`, ventanas, nombres en español/inglés/abreviados).

**Decisión: dataset v3** (`src/generar_v3.py` → `datos/entrenamiento/train_v3.jsonl`, 3,349 ejemplos):
- **Alias legibles en Spider:** `T1`/`T2` se reemplazan por abreviaturas del nombre de la tabla (`student_course` → `sc`). 784 consultas reescritas y re-ejecutadas en MySQL 8.4.10; ninguna falló.
- **12 esquemas propios** (`datos/esquemas_propios/*.sql`, 6–7 tablas con `COMMENT`) con nombres en español (tienda_online, biblioteca, restaurante, banco, gimnasio, inmobiliaria, eventos), inglés (aerolinea, hotel) y abreviados (rrhh, logistica, taller), y **460 pares** (114 fáciles, 141 medios, 205 difíciles) generados con ayuda de un LLM y revisados: fechas (`TIMESTAMPDIFF`, `DATEDIFF`, `DATE_FORMAT`, `YEAR`/`MONTH`), `WITH`, ventanas (`RANK`, `ROW_NUMBER`, `LAG`, acumulados) y subconsultas correlacionadas.
- **Validación por ejecución:** cada esquema se cargó en MySQL 8.4.10 como `propio_<nombre>` y se pobló con datos sintéticos (respetando enums, llaves foráneas, fechas 2022–2026 y NULL en columnas opcionales). Los 460 pares ejecutaron: **0 descartes** (9 devuelven vacío por los datos aleatorios, pero son SQL válido).
- Cada par propio entra 2 veces con distinta redacción de la indicación de columnas (920 ejemplos) para darle peso frente a los 2,429 de Spider.
- `src/chequeo_fuga.py` sobre v3: ningún esquema ni tabla de validación aparece en el entrenamiento.
- Se reentrenan r = 8 y r = 32 con v3 (notebook 02c), mismos hiperparámetros. **H5** (escrita antes de entrenar, en el notebook 02c): con v3 el adapter deja de romper lo que el base acierta e iguala o supera el baseline (0.747).

---

## Entrada 12 — Erick Guerra — Domingo 25 de octubre de 2026

**Resultados del dataset v3 (notebook 02c, Kaggle T4, 3,191 ejemplos de entrenamiento y 158 de loss de validación):**

| Config | Tiempo | Loss train final | Loss val (mín / final) | EX época 1 | EX época 2 |
|---|---|---|---|---|---|
| Baseline (sin adapter) | — | — | — | — | 0.747 |
| r = 8, alpha = 16 | 95.3 min | 0.026 | 0.113 / 0.115 | 0.707 | **0.800** |
| r = 32, alpha = 64 | 96.1 min | 0.017 | 0.101 / 0.101 | 0.720 | **0.800** |

- **H5 confirmada:** ambos adapters v3 superan al baseline (0.800 vs 0.747, +0.053). Por nivel: fácil 1.00, media 0.80, difícil 0.70 (baseline: 1.00 / 0.87 / 0.50). Es la primera vez que el LoRA supera al modelo base.
- Frente al baseline, r8_v3 gana 3 difíciles (val_19, val_37, val_39: fechas, `WITH` y ventanas) y pierde 2 (val_34 media y val_38 difícil). Los alias `T1`/`T2` desaparecieron de las predicciones.
- **H1–H4 con los tres datasets:** H1 confirmada (r = 32 siempre baja más la loss de entrenamiento); H2 confirmada (r = 8 y r = 32 empatan en EX en v1, v2 y v3); H3 no aplica (r = 32 nunca gana); H4 refutada a favor (r = 32 tarda solo +1 %).
- La época 2 vuelve a ser igual o mejor en EX que la época 1, aunque la loss de validación casi no cambie.
- Autocorrección con `ejecutar` sobre r8_v3: EX igual (0.800); 37 preguntas con 1 llamada y 3 con 3 llamadas, 0 arregladas. Tiempo máximo 20.2 s (bajo el límite de 30 s gracias al corte a los 20 s).

**Decisión: adapter final = r8_v3** (copiado a `adapter/`, `usar_adapter: true`). Empata con r32_v3 en EX y, según la regla de desempate del notebook 03, se elige el adapter más pequeño (18.5 MB frente a 73.9 MB). r32_v3 tiene menos consultas que no ejecutan (1 frente a 3), pero sus errores pasan a ser de JOIN y no cambia el EX.

**Prueba de la entrega:** `solucion.py` cargado tal como lo hará el docente (`config.json` + `adapter/`) dio EX 0.800 en las 40 preguntas, con salida idéntica en dos corridas (determinista).

**Predicción para la evaluación oculta** (diapositiva 12): EX ≈ 0.70 con adapter y mejora ≈ +0.04. Es menor que en la validación propia porque elegimos el dataset mirando esa validación (sesgo optimista), porque el IC 95 % pareado de la mejora en 40 preguntas es amplio [−0.11, +0.22] y porque los esquemas ocultos son más grandes y tienen nombres abreviados o en inglés.
