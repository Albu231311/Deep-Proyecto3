-- Esquema propio: inmobiliaria
-- Descripción: agencia de bienes raíces (propiedades, agentes, visitas y contratos)

CREATE TABLE zonas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(60) NOT NULL COMMENT 'Nombre de la zona',
    ciudad VARCHAR(60) NOT NULL COMMENT 'Ciudad'
) COMMENT='Zonas o colonias';

CREATE TABLE agentes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre del agente',
    fecha_ingreso DATE NOT NULL COMMENT 'Fecha de ingreso a la agencia',
    comision_pct DECIMAL(4,2) NOT NULL COMMENT 'Porcentaje de comisión'
) COMMENT='Agentes inmobiliarios';

CREATE TABLE propiedades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    zona_id INT NOT NULL COMMENT 'Zona donde está',
    agente_id INT NOT NULL COMMENT 'Agente a cargo',
    tipo ENUM('Casa','Apartamento','Terreno','Local') NOT NULL COMMENT 'Tipo de propiedad',
    operacion ENUM('Venta','Alquiler') NOT NULL COMMENT 'Tipo de operación',
    precio DECIMAL(12,2) NOT NULL COMMENT 'Precio de venta o renta mensual en quetzales',
    metros INT NOT NULL COMMENT 'Metros cuadrados',
    habitaciones INT COMMENT 'Número de habitaciones',
    fecha_publicacion DATE NOT NULL COMMENT 'Fecha de publicación',
    FOREIGN KEY (zona_id) REFERENCES zonas(id),
    FOREIGN KEY (agente_id) REFERENCES agentes(id)
) COMMENT='Propiedades publicadas';

CREATE TABLE interesados (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre del interesado',
    presupuesto DECIMAL(12,2) COMMENT 'Presupuesto máximo en quetzales'
) COMMENT='Personas interesadas en comprar o alquilar';

CREATE TABLE visitas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    propiedad_id INT NOT NULL COMMENT 'Propiedad visitada',
    interesado_id INT NOT NULL COMMENT 'Quién visitó',
    fecha_hora DATETIME NOT NULL COMMENT 'Fecha y hora de la visita',
    interes ENUM('Bajo','Medio','Alto') COMMENT 'Nivel de interés mostrado',
    FOREIGN KEY (propiedad_id) REFERENCES propiedades(id),
    FOREIGN KEY (interesado_id) REFERENCES interesados(id)
) COMMENT='Visitas a propiedades';

CREATE TABLE contratos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    propiedad_id INT NOT NULL COMMENT 'Propiedad',
    interesado_id INT NOT NULL COMMENT 'Comprador o inquilino',
    fecha_firma DATE NOT NULL COMMENT 'Fecha de firma',
    monto_final DECIMAL(12,2) NOT NULL COMMENT 'Monto acordado',
    FOREIGN KEY (propiedad_id) REFERENCES propiedades(id),
    FOREIGN KEY (interesado_id) REFERENCES interesados(id)
) COMMENT='Contratos de venta o alquiler firmados';
