-- Esquema propio: rrhh
-- Descripción: recursos humanos de una empresa (nombres abreviados)

CREATE TABLE dpto (
    id_dpto INT AUTO_INCREMENT PRIMARY KEY,
    nom_dpto VARCHAR(80) NOT NULL COMMENT 'Nombre del departamento',
    presup DECIMAL(12,2) COMMENT 'Presupuesto anual en quetzales'
) COMMENT='Departamentos de la empresa';

CREATE TABLE pst (
    id_pst INT AUTO_INCREMENT PRIMARY KEY,
    nom_pst VARCHAR(80) NOT NULL COMMENT 'Nombre del puesto',
    sal_min DECIMAL(10,2) NOT NULL COMMENT 'Salario mínimo del puesto',
    sal_max DECIMAL(10,2) NOT NULL COMMENT 'Salario máximo del puesto'
) COMMENT='Puestos de trabajo';

CREATE TABLE emp (
    id_emp INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(60) NOT NULL COMMENT 'Nombre',
    ape VARCHAR(60) NOT NULL COMMENT 'Apellido',
    f_nac DATE COMMENT 'Fecha de nacimiento',
    f_ing DATE NOT NULL COMMENT 'Fecha de ingreso a la empresa',
    id_dpto INT NOT NULL COMMENT 'Departamento',
    id_pst INT NOT NULL COMMENT 'Puesto',
    id_jefe INT COMMENT 'Jefe directo (otro empleado)',
    sal DECIMAL(10,2) NOT NULL COMMENT 'Salario mensual en quetzales',
    est ENUM('A','I','S') NOT NULL DEFAULT 'A' COMMENT 'Estado: A=activo, I=inactivo, S=suspendido',
    FOREIGN KEY (id_dpto) REFERENCES dpto(id_dpto),
    FOREIGN KEY (id_pst) REFERENCES pst(id_pst),
    FOREIGN KEY (id_jefe) REFERENCES emp(id_emp)
) COMMENT='Empleados';

CREATE TABLE nom_pago (
    id_pago INT AUTO_INCREMENT PRIMARY KEY,
    id_emp INT NOT NULL COMMENT 'Empleado',
    f_pago DATE NOT NULL COMMENT 'Fecha de pago',
    sal_bruto DECIMAL(10,2) NOT NULL COMMENT 'Salario bruto del periodo',
    deduc DECIMAL(10,2) NOT NULL COMMENT 'Deducciones (IGSS, ISR)',
    bono DECIMAL(10,2) DEFAULT 0 COMMENT 'Bonificación',
    FOREIGN KEY (id_emp) REFERENCES emp(id_emp)
) COMMENT='Pagos de nómina';

CREATE TABLE asis (
    id_asis INT AUTO_INCREMENT PRIMARY KEY,
    id_emp INT NOT NULL COMMENT 'Empleado',
    fecha DATE NOT NULL COMMENT 'Día laborado',
    h_ent TIME NOT NULL COMMENT 'Hora de entrada',
    h_sal TIME COMMENT 'Hora de salida',
    FOREIGN KEY (id_emp) REFERENCES emp(id_emp)
) COMMENT='Registro de asistencia';

CREATE TABLE vac (
    id_vac INT AUTO_INCREMENT PRIMARY KEY,
    id_emp INT NOT NULL COMMENT 'Empleado',
    f_ini DATE NOT NULL COMMENT 'Inicio de vacaciones',
    f_fin DATE NOT NULL COMMENT 'Fin de vacaciones',
    aprob BOOLEAN DEFAULT FALSE COMMENT 'Si fueron aprobadas',
    FOREIGN KEY (id_emp) REFERENCES emp(id_emp)
) COMMENT='Solicitudes de vacaciones';
