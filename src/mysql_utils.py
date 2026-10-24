
import mysql.connector
from mysql.connector import Error
import os
import re


MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
}

ROOT_USER = os.getenv("MYSQL_ROOT_USER", "root")
ROOT_PASSWORD = os.getenv("MYSQL_ROOT_PASSWORD", "root2026")

READONLY_USER = os.getenv("MYSQL_READONLY_USER", "evaluador")
READONLY_PASSWORD = os.getenv("MYSQL_READONLY_PASSWORD", "eval2026")



# Conexiones


def get_connection(database: str | None = None) -> mysql.connector.MySQLConnection:
    """Conexión con el usuario root. Para administración y carga de esquemas."""
    config = {**MYSQL_CONFIG, "user": ROOT_USER, "password": ROOT_PASSWORD}
    if database:
        config["database"] = database
    return mysql.connector.connect(**config)


def get_readonly_connection(database: str) -> mysql.connector.MySQLConnection:
    """Conexión con el usuario evaluador (solo lectura). Simula al docente."""
    return mysql.connector.connect(
        **MYSQL_CONFIG,
        user=READONLY_USER,
        password=READONLY_PASSWORD,
        database=database,
    )



# Función ejecutar() — réplica del evaluador del docente

def ejecutar(sql: str, database: str, max_filas: int | None = 10) -> dict:
    """
    Ejecuta una consulta SQL con el usuario de solo lectura.

    Parámetros
    ----------
    sql : str
        Consulta SQL a ejecutar.
    database : str
        Nombre de la base de datos sobre la que se ejecuta.

    Retorna
    -------
    dict con:
        - ok (bool): True si la consulta se ejecutó sin errores.
        - columnas (list[str] | None): nombres de las columnas del resultado.
        - filas (list[list] | None): máximo `max_filas` filas del resultado
          (10, como el ejecutar() del docente; None = todas, para comparar en el evaluador).
        - error (str | None): mensaje de error si ok es False.
    """
    conn = None
    cursor = None
    try:
        conn = get_readonly_connection(database)
        cursor = conn.cursor(buffered=True)
        cursor.execute(sql)

        columnas = [desc[0] for desc in cursor.description] if cursor.description else []
        filas = cursor.fetchall() if max_filas is None else cursor.fetchmany(max_filas)
        # Convertir a listas simples (en lugar de tuplas) para facilitar la comparación
        filas = [list(fila) for fila in filas]

        return {
            "ok": True,
            "columnas": columnas,
            "filas": filas,
            "error": None,
        }

    except Error as e:
        return {
            "ok": False,
            "columnas": None,
            "filas": None,
            "error": str(e),
        }

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def hacer_ejecutar(database: str):
    """
    Devuelve una función ejecutar(sql) ligada a una base de datos específica.
    Es la que se pasa como argumento a generar_sql().

    Uso:
        ej = hacer_ejecutar("mi_base")
        resultado = ej("SELECT * FROM clientes LIMIT 5")
    """
    def _ejecutar(sql: str) -> dict:
        return ejecutar(sql, database)
    return _ejecutar


# Administración de esquemas

def cargar_esquema(schema_file: str, db_name: str) -> None:
    """
    Crea (o recrea) una base de datos y ejecuta un archivo .sql con los
    CREATE TABLE y los INSERT.

    Parámetros
    ----------
    schema_file : str
        Ruta al archivo .sql con las sentencias DDL (y opcionalmente DML).
    db_name : str
        Nombre de la base de datos a crear.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"DROP DATABASE IF EXISTS `{db_name}`")
        cursor.execute(f"CREATE DATABASE `{db_name}` DEFAULT CHARACTER SET utf8mb4")
        # Otorgar permisos de solo lectura al evaluador
        # El usuario ya existe (creado por docker-compose), solo otorgar SELECT
        try:
            cursor.execute(
                f"GRANT SELECT ON `{db_name}`.* TO %s@'%%'", (READONLY_USER,)
            )
        except Exception:
            # Si falla (usuario no existe), crearlo primero
            cursor.execute(
                f"CREATE USER IF NOT EXISTS %s@'%%' IDENTIFIED BY %s",
                (READONLY_USER, READONLY_PASSWORD)
            )
            cursor.execute(
                f"GRANT SELECT ON `{db_name}`.* TO %s@'%%'", (READONLY_USER,)
            )
        cursor.execute("FLUSH PRIVILEGES")
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    # Ejecutar el archivo SQL en la base recién creada
    conn = get_connection(database=db_name)
    cursor = conn.cursor()
    try:
        with open(schema_file, "r", encoding="utf-8") as f:
            sql_content = f.read()

        # Separar por sentencias (usando ; como delimitador)
        sentencias = _split_sql(sql_content)
        for stmt in sentencias:
            stmt = stmt.strip()
            if stmt:
                cursor.execute(stmt)
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def obtener_esquema(db_name: str) -> str:
    """
    Devuelve todas las sentencias CREATE TABLE de una base de datos,
    tal como las genera SHOW CREATE TABLE (incluidos los COMMENT).

    Este es el formato que se pasa a generar_sql() como `esquema`.
    """
    conn = get_connection(database=db_name)
    cursor = conn.cursor()
    try:
        cursor.execute("SHOW TABLES")
        tablas = [row[0] for row in cursor.fetchall()]

        creates = []
        for tabla in tablas:
            cursor.execute(f"SHOW CREATE TABLE `{tabla}`")
            row = cursor.fetchone()
            creates.append(row[1])  # La segunda columna es el CREATE TABLE

        return "\n\n".join(creates)
    finally:
        cursor.close()
        conn.close()



# Utilidades internas

def _split_sql(sql_text: str) -> list[str]:
    """
    Divide un texto SQL en sentencias individuales por ';', respetando
    strings entre comillas simples y dobles.
    """
    sentencias = []
    current = []
    in_single_quote = False
    in_double_quote = False
    i = 0

    while i < len(sql_text):
        char = sql_text[i]

        if char == "'" and not in_double_quote:
            # Verificar si es un escape ''
            if in_single_quote and i + 1 < len(sql_text) and sql_text[i + 1] == "'":
                current.append("''")
                i += 2
                continue
            in_single_quote = not in_single_quote
            current.append(char)

        elif char == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
            current.append(char)

        elif char == ";" and not in_single_quote and not in_double_quote:
            stmt = "".join(current).strip()
            if stmt:
                sentencias.append(stmt)
            current = []

        elif char == "-" and not in_single_quote and not in_double_quote:
            # Comentario de línea --
            if i + 1 < len(sql_text) and sql_text[i + 1] == "-":
                # Saltar hasta el final de la línea
                end = sql_text.find("\n", i)
                if end == -1:
                    break
                i = end
                current.append("\n")
            else:
                current.append(char)

        else:
            current.append(char)

        i += 1

    # Última sentencia (sin ; final)
    last = "".join(current).strip()
    if last:
        sentencias.append(last)

    return sentencias


# Prueba rápida
if __name__ == "__main__":
    print("Probando conexión a MySQL...")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]
        print(f"  Conexión exitosa. MySQL versión: {version}")
        cursor.close()
        conn.close()
    except Error as e:
        print(f"    Error de conexión: {e}")
        print("     ¿Está corriendo el contenedor? → docker compose up -d")
