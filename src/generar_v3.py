"""
Dataset v3: train_v2 con alias legibles + pares propios sobre esquemas MySQL.

Diagnóstico de v2 (notebook 03): el LoRA aprende el estilo de Spider y rompe
preguntas que el modelo base acertaba:
  - alias T1/T2/T3 que confunde entre tablas (val_14, val_16, val_29, val_38);
  - sin funciones de fecha de MySQL, porque Spider no las tiene (val_20, val_40);
  - JOIN y GROUP BY más pobres (val_12, val_34).

Cambios:
  1. En los pares de Spider, T1/T2/... se reemplazan por alias derivados del
     nombre de la tabla (student -> s, student_course -> sc). Solo se acepta la
     reescritura si la consulta sigue ejecutándose en MySQL.
  2. Pares escritos con ayuda de un LLM sobre esquemas propios
     (datos/esquemas_propios/*.sql) con COMMENT, nombres en español, inglés y
     abreviados, y consultas MySQL: fechas, WITH, funciones de ventana,
     subconsultas. Cada par se ejecuta en MySQL 8.4.10 sobre la base poblada
     con datos sintéticos; los que fallan van a datos/descartes/.

Uso:  python -m src.generar_v3
"""
import json
import random
import re
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

from src.aumentar_columnas import PLANTILLAS, indicacion
from src.mysql_utils import cargar_esquema, get_connection, obtener_esquema


ENTRADA_V2 = Path("datos/entrenamiento/train_v2.jsonl")
SALIDA = Path("datos/entrenamiento/train_v3.jsonl")
DIR_PROPIOS = Path("datos/esquemas_propios")
DESCARTES = Path("datos/descartes/descartes_v3.jsonl")
SEMILLA = 2026
FILAS_POR_TABLA = 40
# Cada par propio entra dos veces, con distinta redacción de la indicación de columnas,
# para que pesen más frente a los 2,429 de Spider (son los más parecidos a la evaluación)
REPETICIONES_PROPIOS = 2


# 1. Alias legibles en Spider

_ALIAS_T = re.compile(r"`?(\w+)`?\s+AS\s+(T\d+)\b", re.IGNORECASE)
_RESERVADAS = {"as", "at", "by", "do", "if", "in", "is", "on", "or", "to", "add", "all", "and",
               "asc", "div", "end", "for", "key", "mod", "not", "row", "set", "use", "xor"}


def _abreviar(tabla: str, usados: set[str]) -> str:
    partes = [p for p in re.split(r"_+", tabla.lower()) if p]
    base = "".join(p[0] for p in partes) if len(partes) > 1 else tabla.lower()[:1]
    alias, i = base, 2
    while alias in usados or alias in _RESERVADAS:
        alias = (tabla.lower()[:i] if len(partes) == 1 and i <= len(tabla) else f"{base}{i}")
        i += 1
    usados.add(alias)
    return alias


def alias_legibles(sql: str) -> str:
    """Reemplaza T1, T2, ... por alias derivados del nombre de su tabla."""
    mapa, usados = {}, set()
    for tabla, t in _ALIAS_T.findall(sql):
        if t.upper() not in mapa:
            mapa[t.upper()] = _abreviar(tabla, usados)
    if not mapa:
        return sql
    return re.sub(r"\bT\d+\b", lambda m: mapa.get(m.group(0).upper(), m.group(0)), sql,
                  flags=re.IGNORECASE)


# 2. Datos sintéticos (solo para revisar que las consultas devuelvan filas)

_NOMBRES = ["Ana López", "Carlos Pérez", "María García", "José Hernández", "Lucía Morales",
            "Diego Ramírez", "Sofía Castillo", "Luis Méndez", "Elena Ruiz", "Jorge Díaz",
            "Valeria Cruz", "Andrés Flores", "Camila Rojas", "Pablo Ortiz", "Daniela Vega"]
_POOLS = {
    "ciudad": ["Guatemala", "Quetzaltenango", "Antigua", "Escuintla", "Cobán", "Mixco"],
    "city": ["New York", "Chicago", "Miami", "Houston", "Seattle", "Boston"],
    "pais": ["Guatemala", "México", "El Salvador", "Honduras", "Costa Rica"],
    "country": ["USA", "Mexico", "Canada", "Spain", "Brazil"],
    "nombre": _NOMBRES, "name": [n.split()[0] + " Smith" for n in _NOMBRES],
}


