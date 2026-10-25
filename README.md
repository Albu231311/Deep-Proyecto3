# Proyecto 3: Text-to-SQL con LoRA

**Universidad del Valle de Guatemala**  
**Curso:** Deep Learning 2026  
**Catedrático:** Kevin Recinos  

---

## 1. Descripción del Proyecto

Este proyecto implementa el *fine-tuning* de un Modelo de Lenguaje Pequeño (SLM), específicamente `Qwen/Qwen2.5-Coder-1.5B-Instruct`, utilizando adaptación de bajo rango (**LoRA**). El objetivo es recibir como entrada el esquema DDL de una base de datos relacional y una pregunta formulada en lenguaje natural (español), generando como salida una consulta SQL válida y semánticamente exacta para **MySQL 8.4.10** bajo el modo estricto (`ONLY_FULL_GROUP_BY`).

---

## 2. Estructura del Repositorio

```text
Deep-Proyecto3/
├── solucion.py                 # Punto de entrada oficial (función generar_sql)
├── config.json                 # Modelo base, ruta del adapter, usar_adapter y semilla
├── requirements.txt            # Dependencias fijadas (probadas en Kaggle/Colab T4)
├── docker-compose.yml          # Servicio MySQL 8.4.10 oficial
├── adapter/                    # Adapter LoRA final (el que carga solucion.py)
├── adapters_experimentos/      # Adapters de todas las configuraciones (v1, v2, v3, época 1)
├── datos/
│   ├── entrenamiento/          # train.jsonl (v1), train_v2.jsonl, train_v3.jsonl (final)
│   ├── validacion/             # esquemas_val/*.sql y val.jsonl (40 preguntas propias)
│   ├── esquemas_propios/       # 12 esquemas propios (.sql) y sus pares en pares/*.jsonl
│   └── descartes/              # descartes.jsonl y resumen_descartes.md
├── notebooks/
│   ├── 01_datos.ipynb          # Pipeline de datos y análisis de descartes
│   ├── 02_entrenamiento.ipynb  # LoRA r=8 vs r=32 con dataset v1 (Kaggle T4)
│   ├── 02b_entrenamiento_v2.ipynb  # Mismo experimento con dataset v2
│   ├── 02c_entrenamiento_v3.ipynb  # Mismo experimento con dataset v3 (final)
│   ├── 03_evaluacion.ipynb     # EX ponderado de todas las configuraciones y errores
│   └── correr_solucion.ipynb   # Prueba de la entrega en un entorno limpio con MySQL
├── src/
│   ├── mysql_utils.py          # Conexión, SHOW CREATE TABLE y ejecutar() seguro
│   ├── evaluador.py            # Evaluador por ejecución con EX ponderado
│   ├── chequeo_fuga.py         # Verificador de independencia train-validación
│   ├── preparar_datos.py       # Spider: conversión SQLite -> MySQL y filtro (v1)
│   ├── aumentar_columnas.py    # Dataset v2: indicación de columnas y alias
│   ├── generar_v3.py           # Dataset v3: alias legibles + pares propios validados
│   ├── filtro.py               # Filtro de solo lectura (SELECT / WITH)
│   ├── prompt.py               # Prompt único (entrenamiento, inferencia y baseline)
│   └── compat.py               # Parche de compatibilidad peft/torchao en Colab
├── tests/
│   ├── test_filtro.py          # 40 casos del filtro de solo lectura
│   ├── test_mysql_utils.py     # Conexión y permisos
│   └── test_validation_set.py  # Las 40 consultas de validación ejecutan
├── resultados/
│   ├── validacion_propia.csv   # Resultado por pregunta de la configuración final
│   ├── resumen_ex.csv          # EX de todas las configuraciones
│   ├── evaluaciones/           # Detalle por pregunta de cada configuración
│   └── curvas_loss/            # Curvas train/eval loss y métricas de cada entrenamiento
├── BITACORA.md                 # Registro cronológico por integrante
├── CONTRIBUCIONES.md           # División de tareas y evidencias
├── historial_git.txt           # git log --all --stat
└── README.md
```

---

## 3. Requisitos y Entorno de Ejecución

### Entorno Local (Docker)
- Docker Desktop instalado.
- Para levantar el motor de base de datos MySQL 8.4.10:
  ```bash
  docker compose up -d
  ```
  Esto inicia una instancia limpia con:
  - Puerto expuesto: `3306`
  - Usuario administrador: `root` (contraseña en `docker-compose.yml`)
  - Usuario de evaluación de solo lectura: `evaluador` (sin permisos de escritura/modificación)

### Dependencias de Python
Instalar los requerimientos en un entorno virtual con Python 3.10+:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 4. Pipeline de Datos y Validación

### Validación Propia (`val.jsonl`)
El conjunto de validación consta de 40 preguntas redactadas desde cero, divididas equitativamente entre dos esquemas independientes:
1. `sistema_academico` (5 tablas, gestión universitaria)
2. `clinica_salud` (6 tablas, gestión médica y hospitalaria)

Distribución de dificultad:
- **15 Fáciles (peso 1):** Consultas de tabla individual con filtros y orden.
- **15 Medias (peso 2):** Consultas con `JOIN`, agrupaciones `GROUP BY` y condiciones `HAVING`.
- **10 Difíciles (peso 3):** Consultas avanzadas con CTEs (`WITH`), subconsultas correlacionadas, funciones de ventana (`DENSE_RANK`) y manipulación temporal (`TIMESTAMPDIFF`).

Para verificar la ejecución del conjunto de validación:
```bash
PYTHONPATH=. python tests/test_validation_set.py
```

