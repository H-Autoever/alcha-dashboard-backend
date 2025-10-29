-- TimescaleDB 샘플 데이터 초기화 및 삽입에 사용한 쿼리 모음
-- 실행 환경: alcha-timescaledb-0 (psql -U postgres -d alcha_events)

-- 1) 기존 데이터 삭제
DELETE FROM vehicle_telemetry;
DELETE FROM engine_off_events;
DELETE FROM collision_events;
DELETE FROM sudden_acceleration_events;
DELETE FROM warning_light_events;
DELETE FROM periodic_data;

-- 2) 텔레메트리 10,800건 삽입 (VHC-001, VHC-002, VHC-003 각각 3,600건)
-- VHC-001 (3,600건)
INSERT INTO vehicle_telemetry (vehicle_id, vehicle_speed, engine_rpm, throttle_position, timestamp)
SELECT 
    'VHC-001' AS vehicle_id,
    (20 + (random() * 60))::float AS vehicle_speed,
    (800 + (random() * 5200))::int AS engine_rpm,
    (10 + (random() * 70))::float AS throttle_position,
    ('2025-09-23 01:54:26'::timestamp + (gs * interval '1 second'))::timestamptz AS timestamp
FROM generate_series(0, 3599) AS gs;

-- VHC-002 (3,600건)
INSERT INTO vehicle_telemetry (vehicle_id, vehicle_speed, engine_rpm, throttle_position, timestamp)
SELECT 
    'VHC-002' AS vehicle_id,
    (20 + (random() * 60))::float AS vehicle_speed,
    (800 + (random() * 5200))::int AS engine_rpm,
    (10 + (random() * 70))::float AS throttle_position,
    ('2025-09-23 01:54:26'::timestamp + (gs * interval '1 second'))::timestamptz AS timestamp
FROM generate_series(0, 3599) AS gs;

-- VHC-003 (3,600건)
INSERT INTO vehicle_telemetry (vehicle_id, vehicle_speed, engine_rpm, throttle_position, timestamp)
SELECT 
    'VHC-003' AS vehicle_id,
    (20 + (random() * 60))::float AS vehicle_speed,
    (800 + (random() * 5200))::int AS engine_rpm,
    (10 + (random() * 70))::float AS throttle_position,
    ('2025-09-23 01:54:26'::timestamp + (gs * interval '1 second'))::timestamptz AS timestamp
FROM generate_series(0, 3599) AS gs;

-- 3) 충돌 이벤트 삽입 (7건)
INSERT INTO collision_events (vehicle_id, damage, timestamp) VALUES
('VHC-001', 25, '2025-09-23 02:04:26'::timestamptz),
('VHC-001', 45, '2025-09-23 02:19:26'::timestamptz),
('VHC-001', 35, '2025-09-23 02:39:26'::timestamptz),
('VHC-002', 55, '2025-09-23 02:14:26'::timestamptz),
('VHC-002', 30, '2025-09-23 02:34:26'::timestamptz),
('VHC-003', 40, '2025-09-23 02:09:26'::timestamptz),
('VHC-003', 20, '2025-09-23 02:29:26'::timestamptz);

-- 4) 엔진 오프 이벤트 삽입 (7건)
INSERT INTO engine_off_events (vehicle_id, speed, gear_status, gyro, side, ignition, timestamp) VALUES
('VHC-001', 0, 'P', 0.12, 'front', false, '2025-09-23 02:09:26'::timestamptz),
('VHC-001', 0, 'P', 0.15, 'rear', false, '2025-09-23 02:44:26'::timestamptz),
('VHC-002', 0, 'P', 0.08, 'left', false, '2025-09-23 01:59:26'::timestamptz),
('VHC-002', 0, 'P', 0.11, 'right', false, '2025-09-23 02:24:26'::timestamptz),
('VHC-002', 0, 'P', 0.09, 'front', false, '2025-09-23 02:49:26'::timestamptz),
('VHC-003', 0, 'P', 0.13, 'rear', false, '2025-09-23 02:06:26'::timestamptz),
('VHC-003', 0, 'P', 0.10, 'left', false, '2025-09-23 02:42:26'::timestamptz);

-- 5) 급가속 이벤트 삽입 (3건)
INSERT INTO sudden_acceleration_events (vehicle_id, vehicle_speed, throttle_position, gear_position_mode, timestamp) VALUES
('VHC-001', 85.5, 88.0, 'D', '2025-09-23 02:15:26'::timestamptz),
('VHC-002', 75.2, 82.5, 'D', '2025-09-23 02:25:26'::timestamptz),
('VHC-003', 92.1, 90.0, 'D', '2025-09-23 02:35:26'::timestamptz);

