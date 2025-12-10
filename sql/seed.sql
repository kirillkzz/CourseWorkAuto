TRUNCATE TABLE RouteSheets, Vehicles, Routes, Drivers RESTART IDENTITY;

INSERT INTO Drivers (full_name, phone, address) VALUES
('Задорожна Анастасія Олександрівна', '+380501234567', 'м. Київ, вул. Хрещатик, 1'),
('Сидоренко Кирило Васильович', '+380679876543', 'м. Київ, вул. Перемоги, 22'),
('Ковальчук Андрій Віталійович', '+380931112233', 'м. Ірпінь, вул. Соборна, 5'),
('Бондаренко Іван Петрович', '+380445556677', 'м. Бровари, вул. Київська, 10');

INSERT INTO Routes (route_number, mileage_km, cost_per_km) VALUES
('379', 25.5, 1.5),
('420', 18.2, 1.8),
('395', 31.0, 1.4),
('501', 45.0, 1.2);

INSERT INTO Vehicles (license_plate, model, driver_id) VALUES
('AA1234BC', 'Bogdan A092', 1),
('AI5678BI', 'Mercedes Sprinter', 2),
('AA9876CB', 'MAN Lion', 3),
('AI1111AA', 'I-VAN A07', 4);

INSERT INTO RouteSheets (sheet_date, vehicle_id, route_number, fuel_used_liters) VALUES
('2025-11-10', 1, '379', 30.5),
('2025-11-10', 2, '420', 22.0),
('2025-11-10', 3, '395', 35.0),
('2025-11-11', 1, '379', 31.2),
('2025-11-11', 2, '420', 21.5),
('2025-11-12', 4, '501', 40.0);