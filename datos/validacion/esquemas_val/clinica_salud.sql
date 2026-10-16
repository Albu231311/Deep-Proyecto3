
-- Schema: clinica_salud
-- Descripción: Sistema de gestión de una clínica médica
-- Esquema de VALIDACIÓN — NO debe aparecer en entrenamiento


CREATE TABLE departamentos_med (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre del departamento médico',
    piso INT COMMENT 'Piso del edificio',
    extension VARCHAR(10) COMMENT 'Extensión telefónica'
) COMMENT='Departamentos de la clínica';

CREATE TABLE medicos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre completo del médico',
    especialidad VARCHAR(80) NOT NULL COMMENT 'Especialidad médica',
    departamento_id INT COMMENT 'Departamento al que pertenece',
    fecha_ingreso DATE NOT NULL COMMENT 'Fecha de ingreso a la clínica',
    salario DECIMAL(10,2) COMMENT 'Salario mensual en quetzales',
    activo BOOLEAN DEFAULT TRUE COMMENT 'Si el médico está activo',
    FOREIGN KEY (departamento_id) REFERENCES departamentos_med(id)
) COMMENT='Médicos de la clínica';

CREATE TABLE pacientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre completo del paciente',
    fecha_nac DATE COMMENT 'Fecha de nacimiento',
    genero ENUM('M','F') COMMENT 'Género del paciente',
    telefono VARCHAR(20) COMMENT 'Teléfono de contacto',
    direccion VARCHAR(200) COMMENT 'Dirección de residencia',
    tipo_sangre VARCHAR(5) COMMENT 'Tipo de sangre',
    alergias TEXT COMMENT 'Alergias conocidas'
) COMMENT='Pacientes registrados en la clínica';

CREATE TABLE citas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    paciente_id INT NOT NULL COMMENT 'Paciente que asiste a la cita',
    medico_id INT NOT NULL COMMENT 'Médico que atiende',
    fecha_hora DATETIME NOT NULL COMMENT 'Fecha y hora de la cita',
    motivo VARCHAR(200) COMMENT 'Motivo de la consulta',
    diagnostico TEXT COMMENT 'Diagnóstico emitido',
    estado ENUM('Programada','Completada','Cancelada','No asistió') DEFAULT 'Programada' COMMENT 'Estado de la cita',
    costo DECIMAL(8,2) COMMENT 'Costo de la consulta en quetzales',
    FOREIGN KEY (paciente_id) REFERENCES pacientes(id),
    FOREIGN KEY (medico_id) REFERENCES medicos(id)
) COMMENT='Citas médicas programadas y realizadas';

CREATE TABLE medicamentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre del medicamento',
    principio_activo VARCHAR(100) COMMENT 'Principio activo',
    presentacion VARCHAR(80) COMMENT 'Presentación (tabletas, jarabe, etc.)',
    precio DECIMAL(8,2) NOT NULL COMMENT 'Precio unitario en quetzales',
    stock INT DEFAULT 0 COMMENT 'Unidades disponibles en farmacia',
    requiere_receta BOOLEAN DEFAULT TRUE COMMENT 'Si requiere receta médica'
) COMMENT='Catálogo de medicamentos disponibles';

CREATE TABLE recetas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cita_id INT NOT NULL COMMENT 'Cita en la que se emitió la receta',
    medicamento_id INT NOT NULL COMMENT 'Medicamento recetado',
    dosis VARCHAR(100) COMMENT 'Indicaciones de dosis',
    duracion_dias INT COMMENT 'Duración del tratamiento en días',
    cantidad INT DEFAULT 1 COMMENT 'Cantidad de unidades recetadas',
    FOREIGN KEY (cita_id) REFERENCES citas(id),
    FOREIGN KEY (medicamento_id) REFERENCES medicamentos(id)
) COMMENT='Recetas emitidas en consultas';


-- Datos de prueba


INSERT INTO departamentos_med (nombre, piso, extension) VALUES
('Medicina General', 1, '101'),
('Pediatría', 2, '201'),
('Cardiología', 3, '301'),
('Traumatología', 2, '202'),
('Dermatología', 1, '102'),
('Ginecología', 3, '302');

