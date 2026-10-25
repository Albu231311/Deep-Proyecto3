-- Esquema propio: biblioteca
-- Descripción: red de bibliotecas municipales (catálogo, socios, préstamos y multas)

CREATE TABLE autores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre del autor',
    pais VARCHAR(50) COMMENT 'País de origen',
    anio_nacimiento INT COMMENT 'Año de nacimiento'
) COMMENT='Autores de los libros';

CREATE TABLE libros (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(150) NOT NULL COMMENT 'Título del libro',
    autor_id INT NOT NULL COMMENT 'Autor principal',
    genero ENUM('Novela','Ciencia','Historia','Infantil','Poesía','Tecnología') NOT NULL COMMENT 'Género literario',
    anio_publicacion INT COMMENT 'Año de publicación',
    paginas INT COMMENT 'Número de páginas',
    FOREIGN KEY (autor_id) REFERENCES autores(id)
) COMMENT='Títulos del catálogo';

CREATE TABLE sedes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL COMMENT 'Nombre de la sede',
    ciudad VARCHAR(60) NOT NULL COMMENT 'Ciudad donde está la sede'
) COMMENT='Sedes de la red de bibliotecas';

CREATE TABLE ejemplares (
    id INT AUTO_INCREMENT PRIMARY KEY,
    libro_id INT NOT NULL COMMENT 'Libro al que corresponde',
    sede_id INT NOT NULL COMMENT 'Sede donde se guarda',
    estado ENUM('Disponible','Prestado','Dañado','Perdido') DEFAULT 'Disponible' COMMENT 'Estado físico y de circulación',
    FOREIGN KEY (libro_id) REFERENCES libros(id),
    FOREIGN KEY (sede_id) REFERENCES sedes(id)
) COMMENT='Copias físicas de cada libro';

CREATE TABLE socios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre del socio',
    fecha_nacimiento DATE COMMENT 'Fecha de nacimiento',
    fecha_afiliacion DATE NOT NULL COMMENT 'Fecha en que se afilió',
    tipo ENUM('Estudiante','General','Jubilado') NOT NULL COMMENT 'Tipo de membresía'
) COMMENT='Socios de la biblioteca';

CREATE TABLE prestamos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ejemplar_id INT NOT NULL COMMENT 'Ejemplar prestado',
    socio_id INT NOT NULL COMMENT 'Socio que lo pidió',
    fecha_prestamo DATE NOT NULL COMMENT 'Fecha del préstamo',
    fecha_limite DATE NOT NULL COMMENT 'Fecha límite de devolución',
    fecha_devolucion DATE COMMENT 'Fecha real de devolución (NULL si no se ha devuelto)',
    FOREIGN KEY (ejemplar_id) REFERENCES ejemplares(id),
    FOREIGN KEY (socio_id) REFERENCES socios(id)
) COMMENT='Préstamos de ejemplares';

CREATE TABLE multas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prestamo_id INT NOT NULL COMMENT 'Préstamo que generó la multa',
    monto DECIMAL(8,2) NOT NULL COMMENT 'Monto en quetzales',
    pagada BOOLEAN DEFAULT FALSE COMMENT 'Si ya se pagó',
    FOREIGN KEY (prestamo_id) REFERENCES prestamos(id)
) COMMENT='Multas por devolución tardía';
