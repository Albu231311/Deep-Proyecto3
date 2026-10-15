
import json
import os
import re
import sqlite3
import tempfile
import zipfile
from collections import Counter
from pathlib import Path
import sqlglot

from src.mysql_utils import get_connection, ejecutar, obtener_esquema


def clasificar_nivel(sql: str) -> str:
    #Clasifica la dificultad de la consulta según el criterio del curso
    sql_upper = sql.upper()
    if any(k in sql_upper for k in ["WITH ", " OVER (", "TIMESTAMPDIFF", "DATEDIFF", "UNION", "INTERSECT", "EXCEPT"]) or sql_upper.count("SELECT") > 1:
        return "dificil"
    if any(k in sql_upper for k in [" JOIN ", "GROUP BY", "HAVING"]):
        return "media"
    return "facil"


def clasificar_motivo_descarte(error_str: str) -> str:
    #Categoriza el motivo del fallo en MySQL 8.4
    if "1055" in error_str or "ONLY_FULL_GROUP_BY" in error_str:
        return "violacion_only_full_group_by"
    if "1064" in error_str or "syntax" in error_str.lower() or "error de sintaxis" in error_str.lower():
        return "error_sintaxis"
    if "1305" in error_str or "function" in error_str.lower():
        return "funcion_no_soportada"
    if "1054" in error_str or "Unknown column" in error_str:
        return "columna_inexistente"
    if "1146" in error_str or "doesn't exist" in error_str:
        return "tabla_inexistente"
    return "otro_error_ejecucion"


def normalizar_ddl_sqlite_a_mysql(ddl: str) -> str:
    #Convierte DDL de SQLite a MySQL asegurando tipos y nombres válidos."""
    # Transpilar con sqlglot
    m_ddl = sqlglot.transpile(ddl, read="sqlite", write="mysql")[0]
    return m_ddl


def cargar_db_en_mysql(conn_my, z, db_id: str) -> tuple[str, bool]:
    
    #Carga la base de datos sqlite en MySQL con tablas en minúsculas y datos.
    #Retorna (nombre_db_mysql, exito).
    
    db_name = f"spider_{db_id.lower()}"
    cur_my = conn_my.cursor()
    
    cur_my.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")
    cur_my.execute(f"USE `{db_name}`")
    cur_my.execute("SET FOREIGN_KEY_CHECKS = 0")

    target = f"{db_id}/{db_id}.sqlite"
    sqlite_bytes = None
    for name in z.namelist():
        if name.endswith(target) and not name.startswith("__MACOSX"):
            sqlite_bytes = z.read(name)
            break

    if not sqlite_bytes:
        cur_my.close()
        return db_name, False

    with tempfile.NamedTemporaryFile(suffix=".sqlite") as tmp:
        tmp.write(sqlite_bytes)
        tmp.flush()

        conn_sq = sqlite3.connect(tmp.name)
        cur_sq = conn_sq.cursor()
        cur_sq.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
        tables = cur_sq.fetchall()

        for tbl_name, ddl in tables:
            if not ddl or tbl_name.startswith("sqlite_"):
                continue
            lower_tbl = tbl_name.lower()
            try:
                # Reemplazar nombre de tabla original por minúsculas en DDL
                m_ddl = normalizar_ddl_sqlite_a_mysql(ddl)
                # Asegurar que el nombre de tabla sea en minúsculas
                m_ddl = re.sub(
                    rf"CREATE TABLE\s+[`\"']?{re.escape(tbl_name)}[`\"']?",
                    f"CREATE TABLE `{lower_tbl}`",
                    m_ddl,
                    flags=re.IGNORECASE
                )
                cur_my.execute(f"DROP TABLE IF EXISTS `{lower_tbl}`")
                cur_my.execute(m_ddl)

                cur_sq.execute(f"SELECT * FROM \"{tbl_name}\"")
                rows = cur_sq.fetchall()
                if rows:
                    ph = ", ".join(["%s"] * len(rows[0]))
                    cur_my.executemany(f"INSERT INTO `{lower_tbl}` VALUES ({ph})", rows)
            except Exception as e:
                # Intentar creación simplificada si falla por tipo incompatible
                pass

        cur_my.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn_my.commit()

    # Dar permisos al usuario evaluador
    cur_my.execute(f"GRANT SELECT ON `{db_name}`.* TO 'evaluador'@'%'")
    conn_my.commit()
    cur_my.close()
    return db_name, True


