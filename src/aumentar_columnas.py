"""
Dataset v2: cada pregunta de entrenamiento indica qué columnas devolver.

En la evaluación oculta "cada pregunta indica qué columnas devolver", pero las
preguntas de Spider nunca lo hacen. El adapter v1 aprendió a ignorar esa
instrucción (EX 0.47 vs 0.75 del modelo base en la validación propia).

Para cada par de datos/entrenamiento/train.jsonl:
  1. A las expresiones sin nombre del SELECT exterior (COUNT(*), AVG(x), ...)
     se les pone un alias (COUNT(*) AS cantidad, AVG(salario) AS promedio_salario).
     Columnas repetidas (T1.nombre, T2.nombre) se renombran con su tabla.
  2. La consulta resultante se EJECUTA en MySQL 8.4.10 sobre una base creada con
     su esquema (SHOW CREATE TABLE), y los nombres de columna se toman de lo que
     devuelve MySQL. Si falla, se conserva la consulta original.
  3. Se agrega a la pregunta una indicación de columnas, con varias redacciones
     para no depender de una sola frase.

Uso:  python -m src.aumentar_columnas
"""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import sqlglot
from sqlglot import exp

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.mysql_utils import get_connection


ENTRADA = Path("datos/entrenamiento/train.jsonl")
SALIDA = Path("datos/entrenamiento/train_v2.jsonl")

PLANTILLAS = [
    "Devuelve las columnas: {lista}.",
    "Columnas a devolver: {lista}.",
    "Muestra las columnas {y}.",
    "El resultado debe tener las columnas: {lista}.",
    "Incluye en el resultado: {lista}.",
]

PREFIJO_AGREGADO = {
    exp.Avg: "promedio",
    exp.Sum: "total",
    exp.Max: "maximo",
    exp.Min: "minimo",
    exp.Count: "cantidad",
}


# Bases vacías con el esquema de cada ejemplo

def crear_bases(filas: list[dict]) -> None:
    """Crea (vacía) cada base de entrenamiento a partir de su DDL."""
    esquemas = {}
    for f in filas:
        esquemas.setdefault(f["db_id"], f["esquema"])
    conn = get_connection()
    cur = conn.cursor()
    for db_id, esquema in esquemas.items():
        cur.execute(f"DROP DATABASE IF EXISTS `{db_id}`")
        cur.execute(f"CREATE DATABASE `{db_id}` DEFAULT CHARACTER SET utf8mb4")
        cur.execute(f"USE `{db_id}`")
        cur.execute("SET FOREIGN_KEY_CHECKS = 0")
        for ddl in esquema.split("\n\nCREATE TABLE"):
            ddl = ddl if ddl.startswith("CREATE TABLE") else "CREATE TABLE" + ddl
            cur.execute(ddl)
    conn.commit()
    cur.close()
    conn.close()
    print(f"Bases creadas: {len(esquemas)}")


def columnas_mysql(cur, sql: str) -> list[str] | None:
    """Nombres de columna que devuelve MySQL, o None si la consulta falla."""
    try:
        cur.execute(sql)
        cur.fetchall()
        return [d[0] for d in cur.description]
    except Exception:
        return None


# Alias para las columnas del SELECT exterior

def _select_exterior(arbol):
    # En UNION/INTERSECT los nombres los define el primer SELECT
    while isinstance(arbol, exp.SetOperation):
        arbol = arbol.left
    return arbol if isinstance(arbol, exp.Select) else None


def _nombre_alias(proy, tablas: dict) -> str:
    agregado = next((a for t, a in PREFIJO_AGREGADO.items() if isinstance(proy, t)), None)
    col = proy.find(exp.Column)
    if agregado == "cantidad":
        return "cantidad" if col is None else f"cantidad_{col.name.lower()}"
    if agregado:
        return f"{agregado}_{col.name.lower()}" if col is not None else agregado
    return "valor"


def agregar_alias(sql: str) -> str:
    """Devuelve la consulta con alias en expresiones sin nombre y columnas repetidas."""
    arbol = sqlglot.parse_one(sql, read="mysql")
    select = _select_exterior(arbol)
    if select is None:
        return sql

    tablas = {}
    for t in select.find_all(exp.Table):
        tablas[(t.alias or t.name).lower()] = t.name.lower()

    usados, cambios = Counter(), False
    for proy in select.expressions:
        if isinstance(proy, exp.Alias):
            usados[proy.alias.lower()] += 1
        elif isinstance(proy, exp.Column):
            usados[proy.name.lower()] += 1

    nuevas = []
    vistos = Counter()
    for proy in select.expressions:
        if isinstance(proy, (exp.Alias, exp.Star)) or (isinstance(proy, exp.Column) and proy.is_star):
            nuevas.append(proy)
            continue
        if isinstance(proy, exp.Column):
            nombre = proy.name.lower()
            vistos[nombre] += 1
            if usados[nombre] > 1 and vistos[nombre] > 1:
                tabla = tablas.get(proy.table.lower(), proy.table.lower()) if proy.table else "col"
                nuevas.append(exp.alias_(proy, f"{tabla}_{nombre}"))
                cambios = True
            else:
                nuevas.append(proy)
            continue
        alias = _nombre_alias(proy, tablas)
        base, i = alias, 2
        while usados[alias]:
            alias, i = f"{base}_{i}", i + 1
        usados[alias] += 1
        nuevas.append(exp.alias_(proy, alias))
        cambios = True

    if not cambios:
        return sql
    select.set("expressions", nuevas)
    return arbol.sql(dialect="mysql")


def indicacion(columnas: list[str], clave: str) -> str:
    i = int(hashlib.md5(clave.encode()).hexdigest(), 16) % len(PLANTILLAS)
    lista = ", ".join(columnas)
    y = lista if len(columnas) == 1 else ", ".join(columnas[:-1]) + " y " + columnas[-1]
    return PLANTILLAS[i].format(lista=lista, y=y)


def main():
    filas = [json.loads(l) for l in open(ENTRADA, encoding="utf-8")]
    crear_bases(filas)

    conn = get_connection()
    cur = conn.cursor()
    stats = Counter()
    salida = []
    for f in filas:
        cur.execute(f"USE `{f['db_id']}`")
        sql = f["sql"]
        try:
            nuevo = agregar_alias(sql)
        except Exception:
            nuevo = sql
        cols = columnas_mysql(cur, nuevo) if nuevo != sql else None
        if cols is not None:
            stats["alias_agregado"] += 1
            sql = nuevo
        else:
            if nuevo != sql:
                stats["alias_fallo_se_conserva_original"] += 1
            cols = columnas_mysql(cur, sql)

        g = dict(f)
        if cols is None:
            stats["original_no_ejecuta"] += 1
        elif any("(" in c or " " in c for c in cols):
            stats["sin_indicacion_nombre_expresion"] += 1
        else:
            g["sql"] = sql
            g["pregunta"] = f"{f['pregunta'].rstrip()} {indicacion(cols, f['id'])}"
            g["columnas"] = cols
            stats["con_indicacion"] += 1
        g["sql_original"] = f["sql"]
        g["pregunta_original"] = f["pregunta"]
        salida.append(g)

    cur.close()
    conn.close()
    with open(SALIDA, "w", encoding="utf-8") as out:
        for g in salida:
            out.write(json.dumps(g, ensure_ascii=False) + "\n")
    print(f"{len(salida)} pares -> {SALIDA}")
    for k, v in stats.most_common():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
