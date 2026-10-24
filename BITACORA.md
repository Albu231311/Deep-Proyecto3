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
