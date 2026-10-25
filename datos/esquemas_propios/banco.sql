-- Esquema propio: banco
-- Descripción: banco comercial (clientes, cuentas, transacciones, préstamos y tarjetas)

CREATE TABLE agencias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL COMMENT 'Nombre de la agencia',
    ciudad VARCHAR(60) NOT NULL COMMENT 'Ciudad',
    fecha_apertura DATE NOT NULL COMMENT 'Fecha de apertura'
) COMMENT='Agencias bancarias';

CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre completo',
    dpi VARCHAR(13) NOT NULL UNIQUE COMMENT 'Documento personal de identificación',
    fecha_nacimiento DATE COMMENT 'Fecha de nacimiento',
    ciudad VARCHAR(60) COMMENT 'Ciudad de residencia',
    ingreso_mensual DECIMAL(10,2) COMMENT 'Ingreso mensual declarado en quetzales'
) COMMENT='Clientes del banco';

CREATE TABLE cuentas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL COMMENT 'Titular',
    agencia_id INT NOT NULL COMMENT 'Agencia donde se abrió',
    tipo ENUM('Ahorro','Monetaria','Plazo fijo') NOT NULL COMMENT 'Tipo de cuenta',
    moneda ENUM('GTQ','USD') NOT NULL DEFAULT 'GTQ' COMMENT 'Moneda de la cuenta',
    saldo DECIMAL(12,2) NOT NULL DEFAULT 0 COMMENT 'Saldo actual',
    fecha_apertura DATE NOT NULL COMMENT 'Fecha de apertura',
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (agencia_id) REFERENCES agencias(id)
) COMMENT='Cuentas bancarias';

CREATE TABLE transacciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cuenta_id INT NOT NULL COMMENT 'Cuenta afectada',
    tipo ENUM('Depósito','Retiro','Transferencia') NOT NULL COMMENT 'Tipo de movimiento',
    monto DECIMAL(12,2) NOT NULL COMMENT 'Monto del movimiento',
    fecha_hora DATETIME NOT NULL COMMENT 'Fecha y hora del movimiento',
    FOREIGN KEY (cuenta_id) REFERENCES cuentas(id)
) COMMENT='Movimientos de las cuentas';

CREATE TABLE prestamos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL COMMENT 'Cliente deudor',
    monto DECIMAL(12,2) NOT NULL COMMENT 'Monto otorgado',
    tasa_anual DECIMAL(5,2) NOT NULL COMMENT 'Tasa de interés anual (%)',
    plazo_meses INT NOT NULL COMMENT 'Plazo en meses',
    fecha_otorgado DATE NOT NULL COMMENT 'Fecha de desembolso',
    estado ENUM('Vigente','Pagado','En mora') NOT NULL COMMENT 'Estado del préstamo',
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
) COMMENT='Préstamos otorgados';

CREATE TABLE tarjetas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL COMMENT 'Titular',
    marca ENUM('Visa','Mastercard','Amex') NOT NULL COMMENT 'Marca',
    limite DECIMAL(10,2) NOT NULL COMMENT 'Límite de crédito',
    fecha_vencimiento DATE NOT NULL COMMENT 'Fecha de vencimiento',
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
) COMMENT='Tarjetas de crédito';
