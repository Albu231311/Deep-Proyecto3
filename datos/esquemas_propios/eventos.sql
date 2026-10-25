-- Esquema propio: eventos
-- Descripción: boletería de conciertos y eventos

CREATE TABLE artistas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre artístico',
    genero_musical ENUM('Rock','Pop','Salsa','Reggaetón','Clásica','Jazz') NOT NULL COMMENT 'Género musical',
    pais VARCHAR(50) COMMENT 'País de origen'
) COMMENT='Artistas';

CREATE TABLE recintos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre del recinto',
    ciudad VARCHAR(60) NOT NULL COMMENT 'Ciudad',
    aforo INT NOT NULL COMMENT 'Capacidad máxima de personas'
) COMMENT='Recintos (estadios, teatros, salones)';

CREATE TABLE eventos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    artista_id INT NOT NULL COMMENT 'Artista principal',
    recinto_id INT NOT NULL COMMENT 'Recinto',
    fecha_hora DATETIME NOT NULL COMMENT 'Fecha y hora del evento',
    estado ENUM('Programado','Realizado','Cancelado') NOT NULL COMMENT 'Estado del evento',
    FOREIGN KEY (artista_id) REFERENCES artistas(id),
    FOREIGN KEY (recinto_id) REFERENCES recintos(id)
) COMMENT='Eventos programados';

CREATE TABLE zonas_evento (
    id INT AUTO_INCREMENT PRIMARY KEY,
    evento_id INT NOT NULL COMMENT 'Evento',
    nombre_zona ENUM('General','Preferencia','VIP') NOT NULL COMMENT 'Zona del recinto',
    precio DECIMAL(8,2) NOT NULL COMMENT 'Precio del boleto en quetzales',
    FOREIGN KEY (evento_id) REFERENCES eventos(id)
) COMMENT='Zonas y precios de cada evento';

CREATE TABLE compradores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre del comprador',
    email VARCHAR(120) NOT NULL UNIQUE COMMENT 'Correo',
    fecha_nacimiento DATE COMMENT 'Fecha de nacimiento'
) COMMENT='Compradores de boletos';

CREATE TABLE boletos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    zona_evento_id INT NOT NULL COMMENT 'Zona del evento',
    comprador_id INT NOT NULL COMMENT 'Comprador',
    fecha_compra DATETIME NOT NULL COMMENT 'Fecha y hora de compra',
    usado BOOLEAN DEFAULT FALSE COMMENT 'Si se escaneó en la entrada',
    FOREIGN KEY (zona_evento_id) REFERENCES zonas_evento(id),
    FOREIGN KEY (comprador_id) REFERENCES compradores(id)
) COMMENT='Boletos vendidos';
