# Contribuciones — Proyecto 3: Text-to-SQL con LoRA

## Integrantes y Roles principales

| Integrante | Área principal | Responsabilidades clave |
|---|---|---|
| **Carlos Alburez** (`Albu231311`) | **Datos** + **Validación y errores** | Pipeline de datos, conversión SQLite->MySQL 8.4, reporte de descartes, validation set propio (40 preguntas), evaluador EX ponderado, chequeo de fuga, notebooks 01 y 03, README |
| **Erick Guerra** (`erickguerra2`) | **Entrenamiento** + **Inferencia** | `solucion.py`, filtro de solo lectura, `prompt.py`, baseline, entrenamiento LoRA (Config 1 vs Config 2) con datasets v1/v2/v3, esquemas propios, experimento de inferencia, notebooks 02/02b/02c y `correr_solucion`, extensión del 03, presentación |

---

## Tabla de contribuciones y evidencias

| Tarea | Responsable | Estado | Evidencia / Commit |
|---|---|---|---|
| `docker-compose.yml` y `src/mysql_utils.py` | Carlos Alburez | **Completado** | `feat(datos): MySQL 8.4.10 en Docker y utilidades de conexión` |
| `BITACORA.md` y `CONTRIBUCIONES.md` | Carlos Alburez | **Completado** | `docs: bitácora y tabla de contribuciones` |
| Descarga de Spider y carga en MySQL | Carlos Alburez | **Completado** | `feat(datos): carga de bases de Spider en MySQL` |
| Conversión SQL Spider → MySQL y filtro por ejecución | Carlos Alburez | **Completado** | `feat(datos): conversión a MySQL y filtro por ejecución` |
| Traducción de preguntas al español (MultiSpider) | Carlos Alburez | **Completado** | `feat(datos): traducción de preguntas al español` |
| Validation set propio (2 esquemas + 40 preguntas validadas) | Carlos Alburez | **Completado** | `feat(validacion): 2 esquemas y 40 preguntas propias` |
| `src/evaluador.py` (EX ponderado 1/2/3 y categorías) | Carlos Alburez | **Completado** | `feat(validacion): evaluador por ejecución con EX ponderado` |
| Dataset final (`train.jsonl`, ≥2,400 pares) + `chequeo_fuga.py` | Carlos Alburez | **Completado** | `feat(datos): dataset final de entrenamiento y chequeo de fuga` |
| Reporte de descartes (`resumen_descartes.md`) | Carlos Alburez | **Completado** | `docs(datos): reporte de descartes` |
| `notebooks/01_datos.ipynb` (pipeline explicativo) | Carlos Alburez | **Completado** | `docs(notebooks): notebook 01 de preparación de datos y validación` |
| `notebooks/03_evaluacion.ipynb` (base y métricas) | Carlos Alburez | **Completado** | `docs: notebook 03 de evaluación y documentación inicial` |
| `README.md` (arquitectura, ejecución y licencias) | Carlos Alburez | **Completado** | `docs: README con ejecución, licencias y uso de IA` |
| Estructura base del modelo (`config.json`, `prompt.py`) | Erick Guerra | **Completado** | `313430f feat(modelo): config.json y prompt estandarizado` |
| `src/filtro.py` y `tests/test_filtro.py` | Erick Guerra | **Completado** | `6e92031 feat(inferencia): filtro de solo lectura y limpieza de salida con pruebas` |
| `solucion.py` (`generar_sql` con autocorrección) | Erick Guerra | **Completado** | `dfc35b7`, `e1435ad`, `f17ae72` |
| Notebook 02 de entrenamiento (Colab y Kaggle) | Erick Guerra | **Completado** | `fec6c32`, `f99fa52`, `2676161`, `9939630`, `b8a9191`, `6d6e8ec`, `2e96f88` |
| Corrección del evaluador (comparar resultado completo) | Erick Guerra | **Completado** | `01c82a3 fix(evaluacion): comparar el resultado completo y no solo 10 filas` |
| Preguntas de validación indican columnas a devolver | Erick Guerra | **Completado** | `7eba9a6 feat(validacion): las preguntas indican qué columnas devolver` |
| Baseline sin adapter (EX, determinismo y errores) | Erick Guerra | **Completado** | `2419a92 feat(evaluacion): evaluación del baseline, determinismo y análisis de errores` |
| Entrenamiento Config 1 (r=8) y Config 2 (r=32), dataset v1 | Erick Guerra | **Completado** | `2154f89`, `368461a`, `258adcf`, `a6e3bb3`, `f33b539` |
| Dataset v2 (indicación de columnas) y notebook 02b | Erick Guerra | **Completado** | `1be53c4`, `100194c`, `5537b19`, `fabba01`, `94d8e4e`, `51bb85b`, `cedeb1d` |
| 12 esquemas propios con 460 pares MySQL y dataset v3 | Erick Guerra | **Completado** | `67c1907`, `d5a0cfd`, `316e271` |
| Experimento de inferencia (autocorrección con `ejecutar`) | Erick Guerra | **Completado** | `a6e3bb3`, `cedeb1d` |
| `requirements.txt` con versiones probadas | Erick Guerra | **Completado** | `90b0c50 chore: fijar versiones probadas de transformers, peft y accelerate` |
| `notebooks/correr_solucion.ipynb` (entorno limpio + MySQL) | Erick Guerra | **Completado** | `433ee48 feat: notebook de prueba de la entrega en entorno limpio con MySQL 8.4.10` |
| Bitácora, entradas 7–12 | Erick Guerra | **Completado** | `700099d`, `779e157` y commit de entradas 11–12 |
| Dataset v3 entrenado y adapter final (r8_v3, EX 0.800) | Erick Guerra | **Completado** | `fd5470e`, `e1e4387`, `079cab4` y commit del adapter final |
| `presentacion.pdf` (≤12 diapositivas) | Erick Guerra | *En progreso* | Se sube al final |
| Prueba final en Colab T4 limpio (`correr_solucion.ipynb`) | Ambos | *Pendiente* | Por realizar conjuntamente |
| `historial_git.txt` final | Carlos Alburez | *Pendiente* | Al cierre previo a la entrega |
