import sys
import os

# Agregar la raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.filtro import es_solo_lectura, limpiar_salida


# Consultas que el filtro DEBE aceptar
VALIDAS = [
    "SELECT nombre FROM estudiantes",
    "select nombre, carrera from estudiantes where estado = 'Activo';",
    "SELECT * FROM t WHERE estado = 'DELETE'",                      # palabra prohibida dentro de un string
    "SELECT `update`, `drop` FROM bitacora",                        # identificadores con backticks
    "SELECT REPLACE(nombre, 'a', 'b') FROM clientes",               # REPLACE como función
    "SELECT created_at, updated_at FROM pedidos",                   # palabras clave como parte de un nombre
    "WITH t AS (SELECT id FROM a) SELECT * FROM t",
    "(SELECT id FROM a) UNION (SELECT id FROM b)",
    "SELECT nombre, RANK() OVER (ORDER BY nota DESC) AS r FROM notas",
    "SELECT * FROM t WHERE c = 'a;b'",                              # ';' dentro de un string
    "SELECT * FROM t -- comentario con DROP\nWHERE id = 1",          # palabra prohibida en un comentario
]

# Consultas que el filtro DEBE rechazar
PELIGROSAS = [
    "",
    "   ",
    "DROP TABLE estudiantes",
    "DELETE FROM estudiantes",
    "UPDATE estudiantes SET estado = 'Baja'",
    "INSERT INTO clientes (nombre) VALUES ('x')",
    "TRUNCATE TABLE pedidos",
    "ALTER TABLE t ADD COLUMN x INT",
    "CREATE TABLE x (id INT)",
    "GRANT ALL ON *.* TO 'x'@'%'",
    "REPLACE INTO t VALUES (1)",
    "SELECT 1; DROP TABLE estudiantes",                             # múltiples sentencias
    "SELECT 1; SELECT 2",
    "SELECT '--'; DROP TABLE t",                                    # '--' dentro de string no oculta el DROP
    "SELECT 'abc; DROP TABLE t",                                    # string sin cerrar
    "WITH t AS (SELECT id FROM a) DELETE FROM a WHERE id IN (SELECT id FROM t)",
    "SELECT * INTO OUTFILE '/tmp/x' FROM t",
    "SELECT * FROM t /*! ; DROP TABLE t */",                        # comentario ejecutable de MySQL
    "SELECT * FROM t FOR UPDATE",
    "SELECT SLEEP(100)",
    "SHOW TABLES",
    "Aquí está la consulta",
]

# (salida cruda del modelo, consulta esperada después de limpiar)
SALIDAS = [
    ("```sql\nSELECT nombre FROM t;\n```", "SELECT nombre FROM t"),
    ("Aquí está la consulta:\n```sql\nSELECT a\nFROM t\n```\nEsta consulta devuelve...", "SELECT a\nFROM t"),
    ("SELECT id FROM t;\n\nExplicación: selecciona los ids", "SELECT id FROM t"),
    ("La consulta es: SELECT id FROM t", "SELECT id FROM t"),
    ("SELECT * FROM t WHERE c = 'a;b';", "SELECT * FROM t WHERE c = 'a;b'"),
    ("WITH x AS (SELECT 1) SELECT * FROM x; SELECT 2", "WITH x AS (SELECT 1) SELECT * FROM x"),
    ("```\nSELECT 1\n", "SELECT 1"),                                 # bloque sin cerrar
]


def test_acepta_consultas_validas():
    for sql in VALIDAS:
        assert es_solo_lectura(sql), f"Debió aceptar: {sql!r}"


def test_rechaza_consultas_peligrosas():
    for sql in PELIGROSAS:
        assert not es_solo_lectura(sql), f"Debió rechazar: {sql!r}"


def test_limpiar_salida():
    for cruda, esperada in SALIDAS:
        obtenida = limpiar_salida(cruda)
        assert obtenida == esperada, f"{cruda!r} -> {obtenida!r} (esperado {esperada!r})"
        assert es_solo_lectura(obtenida)


def main():
    print("1. Consultas válidas...")
    test_acepta_consultas_validas()
    print(f"   {len(VALIDAS)} aceptadas")

    print("2. Consultas peligrosas...")
    test_rechaza_consultas_peligrosas()
    print(f"   {len(PELIGROSAS)} rechazadas")

    print("3. Limpieza de salidas del modelo...")
    test_limpiar_salida()
    print(f"   {len(SALIDAS)} limpiadas correctamente")

    print("TODAS LAS PRUEBAS PASARON ")


if __name__ == "__main__":
    main()
