CREATE DATABASE IF NOT EXISTS hotel_website;
USE hotel_website;

-- 1. Guests Table
CREATE TABLE IF NOT EXISTS Guests (
    guest_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    contact_number VARCHAR(15),
    email VARCHAR(100),
    address VARCHAR(255),
    dob DATE
);

-- 2. Rooms Table
CREATE TABLE IF NOT EXISTS Rooms (
    room_id INT AUTO_INCREMENT PRIMARY KEY,
    room_number INT UNIQUE,
    room_type VARCHAR(20),
    room_status VARCHAR(15), -- Available, Booked, Maintenance
    price_per_night DECIMAL(10, 2)
);

-- 3. Bookings Table
CREATE TABLE IF NOT EXISTS Bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    guest_id INT,
    room_id INT,
    check_in_date DATE,
    check_out_date DATE,
    booking_status VARCHAR(20),
    FOREIGN KEY (guest_id) REFERENCES Guests(guest_id),
    FOREIGN KEY (room_id) REFERENCES Rooms(room_id)
);

-- 4. Payments Table
CREATE TABLE IF NOT EXISTS Payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT,
    amount DECIMAL(10, 2),
    payment_date DATE,
    payment_method VARCHAR(20),
    FOREIGN KEY (booking_id) REFERENCES Bookings(booking_id)
);

-- Sample data (optional)
INSERT INTO Rooms (room_number, room_type, room_status, price_per_night)
VALUES (101, 'Single', 'Available', 5000),
       (102, 'Double', 'Available', 8000),
       (103, 'Suite', 'Available', 15000);
