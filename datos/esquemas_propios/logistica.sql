-- Esquema propio: logistica
-- Descripción: empresa de distribución (nombres en inglés abreviados)

CREATE TABLE wh (
    wh_id INT AUTO_INCREMENT PRIMARY KEY,
    wh_name VARCHAR(80) NOT NULL COMMENT 'Warehouse name',
    city VARCHAR(60) NOT NULL COMMENT 'City',
    cap_m3 INT NOT NULL COMMENT 'Storage capacity in cubic meters'
) COMMENT='Warehouses';

CREATE TABLE prod (
    prod_id INT AUTO_INCREMENT PRIMARY KEY,
    sku VARCHAR(20) NOT NULL UNIQUE COMMENT 'Stock keeping unit',
    descr VARCHAR(120) NOT NULL COMMENT 'Product description',
    cat ENUM('ELEC','FOOD','TEXT','TOOL') NOT NULL COMMENT 'Category code',
    unit_cost DECIMAL(10,2) NOT NULL COMMENT 'Unit cost in USD',
    wt_kg DECIMAL(6,2) COMMENT 'Unit weight in kg'
) COMMENT='Products';

CREATE TABLE inv (
    wh_id INT NOT NULL COMMENT 'Warehouse',
    prod_id INT NOT NULL COMMENT 'Product',
    qty INT NOT NULL COMMENT 'Units on hand',
    upd_at DATETIME NOT NULL COMMENT 'Last update',
    PRIMARY KEY (wh_id, prod_id),
    FOREIGN KEY (wh_id) REFERENCES wh(wh_id),
    FOREIGN KEY (prod_id) REFERENCES prod(prod_id)
) COMMENT='Inventory per warehouse';

CREATE TABLE drv (
    drv_id INT AUTO_INCREMENT PRIMARY KEY,
    drv_name VARCHAR(100) NOT NULL COMMENT 'Driver name',
    lic_exp DATE NOT NULL COMMENT 'Driver license expiration date',
    hired DATE NOT NULL COMMENT 'Hire date'
) COMMENT='Drivers';

CREATE TABLE veh (
    veh_id INT AUTO_INCREMENT PRIMARY KEY,
    plate VARCHAR(10) NOT NULL UNIQUE COMMENT 'License plate',
    vtype ENUM('Van','Truck','Motorbike') NOT NULL COMMENT 'Vehicle type',
    max_kg INT NOT NULL COMMENT 'Maximum load in kg'
) COMMENT='Vehicles';

CREATE TABLE shp (
    shp_id INT AUTO_INCREMENT PRIMARY KEY,
    wh_id INT NOT NULL COMMENT 'Origin warehouse',
    drv_id INT NOT NULL COMMENT 'Driver',
    veh_id INT NOT NULL COMMENT 'Vehicle',
    dest_city VARCHAR(60) NOT NULL COMMENT 'Destination city',
    shp_dt DATETIME NOT NULL COMMENT 'Departure date and time',
    dlv_dt DATETIME COMMENT 'Delivery date and time (NULL if in transit)',
    st ENUM('P','T','D','X') NOT NULL COMMENT 'Status: P=pending, T=in transit, D=delivered, X=cancelled',
    FOREIGN KEY (wh_id) REFERENCES wh(wh_id),
    FOREIGN KEY (drv_id) REFERENCES drv(drv_id),
    FOREIGN KEY (veh_id) REFERENCES veh(veh_id)
) COMMENT='Shipments';

CREATE TABLE shp_ln (
    shp_id INT NOT NULL COMMENT 'Shipment',
    prod_id INT NOT NULL COMMENT 'Product shipped',
    qty INT NOT NULL COMMENT 'Units shipped',
    PRIMARY KEY (shp_id, prod_id),
    FOREIGN KEY (shp_id) REFERENCES shp(shp_id),
    FOREIGN KEY (prod_id) REFERENCES prod(prod_id)
) COMMENT='Lines of each shipment';