INSERT INTO medicos (nombre, especialidad, departamento_id, fecha_ingreso, salario, activo) VALUES
('Dr. Alejandro Vásquez', 'Medicina General', 1, '2018-03-15', 18000.00, TRUE),
('Dra. Patricia Morán', 'Pediatría', 2, '2016-08-01', 22000.00, TRUE),
('Dr. Ricardo Estrada', 'Cardiología', 3, '2014-01-20', 28000.00, TRUE),
('Dra. Elena Juárez', 'Traumatología', 4, '2019-05-10', 25000.00, TRUE),
('Dr. Manuel Aguilar', 'Dermatología', 5, '2020-11-01', 19000.00, TRUE),
('Dra. Laura Pineda', 'Ginecología', 6, '2017-02-28', 24000.00, TRUE),
('Dr. Jorge Méndez', 'Medicina General', 1, '2021-09-15', 16000.00, TRUE),
('Dra. Silvia Ramos', 'Pediatría', 2, '2022-01-10', 20000.00, TRUE),
('Dr. Óscar Barrios', 'Cardiología', 3, '2015-06-20', 27000.00, FALSE);

INSERT INTO pacientes (nombre, fecha_nac, genero, telefono, direccion, tipo_sangre, alergias) VALUES
('Pedro Alvarado', '1985-04-12', 'M', '5555-1234', 'Zona 10, Guatemala', 'O+', NULL),
('Rosa Cifuentes', '1990-08-25', 'F', '5555-2345', 'Zona 14, Guatemala', 'A+', 'Penicilina'),
('Miguel Ángel Santos', '1978-12-03', 'M', '5555-3456', 'Zona 1, Mixco', 'B+', NULL),
('Lucía Fernández', '2015-06-18', 'F', '5555-4567', 'Zona 7, Guatemala', 'O-', 'Ibuprofeno'),
('Jorge Castañeda', '1960-02-28', 'M', '5555-5678', 'Zona 11, Guatemala', 'AB+', 'Aspirina, Sulfas'),
('Carmen Villatoro', '1995-10-14', 'F', '5555-6789', 'Zona 5, Guatemala', 'A-', NULL),
('Roberto Mazariegos', '2008-03-22', 'M', '5555-7890', 'Zona 18, Guatemala', 'O+', NULL),
('Daniela Reyes', '1988-07-09', 'F', '5555-8901', 'Zona 4, Guatemala', 'B-', 'Látex'),
('Héctor Solano', '1972-11-30', 'M', '5555-9012', 'Zona 12, Guatemala', 'A+', NULL),
('Martha Godínez', '2000-01-05', 'F', '5555-0123', 'Zona 2, Guatemala', 'O+', NULL),
('Sergio Ponce', '1955-09-17', 'M', '5555-1111', 'Zona 9, Guatemala', 'AB-', 'Penicilina, Mariscos'),
('Claudia Arriaza', '2019-12-01', 'F', '5555-2222', 'Zona 16, Guatemala', 'O+', NULL);

INSERT INTO citas (paciente_id, medico_id, fecha_hora, motivo, diagnostico, estado, costo) VALUES
-- Pedro Alvarado
(1, 1, '2024-09-10 08:30:00', 'Chequeo general', 'Paciente sano, presión normal', 'Completada', 350.00),
(1, 3, '2024-10-05 10:00:00', 'Dolor en el pecho', 'Arritmia leve, seguimiento', 'Completada', 600.00),
-- Rosa Cifuentes
(2, 1, '2024-09-15 09:00:00', 'Dolor de cabeza recurrente', 'Migraña tensional', 'Completada', 350.00),
(2, 5, '2024-09-22 11:00:00', 'Erupción en la piel', 'Dermatitis de contacto', 'Completada', 400.00),
-- Miguel Ángel Santos
(3, 3, '2024-09-20 08:00:00', 'Control cardiovascular', 'Hipertensión controlada', 'Completada', 600.00),
(3, 1, '2024-10-01 14:00:00', 'Revisión de presión', 'Sin cambios', 'Completada', 350.00),
-- Lucía Fernández (menor)
(4, 2, '2024-09-12 10:00:00', 'Fiebre y tos', 'Infección de vías respiratorias', 'Completada', 300.00),
(4, 2, '2024-10-08 09:30:00', 'Control post-tratamiento', 'Recuperada, alta', 'Completada', 300.00),
-- Jorge Castañeda
(5, 3, '2024-09-18 08:30:00', 'Dolor en el pecho al caminar', 'Angina de pecho, requiere cateterismo', 'Completada', 800.00),
(5, 4, '2024-10-10 11:00:00', 'Dolor en rodilla derecha', 'Artrosis de rodilla grado II', 'Completada', 500.00),
-- Carmen Villatoro
(6, 6, '2024-09-25 15:00:00', 'Control ginecológico', 'Sin hallazgos anormales', 'Completada', 450.00),
(6, 1, '2024-10-12 08:00:00', 'Malestar estomacal', NULL, 'Programada', 350.00),
-- Roberto Mazariegos (menor)
(7, 2, '2024-09-28 10:00:00', 'Vacunación', 'Vacuna aplicada sin reacción', 'Completada', 200.00),
-- Daniela Reyes
(8, 5, '2024-10-02 14:30:00', 'Acné severo', 'Acné quístico, tratamiento oral', 'Completada', 400.00),
(8, 6, '2024-10-15 09:00:00', 'Control anual', NULL, 'Programada', 450.00),
-- Héctor Solano
(9, 4, '2024-09-30 08:00:00', 'Fractura en muñeca', 'Fractura de Colles, inmovilización', 'Completada', 700.00),
-- Martha Godínez
(10, 1, '2024-10-03 11:00:00', 'Dolor de garganta', 'Faringitis viral', 'Completada', 350.00),
-- Sergio Ponce
(11, 3, '2024-10-07 08:30:00', 'Arritmia', 'Fibrilación auricular, medicación', 'Completada', 800.00),
(11, 1, '2024-10-14 10:00:00', 'Control general', NULL, 'Cancelada', 0.00),
-- Claudia Arriaza (menor)
(12, 2, '2024-10-09 09:00:00', 'Control pediátrico', 'Desarrollo normal para la edad', 'Completada', 300.00),
-- Citas que no asistieron
(3, 1, '2024-10-15 09:00:00', 'Control de presión', NULL, 'No asistió', 0.00),
(9, 4, '2024-10-20 10:00:00', 'Retiro de yeso', NULL, 'Programada', 300.00);