def _valor(col: dict, i: int, rng: random.Random, padres: dict):
    nombre, tipo, ctype = col["nombre"], col["tipo"], col["column_type"]
    if col["fk"]:
        return rng.randint(1, padres[col["fk"]])
    if col["nulo"] and rng.random() < 0.15:
        return None
    if tipo == "enum":
        return rng.choice(re.findall(r"'((?:[^']|'')*)'", ctype)).replace("''", "'")
    if tipo in ("date", "datetime", "timestamp"):
        d = datetime(2022, 1, 1) + timedelta(days=rng.randint(0, 1755), minutes=rng.randint(480, 1140))
        return d.date() if tipo == "date" else d
    if tipo == "time":
        return f"{rng.randint(7, 21):02d}:{rng.choice(['00', '15', '30', '45'])}:00"
    if tipo == "year":
        return rng.randint(2015, 2026)
    if ctype.startswith("tinyint(1)"):
        return int(rng.random() < 0.7)
    if tipo in ("int", "smallint", "mediumint", "bigint", "tinyint"):
        return rng.randint(1, 120 if tipo != "tinyint" else 100)
    if tipo in ("decimal", "float", "double"):
        return round(rng.uniform(10, 5000), 2)
    largo = col["largo"] or 200
    if col["unico"]:
        v = f"{nombre}_{i}"
        return v if len(v) <= largo else f"{nombre[:max(0, largo - len(str(i)))]}{i}"
    for clave, pool in _POOLS.items():
        if nombre.lower() == clave or nombre.lower().startswith(clave + "_"):
            return rng.choice(pool)[:largo]
    if "nombre" in nombre.lower() or "name" in nombre.lower():
        return f"{rng.choice(_NOMBRES)} {i}"[:largo]
    return f"{nombre} {i % 12}"[:largo]


def poblar(db: str, rng: random.Random) -> None:
    conn = get_connection(db)
    cur = conn.cursor()
    cur.execute("""SELECT c.TABLE_NAME, c.COLUMN_NAME, c.DATA_TYPE, c.COLUMN_TYPE, c.EXTRA,
                          c.CHARACTER_MAXIMUM_LENGTH, c.COLUMN_KEY, c.IS_NULLABLE, k.REFERENCED_TABLE_NAME
                   FROM information_schema.COLUMNS c
                   LEFT JOIN information_schema.KEY_COLUMN_USAGE k
                     ON k.TABLE_SCHEMA = c.TABLE_SCHEMA AND k.TABLE_NAME = c.TABLE_NAME
                    AND k.COLUMN_NAME = c.COLUMN_NAME AND k.REFERENCED_TABLE_NAME IS NOT NULL
                   WHERE c.TABLE_SCHEMA = %s ORDER BY c.TABLE_NAME, c.ORDINAL_POSITION""", (db,))
    tablas = defaultdict(list)
    for t, c, tipo, ctype, extra, largo, llave, nulo, ref in cur.fetchall():
        if "auto_increment" in extra or "GENERATED" in extra.upper():
            continue
        tablas[t].append({"nombre": c, "tipo": tipo, "column_type": ctype, "largo": largo,
                          "unico": llave in ("UNI", "PRI") and not ref, "fk": ref,
                          "nulo": nulo == "YES"})
    # Orden topológico: primero las tablas referenciadas
    orden, pendientes = [], dict(tablas)
    while pendientes:
        listas = [t for t, cols in pendientes.items()
                  if all(c["fk"] in orden or c["fk"] == t or c["fk"] not in pendientes for c in cols if c["fk"])]
        listas = listas or [next(iter(pendientes))]
        for t in sorted(listas):
            orden.append(t)
            pendientes.pop(t)
    cur.execute("SET FOREIGN_KEY_CHECKS = 0")
    filas = {}
    for t in orden:
        n = FILAS_POR_TABLA * (2 if sum(bool(c["fk"]) for c in tablas[t]) >= 2 else 1)
        filas[t] = n
        cols = tablas[t]
        padres = {c["fk"]: filas.get(c["fk"], FILAS_POR_TABLA) for c in cols if c["fk"]}
        valores = [tuple(_valor(c, i + 1, rng, padres) for c in cols) for i in range(n)]
        lista = ", ".join(f"`{c['nombre']}`" for c in cols)
        ph = ", ".join(["%s"] * len(cols))
        cur.executemany(f"INSERT IGNORE INTO `{t}` ({lista}) VALUES ({ph})", valores)
    cur.execute("SET FOREIGN_KEY_CHECKS = 1")
    conn.commit()
    cur.close()
    conn.close()


