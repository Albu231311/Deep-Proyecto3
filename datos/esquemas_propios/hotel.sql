-- Esquema propio: hotel
-- Descripción: cadena hotelera (nombres en inglés)

CREATE TABLE hotels (
    hotel_id INT AUTO_INCREMENT PRIMARY KEY,
    hotel_name VARCHAR(100) NOT NULL COMMENT 'Hotel name',
    city VARCHAR(60) NOT NULL COMMENT 'City',
    stars TINYINT NOT NULL COMMENT 'Star rating (1-5)'
) COMMENT='Hotels of the chain';

CREATE TABLE rooms (
    room_id INT AUTO_INCREMENT PRIMARY KEY,
    hotel_id INT NOT NULL COMMENT 'Hotel',
    room_number VARCHAR(10) NOT NULL COMMENT 'Room number',
    room_type ENUM('Single','Double','Suite') NOT NULL COMMENT 'Room type',
    nightly_rate DECIMAL(8,2) NOT NULL COMMENT 'Price per night in USD',
    FOREIGN KEY (hotel_id) REFERENCES hotels(hotel_id)
) COMMENT='Rooms';

CREATE TABLE guests (
    guest_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL COMMENT 'Guest name',
    email VARCHAR(120) NOT NULL UNIQUE COMMENT 'Email',
    country VARCHAR(60) COMMENT 'Country of residence',
    vip BOOLEAN DEFAULT FALSE COMMENT 'VIP guest'
) COMMENT='Guests';

CREATE TABLE reservations (
    reservation_id INT AUTO_INCREMENT PRIMARY KEY,
    guest_id INT NOT NULL COMMENT 'Guest',
    room_id INT NOT NULL COMMENT 'Room',
    check_in DATE NOT NULL COMMENT 'Check-in date',
    check_out DATE NOT NULL COMMENT 'Check-out date',
    status ENUM('Booked','CheckedIn','Completed','Cancelled') NOT NULL COMMENT 'Reservation status',
    FOREIGN KEY (guest_id) REFERENCES guests(guest_id),
    FOREIGN KEY (room_id) REFERENCES rooms(room_id)
) COMMENT='Room reservations';

CREATE TABLE services (
    service_id INT AUTO_INCREMENT PRIMARY KEY,
    service_name VARCHAR(80) NOT NULL COMMENT 'Service name (spa, laundry, minibar...)',
    category ENUM('Food','Spa','Laundry','Transport') NOT NULL COMMENT 'Service category',
    price DECIMAL(8,2) NOT NULL COMMENT 'Unit price in USD'
) COMMENT='Extra services';

CREATE TABLE service_charges (
    charge_id INT AUTO_INCREMENT PRIMARY KEY,
    reservation_id INT NOT NULL COMMENT 'Reservation charged',
    service_id INT NOT NULL COMMENT 'Service consumed',
    quantity INT NOT NULL COMMENT 'Units',
    charged_at DATETIME NOT NULL COMMENT 'When it was charged',
    FOREIGN KEY (reservation_id) REFERENCES reservations(reservation_id),
    FOREIGN KEY (service_id) REFERENCES services(service_id)
) COMMENT='Services charged to each reservation';

CREATE TABLE reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    reservation_id INT NOT NULL COMMENT 'Reviewed stay',
    rating TINYINT NOT NULL COMMENT 'Score from 1 to 5',
    review_date DATE NOT NULL COMMENT 'Review date',
    FOREIGN KEY (reservation_id) REFERENCES reservations(reservation_id)
) COMMENT='Guest reviews';
