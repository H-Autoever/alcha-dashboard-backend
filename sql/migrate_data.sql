-- 기존 basic_info 데이터를 새 테이블 구조로 마이그레이션

-- 1. vehicles 테이블에 고유한 차량 정보 삽입
INSERT INTO vehicles (vehicle_id, model, year)
SELECT DISTINCT vehicle_id, model, year
FROM basic_info
ORDER BY vehicle_id;

-- 2. daily_metrics 테이블에 일별 데이터 삽입
INSERT INTO daily_metrics (vehicle_id, total_distance, average_speed, fuel_efficiency, analysis_date)
SELECT 
    vehicle_id,
    total_distance,
    average_speed,
    fuel_efficiency,
    analysis_date
FROM basic_info
ORDER BY vehicle_id, analysis_date;

-- 3. 마이그레이션 결과 확인
SELECT 'vehicles 테이블 데이터' as table_name, COUNT(*) as count FROM vehicles
UNION ALL
SELECT 'daily_metrics 테이블 데이터' as table_name, COUNT(*) as count FROM daily_metrics
UNION ALL
SELECT '기존 basic_info 테이블 데이터' as table_name, COUNT(*) as count FROM basic_info;