INSERT INTO medicamentos (nombre, principio_activo, presentacion, precio, stock, requiere_receta) VALUES
('Paracetamol 500mg', 'Paracetamol', 'Caja 20 tabletas', 25.00, 200, FALSE),
('Ibuprofeno 400mg', 'Ibuprofeno', 'Caja 20 tabletas', 35.00, 150, FALSE),
('Amoxicilina 500mg', 'Amoxicilina', 'Caja 21 cápsulas', 65.00, 80, TRUE),
('Losartán 50mg', 'Losartán potásico', 'Caja 30 tabletas', 90.00, 120, TRUE),
('Metoprolol 50mg', 'Metoprolol tartrato', 'Caja 30 tabletas', 75.00, 100, TRUE),
('Isotretinoína 20mg', 'Isotretinoína', 'Caja 30 cápsulas', 350.00, 30, TRUE),
('Warfarina 5mg', 'Warfarina sódica', 'Caja 30 tabletas', 55.00, 60, TRUE),
('Diclofenaco gel', 'Diclofenaco', 'Tubo 60g', 45.00, 90, FALSE),
('Omeprazol 20mg', 'Omeprazol', 'Caja 14 cápsulas', 40.00, 180, FALSE),
('Cetirizina 10mg', 'Cetirizina', 'Caja 10 tabletas', 30.00, 140, FALSE);

INSERT INTO recetas (cita_id, medicamento_id, dosis, duracion_dias, cantidad) VALUES
-- Pedro: arritmia
(2, 5, '1 tableta cada 12 horas', 30, 2),
-- Rosa: migraña
(3, 1, '1 tableta cada 8 horas si hay dolor', 7, 1),
-- Rosa: dermatitis
(4, 10, '1 tableta cada 24 horas', 10, 1),
-- Miguel: hipertensión
(5, 4, '1 tableta cada 24 horas', 90, 3),
-- Lucía: infección respiratoria
(7, 3, '1 cápsula cada 8 horas', 7, 1),
(7, 1, '1 tableta cada 6 horas si hay fiebre', 5, 1),
-- Jorge: angina
(9, 5, '1 tableta cada 12 horas', 30, 2),
(9, 9, '1 cápsula cada 24 horas en ayunas', 30, 1),
-- Jorge: artrosis
(10, 2, '1 tableta cada 8 horas con comida', 14, 1),
(10, 8, 'Aplicar en rodilla 3 veces al día', 14, 1),
-- Daniela: acné
(14, 6, '1 cápsula cada 24 horas con comida', 90, 3),
-- Héctor: fractura
(16, 1, '1 tableta cada 6 horas si hay dolor', 10, 2),
-- Sergio: fibrilación
(18, 7, '1 tableta cada 24 horas', 30, 1),
(18, 5, '1 tableta cada 12 horas', 30, 2),
-- Martha: faringitis
(17, 1, '1 tableta cada 8 horas', 5, 1),
(17, 9, '1 cápsula cada 24 horas', 7, 1);
