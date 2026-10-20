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
├── config.json                 # Configuración de modelo, adapter y semilla
├── requirements.txt            # Dependencias fijadas para entorno local y Colab
├── docker-compose.yml          # Servicio MySQL 8.4.10 oficial
├── adapter/                    # Pesos entrenados del adapter LoRA final
├── datos/
│   ├── entrenamiento/          # train.jsonl (≥2,400 pares pregunta-SQL válidos)
│   ├── validacion/             # esquemas_val/*.sql y val.jsonl (40 preguntas propias)
│   ├── esquemas_propios/       # Esquemas sintéticos con comentarios
│   └── descartes/              # descartes.jsonl y resumen_descartes.md
├── notebooks/
│   ├── 01_datos.ipynb          # Pipeline de datos y análisis de descartes
│   ├── 02_entrenamiento.ipynb  # Fine-tuning con LoRA (Config 1 vs Config 2)
│   ├── 03_evaluacion.ipynb     # Evaluación de EX ponderado y análisis de errores
│   └── correr_solucion.ipynb   # Validación en Google Colab T4 limpio
├── src/
│   ├── mysql_utils.py          # Conexión, SHOW CREATE TABLE y ejecutar() seguro
│   ├── evaluador.py            # Evaluador oficial por ejecución con EX ponderado
│   ├── chequeo_fuga.py         # Verificador de independencia train-validación
│   ├── preparar_datos.py       # Pipeline de extracción, transpilation y filtrado
│   ├── filtro.py               # Filtro de solo lectura (SELECT / WITH)
│   └── prompt.py               # Plantilla estándar de formateo de prompts
├── tests/
│   ├── test_mysql_utils.py     # Pruebas unitarias de conexión y permisos
│   └── test_validation_set.py  # Verificación al 100% de consultas de validación
├── resultados/
│   ├── validacion_propia.csv   # Resultados detallados por pregunta
│   └── curvas_loss/            # Gráficas de convergencia train/eval loss
├── BITACORA.md                 # Registro cronológico de actividades por integrante
├── CONTRIBUCIONES.md           # Tabla formal de división de tareas y evidencias
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

## 5. Licencias y Fuentes

- **Spider Dataset:** Licenciado bajo [Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/). Yale LILY Lab.
- **MultiSpider:** Licenciado bajo Creative Commons CC BY-SA 4.0. Adaptaciones y traducciones multilingües.
- **Modelo Base (Qwen2.5-Coder):** Alibaba Cloud / Qwen Team, licenciado bajo [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).

---

## 6. Declaración de Uso de Inteligencia Artificial

En conformidad con las políticas de integridad académica del curso:
- **Modelos LLM:** Se emplearon herramientas asistivas basadas en LLMs para la formulación inicial de esquemas sintéticos y asistencia en la transpilación de consultas complejas.
- **Validación Humana:** Todas las sentencias DDL, consultas SQL de referencia y categorizaciones de error fueron inspeccionadas, ajustadas y validadas mediante ejecución directa en el motor MySQL 8.4.10.