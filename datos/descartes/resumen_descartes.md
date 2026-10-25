# Reporte de Descartes — Dataset de Entrenamiento

- **Total de pares evaluados:** 7101
- **Pares aceptados (ejecutan 100% en MySQL 8.4.10):** 2429 (34.2%)
- **Pares descartados:** 4672 (65.8%)

## Distribución por nivel de dificultad de los pares aceptados

| Nivel | Cantidad | Porcentaje |
|---|---:|---:|
| **Facil** | 1037 | 42.7% |
| **Dificil** | 382 | 15.7% |
| **Media** | 1010 | 41.6% |
| **Total** | **2429** | **100.0%** |

## Desglose de motivos de descarte

| Motivo | Cantidad | Descripción |
|---|---:|---|
| `violacion_only_full_group_by` | 42 | Consultas con columnas no agrupadas en SELECT sin agregación, rechazadas por el modo estricto de MySQL 8.4 |
| `funcion_no_soportada` | 2 | Funciones nativas de SQLite sin equivalente directo o no transpiladas |
| `columna_inexistente` | 854 | Discrepancia entre los identificadores de columna en la consulta y el DDL |
| `error_sintaxis` | 0 | Error en transpilation sqlglot o palabras reservadas MySQL sin escapar |
| `tabla_inexistente` | 3750 | Tablas no creadas por restricciones de foreign keys complejas |
| `otro_error_ejecucion` | 24 | Errores de tipo o ejecución en MySQL 8.4 |

## Ejemplos representativos de descartes

### Ejemplo 1 (tabla_inexistente)
- **Base de datos:** `scholar`
- **Pregunta:** artículos que son coautores de ''Peter Mertens'' y ''Dina Barbian''
- **Consulta SQLite:** `SELECT DISTINCT t3.paperid FROM writes AS t3 JOIN author AS t2 ON t3.authorid  =  t2.authorid JOIN writes AS t4 ON t4.paperid  =  t3.paperid JOIN author AS t1 ON t4.authorid  =  t1.authorid WHERE t2.authorname  =  "Peter Mertens" AND t1.authorname  =  "Dina Barbian";`
- **Consulta MySQL transpilada:** `SELECT DISTINCT t3.paperid FROM writes AS t3 JOIN author AS t2 ON t3.authorid = t2.authorid JOIN writes AS t4 ON t4.paperid = t3.paperid JOIN author AS t1 ON t4.authorid = t1.authorid WHERE t2.authorname = `Peter Mertens` AND t1.authorname = `Dina Barbian``
- **Error MySQL:** `1146 (42S02): Table 'spider_scholar.writes' doesn't exist`

### Ejemplo 2 (tabla_inexistente)
- **Base de datos:** `scholar`
- **Pregunta:** artículos escritos por ''Peter Mertens'' y ''Dina Barbian''
- **Consulta SQLite:** `SELECT DISTINCT t3.paperid FROM writes AS t3 JOIN author AS t2 ON t3.authorid  =  t2.authorid JOIN writes AS t4 ON t4.paperid  =  t3.paperid JOIN author AS t1 ON t4.authorid  =  t1.authorid WHERE t2.authorname  =  "Peter Mertens" AND t1.authorname  =  "Dina Barbian";`
- **Consulta MySQL transpilada:** `SELECT DISTINCT t3.paperid FROM writes AS t3 JOIN author AS t2 ON t3.authorid = t2.authorid JOIN writes AS t4 ON t4.paperid = t3.paperid JOIN author AS t1 ON t4.authorid = t1.authorid WHERE t2.authorname = `Peter Mertens` AND t1.authorname = `Dina Barbian``
- **Error MySQL:** `1146 (42S02): Table 'spider_scholar.writes' doesn't exist`

