CREATE TABLE IF NOT EXISTS Drivers (
    driver_id SERIAL PRIMARY KEY,
    full_name TEXT NOT NULL,
    phone VARCHAR(20) UNIQUE,
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Routes (
    route_number VARCHAR(10) PRIMARY KEY,
    mileage_km REAL NOT NULL,
    cost_per_km REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS Vehicles (
    vehicle_id SERIAL PRIMARY KEY,
    license_plate VARCHAR(10) NOT NULL UNIQUE,
    model VARCHAR(50),
    driver_id INT REFERENCES Drivers(driver_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS RouteSheets (
    sheet_id SERIAL PRIMARY KEY,
    sheet_date DATE NOT NULL,
    vehicle_id INT REFERENCES Vehicles(vehicle_id) ON DELETE CASCADE,
    route_number VARCHAR(10) REFERENCES Routes(route_number) ON DELETE CASCADE,
    fuel_used_liters REAL,
    revenue REAL GENERATED ALWAYS AS (0) STORED
);

CREATE TABLE IF NOT EXISTS Users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);