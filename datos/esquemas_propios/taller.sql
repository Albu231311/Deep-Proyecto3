-- Esquema propio: taller
-- Descripción: taller mecánico (nombres en español abreviados)

CREATE TABLE cli (
    id_cli INT AUTO_INCREMENT PRIMARY KEY,
    nom_cli VARCHAR(100) NOT NULL COMMENT 'Nombre del cliente',
    tel VARCHAR(15) COMMENT 'Teléfono',
    f_reg DATE NOT NULL COMMENT 'Fecha de registro'
) COMMENT='Clientes del taller';

CREATE TABLE veh (
    id_veh INT AUTO_INCREMENT PRIMARY KEY,
    id_cli INT NOT NULL COMMENT 'Propietario',
    placa VARCHAR(10) NOT NULL UNIQUE COMMENT 'Placa',
    marca VARCHAR(40) NOT NULL COMMENT 'Marca del vehículo',
    anio INT NOT NULL COMMENT 'Año del modelo',
    km INT COMMENT 'Kilometraje actual',
    FOREIGN KEY (id_cli) REFERENCES cli(id_cli)
) COMMENT='Vehículos de los clientes';

CREATE TABLE mec (
    id_mec INT AUTO_INCREMENT PRIMARY KEY,
    nom_mec VARCHAR(100) NOT NULL COMMENT 'Nombre del mecánico',
    espec ENUM('Motor','Frenos','Eléctrico','Carrocería') NOT NULL COMMENT 'Especialidad',
    f_ing DATE NOT NULL COMMENT 'Fecha de ingreso'
) COMMENT='Mecánicos';

CREATE TABLE ord (
    id_ord INT AUTO_INCREMENT PRIMARY KEY,
    id_veh INT NOT NULL COMMENT 'Vehículo atendido',
    id_mec INT NOT NULL COMMENT 'Mecánico responsable',
    f_ent DATE NOT NULL COMMENT 'Fecha de entrada al taller',
    f_sal DATE COMMENT 'Fecha de salida (NULL si sigue en el taller)',
    est ENUM('ABI','PRO','TER') NOT NULL COMMENT 'Estado: ABI=abierta, PRO=en proceso, TER=terminada',
    mo DECIMAL(10,2) NOT NULL COMMENT 'Costo de mano de obra en quetzales',
    FOREIGN KEY (id_veh) REFERENCES veh(id_veh),
    FOREIGN KEY (id_mec) REFERENCES mec(id_mec)
) COMMENT='Órdenes de servicio';

CREATE TABLE rep (
    id_rep INT AUTO_INCREMENT PRIMARY KEY,
    desc_rep VARCHAR(100) NOT NULL COMMENT 'Descripción del repuesto',
    p_unit DECIMAL(10,2) NOT NULL COMMENT 'Precio unitario en quetzales',
    exist INT NOT NULL COMMENT 'Existencias en bodega'
) COMMENT='Repuestos';

CREATE TABLE ord_rep (
    id_ord INT NOT NULL COMMENT 'Orden de servicio',
    id_rep INT NOT NULL COMMENT 'Repuesto usado',
    cant INT NOT NULL COMMENT 'Cantidad usada',
    PRIMARY KEY (id_ord, id_rep),
    FOREIGN KEY (id_ord) REFERENCES ord(id_ord),
    FOREIGN KEY (id_rep) REFERENCES rep(id_rep)
) COMMENT='Repuestos usados en cada orden';

CREATE TABLE fac (
    id_fac INT AUTO_INCREMENT PRIMARY KEY,
    id_ord INT NOT NULL COMMENT 'Orden facturada',
    f_fac DATE NOT NULL COMMENT 'Fecha de la factura',
    total DECIMAL(10,2) NOT NULL COMMENT 'Total facturado en quetzales',
    pagada BOOLEAN DEFAULT FALSE COMMENT 'Si ya fue pagada',
    FOREIGN KEY (id_ord) REFERENCES ord(id_ord)
) COMMENT='Facturas';