### Ejemplo 3 (tabla_inexistente)
- **Base de datos:** `scholar`
- **Pregunta:** ¿Cuáles son los artículos que tienen a''Peter Mertens'' y ''Dina Barbian'' como coautores?
- **Consulta SQLite:** `SELECT DISTINCT t3.paperid FROM writes AS t3 JOIN author AS t2 ON t3.authorid  =  t2.authorid JOIN writes AS t4 ON t4.paperid  =  t3.paperid JOIN author AS t1 ON t4.authorid  =  t1.authorid WHERE t2.authorname  =  "Peter Mertens" AND t1.authorname  =  "Dina Barbian";`
- **Consulta MySQL transpilada:** `SELECT DISTINCT t3.paperid FROM writes AS t3 JOIN author AS t2 ON t3.authorid = t2.authorid JOIN writes AS t4 ON t4.paperid = t3.paperid JOIN author AS t1 ON t4.authorid = t1.authorid WHERE t2.authorname = `Peter Mertens` AND t1.authorname = `Dina Barbian``
- **Error MySQL:** `1146 (42S02): Table 'spider_scholar.writes' doesn't exist`

### Ejemplo 4 (tabla_inexistente)
- **Base de datos:** `scholar`
- **Pregunta:** ¿Qué artículos han escrito ''Peter Mertens'' y ''Dina Barbian''?
- **Consulta SQLite:** `SELECT DISTINCT t3.paperid FROM writes AS t3 JOIN author AS t2 ON t3.authorid  =  t2.authorid JOIN writes AS t4 ON t4.paperid  =  t3.paperid JOIN author AS t1 ON t4.authorid  =  t1.authorid WHERE t2.authorname  =  "Peter Mertens" AND t1.authorname  =  "Dina Barbian";`
- **Consulta MySQL transpilada:** `SELECT DISTINCT t3.paperid FROM writes AS t3 JOIN author AS t2 ON t3.authorid = t2.authorid JOIN writes AS t4 ON t4.paperid = t3.paperid JOIN author AS t1 ON t4.authorid = t1.authorid WHERE t2.authorname = `Peter Mertens` AND t1.authorname = `Dina Barbian``
- **Error MySQL:** `1146 (42S02): Table 'spider_scholar.writes' doesn't exist`

### Ejemplo 5 (tabla_inexistente)
- **Base de datos:** `scholar`
- **Pregunta:** ¿Qué artículo escribieron juntos ''Peter Mertens'' y ''Dina Barbian''?
- **Consulta SQLite:** `SELECT DISTINCT t3.paperid FROM writes AS t3 JOIN author AS t2 ON t3.authorid  =  t2.authorid JOIN writes AS t4 ON t4.paperid  =  t3.paperid JOIN author AS t1 ON t4.authorid  =  t1.authorid WHERE t2.authorname  =  "Peter Mertens" AND t1.authorname  =  "Dina Barbian";`
- **Consulta MySQL transpilada:** `SELECT DISTINCT t3.paperid FROM writes AS t3 JOIN author AS t2 ON t3.authorid = t2.authorid JOIN writes AS t4 ON t4.paperid = t3.paperid JOIN author AS t1 ON t4.authorid = t1.authorid WHERE t2.authorname = `Peter Mertens` AND t1.authorname = `Dina Barbian``
- **Error MySQL:** `1146 (42S02): Table 'spider_scholar.writes' doesn't exist`


---

## Descartes de los datasets v2 y v3

Los datasets v2 y v3 parten de los 2,429 pares aceptados arriba; las consultas que se modificaron se volvieron a ejecutar en MySQL 8.4.10.

| Paso | Script | Consultas ejecutadas | Fallaron | Qué se hizo |
|---|---|---|---|---|
| v2: alias a expresiones del SELECT (`COUNT(*) AS cantidad`) | `src/aumentar_columnas.py` | 761 modificadas | 0 | Si una reescritura fallara, se conserva la consulta original (ya validada); no se pierde el par |
| v3: alias legibles en lugar de `T1`/`T2` | `src/generar_v3.py` | 784 modificadas | 0 | Igual: si fallara, se conserva la original |
| v3: 460 pares propios sobre 12 esquemas (generados con LLM) | `src/generar_v3.py` | 460 | **0** | Los que fallan van a `descartes_v3.jsonl`; quedó **vacío** porque todos ejecutaron |

Los pares propios se ejecutaron sobre cada esquema de `datos/esquemas_propios/` cargado como la base `propio_<nombre>` y poblado con datos sintéticos (40 filas por tabla, respetando enums, llaves foráneas y fechas 2022–2026). 9 de los 460 devuelven 0 filas por los datos aleatorios, pero ejecutan sin error, así que se conservan.
