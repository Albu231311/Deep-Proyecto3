
-- Schema: sistema_academico
-- Descripción: Sistema de gestión académica universitaria
-- Esquema de VALIDACIÓN — NO debe aparecer en entrenamiento

CREATE TABLE departamentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre del departamento académico',
    edificio VARCHAR(50) COMMENT 'Edificio donde se ubica',
    telefono VARCHAR(20) COMMENT 'Teléfono de contacto',
    presupuesto_anual DECIMAL(12,2) COMMENT 'Presupuesto anual en USD'
) COMMENT='Departamentos académicos de la universidad';

CREATE TABLE profesores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre completo del profesor',
    email VARCHAR(150) COMMENT 'Correo institucional',
    departamento_id INT NOT NULL COMMENT 'Departamento al que pertenece',
    fecha_contratacion DATE NOT NULL COMMENT 'Fecha de contratación',
    salario DECIMAL(10,2) COMMENT 'Salario mensual en USD',
    grado_academico ENUM('Licenciatura','Maestría','Doctorado') DEFAULT 'Maestría' COMMENT 'Máximo grado académico',
    FOREIGN KEY (departamento_id) REFERENCES departamentos(id)
) COMMENT='Profesores de la universidad';

CREATE TABLE estudiantes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre completo del estudiante',
    email VARCHAR(150) COMMENT 'Correo institucional',
    fecha_nacimiento DATE COMMENT 'Fecha de nacimiento',
    semestre_actual INT DEFAULT 1 COMMENT 'Semestre que cursa actualmente',
    carrera VARCHAR(100) COMMENT 'Nombre de la carrera',
    promedio_acumulado DECIMAL(4,2) COMMENT 'Promedio acumulado (0-100)',
    estado ENUM('Activo','Inactivo','Graduado','Suspendido') DEFAULT 'Activo' COMMENT 'Estado del estudiante',
    fecha_ingreso DATE COMMENT 'Fecha de primer ingreso'
) COMMENT='Estudiantes matriculados';

CREATE TABLE cursos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL COMMENT 'Código del curso, ej: CC2001',
    nombre VARCHAR(150) NOT NULL COMMENT 'Nombre del curso',
    creditos INT NOT NULL DEFAULT 3 COMMENT 'Número de créditos',
    departamento_id INT NOT NULL COMMENT 'Departamento que ofrece el curso',
    profesor_id INT COMMENT 'Profesor asignado',
    semestre VARCHAR(10) COMMENT 'Semestre en que se imparte, ej: 2024-1',
    cupo_maximo INT DEFAULT 30 COMMENT 'Capacidad máxima de estudiantes',
    FOREIGN KEY (departamento_id) REFERENCES departamentos(id),
    FOREIGN KEY (profesor_id) REFERENCES profesores(id)
) COMMENT='Cursos ofrecidos por semestre';

CREATE TABLE inscripciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    estudiante_id INT NOT NULL COMMENT 'Estudiante inscrito',
    curso_id INT NOT NULL COMMENT 'Curso al que se inscribió',
    fecha_inscripcion DATE NOT NULL COMMENT 'Fecha de inscripción',
    calificacion DECIMAL(5,2) COMMENT 'Calificación final (0-100), NULL si no ha sido calificado',
    estado ENUM('Inscrito','Aprobado','Reprobado','Retirado') DEFAULT 'Inscrito' COMMENT 'Estado de la inscripción',
    FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id),
    FOREIGN KEY (curso_id) REFERENCES cursos(id)
) COMMENT='Inscripciones de estudiantes a cursos';


-- Datos de prueba

INSERT INTO departamentos (nombre, edificio, telefono, presupuesto_anual) VALUES
('Ciencias de la Computación', 'T-3', '2418-8000', 150000.00),
('Matemáticas', 'T-3', '2418-8010', 120000.00),
('Ingeniería Industrial', 'T-5', '2418-8020', 180000.00),
('Física', 'T-4', '2418-8030', 95000.00),
('Química', 'T-4', '2418-8040', 110000.00);