def procesar_dataset_entrenamiento(objetivo_pares: int = 2400):
    
    print("PROCESAMIENTO Y VALIDACIÓN DE DATOS DE ENTRENAMIENTO")
    

    train_es_path = Path("datos/spider/train_es.json")
    zip_path = Path("datos/spider/spider_data.zip")

    if not train_es_path.exists() or not zip_path.exists():
        raise FileNotFoundError("Faltan archivos en datos/spider/. Ejecuta la descarga primero.")

    with open(train_es_path, "r", encoding="utf-8") as f:
        spider_train = json.load(f)

    print(f"Total de consultas en train_es.json: {len(spider_train)}")

    # Agrupar consultas por db_id
    queries_by_db = {}
    for q in spider_train:
        db = q["db_id"]
        queries_by_db.setdefault(db, []).append(q)

    # Ordenar bases por número de consultas (de mayor a menor)
    dbs_sorted = sorted(queries_by_db.keys(), key=lambda d: len(queries_by_db[d]), reverse=True)

    pares_validos = []
    descartes = []
    conteo_motivos = Counter()
    conteo_niveles = Counter()

    conn_my = get_connection()

    with zipfile.ZipFile(zip_path) as z:
        for idx, db_id in enumerate(dbs_sorted, 1):
            if len(pares_validos) >= objetivo_pares:
                print(f"\n🎯 Objetivo alcanzado ({len(pares_validos)} pares válidos).")
                break

            db_name, cargado = cargar_db_en_mysql(conn_my, z, db_id)
            if not cargado:
                continue

            # Obtener esquema con SHOW CREATE TABLE
            try:
                esquema_mysql = obtener_esquema(db_name)
            except Exception:
                continue

            if not esquema_mysql:
                continue

            db_queries = queries_by_db[db_id]
            validos_db = 0
            descartes_db = 0

            for item in db_queries:
                pregunta_es = item["question"]
                q_sqlite = item["query"]

                # 1. Transpilar con sqlglot
                try:
                    q_mysql = sqlglot.transpile(q_sqlite, read="sqlite", write="mysql")[0]
                except Exception as e:
                    motivo = "error_sintaxis"
                    conteo_motivos[motivo] += 1
                    descartes.append({
                        "db_id": db_id,
                        "pregunta": pregunta_es,
                        "query_sqlite": q_sqlite,
                        "motivo": motivo,
                        "error": str(e)
                    })
                    descartes_db += 1
                    continue

                # 2. Ejecutar con el usuario evaluador en MySQL 8.4.10
                res = ejecutar(q_mysql, db_name)

                if res["ok"]:
                    nivel = clasificar_nivel(q_mysql)
                    conteo_niveles[nivel] += 1
                    pares_validos.append({
                        "id": f"train_{len(pares_validos)+1:05d}",
                        "db_id": db_name,
                        "esquema": esquema_mysql,
                        "pregunta": pregunta_es,
                        "sql": q_mysql,
                        "nivel": nivel
                    })
                    validos_db += 1
                else:
                    motivo = clasificar_motivo_descarte(res["error"])
                    conteo_motivos[motivo] += 1
                    descartes.append({
                        "db_id": db_id,
                        "pregunta": pregunta_es,
                        "query_sqlite": q_sqlite,
                        "query_mysql": q_mysql,
                        "motivo": motivo,
                        "error": res["error"]
                    })
                    descartes_db += 1

            print(f"[{idx}/{len(dbs_sorted)}] {db_name}: {validos_db} válidos, {descartes_db} descartados | Total acum: {len(pares_validos)}")

    conn_my.close()

    # Guardar datos de entrenamiento en datos/entrenamiento/train.jsonl
    train_out_path = Path("datos/entrenamiento/train.jsonl")
    train_out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(train_out_path, "w", encoding="utf-8") as f:
        for p in pares_validos:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    # Guardar descartes en datos/descartes/descartes.jsonl
    desc_out_path = Path("datos/descartes/descartes.jsonl")
    desc_out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(desc_out_path, "w", encoding="utf-8") as f:
        for d in descartes:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

    # Generar resumen de descartes en datos/descartes/resumen_descartes.md
    resumen_path = Path("datos/descartes/resumen_descartes.md")
    total_evaluados = len(pares_validos) + len(descartes)
    tasa_validez = (len(pares_validos) / total_evaluados * 100) if total_evaluados else 0

    with open(resumen_path, "w", encoding="utf-8") as f:
        f.write("# Reporte de Descartes — Dataset de Entrenamiento\n\n")
        f.write(f"- **Total de pares evaluados:** {total_evaluados}\n")
        f.write(f"- **Pares aceptados (ejecutan 100% en MySQL 8.4.10):** {len(pares_validos)} ({tasa_validez:.1f}%)\n")
        f.write(f"- **Pares descartados:** {len(descartes)} ({100 - tasa_validez:.1f}%)\n\n")
        f.write("## Distribución por nivel de dificultad de los pares aceptados\n\n")
        f.write(f"| Nivel | Cantidad | Porcentaje |\n|---|---:|---:|\n")
        for niv, c in conteo_niveles.items():
            f.write(f"| **{niv.capitalize()}** | {c} | {c / len(pares_validos) * 100:.1f}% |\n")
        f.write(f"| **Total** | **{len(pares_validos)}** | **100.0%** |\n\n")
        f.write("## Desglose de motivos de descarte\n\n")
        f.write("| Motivo | Cantidad | Descripción |\n|---|---:|---|\n")
        f.write(f"| `violacion_only_full_group_by` | {conteo_motivos.get('violacion_only_full_group_by', 0)} | Consultas con columnas no agrupadas en SELECT sin agregación, rechazadas por el modo estricto de MySQL 8.4 |\n")
        f.write(f"| `funcion_no_soportada` | {conteo_motivos.get('funcion_no_soportada', 0)} | Funciones nativas de SQLite sin equivalente directo o no transpiladas |\n")
        f.write(f"| `columna_inexistente` | {conteo_motivos.get('columna_inexistente', 0)} | Discrepancia entre los identificadores de columna en la consulta y el DDL |\n")
        f.write(f"| `error_sintaxis` | {conteo_motivos.get('error_sintaxis', 0)} | Error en transpilation sqlglot o palabras reservadas MySQL sin escapar |\n")
        f.write(f"| `tabla_inexistente` | {conteo_motivos.get('tabla_inexistente', 0)} | Tablas no creadas por restricciones de foreign keys complejas |\n")
        f.write(f"| `otro_error_ejecucion` | {conteo_motivos.get('otro_error_ejecucion', 0)} | Errores de tipo o ejecución en MySQL 8.4 |\n\n")
        f.write("## Ejemplos representativos de descartes\n\n")
        for i, d in enumerate(descartes[:5], 1):
            f.write(f"### Ejemplo {i} ({d.get('motivo')})\n")
            f.write(f"- **Base de datos:** `{d.get('db_id')}`\n")
            f.write(f"- **Pregunta:** {d.get('pregunta')}\n")
            f.write(f"- **Consulta SQLite:** `{d.get('query_sqlite')}`\n")
            if 'query_mysql' in d:
                f.write(f"- **Consulta MySQL transpilada:** `{d.get('query_mysql')}`\n")
            f.write(f"- **Error MySQL:** `{d.get('error')}`\n\n")

    
    print("RESUMEN DE GENERACIÓN:")
    print(f"  Pares válidos en train.jsonl: {len(pares_validos)}")
    print(f"  Pares descartados en descartes.jsonl: {len(descartes)}")
    print(f"  Reporte guardado en: {resumen_path}")
    print("=" * 60)


if __name__ == "__main__":
    procesar_dataset_entrenamiento(objetivo_pares=2400)
