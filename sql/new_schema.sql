-- 새로운 테이블 구조 (vehicles + daily_metrics 분리)
-- 기존 basic_info 테이블을 대체

-- 1. vehicles 테이블 (고정 정보)
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id VARCHAR(50) PRIMARY KEY COMMENT '차량 고유 ID',
    model VARCHAR(100) NOT NULL COMMENT '차량 모델명',
    year INT COMMENT '차량 연식',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '차량 등록일시'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='차량 기본 정보 테이블';

-- 2. daily_metrics 테이블 (변동 데이터)
CREATE TABLE IF NOT EXISTS daily_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '레코드 고유 ID',
    vehicle_id VARCHAR(50) NOT NULL COMMENT '차량 고유 ID',
    total_distance FLOAT COMMENT '총 주행 거리 (km)',
    average_speed FLOAT COMMENT '평균 주행 속도 (km/h)',
    fuel_efficiency FLOAT COMMENT '연비 (km/L 또는 km/kWh)',
    analysis_date DATE NOT NULL COMMENT '데이터 분석 기준 일자',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '데이터 생성일시',
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE CASCADE,
    UNIQUE KEY unique_vehicle_date (vehicle_id, analysis_date) COMMENT '차량 ID와 분석 날짜의 유니크 조합'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='일별 차량 성능 지표 테이블';

-- 3. 기존 테이블들 (used_car, insurance) - 외래키 참조 수정 필요
-- used_car 테이블 재생성 (vehicles 테이블 참조)
DROP TABLE IF EXISTS used_car;
CREATE TABLE IF NOT EXISTS used_car (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '레코드 고유 ID',
    vehicle_id VARCHAR(50) NOT NULL COMMENT '차량 고유 ID',
    market_value DECIMAL(10,2) COMMENT '시장 가치 (원)',
    depreciation_rate FLOAT COMMENT '감가상각률 (%)',
    condition_score INT COMMENT '차량 상태 점수 (1-10)',
    mileage_impact FLOAT COMMENT '주행거리 영향도',
    analysis_date DATE COMMENT '분석 기준 일자',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '데이터 생성일시',
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE CASCADE,
    UNIQUE KEY unique_vehicle_date (vehicle_id, analysis_date) COMMENT '차량 ID와 분석 날짜의 유니크 조합'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='중고차 평가 정보 테이블';

-- insurance 테이블 재생성 (vehicles 테이블 참조)
DROP TABLE IF EXISTS insurance;
CREATE TABLE IF NOT EXISTS insurance (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '레코드 고유 ID',
    vehicle_id VARCHAR(50) NOT NULL COMMENT '차량 고유 ID',
    risk_score FLOAT COMMENT '위험도 점수 (0-100)',
    premium_estimate DECIMAL(10,2) COMMENT '예상 보험료 (원)',
    accident_history INT COMMENT '사고 이력 횟수',
    driver_age_factor FLOAT COMMENT '운전자 연령 계수',
    analysis_date DATE COMMENT '분석 기준 일자',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '데이터 생성일시',
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE CASCADE,
    UNIQUE KEY unique_vehicle_date (vehicle_id, analysis_date) COMMENT '차량 ID와 분석 날짜의 유니크 조합'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='보험 위험도 평가 테이블';
