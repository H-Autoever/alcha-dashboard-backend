-- Alcha Dashboard Initial Database Setup (vehicle tabs edition)
-- Drops legacy tables, creates new evaluation and driving habit structures, and seeds sample data.

-- Cleanup legacy / staging tables
DROP TABLE IF EXISTS used_car;
DROP TABLE IF EXISTS insurance;
DROP TABLE IF EXISTS vehicle_score_daily;
DROP TABLE IF EXISTS driving_habit_monthly;
DROP TABLE IF EXISTS daily_metrics;
DROP TABLE IF EXISTS vehicles;

-- 1. vehicles table (static metadata)
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id VARCHAR(50) PRIMARY KEY,
    model VARCHAR(100) NOT NULL,
    year INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. daily_metrics table (daily operational metrics)
CREATE TABLE IF NOT EXISTS daily_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id VARCHAR(50) NOT NULL,
    total_distance FLOAT,
    average_speed FLOAT,
    fuel_efficiency FLOAT,
    analysis_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_daily_metrics_vehicle FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE CASCADE,
    UNIQUE KEY uq_daily_metrics_vehicle_date (vehicle_id, analysis_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. vehicle_score_daily table (daily evaluation scores)
CREATE TABLE IF NOT EXISTS vehicle_score_daily (
    vehicle_id VARCHAR(50) NOT NULL,
    analysis_date DATE NOT NULL,
    final_score INT,
    engine_powertrain_score INT,
    transmission_drivetrain_score INT,
    brake_suspension_score INT,
    adas_safety_score INT,
    electrical_battery_score INT,
    other_score INT,
    engine_rpm_avg INT,
    engine_coolant_temp_avg FLOAT,
    transmission_oil_temp_avg FLOAT,
    battery_voltage_avg FLOAT,
    alternator_output_avg FLOAT,
    temperature_ambient_avg FLOAT,
    dtc_count INT,
    gear_change_count INT,
    abs_activation_count INT,
    suspension_shock_count INT,
    adas_sensor_fault_count INT,
    aeb_activation_count INT,
    engine_start_count INT,
    suddenacc_count INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (vehicle_id, analysis_date),
    CONSTRAINT fk_score_vehicle FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE CASCADE,
    INDEX idx_vehicle_score_date (analysis_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. driving_habit_monthly table (monthly driving habit aggregates)
CREATE TABLE IF NOT EXISTS driving_habit_monthly (
    vehicle_id VARCHAR(50) NOT NULL,
    analysis_month DATE NOT NULL,
    acceleration_events INT,
    lane_departure_events INT,
    night_drive_ratio FLOAT,
    avg_drive_duration_minutes FLOAT,
    avg_speed FLOAT,
    avg_distance FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (vehicle_id, analysis_month),
    CONSTRAINT fk_habit_vehicle FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE CASCADE,
    INDEX idx_habit_month (analysis_month)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Seed vehicles
INSERT INTO vehicles (vehicle_id, model, year) VALUES
('VHC-001', 'Hyundai IONIQ 5', 2022),
('VHC-002', 'Kia EV6', 2023),
('VHC-003', 'Genesis GV60', 2024)
ON DUPLICATE KEY UPDATE
    model = VALUES(model),
    year = VALUES(year);

-- 6. Seed daily metrics (latest five days per vehicle)
INSERT INTO daily_metrics (vehicle_id, total_distance, average_speed, fuel_efficiency, analysis_date) VALUES
('VHC-001', 15200.3, 58.2, 6.8, '2024-10-01'),
('VHC-001', 15325.7, 58.8, 6.7, '2024-10-02'),
('VHC-001', 15450.1, 58.5, 6.9, '2024-10-03'),
('VHC-001', 15575.4, 59.1, 6.8, '2024-10-04'),
('VHC-001', 15700.8, 59.4, 6.6, '2024-10-05'),
('VHC-002', 17800.5, 61.4, 6.5, '2024-10-01'),
('VHC-002', 17925.9, 62.0, 6.4, '2024-10-02'),
('VHC-002', 18050.2, 61.7, 6.6, '2024-10-03'),
('VHC-002', 18175.6, 62.3, 6.5, '2024-10-04'),
('VHC-002', 18300.0, 62.6, 6.3, '2024-10-05'),
('VHC-003', 16500.8, 63.7, 6.1, '2024-10-01'),
('VHC-003', 16625.2, 64.3, 6.0, '2024-10-02'),
('VHC-003', 16750.5, 64.0, 6.2, '2024-10-03'),
('VHC-003', 16875.9, 64.6, 6.1, '2024-10-04'),
('VHC-003', 17000.3, 64.9, 5.9, '2024-10-05')
ON DUPLICATE KEY UPDATE
    total_distance = VALUES(total_distance),
    average_speed = VALUES(average_speed),
    fuel_efficiency = VALUES(fuel_efficiency);

-- 7. Seed vehicle scores (three most recent days per vehicle)
INSERT INTO vehicle_score_daily (
    vehicle_id, analysis_date, final_score,
    engine_powertrain_score, transmission_drivetrain_score,
    brake_suspension_score, adas_safety_score,
    electrical_battery_score, other_score,
    engine_rpm_avg, engine_coolant_temp_avg,
    transmission_oil_temp_avg, battery_voltage_avg,
    alternator_output_avg, temperature_ambient_avg,
    dtc_count, gear_change_count,
    abs_activation_count, suspension_shock_count,
    adas_sensor_fault_count, aeb_activation_count,
    engine_start_count, suddenacc_count
) VALUES
('VHC-001', '2024-10-03', 86, 88, 84, 85, 87, 90, 82,
 2150, 82.4, 78.6, 13.8, 14.5, 21.5, 2, 42, 3, 5, 0, 2, 8, 4),
('VHC-001', '2024-10-04', 87, 89, 85, 86, 88, 91, 83,
 2165, 82.1, 78.1, 13.9, 14.6, 21.2, 1, 40, 2, 4, 0, 1, 7, 3),
('VHC-001', '2024-10-05', 88, 90, 86, 87, 89, 92, 84,
 2178, 81.9, 77.8, 14.0, 14.6, 21.0, 1, 41, 2, 4, 0, 1, 7, 2),
('VHC-002', '2024-10-03', 79, 81, 78, 77, 80, 82, 76,
 2040, 84.3, 80.2, 13.6, 14.2, 22.1, 3, 48, 4, 6, 1, 3, 9, 6),
('VHC-002', '2024-10-04', 80, 82, 79, 78, 81, 83, 77,
 2052, 84.0, 80.0, 13.7, 14.2, 21.9, 3, 47, 4, 6, 1, 2, 9, 5),
('VHC-002', '2024-10-05', 82, 83, 80, 79, 82, 84, 78,
 2065, 83.7, 79.6, 13.8, 14.3, 21.7, 2, 45, 3, 5, 1, 2, 8, 4),
('VHC-003', '2024-10-03', 91, 92, 90, 89, 93, 94, 88,
 1985, 80.1, 75.5, 13.9, 14.7, 20.4, 1, 35, 1, 3, 0, 1, 6, 2),
('VHC-003', '2024-10-04', 92, 93, 91, 90, 94, 95, 89,
 1992, 79.8, 75.1, 14.0, 14.8, 20.2, 1, 34, 1, 3, 0, 1, 6, 2),
('VHC-003', '2024-10-05', 93, 94, 92, 91, 95, 96, 90,
 1998, 79.5, 74.8, 14.1, 14.8, 20.0, 0, 34, 1, 2, 0, 1, 5, 1)
ON DUPLICATE KEY UPDATE
    final_score = VALUES(final_score),
    engine_powertrain_score = VALUES(engine_powertrain_score),
    transmission_drivetrain_score = VALUES(transmission_drivetrain_score),
    brake_suspension_score = VALUES(brake_suspension_score),
    adas_safety_score = VALUES(adas_safety_score),
    electrical_battery_score = VALUES(electrical_battery_score),
    other_score = VALUES(other_score),
    engine_rpm_avg = VALUES(engine_rpm_avg),
    engine_coolant_temp_avg = VALUES(engine_coolant_temp_avg),
    transmission_oil_temp_avg = VALUES(transmission_oil_temp_avg),
    battery_voltage_avg = VALUES(battery_voltage_avg),
    alternator_output_avg = VALUES(alternator_output_avg),
    temperature_ambient_avg = VALUES(temperature_ambient_avg),
    dtc_count = VALUES(dtc_count),
    gear_change_count = VALUES(gear_change_count),
    abs_activation_count = VALUES(abs_activation_count),
    suspension_shock_count = VALUES(suspension_shock_count),
    adas_sensor_fault_count = VALUES(adas_sensor_fault_count),
    aeb_activation_count = VALUES(aeb_activation_count),
    engine_start_count = VALUES(engine_start_count),
    suddenacc_count = VALUES(suddenacc_count);

-- 8. Seed driving habit monthly aggregates (latest two months per vehicle)
INSERT INTO driving_habit_monthly (
    vehicle_id, analysis_month,
    acceleration_events, lane_departure_events,
    night_drive_ratio, avg_drive_duration_minutes,
    avg_speed, avg_distance
) VALUES
('VHC-001', '2024-09-01', 120, 8, 0.28, 42.5, 58.3, 36.7),
('VHC-001', '2024-10-01', 135, 6, 0.25, 44.1, 59.0, 38.2),
('VHC-002', '2024-09-01', 98, 11, 0.34, 39.8, 60.7, 32.4),
('VHC-002', '2024-10-01', 105, 9, 0.32, 41.0, 61.2, 33.1),
('VHC-003', '2024-09-01', 76, 5, 0.21, 46.3, 62.5, 40.8),
('VHC-003', '2024-10-01', 81, 4, 0.19, 47.6, 63.2, 41.5)
ON DUPLICATE KEY UPDATE
    acceleration_events = VALUES(acceleration_events),
    lane_departure_events = VALUES(lane_departure_events),
    night_drive_ratio = VALUES(night_drive_ratio),
    avg_drive_duration_minutes = VALUES(avg_drive_duration_minutes),
    avg_speed = VALUES(avg_speed),
    avg_distance = VALUES(avg_distance);

-- 9. Verification
SELECT 'Database initialization completed' AS status;
SELECT 'Total vehicles' AS description, COUNT(*) AS count FROM vehicles
UNION ALL
SELECT 'Daily metrics rows', COUNT(*) FROM daily_metrics
UNION ALL
SELECT 'Vehicle score rows', COUNT(*) FROM vehicle_score_daily
UNION ALL
SELECT 'Driving habit rows', COUNT(*) FROM driving_habit_monthly;
