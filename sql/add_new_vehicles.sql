-- VHC-004부터 VHC-010까지 새로운 차량 데이터 추가

-- 1. vehicles 테이블에 새로운 차량 정보 추가
INSERT INTO vehicles (vehicle_id, model, year) VALUES
('VHC-004', 'Tesla Model Y', 2023),
('VHC-005', 'BMW iX3', 2022),
('VHC-006', 'Mercedes EQC', 2024),
('VHC-007', 'Audi e-tron', 2023),
('VHC-008', 'Volkswagen ID.4', 2022),
('VHC-009', 'Nissan Ariya', 2024),
('VHC-010', 'Ford Mustang Mach-E', 2023);

-- 2. daily_metrics 테이블에 각 차량의 5일간 데이터 추가
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

-- 3. 데이터 추가 결과 확인
SELECT 'vehicles 테이블 총 차량 수' as description, COUNT(*) as count FROM vehicles
UNION ALL
SELECT 'daily_metrics 테이블 총 레코드 수' as description, COUNT(*) as count FROM daily_metrics
UNION ALL
SELECT '새로 추가된 차량 수' as description, COUNT(*) as count FROM vehicles WHERE vehicle_id >= 'VHC-004';
