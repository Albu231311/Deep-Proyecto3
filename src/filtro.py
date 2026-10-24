"""
Filtro de solo lectura y post-procesamiento de la salida del modelo.

es_solo_lectura(sql) garantiza que solucion.py nunca devuelva una consulta
que modifique la base (penalización de -10 en la rúbrica).
"""
import re


# Palabras que no pueden aparecer fuera de strings / identificadores con backticks.
# REPLACE no está aquí porque también es una función de texto válida en un SELECT;
# como sentencia ya queda bloqueada porque exigimos que la consulta empiece con SELECT/WITH.
PALABRAS_PROHIBIDAS = {
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE",
    "GRANT", "REVOKE", "RENAME", "CALL", "LOAD", "HANDLER", "LOCK", "UNLOCK",
    "SET", "INTO", "OUTFILE", "DUMPFILE", "EXECUTE", "PREPARE", "DEALLOCATE",
    "SHUTDOWN", "KILL", "FLUSH", "RESET", "INSTALL", "UNINSTALL", "SLEEP",
    "BENCHMARK",
}

# SQL de respaldo: una consulta válida y de solo lectura
SQL_RESPALDO = "SELECT 1"


# Una sola pasada de izquierda a derecha: así un '--' dentro de un string no se
# confunde con un comentario (y viceversa).
_LITERALES = re.compile(
    r"'(?:[^'\\]|\\.|'')*'"       # string con comillas simples
    r'|"(?:[^"\\]|\\.|"")*"'      # string con comillas dobles
    r"|`[^`]*`"                   # identificador con backticks
    r"|/\*.*?\*/"                 # comentario de bloque
    r"|(?:--|#)[^\n]*",           # comentario de línea
    re.DOTALL,
)


def _quitar_literales(sql: str) -> str:
    """
    Reemplaza strings, identificadores con backticks y comentarios por un
    marcador neutro, para poder buscar palabras clave sin falsos positivos
    (p. ej. WHERE estado = 'DELETE' o una columna `update`).
    """
    return _LITERALES.sub(" x ", sql)


def es_solo_lectura(sql: str) -> bool:
    """
    True solo si `sql` es UNA sentencia SELECT o WITH ... SELECT.
    Rechaza sentencias de modificación, múltiples sentencias y comentarios
    ejecutables de MySQL (/*! ... */).
    """
    if not sql or not sql.strip():
        return False
    if "/*!" in sql:
        return False

    limpio = _quitar_literales(sql).strip()
    # Se permite un único ';' al final
    limpio = re.sub(r";\s*$", "", limpio)
    if ";" in limpio:
        return False

    palabras = re.findall(r"[A-Za-z_]+", limpio.upper())
    if not palabras or palabras[0] not in ("SELECT", "WITH"):
        # También se acepta "(SELECT ...)" porque findall ignora el paréntesis
        return False
    if palabras[0] == "WITH" and "SELECT" not in palabras:
        return False
    if PALABRAS_PROHIBIDAS.intersection(palabras):
        return False
    return True


# Post-procesamiento de la salida del modelo

def _cortar_en_punto_y_coma(sql: str) -> str:
    """Corta en el primer ';' que no esté dentro de un string."""
    comilla = None
    for i, c in enumerate(sql):
        if comilla:
            if c == comilla:
                comilla = None
        elif c in ("'", '"', "`"):
            comilla = c
        elif c == ";":
            return sql[:i]
    return sql


def limpiar_salida(texto: str) -> str:
    """
    Extrae una sola consulta SQL del texto generado:
    quita bloques ```sql```, explicaciones antes/después y el ';' final.
    """
    texto = texto.strip()

    # 1. Si hay un bloque de código markdown, quedarse con su contenido
    bloque = re.search(r"```(?:sql|mysql)?\s*\n?(.*?)(```|$)", texto, re.DOTALL | re.IGNORECASE)
    if bloque:
        texto = bloque.group(1).strip()
    else:
        # Sin bloque: la explicación suele venir después de una línea en blanco
        texto = re.split(r"\n\s*\n", texto, maxsplit=1)[0]

    # 2. Empezar en el primer SELECT / WITH (descarta "Aquí está la consulta:")
    inicio = re.search(r"\b(SELECT|WITH)\b", texto, re.IGNORECASE)
    if inicio:
        texto = texto[inicio.start():]

    # 3. Una sola sentencia, sin ';' final
    texto = _cortar_en_punto_y_coma(texto)
    return texto.strip()
