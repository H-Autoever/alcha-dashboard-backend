-- MySQL schema for Alcha Dashboard

CREATE TABLE IF NOT EXISTS basic_info (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '레코드 고유 ID',
    vehicle_id VARCHAR(50) NOT NULL COMMENT '차량 고유 ID (예: VIN 또는 내부 ID)',
    model VARCHAR(100) NOT NULL COMMENT '차량 모델명 (예: Tesla Model 3)',
    year INT COMMENT '차량 연식 (예: 2023)',
    total_distance FLOAT COMMENT '총 주행 거리 (km, Redshift에서 SUM 계산)',
    average_speed FLOAT COMMENT '평균 주행 속도 (km/h, Redshift에서 AVG 계산)',
    fuel_efficiency FLOAT COMMENT '연비 (km/L 또는 km/kWh, Redshift에서 SUM(distance)/SUM(fuel) 계산)',
    collision_events TEXT COMMENT '충돌 이력 시점 목록 (comma-separated timestamps, Redshift에서 STRING_AGG(event_time, ",") 계산)',
    analysis_date DATE COMMENT '데이터 분석 기준 일자',
    UNIQUE KEY unique_vehicle_date (vehicle_id, analysis_date) COMMENT '차량 ID와 분석 날짜의 유니크 조합'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='메인 기능용 기본 차량 정보 테이블';

CREATE TABLE IF NOT EXISTS used_car (
    vehicle_id VARCHAR(50) PRIMARY KEY COMMENT '차량 고유 ID',
    engine_score INT COMMENT '엔진 상태 점수 (0-100)',
    battery_score INT COMMENT '배터리 상태 점수 (0-100)',
    tire_score INT COMMENT '타이어 상태 점수 (0-100)',
    brake_score INT COMMENT '브레이크 상태 점수 (0-100)',
    fuel_efficiency_score INT COMMENT '연비 효율 점수 (0-100)',
    overall_grade INT COMMENT '종합 등급 (0-100)',
    analysis_date DATE COMMENT '데이터 분석 기준 일자',
    CONSTRAINT fk_used_car_basic_info FOREIGN KEY (vehicle_id) REFERENCES basic_info(vehicle_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='중고차 서비스용 차량 상태 평가 테이블';

CREATE TABLE IF NOT EXISTS insurance (
    vehicle_id VARCHAR(50) PRIMARY KEY COMMENT '차량 고유 ID',
    over_speed_risk INT COMMENT '과속 위험도 점수 (0-100)',
    sudden_accel_risk INT COMMENT '급가속/급정지 위험도 점수 (0-100)',
    sudden_turn_risk INT COMMENT '급회전 위험도 점수 (0-100)',
    night_drive_risk INT COMMENT '야간 주행 위험도 점수 (0-100)',
    overall_grade INT COMMENT '종합 등급 (0-100)',
    analysis_date DATE COMMENT '데이터 분석 기준 일자',
    CONSTRAINT fk_insurance_basic_info FOREIGN KEY (vehicle_id) REFERENCES basic_info(vehicle_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='보험 서비스용 위험도 평가 테이블';

-- Seed dummy data
INSERT INTO basic_info (vehicle_id, model, year, total_distance, average_speed, fuel_efficiency, collision_events, analysis_date) VALUES
('VHC-001', 'Hyundai Ioniq 5', 2023, 15234.5, 62.3, 6.1, '2023-09-01T12:10:00,2024-01-21T08:45:00', '2024-10-01'),
('VHC-002', 'Kia EV6', 2022, 22340.9, 58.7, 6.5, '', '2024-10-01'),
('VHC-003', 'Genesis GV60', 2024, 8340.2, 54.1, 6.8, '2024-05-11T14:22:00', '2024-10-01')
ON DUPLICATE KEY UPDATE model=VALUES(model);

INSERT INTO used_car (vehicle_id, engine_score, battery_score, tire_score, brake_score, fuel_efficiency_score, overall_grade, analysis_date) VALUES
('VHC-001', 85, 90, 80, 82, 88, 85, '2024-10-01'),
('VHC-002', 78, 83, 75, 80, 84, 80, '2024-10-01'),
('VHC-003', 92, 94, 88, 90, 91, 91, '2024-10-01')
ON DUPLICATE KEY UPDATE overall_grade=VALUES(overall_grade);

INSERT INTO insurance (vehicle_id, over_speed_risk, sudden_accel_risk, sudden_turn_risk, night_drive_risk, overall_grade, analysis_date) VALUES
('VHC-001', 40, 35, 30, 45, 38, '2024-10-01'),
('VHC-002', 55, 50, 48, 60, 53, '2024-10-01'),
('VHC-003', 25, 20, 22, 30, 24, '2024-10-01')
ON DUPLICATE KEY UPDATE overall_grade=VALUES(overall_grade);