INSERT INTO profesores (nombre, email, departamento_id, fecha_contratacion, salario, grado_academico) VALUES
('Dr. Roberto Figueroa', 'rfigueroa@uvg.edu.gt', 1, '2015-01-15', 3500.00, 'Doctorado'),
('Dra. Lucía Méndez', 'lmendez@uvg.edu.gt', 1, '2018-06-01', 3200.00, 'Doctorado'),
('Ing. Marco Castillo', 'mcastillo@uvg.edu.gt', 3, '2020-01-10', 2800.00, 'Maestría'),
('Lic. Ana Ramírez', 'aramirez@uvg.edu.gt', 2, '2019-03-20', 2500.00, 'Maestría'),
('Dr. Pedro Solís', 'psolis@uvg.edu.gt', 4, '2012-08-15', 3800.00, 'Doctorado'),
('Dra. Carmen Ochoa', 'cochoa@uvg.edu.gt', 2, '2016-02-28', 3100.00, 'Doctorado'),
('Ing. José Herrera', 'jherrera@uvg.edu.gt', 3, '2021-07-01', 2600.00, 'Maestría'),
('Dr. Fernando Paz', 'fpaz@uvg.edu.gt', 5, '2014-11-10', 3400.00, 'Doctorado');

INSERT INTO estudiantes (nombre, email, fecha_nacimiento, semestre_actual, carrera, promedio_acumulado, estado, fecha_ingreso) VALUES
('Carlos García', 'cgarcia@uvg.edu.gt', '2003-05-12', 6, 'Ciencias de la Computación', 82.50, 'Activo', '2022-01-15'),
('María López', 'mlopez@uvg.edu.gt', '2002-11-03', 8, 'Ciencias de la Computación', 91.20, 'Activo', '2021-01-15'),
('Juan Pérez', 'jperez@uvg.edu.gt', '2004-02-28', 4, 'Ingeniería Industrial', 75.80, 'Activo', '2023-01-15'),
('Ana Martínez', 'amartinez@uvg.edu.gt', '2003-08-15', 6, 'Matemáticas', 88.90, 'Activo', '2022-01-15'),
('Diego Morales', 'dmorales@uvg.edu.gt', '2001-12-20', 10, 'Ciencias de la Computación', 94.30, 'Activo', '2020-01-15'),
('Sofía Hernández', 'shernandez@uvg.edu.gt', '2003-04-10', 6, 'Ingeniería Industrial', 79.60, 'Activo', '2022-01-15'),
('Luis Ramírez', 'lramirez@uvg.edu.gt', '2004-07-22', 4, 'Física', 70.40, 'Activo', '2023-01-15'),
('Valentina Cruz', 'vcruz@uvg.edu.gt', '2002-09-05', 8, 'Química', 86.70, 'Activo', '2021-01-15'),
('Roberto Sánchez', 'rsanchez@uvg.edu.gt', '2003-01-18', 6, 'Ciencias de la Computación', 67.90, 'Suspendido', '2022-01-15'),
('Isabela Torres', 'itorres@uvg.edu.gt', '2001-06-30', 10, 'Matemáticas', 92.10, 'Graduado', '2020-01-15'),
('Andrés Flores', 'aflores@uvg.edu.gt', '2004-03-14', 4, 'Ingeniería Industrial', 77.30, 'Activo', '2023-01-15'),
('Camila Reyes', 'creyes@uvg.edu.gt', '2003-10-25', 6, 'Ciencias de la Computación', 85.40, 'Activo', '2022-01-15'),
('Emilio Vargas', 'evargas@uvg.edu.gt', '2002-07-08', 8, 'Física', 73.60, 'Inactivo', '2021-01-15'),
('Gabriela Ruiz', 'gruiz@uvg.edu.gt', '2004-12-01', 2, 'Matemáticas', 90.80, 'Activo', '2024-01-15'),
('Fernando Díaz', 'fdiaz@uvg.edu.gt', '2003-05-20', 6, 'Química', 81.20, 'Activo', '2022-01-15');

