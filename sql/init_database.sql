-- Alcha Dashboard Initial Database Setup
-- Schema creation + basic vehicle data + 5-day sample data

-- 1. vehicles table (fixed information)
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id VARCHAR(50) PRIMARY KEY,
    model VARCHAR(100) NOT NULL,
    year INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. daily_metrics table (variable data)
CREATE TABLE IF NOT EXISTS daily_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id VARCHAR(50) NOT NULL,
    total_distance FLOAT,
    average_speed FLOAT,
    fuel_efficiency FLOAT,
    analysis_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE CASCADE,
    UNIQUE KEY unique_vehicle_date (vehicle_id, analysis_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. used_car table (used car evaluation information)
DROP TABLE IF EXISTS used_car;
CREATE TABLE IF NOT EXISTS used_car (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id VARCHAR(50) NOT NULL,
    market_value DECIMAL(10,2),
    depreciation_rate FLOAT,
    condition_score INT,
    mileage_impact FLOAT,
    analysis_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE CASCADE,
    UNIQUE KEY unique_vehicle_date (vehicle_id, analysis_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. insurance table (insurance risk assessment)
DROP TABLE IF EXISTS insurance;
CREATE TABLE IF NOT EXISTS insurance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id VARCHAR(50) NOT NULL,
    risk_score FLOAT,
    premium_estimate DECIMAL(10,2),
    accident_history INT,
    driver_age_factor FLOAT,
    analysis_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE CASCADE,
    UNIQUE KEY unique_vehicle_date (vehicle_id, analysis_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Basic vehicle data addition (VHC-001~010)
INSERT INTO vehicles (vehicle_id, model, year) VALUES
('VHC-001', 'Hyundai IONIQ 5', 2022),
('VHC-002', 'Kia EV6', 2023),
('VHC-003', 'Genesis GV60', 2024),
('VHC-004', 'Tesla Model Y', 2023),
('VHC-005', 'BMW iX3', 2022),
('VHC-006', 'Mercedes EQC', 2024),
('VHC-007', 'Audi e-tron', 2023),
('VHC-008', 'Volkswagen ID.4', 2022),
('VHC-009', 'Nissan Ariya', 2024),
('VHC-010', 'Ford Mustang Mach-E', 2023);

-- 6. 5-day sample data for each vehicle
-- VHC-001 (Hyundai IONIQ 5)
INSERT INTO daily_metrics (vehicle_id, total_distance, average_speed, fuel_efficiency, analysis_date) VALUES
('VHC-001', 15200.3, 58.2, 6.8, '2024-10-01'),
('VHC-001', 15325.7, 58.8, 6.7, '2024-10-02'),
('VHC-001', 15450.1, 58.5, 6.9, '2024-10-03'),
('VHC-001', 15575.4, 59.1, 6.8, '2024-10-04'),
('VHC-001', 15700.8, 59.4, 6.6, '2024-10-05');

-- VHC-002 (Kia EV6)
INSERT INTO daily_metrics (vehicle_id, total_distance, average_speed, fuel_efficiency, analysis_date) VALUES
('VHC-002', 17800.5, 61.4, 6.5, '2024-10-01'),
('VHC-002', 17925.9, 62.0, 6.4, '2024-10-02'),
('VHC-002', 18050.2, 61.7, 6.6, '2024-10-03'),
('VHC-002', 18175.6, 62.3, 6.5, '2024-10-04'),
('VHC-002', 18300.0, 62.6, 6.3, '2024-10-05');

-- VHC-003 (Genesis GV60)
INSERT INTO daily_metrics (vehicle_id, total_distance, average_speed, fuel_efficiency, analysis_date) VALUES
('VHC-003', 16500.8, 63.7, 6.1, '2024-10-01'),
('VHC-003', 16625.2, 64.3, 6.0, '2024-10-02'),
('VHC-003', 16750.5, 64.0, 6.2, '2024-10-03'),
('VHC-003', 16875.9, 64.6, 6.1, '2024-10-04'),
('VHC-003', 17000.3, 64.9, 5.9, '2024-10-05');

-- VHC-004 (Tesla Model Y)
INSERT INTO daily_metrics (vehicle_id, total_distance, average_speed, fuel_efficiency, analysis_date) VALUES
('VHC-004', 18500.2, 68.5, 5.8, '2024-10-01'),
('VHC-004', 18680.7, 69.1, 5.9, '2024-10-02'),
('VHC-004', 18865.3, 68.8, 5.7, '2024-10-03'),
('VHC-004', 19045.8, 69.3, 5.8, '2024-10-04'),
('VHC-004', 19220.1, 68.9, 5.9, '2024-10-05');

-- VHC-005 (BMW iX3)
INSERT INTO daily_metrics (vehicle_id, total_distance, average_speed, fuel_efficiency, analysis_date) VALUES
('VHC-005', 14200.5, 65.2, 6.2, '2024-10-01'),
('VHC-005', 14325.8, 65.8, 6.1, '2024-10-02'),
('VHC-005', 14450.2, 65.5, 6.3, '2024-10-03'),
('VHC-005', 14575.6, 65.9, 6.2, '2024-10-04'),
('VHC-005', 14700.9, 66.1, 6.1, '2024-10-05');

-- VHC-006 (Mercedes EQC)
INSERT INTO daily_metrics (vehicle_id, total_distance, average_speed, fuel_efficiency, analysis_date) VALUES
('VHC-006', 9800.3, 62.7, 6.0, '2024-10-01'),
('VHC-006', 9925.7, 63.2, 5.9, '2024-10-02'),
('VHC-006', 10050.1, 62.9, 6.1, '2024-10-03'),
('VHC-006', 10175.4, 63.5, 6.0, '2024-10-04'),
('VHC-006', 10300.8, 63.8, 5.8, '2024-10-05');

-- VHC-007 (Audi e-tron)
INSERT INTO daily_metrics (vehicle_id, total_distance, average_speed, fuel_efficiency, analysis_date) VALUES
('VHC-007', 16800.9, 64.3, 5.6, '2024-10-01'),
('VHC-007', 16925.2, 64.8, 5.7, '2024-10-02'),
('VHC-007', 17050.6, 64.5, 5.5, '2024-10-03'),
('VHC-007', 17175.9, 65.1, 5.6, '2024-10-04'),
('VHC-007', 17300.3, 65.4, 5.8, '2024-10-05');

-- VHC-008 (Volkswagen ID.4)
INSERT INTO daily_metrics (vehicle_id, total_distance, average_speed, fuel_efficiency, analysis_date) VALUES
('VHC-008', 12500.7, 61.8, 6.4, '2024-10-01'),
('VHC-008', 12625.1, 62.3, 6.3, '2024-10-02'),
('VHC-008', 12750.5, 62.0, 6.5, '2024-10-03'),
('VHC-008', 12875.8, 62.6, 6.4, '2024-10-04'),
('VHC-008', 13000.2, 62.9, 6.2, '2024-10-05');

-- VHC-009 (Nissan Ariya)
INSERT INTO daily_metrics (vehicle_id, total_distance, average_speed, fuel_efficiency, analysis_date) VALUES
('VHC-009', 11200.4, 59.5, 6.7, '2024-10-01'),
('VHC-009', 11325.8, 60.1, 6.6, '2024-10-02'),
('VHC-009', 11450.2, 59.8, 6.8, '2024-10-03'),
('VHC-009', 11575.5, 60.4, 6.7, '2024-10-04'),
('VHC-009', 11700.9, 60.7, 6.5, '2024-10-05');

-- VHC-010 (Ford Mustang Mach-E)
INSERT INTO daily_metrics (vehicle_id, total_distance, average_speed, fuel_efficiency, analysis_date) VALUES
('VHC-010', 19800.6, 70.2, 5.4, '2024-10-01'),
('VHC-010', 19925.9, 70.8, 5.5, '2024-10-02'),
('VHC-010', 20050.3, 70.5, 5.3, '2024-10-03'),
('VHC-010', 20175.7, 71.1, 5.4, '2024-10-04'),
('VHC-010', 20300.1, 71.4, 5.6, '2024-10-05');

-- 7. Initialization completion check
SELECT 'Database initialization completed' as status;
SELECT 'Total vehicles count' as description, COUNT(*) as count FROM vehicles
UNION ALL
SELECT 'Total daily_metrics records' as description, COUNT(*) as count FROM daily_metrics;