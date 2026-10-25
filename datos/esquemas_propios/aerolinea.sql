-- Esquema propio: aerolinea
-- Descripción: aerolínea regional (nombres en inglés)

CREATE TABLE airports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code CHAR(3) NOT NULL UNIQUE COMMENT 'IATA code',
    name VARCHAR(100) NOT NULL COMMENT 'Airport name',
    city VARCHAR(60) NOT NULL COMMENT 'City served',
    country VARCHAR(60) NOT NULL COMMENT 'Country'
) COMMENT='Airports served by the airline';

CREATE TABLE aircraft (
    id INT AUTO_INCREMENT PRIMARY KEY,
    model VARCHAR(60) NOT NULL COMMENT 'Aircraft model',
    seats INT NOT NULL COMMENT 'Seating capacity',
    year_built INT COMMENT 'Year of manufacture'
) COMMENT='Fleet';

CREATE TABLE flights (
    id INT AUTO_INCREMENT PRIMARY KEY,
    flight_no VARCHAR(10) NOT NULL COMMENT 'Flight number',
    origin_id INT NOT NULL COMMENT 'Departure airport',
    dest_id INT NOT NULL COMMENT 'Arrival airport',
    aircraft_id INT NOT NULL COMMENT 'Aircraft assigned',
    dep_time DATETIME NOT NULL COMMENT 'Scheduled departure',
    arr_time DATETIME NOT NULL COMMENT 'Scheduled arrival',
    status ENUM('Scheduled','Departed','Arrived','Delayed','Cancelled') NOT NULL COMMENT 'Flight status',
    base_fare DECIMAL(8,2) NOT NULL COMMENT 'Base fare in USD',
    FOREIGN KEY (origin_id) REFERENCES airports(id),
    FOREIGN KEY (dest_id) REFERENCES airports(id),
    FOREIGN KEY (aircraft_id) REFERENCES aircraft(id)
) COMMENT='Scheduled flights';

CREATE TABLE passengers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT 'Full name',
    birth_date DATE COMMENT 'Date of birth',
    country VARCHAR(60) COMMENT 'Nationality',
    frequent_flyer BOOLEAN DEFAULT FALSE COMMENT 'Member of the loyalty program'
) COMMENT='Passengers';

CREATE TABLE bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    flight_id INT NOT NULL COMMENT 'Booked flight',
    passenger_id INT NOT NULL COMMENT 'Passenger',
    booked_at DATETIME NOT NULL COMMENT 'When the booking was made',
    class ENUM('Economy','Business','First') NOT NULL COMMENT 'Cabin class',
    price DECIMAL(8,2) NOT NULL COMMENT 'Price paid in USD',
    FOREIGN KEY (flight_id) REFERENCES flights(id),
    FOREIGN KEY (passenger_id) REFERENCES passengers(id)
) COMMENT='Ticket bookings';

CREATE TABLE crew (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT 'Crew member name',
    role ENUM('Pilot','Copilot','Attendant') NOT NULL COMMENT 'Role on board',
    hire_date DATE NOT NULL COMMENT 'Hire date'
) COMMENT='Crew members';

CREATE TABLE flight_crew (
    flight_id INT NOT NULL COMMENT 'Flight',
    crew_id INT NOT NULL COMMENT 'Crew member',
    PRIMARY KEY (flight_id, crew_id),
    FOREIGN KEY (flight_id) REFERENCES flights(id),
    FOREIGN KEY (crew_id) REFERENCES crew(id)
) COMMENT='Crew assigned to each flight';