INSERT INTO cursos (codigo, nombre, creditos, departamento_id, profesor_id, semestre, cupo_maximo) VALUES
('CC2001', 'Algoritmos y Estructuras de Datos', 4, 1, 1, '2024-2', 35),
('CC3010', 'Bases de Datos', 4, 1, 2, '2024-2', 30),
('CC4050', 'Inteligencia Artificial', 4, 1, 1, '2024-2', 25),
('MA1001', 'Cálculo 1', 5, 2, 4, '2024-2', 40),
('MA2003', 'Álgebra Lineal', 4, 2, 6, '2024-2', 35),
('II2010', 'Investigación de Operaciones', 4, 3, 3, '2024-2', 30),
('II3020', 'Control de Calidad', 3, 3, 7, '2024-2', 30),
('FS1001', 'Física 1', 5, 4, 5, '2024-2', 45),
('QM1001', 'Química General', 5, 5, 8, '2024-2', 40),
('CC2005', 'Programación Orientada a Objetos', 3, 1, 2, '2024-2', 35),
('MA3005', 'Ecuaciones Diferenciales', 4, 2, 4, '2024-1', 30),
('II1005', 'Introducción a la Ingeniería Industrial', 3, 3, 3, '2024-1', 40);

INSERT INTO inscripciones (estudiante_id, curso_id, fecha_inscripcion, calificacion, estado) VALUES
-- Carlos García (CC)
(1, 1, '2024-07-15', 78.50, 'Aprobado'),
(1, 2, '2024-07-15', 85.00, 'Aprobado'),
(1, 4, '2024-07-15', 62.30, 'Reprobado'),
-- María López (CC)
(2, 1, '2024-07-15', 95.00, 'Aprobado'),
(2, 3, '2024-07-15', 92.00, 'Aprobado'),
(2, 5, '2024-07-15', 88.50, 'Aprobado'),
-- Juan Pérez (II)
(3, 6, '2024-07-15', 71.00, 'Aprobado'),
(3, 4, '2024-07-15', 68.00, 'Aprobado'),
(3, 7, '2024-07-15', NULL, 'Inscrito'),
-- Ana Martínez (Mat)
(4, 4, '2024-07-15', 96.00, 'Aprobado'),
(4, 5, '2024-07-15', 93.00, 'Aprobado'),
(4, 1, '2024-07-15', 84.00, 'Aprobado'),
-- Diego Morales (CC)
(5, 3, '2024-07-15', 98.00, 'Aprobado'),
(5, 2, '2024-07-15', 97.50, 'Aprobado'),
-- Sofía Hernández (II)
(6, 6, '2024-07-15', 82.00, 'Aprobado'),
(6, 7, '2024-07-15', NULL, 'Inscrito'),
(6, 4, '2024-07-15', 74.50, 'Aprobado'),
-- Luis Ramírez (Fís)
(7, 8, '2024-07-15', 65.00, 'Aprobado'),
(7, 4, '2024-07-15', 58.00, 'Reprobado'),
-- Valentina Cruz (Quím)
(8, 9, '2024-07-15', 91.00, 'Aprobado'),
(8, 4, '2024-07-15', 87.00, 'Aprobado'),
-- Roberto Sánchez (CC, suspendido)
(9, 1, '2024-07-15', 45.00, 'Reprobado'),
(9, 2, '2024-07-15', 52.00, 'Reprobado'),
-- Isabela Torres (Mat, graduada)
(10, 5, '2024-07-15', 97.00, 'Aprobado'),
(10, 11, '2024-01-15', 94.00, 'Aprobado'),
-- Andrés Flores (II)
(11, 6, '2024-07-15', NULL, 'Inscrito'),
(11, 12, '2024-01-15', 80.00, 'Aprobado'),
-- Camila Reyes (CC)
(12, 1, '2024-07-15', 88.00, 'Aprobado'),
(12, 2, '2024-07-15', 90.00, 'Aprobado'),
(12, 10, '2024-07-15', 86.00, 'Aprobado'),
-- Emilio Vargas (Fís, inactivo)
(13, 8, '2024-07-15', 60.00, 'Retirado'),
-- Gabriela Ruiz (Mat)
(14, 4, '2024-07-15', NULL, 'Inscrito'),
(14, 5, '2024-07-15', NULL, 'Inscrito'),
-- Fernando Díaz (Quím)
(15, 9, '2024-07-15', 78.00, 'Aprobado'),
(15, 4, '2024-07-15', 72.00, 'Aprobado');
