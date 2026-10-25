-- Esquema propio: tienda_online
-- Descripción: comercio electrónico (clientes, catálogo, pedidos, pagos y envíos)

CREATE TABLE categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL COMMENT 'Nombre de la categoría',
    descripcion VARCHAR(200) COMMENT 'Descripción corta'
) COMMENT='Categorías del catálogo';

CREATE TABLE productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL COMMENT 'Nombre del producto',
    categoria_id INT NOT NULL COMMENT 'Categoría del producto',
    precio DECIMAL(10,2) NOT NULL COMMENT 'Precio de venta en quetzales',
    stock INT NOT NULL DEFAULT 0 COMMENT 'Unidades en bodega',
    fecha_alta DATE NOT NULL COMMENT 'Fecha en que se agregó al catálogo',
    activo BOOLEAN DEFAULT TRUE COMMENT 'Si se puede comprar',
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
) COMMENT='Productos a la venta';

CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre completo',
    email VARCHAR(120) NOT NULL UNIQUE COMMENT 'Correo electrónico',
    ciudad VARCHAR(60) COMMENT 'Ciudad de residencia',
    fecha_registro DATE NOT NULL COMMENT 'Fecha de registro en la tienda',
    segmento ENUM('Regular','Premium','Mayorista') DEFAULT 'Regular' COMMENT 'Segmento comercial'
) COMMENT='Clientes registrados';

CREATE TABLE pedidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL COMMENT 'Cliente que hizo el pedido',
    fecha DATETIME NOT NULL COMMENT 'Fecha y hora del pedido',
    estado ENUM('Pendiente','Pagado','Enviado','Entregado','Cancelado') NOT NULL COMMENT 'Estado del pedido',
    total DECIMAL(10,2) NOT NULL COMMENT 'Monto total en quetzales',
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
) COMMENT='Pedidos realizados';

CREATE TABLE detalle_pedido (
    pedido_id INT NOT NULL COMMENT 'Pedido',
    producto_id INT NOT NULL COMMENT 'Producto comprado',
    cantidad INT NOT NULL COMMENT 'Unidades compradas',
    precio_unitario DECIMAL(10,2) NOT NULL COMMENT 'Precio cobrado por unidad',
    PRIMARY KEY (pedido_id, producto_id),
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
    FOREIGN KEY (producto_id) REFERENCES productos(id)
) COMMENT='Líneas de cada pedido';

CREATE TABLE pagos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pedido_id INT NOT NULL COMMENT 'Pedido pagado',
    metodo ENUM('Tarjeta','Transferencia','Efectivo') NOT NULL COMMENT 'Método de pago',
    monto DECIMAL(10,2) NOT NULL COMMENT 'Monto pagado en quetzales',
    fecha_pago DATETIME NOT NULL COMMENT 'Fecha y hora del pago',
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
) COMMENT='Pagos recibidos';

CREATE TABLE envios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pedido_id INT NOT NULL COMMENT 'Pedido enviado',
    transportista VARCHAR(60) NOT NULL COMMENT 'Empresa de transporte',
    fecha_envio DATE NOT NULL COMMENT 'Fecha de salida',
    fecha_entrega DATE COMMENT 'Fecha de entrega (NULL si no ha llegado)',
    costo_envio DECIMAL(8,2) NOT NULL COMMENT 'Costo del envío en quetzales',
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
) COMMENT='Envíos de pedidos';
