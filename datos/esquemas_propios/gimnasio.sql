-- Esquema propio: gimnasio
-- Descripción: cadena de gimnasios (membresías, clases, instructores y asistencias)

CREATE TABLE planes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(60) NOT NULL COMMENT 'Nombre del plan',
    precio_mensual DECIMAL(8,2) NOT NULL COMMENT 'Precio mensual en quetzales',
    acceso_clases BOOLEAN DEFAULT TRUE COMMENT 'Si incluye clases grupales'
) COMMENT='Planes de membresía';

CREATE TABLE miembros (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre del miembro',
    genero ENUM('M','F') COMMENT 'Género',
    fecha_nacimiento DATE COMMENT 'Fecha de nacimiento',
    ciudad VARCHAR(60) COMMENT 'Ciudad'
) COMMENT='Miembros del gimnasio';

CREATE TABLE membresias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    miembro_id INT NOT NULL COMMENT 'Miembro',
    plan_id INT NOT NULL COMMENT 'Plan contratado',
    fecha_inicio DATE NOT NULL COMMENT 'Inicio de la membresía',
    fecha_fin DATE NOT NULL COMMENT 'Fin de la membresía',
    estado ENUM('Activa','Vencida','Congelada') NOT NULL COMMENT 'Estado',
    FOREIGN KEY (miembro_id) REFERENCES miembros(id),
    FOREIGN KEY (plan_id) REFERENCES planes(id)
) COMMENT='Membresías contratadas';

CREATE TABLE instructores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre del instructor',
    especialidad ENUM('Yoga','Spinning','Crossfit','Pilates','Zumba') NOT NULL COMMENT 'Especialidad',
    tarifa_hora DECIMAL(8,2) NOT NULL COMMENT 'Pago por hora en quetzales'
) COMMENT='Instructores';

CREATE TABLE clases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    instructor_id INT NOT NULL COMMENT 'Instructor que la imparte',
    tipo ENUM('Yoga','Spinning','Crossfit','Pilates','Zumba') NOT NULL COMMENT 'Tipo de clase',
    inicio DATETIME NOT NULL COMMENT 'Fecha y hora de inicio',
    duracion_min INT NOT NULL COMMENT 'Duración en minutos',
    cupo INT NOT NULL COMMENT 'Cupo máximo',
    FOREIGN KEY (instructor_id) REFERENCES instructores(id)
) COMMENT='Clases grupales programadas';

CREATE TABLE asistencias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    clase_id INT NOT NULL COMMENT 'Clase',
    miembro_id INT NOT NULL COMMENT 'Miembro que asistió',
    calificacion TINYINT COMMENT 'Calificación de la clase (1-5)',
    FOREIGN KEY (clase_id) REFERENCES clases(id),
    FOREIGN KEY (miembro_id) REFERENCES miembros(id)
) COMMENT='Asistencia a clases';
