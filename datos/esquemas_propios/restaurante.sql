-- Esquema propio: restaurante
-- Descripción: cadena de restaurantes (menú, órdenes, meseros y reservaciones)

CREATE TABLE sucursales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL COMMENT 'Nombre de la sucursal',
    ciudad VARCHAR(60) NOT NULL COMMENT 'Ciudad',
    capacidad INT NOT NULL COMMENT 'Número de comensales que caben'
) COMMENT='Sucursales de la cadena';

CREATE TABLE meseros (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre del mesero',
    sucursal_id INT NOT NULL COMMENT 'Sucursal donde trabaja',
    fecha_contrato DATE NOT NULL COMMENT 'Fecha de contratación',
    turno ENUM('Mañana','Tarde','Noche') NOT NULL COMMENT 'Turno asignado',
    FOREIGN KEY (sucursal_id) REFERENCES sucursales(id)
) COMMENT='Meseros';

CREATE TABLE platillos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre del platillo',
    tipo ENUM('Entrada','Plato fuerte','Postre','Bebida') NOT NULL COMMENT 'Tipo de platillo',
    precio DECIMAL(8,2) NOT NULL COMMENT 'Precio en quetzales',
    vegetariano BOOLEAN DEFAULT FALSE COMMENT 'Si es apto para vegetarianos'
) COMMENT='Menú';

CREATE TABLE ordenes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sucursal_id INT NOT NULL COMMENT 'Sucursal',
    mesero_id INT NOT NULL COMMENT 'Mesero que atendió',
    mesa INT NOT NULL COMMENT 'Número de mesa',
    fecha_hora DATETIME NOT NULL COMMENT 'Fecha y hora de la orden',
    propina DECIMAL(8,2) DEFAULT 0 COMMENT 'Propina en quetzales',
    FOREIGN KEY (sucursal_id) REFERENCES sucursales(id),
    FOREIGN KEY (mesero_id) REFERENCES meseros(id)
) COMMENT='Órdenes (cuentas) de cada mesa';

CREATE TABLE orden_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    orden_id INT NOT NULL COMMENT 'Orden',
    platillo_id INT NOT NULL COMMENT 'Platillo pedido',
    cantidad INT NOT NULL COMMENT 'Porciones',
    FOREIGN KEY (orden_id) REFERENCES ordenes(id),
    FOREIGN KEY (platillo_id) REFERENCES platillos(id)
) COMMENT='Platillos de cada orden';

CREATE TABLE reservaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sucursal_id INT NOT NULL COMMENT 'Sucursal reservada',
    nombre_cliente VARCHAR(100) NOT NULL COMMENT 'Nombre de quien reserva',
    fecha_hora DATETIME NOT NULL COMMENT 'Fecha y hora de la reservación',
    personas INT NOT NULL COMMENT 'Número de personas',
    estado ENUM('Confirmada','Cancelada','Cumplida') NOT NULL COMMENT 'Estado de la reservación',
    FOREIGN KEY (sucursal_id) REFERENCES sucursales(id)
) COMMENT='Reservaciones';
