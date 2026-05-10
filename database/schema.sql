-- ============================================================
-- Traveloop Database Schema
-- ============================================================

CREATE DATABASE IF NOT EXISTS traveloop;
USE traveloop;

-- Users
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    profile_photo VARCHAR(255) DEFAULT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cities (pre-seeded reference data)
CREATE TABLE IF NOT EXISTS cities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    region VARCHAR(100),
    cost_index DECIMAL(5,2) DEFAULT 1.00,
    popularity INT DEFAULT 0,
    image_url VARCHAR(255) DEFAULT NULL,
    UNIQUE KEY unique_city_country (name, country)
);

-- Activities (linked to cities)
CREATE TABLE IF NOT EXISTS activities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    city_id INT NOT NULL,
    name VARCHAR(150) NOT NULL,
    category VARCHAR(50),
    cost DECIMAL(8,2) DEFAULT 0.00,
    duration_hours DECIMAL(4,1) DEFAULT 1.0,
    description TEXT,
    FOREIGN KEY (city_id) REFERENCES cities(id) ON DELETE CASCADE
);

-- Trips
CREATE TABLE IF NOT EXISTS trips (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    destination VARCHAR(150),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    cover_photo VARCHAR(255) DEFAULT NULL,
    total_budget DECIMAL(10,2) DEFAULT 0.00,
    status ENUM('upcoming','ongoing','completed') DEFAULT 'upcoming',
    is_public BOOLEAN DEFAULT FALSE,
    share_token VARCHAR(100) UNIQUE DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Itinerary Days (one row per day of a trip)
CREATE TABLE IF NOT EXISTS itinerary_days (
    id INT AUTO_INCREMENT PRIMARY KEY,
    trip_id INT NOT NULL,
    day_number INT NOT NULL,
    day_date DATE NOT NULL,
    city VARCHAR(100),
    notes TEXT,
    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE
);

-- Itinerary Items (activities per day)
CREATE TABLE IF NOT EXISTS itinerary_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    day_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    start_time TIME DEFAULT NULL,
    end_time TIME DEFAULT NULL,
    cost DECIMAL(8,2) DEFAULT 0.00,
    category VARCHAR(50) DEFAULT 'general',
    FOREIGN KEY (day_id) REFERENCES itinerary_days(id) ON DELETE CASCADE
);

-- Budget (per trip, per category)
CREATE TABLE IF NOT EXISTS budgets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    trip_id INT NOT NULL,
    category VARCHAR(50) NOT NULL,
    estimated DECIMAL(10,2) DEFAULT 0.00,
    actual DECIMAL(10,2) DEFAULT 0.00,
    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE
);

-- Expenses (detailed expense tracker)
CREATE TABLE IF NOT EXISTS expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    trip_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    category VARCHAR(50) DEFAULT 'general',
    expense_date DATE DEFAULT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE
);

-- Packing Checklist
CREATE TABLE IF NOT EXISTS packing_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    trip_id INT NOT NULL,
    item_name VARCHAR(150) NOT NULL,
    category VARCHAR(50) DEFAULT 'general',
    is_packed BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE
);

-- Trip Notes / Journal
CREATE TABLE IF NOT EXISTS trip_notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    trip_id INT NOT NULL,
    day_id INT DEFAULT NULL,
    title VARCHAR(150),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE,
    FOREIGN KEY (day_id) REFERENCES itinerary_days(id) ON DELETE SET NULL
);

-- ============================================================
-- Seed Data
-- ============================================================

INSERT IGNORE INTO cities (name, country, region, cost_index, popularity, image_url) VALUES
('Paris', 'France', 'Europe', 3.50, 95, 'images/cities/paris.jpg'),
('Tokyo', 'Japan', 'Asia', 3.20, 92, 'images/cities/tokyo.avif'),
('New York', 'USA', 'North America', 4.00, 90, 'images/cities/new-york.jpg'),
('Bali', 'Indonesia', 'Asia', 1.50, 88, 'images/cities/bali.jpg'),
('London', 'UK', 'Europe', 3.80, 87, 'images/cities/london.jpg'),
('Rome', 'Italy', 'Europe', 2.80, 85, 'images/cities/rome.jpg'),
('Bangkok', 'Thailand', 'Asia', 1.20, 84, 'images/cities/bangkok.jpg'),
('Dubai', 'UAE', 'Middle East', 3.60, 83, 'images/cities/dubai.avif'),
('Barcelona', 'Spain', 'Europe', 2.60, 82, 'images/cities/barcelona.jpg'),
('Sydney', 'Australia', 'Oceania', 3.40, 80, 'images/cities/sydeny.jpg'),
('Mumbai', 'India', 'Asia', 1.00, 78, 'images/cities/mumbai.jpg'),
('Cape Town', 'South Africa', 'Africa', 1.80, 75, 'images/cities/cape-twon.jpg');

INSERT IGNORE INTO activities (city_id, name, category, cost, duration_hours, description) VALUES
(1, 'Eiffel Tower Visit', 'sightseeing', 25.00, 2.0, 'Visit the iconic Eiffel Tower'),
(1, 'Louvre Museum', 'culture', 17.00, 3.0, 'World famous art museum'),
(1, 'Seine River Cruise', 'adventure', 15.00, 1.5, 'Scenic boat cruise'),
(2, 'Mount Fuji Day Trip', 'adventure', 50.00, 8.0, 'Day trip to Mount Fuji'),
(2, 'Shibuya Crossing', 'sightseeing', 0.00, 1.0, 'Famous pedestrian crossing'),
(2, 'Tsukiji Fish Market', 'food', 20.00, 2.0, 'Fresh seafood market tour'),
(4, 'Ubud Rice Terraces', 'nature', 10.00, 3.0, 'Scenic rice terrace walk'),
(4, 'Kuta Beach', 'leisure', 0.00, 4.0, 'Famous beach in Bali'),
(6, 'Colosseum Tour', 'culture', 18.00, 2.5, 'Ancient Roman amphitheatre'),
(6, 'Vatican Museums', 'culture', 20.00, 3.0, 'World class art and history');
