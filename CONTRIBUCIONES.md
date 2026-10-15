# Contribuciones — Proyecto 3: Text-to-SQL con LoRA

## Integrantes y Roles principales

| Integrante | Área principal | Responsabilidades clave |
|---|---|---|
| **Carlos Alburez** (`Albu231311`) | **Datos** + **Validación y errores** | Pipeline de datos, conversión SQLite->MySQL 8.4, reporte de descartes, validation set propio (40 preguntas), evaluador EX ponderado, chequeo de fuga, notebooks 01 y 03, README |
| **Erick Guerra** (`Compañero`) | **Entrenamiento** + **Inferencia** | `solucion.py`, filtro de solo lectura, `prompt.py`, baseline, entrenamiento LoRA (Config 1 vs Config 2), experimento de inferencia, notebook 02, presentación |

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
| Estructura base del modelo (`config.json`, `prompt.py`) | Erick Guerra | *Pendiente* | Por realizar por Erick Guerra |
| Notebooks de entrenamiento y Colab (`02_entrenamiento.ipynb`) | Erick Guerra | *Pendiente* | Por realizar por Erick Guerra |
| `solucion.py`, `src/filtro.py` y pruebas | Erick Guerra | *Pendiente* | Por realizar por Erick Guerra |
| Baseline sin adapter | Erick Guerra | *Pendiente* | Por realizar por Erick Guerra |
| Entrenamiento Config 1 (r=8) y Config 2 (r=32) | Erick Guerra | *Pendiente* | Por realizar por Erick Guerra |
| Experimento de inferencia (autocorrección con `ejecutar`) | Erick Guerra | *Pendiente* | Por realizar por Erick Guerra |
| `presentacion.pdf` (≤12 diapositivas) | Erick Guerra | *Pendiente* | Por realizar por Erick Guerra |
| Prueba final en Colab T4 limpio (`correr_solucion.ipynb`) | Ambos | *Pendiente* | Por realizar conjuntamente |
| `historial_git.txt` final | Carlos Alburez | *Pendiente* | Al cierre previo a la entrega |
