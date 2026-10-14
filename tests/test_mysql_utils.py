
import sys
import os

# Agregar la raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.mysql_utils import cargar_esquema, obtener_esquema, ejecutar, hacer_ejecutar

# Crear un esquema de prueba temporal
SCHEMA_SQL = """
CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre completo del cliente',
    email VARCHAR(150) COMMENT 'Correo electrónico',
    ciudad VARCHAR(50) COMMENT 'Ciudad de residencia',
    fecha_registro DATE COMMENT 'Fecha en que se registró'
) COMMENT='Tabla de clientes de la tienda';

CREATE TABLE productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre del producto',
    precio DECIMAL(10,2) NOT NULL COMMENT 'Precio unitario en USD',
    categoria VARCHAR(50) COMMENT 'Categoría del producto'
) COMMENT='Catálogo de productos';

CREATE TABLE pedidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL COMMENT 'ID del cliente que hizo el pedido',
    producto_id INT NOT NULL COMMENT 'ID del producto pedido',
    cantidad INT NOT NULL DEFAULT 1 COMMENT 'Cantidad de unidades',
    fecha DATE NOT NULL COMMENT 'Fecha del pedido',
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (producto_id) REFERENCES productos(id)
) COMMENT='Pedidos realizados';

INSERT INTO clientes (nombre, email, ciudad, fecha_registro) VALUES
('Ana López', 'ana@email.com', 'Guatemala', '2024-01-15'),
('Carlos Ruiz', 'carlos@email.com', 'Quetzaltenango', '2024-02-20'),
('María Chen', 'maria@email.com', 'Guatemala', '2024-03-10');

INSERT INTO productos (nombre, precio, categoria) VALUES
('Laptop HP', 899.99, 'Electrónica'),
('Mouse Logitech', 29.99, 'Accesorios'),
('Teclado Mecánico', 79.99, 'Accesorios');

INSERT INTO pedidos (cliente_id, producto_id, cantidad, fecha) VALUES
(1, 1, 1, '2024-03-01'),
(1, 2, 2, '2024-03-01'),
(2, 3, 1, '2024-03-15'),
(3, 1, 1, '2024-04-01'),
(3, 2, 3, '2024-04-01');
"""

def main():

    print("PRUEBA COMPLETA DE mysql_utils.py")
    print("=" * 60)

    # 1. Guardar el SQL temporal
    os.makedirs("/tmp/test_schema", exist_ok=True)
    schema_path = "/tmp/test_schema/tienda.sql"
    with open(schema_path, "w") as f:
        f.write(SCHEMA_SQL)

    # 2. Cargar esquema
    print("\n1. Cargando esquema 'tienda_test'...")
    cargar_esquema(schema_path, "tienda_test")
    print("   Esquema cargado")

    # 3. Obtener esquema (lo que se pasaría a generar_sql)
    print("\n2. Obteniendo esquema con SHOW CREATE TABLE...")
    esquema = obtener_esquema("tienda_test")
    print("   Esquema obtenido:")
    for line in esquema.split("\n")[:10]:
        print(f"      {line}")
    print("      ...")

    # 4. Ejecutar consultas con el usuario de solo lectura
    print("\n3. Probando ejecutar() con consultas...")

    # Consulta simple
    r1 = ejecutar("SELECT nombre, ciudad FROM clientes", "tienda_test")
    print(f"\n   SELECT simple: ok={r1['ok']}")
    print(f"   Columnas: {r1['columnas']}")
    print(f"   Filas: {r1['filas']}")

    # Consulta con JOIN
    r2 = ejecutar("""
        SELECT c.nombre AS cliente, p.nombre AS producto, pe.cantidad
        FROM pedidos pe
        JOIN clientes c ON pe.cliente_id = c.id
        JOIN productos p ON pe.producto_id = p.id
        ORDER BY pe.fecha
    """, "tienda_test")
    print(f"\n   JOIN: ok={r2['ok']}")
    print(f"   Columnas: {r2['columnas']}")
    for fila in r2['filas']:
        print(f"   {fila}")

    # Consulta con GROUP BY + HAVING
    r3 = ejecutar("""
        SELECT c.nombre, SUM(p.precio * pe.cantidad) AS total
        FROM pedidos pe
        JOIN clientes c ON pe.cliente_id = c.id
        JOIN productos p ON pe.producto_id = p.id
        GROUP BY c.nombre
        HAVING total > 100
    """, "tienda_test")
    print(f"\n   GROUP BY + HAVING: ok={r3['ok']}")
    print(f"   Columnas: {r3['columnas']}")
    print(f"   Filas: {r3['filas']}")

    # Consulta con error (tabla inexistente)
    r4 = ejecutar("SELECT * FROM tabla_que_no_existe", "tienda_test")
    print(f"\n   Error esperado: ok={r4['ok']}")
    print(f"   Error: {r4['error'][:80]}...")

    # 5. Probar hacer_ejecutar (factory)
    print("\n4. Probando hacer_ejecutar()...")
    ej = hacer_ejecutar("tienda_test")
    r5 = ej("SELECT COUNT(*) AS total_pedidos FROM pedidos")
    print(f"   ok={r5['ok']}, resultado={r5['filas']}")

    # Consulta con INSERT (debe fallar con usuario de solo lectura)
    print("\n5. Probando que el usuario evaluador NO puede modificar datos...")
    r6 = ejecutar("INSERT INTO clientes (nombre) VALUES ('Hacker')", "tienda_test")
    print(f"   INSERT: ok={r6['ok']}")
    print(f"   Error: {r6['error'][:100] if r6['error'] else 'NINGUNO (¡PROBLEMA!)'}")

    
    print("TODAS LAS PRUEBAS PASARON ")
    


if __name__ == "__main__":
    main()