-- 6) 경고등 이벤트 삽입 (3건)
INSERT INTO warning_light_events (vehicle_id, warning_type, timestamp) VALUES
('VHC-001', 'engine_check', '2025-09-23 02:10:26'::timestamptz),
('VHC-002', 'engine_oil_check', '2025-09-23 02:20:26'::timestamptz),
('VHC-003', 'airbag_check', '2025-09-23 02:30:26'::timestamptz);

-- 7) 주기적 데이터 삽입 (9건; 차량별 3건)
INSERT INTO periodic_data (
  vehicle_id, location_latitude, location_longitude, location_altitude,
  temperature_cabin, temperature_ambient, battery_voltage,
  tpms_front_left, tpms_front_right, tpms_rear_left, tpms_rear_right,
  accelerometer_x, accelerometer_y, accelerometer_z, fuel_level,
  engine_coolant_temp, transmission_oil_temp, timestamp
) VALUES
('VHC-001', 37.5666, 126.9781, 35.0, 24.5, 18.7, 12.8, 235.5, 234.2, 233.8, 234.1, 0.01, -0.02, 9.98, 85.2, 25.5, 22.3, '2025-09-23 01:54:26'::timestamptz),
('VHC-001', 37.5671, 126.9786, 36.2, 25.1, 19.2, 12.6, 234.8, 235.1, 234.5, 233.9, 0.02, -0.01, 9.99, 84.8, 26.1, 23.0, '2025-09-23 02:04:26'::timestamptz),
('VHC-001', 37.5668, 126.9783, 34.8, 24.8, 18.9, 12.7, 235.2, 234.7, 234.0, 234.3, 0.00, -0.03, 9.97, 85.0, 25.8, 22.7, '2025-09-23 02:14:26'::timestamptz),
('VHC-002', 37.5669, 126.9784, 35.5, 24.7, 18.8, 12.9, 234.9, 235.3, 234.2, 234.6, 0.01, -0.02, 9.98, 86.1, 25.9, 22.8, '2025-09-23 01:54:26'::timestamptz),
('VHC-002', 37.5672, 126.9787, 36.0, 25.0, 19.0, 12.5, 235.0, 234.8, 234.4, 234.0, 0.02, -0.01, 9.99, 85.7, 26.0, 22.9, '2025-09-23 02:04:26'::timestamptz),
('VHC-002', 37.5667, 126.9782, 35.2, 24.9, 18.9, 12.8, 234.7, 235.2, 234.1, 234.5, 0.00, -0.03, 9.97, 85.9, 25.7, 22.6, '2025-09-23 02:14:26'::timestamptz),
('VHC-003', 37.5670, 126.9785, 35.8, 24.6, 18.7, 12.7, 235.1, 234.9, 234.3, 234.7, 0.01, -0.02, 9.98, 85.5, 25.8, 22.7, '2025-09-23 01:54:26'::timestamptz),
('VHC-003', 37.5673, 126.9788, 36.3, 25.2, 19.1, 12.6, 234.6, 235.4, 234.0, 234.8, 0.02, -0.01, 9.99, 85.3, 26.2, 23.1, '2025-09-23 02:04:26'::timestamptz),
('VHC-003', 37.5665, 126.9780, 35.1, 24.8, 18.8, 12.9, 235.3, 234.5, 234.6, 234.2, 0.00, -0.03, 9.97, 85.8, 25.9, 22.8, '2025-09-23 02:14:26'::timestamptz);

-- 8) 검증 쿼리
SELECT 'vehicle_telemetry' AS table_name, COUNT(*) AS count FROM vehicle_telemetry;
SELECT 'engine_off_events' AS table_name, COUNT(*) AS count FROM engine_off_events;
SELECT 'collision_events' AS table_name, COUNT(*) AS count FROM collision_events;
SELECT 'sudden_acceleration_events' AS table_name, COUNT(*) AS count FROM sudden_acceleration_events;
SELECT 'warning_light_events' AS table_name, COUNT(*) AS count FROM warning_light_events;
SELECT 'periodic_data' AS table_name, COUNT(*) AS count FROM periodic_data;

-- 차량별 텔레메트리 분포 확인
SELECT vehicle_id, COUNT(*) AS count
FROM vehicle_telemetry
GROUP BY vehicle_id
ORDER BY vehicle_id;