### Dataset de Entrenamiento y Reporte de Descartes
Para reproducir la extracción, transpilación SQLite -> MySQL 8.4 y validación por ejecución real:
```bash
PYTHONPATH=. python src/preparar_datos.py
```
- Salida aceptada: `datos/entrenamiento/train.jsonl` (2,429 pares validados).
- Salida descartada: `datos/descartes/descartes.jsonl` y análisis estructurado en `datos/descartes/resumen_descartes.md`.

### Verificación de Fuga de Datos
Para certificar que ningún esquema ni tabla de validación fue incluido en el entrenamiento:
```bash
PYTHONPATH=. python src/chequeo_fuga.py
```

---

## 5. Uso de `solucion.py`

```python
from solucion import generar_sql

esquema = "CREATE TABLE ..."   # salida de SHOW CREATE TABLE de cada tabla
sql = generar_sql(esquema, "¿Cuántos clientes hay por ciudad? Devuelve las columnas: ciudad, total.")

# Opcional: con ejecutar, el modelo ve el error o el resultado y puede corregir (máx. 3 llamadas)
sql = generar_sql(esquema, pregunta, ejecutar=mi_funcion_ejecutar)
```

- El modelo y el adapter se cargan **una sola vez al importar** (7–13 s en GPU) según `config.json`. Con `"usar_adapter": false` se usa el modelo base (baseline).
- Generación greedy (`do_sample=False`) con semilla fija: la misma entrada produce siempre la misma consulta.
- Toda salida pasa por `src/filtro.py`: si no es un único `SELECT`/`WITH` de solo lectura, se devuelve `SELECT 1`.
- Para probar la entrega en un entorno limpio (instala MySQL 8.4.10, las dependencias y evalúa las 40 preguntas): `notebooks/correr_solucion.ipynb`.

Evaluación local de una configuración (requiere MySQL en Docker y las bases de validación cargadas):
```bash
PYTHONPATH=. python -m jupyter nbconvert --to notebook --execute notebooks/03_evaluacion.ipynb
```

---

## 6. Entrenamiento

Los notebooks 02, 02b y 02c se ejecutaron en **Kaggle** (GPU T4, *Save & Run All*). Necesitan *Internet: On* y un secret `GITHUB_TOKEN`: al terminar cada configuración suben su adapter, curvas y métricas al repositorio, para no perder el trabajo si la sesión se corta. En una corrida entrenan las dos configuraciones (`r = 8` y `r = 32`, `alpha = 2r`), que solo difieren en el rango.

Hiperparámetros comunes: LoRA sobre `q,k,v,o,gate,up,down`, dropout 0.05, learning rate 2e-4, 2 épocas, batch efectivo 16 (2 × 8 de acumulación), longitud máxima 2048, loss solo sobre la consulta SQL (prompt enmascarado), adapter guardado en `float16`. Para regenerar los datasets:
```bash
PYTHONPATH=. python -m src.aumentar_columnas  # train_v2.jsonl
PYTHONPATH=. python -m src.generar_v3          # train_v3.jsonl (requiere MySQL)
```

---

## 7. Resultados (validación propia, EX ponderado)

| Versión | Dataset | EX | Fácil / media / difícil |
|---|---|---|---|
| Baseline (sin adapter) | — | 0.747 | 1.00 / 0.87 / 0.50 |
| LoRA r = 8 / r = 32 | v1: Spider en español | 0.467 / 0.467 | 1.00 / 0.47 / 0.20 |
| LoRA r = 8 / r = 32 | v2: + indicación de columnas | 0.520 / 0.520 | 1.00 / 0.60 / 0.20 |
| **LoRA r = 8 (entregado)** / r = 32 | v3: + alias legibles y 460 pares propios MySQL | **0.800** / 0.800 | 1.00 / 0.80 / 0.70 |

El adapter entregado (`adapter/`) es **r8_v3**: empata con r32_v3 y es 4 veces más pequeño (18.5 MB). Detalle por pregunta en `resultados/validacion_propia.csv`; todas las configuraciones en `resultados/resumen_ex.csv`; análisis completo en `notebooks/03_evaluacion.ipynb` y `BITACORA.md`.

---

## 8. Licencias y Fuentes

- **Spider Dataset:** Licenciado bajo [Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/). Yale LILY Lab.
- **MultiSpider:** Licenciado bajo Creative Commons CC BY-SA 4.0. Adaptaciones y traducciones multilingües.
- **Modelo Base (Qwen2.5-Coder):** Alibaba Cloud / Qwen Team, licenciado bajo [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).

---

## 9. Declaración de Uso de Inteligencia Artificial

En conformidad con las políticas de integridad académica del curso:
- **Asistente de programación:** se usó Claude Code (Anthropic) como ayuda para partes del codigo y depurar código (`solucion.py`, filtro, notebooks de entrenamiento y evaluación, generadores de datasets), diagnosticar errores de entorno (Colab/Kaggle, versiones de `peft`/`transformers`) y ayuda con la documentación.
- **Pares generados con LLM:** los 12 esquemas de `datos/esquemas_propios/` y sus 460 pares pregunta-SQL se generaron con ayuda de un LLM (Claude), como permite el enunciado ("pares generados con un LLM sobre al menos 10 esquemas propios"). Todos se ejecutaron en MySQL 8.4.10 sobre las bases pobladas con datos sintéticos; los que fallaran irían a `datos/descartes/` (no falló ninguno).
- **Validación humana:** las sentencias DDL, las consultas de referencia de la validación propia, la refinación de hipótesis y las decisiones experimentales fueron revisadas por los integrantes, y toda consulta se validó por ejecución directa en MySQL 8.4.10.