# 3. Pares propios

def pares_propios(stats: Counter, descartes: list) -> list[dict]:
    rng = random.Random(SEMILLA)
    salida = []
    for ddl in sorted(DIR_PROPIOS.glob("*.sql")):
        nombre = ddl.stem
        db = f"propio_{nombre}"
        cargar_esquema(str(ddl), db)
        poblar(db, rng)
        esquema = obtener_esquema(db)
        archivo = DIR_PROPIOS / "pares" / f"{nombre}.jsonl"
        conn = get_connection(db)
        cur = conn.cursor()
        for k, linea in enumerate(open(archivo, encoding="utf-8")):
            if not linea.strip():
                continue
            p = json.loads(linea)
            ident = f"{nombre}_{k + 1:03d}"
            try:
                cur.execute(p["sql"])
                filas = cur.fetchall()
                cols = [d[0] for d in cur.description]
            except Exception as e:
                stats["propio_no_ejecuta"] += 1
                descartes.append({"id": ident, "db_id": db, "pregunta": p["pregunta"], "sql": p["sql"],
                                  "motivo": "error_mysql", "error": str(e)})
                continue
            if not filas:
                stats["propio_sin_filas_(se_conserva)"] += 1
                print(f"  [sin filas] {ident}: {p['sql'][:110]}")
            stats["propio_ok"] += 1
            primera = indicacion(cols, ident)
            i0 = next(i for i, t in enumerate(PLANTILLAS) if t.split("{")[0] in primera)
            for rep in range(REPETICIONES_PROPIOS):
                plantilla = PLANTILLAS[(i0 + rep) % len(PLANTILLAS)]
                lista = ", ".join(cols)
                y = lista if len(cols) == 1 else ", ".join(cols[:-1]) + " y " + cols[-1]
                salida.append({
                    "id": f"propio_{ident}" + (f"_r{rep + 1}" if rep else ""), "db_id": db, "esquema": esquema,
                    "pregunta": f"{p['pregunta'].rstrip()} {plantilla.format(lista=lista, y=y)}",
                    "sql": p["sql"], "nivel": p["nivel"], "columnas": cols,
                    "sql_original": p["sql"], "pregunta_original": p["pregunta"],
                })
        cur.close()
        conn.close()
        print(f"{nombre}: {sum(1 for s in salida if s['db_id'] == db) // REPETICIONES_PROPIOS} pares")
    return salida


def spider_alias(stats: Counter) -> list[dict]:
    filas = [json.loads(l) for l in open(ENTRADA_V2, encoding="utf-8")]
    conn = get_connection()
    cur = conn.cursor()
    for f in filas:
        nuevo = alias_legibles(f["sql"])
        if nuevo == f["sql"]:
            continue
        try:
            cur.execute(f"USE `{f['db_id']}`")
            cur.execute(nuevo)
            cur.fetchall()
            f["sql"] = nuevo
            stats["spider_alias_reescrito"] += 1
        except Exception:
            stats["spider_alias_falla_se_conserva"] += 1
    cur.close()
    conn.close()
    return filas


def main():
    stats, descartes = Counter(), []
    spider = spider_alias(stats)
    propios = pares_propios(stats, descartes)
    with open(SALIDA, "w", encoding="utf-8") as out:
        for g in spider + propios:
            out.write(json.dumps(g, ensure_ascii=False) + "\n")
    with open(DESCARTES, "w", encoding="utf-8") as out:
        for d in descartes:
            out.write(json.dumps(d, ensure_ascii=False) + "\n")
    print(f"\n{len(spider)} Spider + {len(propios)} propios = {len(spider) + len(propios)} -> {SALIDA}")
    print("Niveles propios:", Counter(p["nivel"] for p in propios))
    for k, v in stats.most_common():
        print(f"  {k}: {v}")
    for d in descartes:
        print(f"  [descartado] {d['id']}: {d['error'][:150]}")


if __name__ == "__main__":
    main()
