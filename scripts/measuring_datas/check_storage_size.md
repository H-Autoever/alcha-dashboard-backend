# 데이터베이스 저장 용량 비교 가이드

동일한 데이터를 MongoDB와 TimescaleDB에 저장했을 때의 용량을 비교하는 명령어입니다.

## 📊 MongoDB 용량 조회

### 1. 데이터베이스 전체 용량
```javascript
// MongoDB 셸 접속
mongosh -u admin -p adminpassword --authenticationDatabase admin

// 데이터베이스 선택
use alcha_events

// 데이터베이스 전체 통계 (용량 포함)
db.stats(1024*1024)  // MB 단위로 표시
```

### 2. 특정 컬렉션 용량 조회

#### 실제 텔레메트리 데이터 (`realtime-storage-data`)
```javascript
db.getCollection('realtime-storage-data').stats(1024*1024)
```

#### 테스트 데이터 (`write_performance_test`)
```javascript
db.getCollection('write_performance_test').stats(1024*1024)
```

### 3. 모든 컬렉션 용량 일괄 조회
```javascript
db.getCollectionNames().forEach(function(collection) {
    var stats = db[collection].stats(1024*1024);
    print(collection + ":");
    print("  데이터 크기: " + stats.size + " MB");
    print("  저장 공간: " + stats.storageSize + " MB");
    print("  인덱스 크기: " + stats.totalIndexSize + " MB");
    print("  총 문서 수: " + stats.count);
    print("---");
});
```

### 4. 중요 필드 설명
- **`size`**: 컬렉션 내 문서들의 실제 데이터 크기 (압축 전)
- **`storageSize`**: 디스크에 실제로 차지하는 저장 공간 (압축 포함)
- **`totalIndexSize`**: 인덱스가 차지하는 공간
- **`count`**: 문서 개수

---

## 📊 TimescaleDB 용량 조회

### 1. 데이터베이스 전체 용량
```sql
-- PostgreSQL/TimescaleDB 접속
psql -h localhost -p 5432 -U alcha -d alcha_events

-- 데이터베이스 전체 크기
SELECT pg_size_pretty(pg_database_size('alcha_events')) AS database_size;
```

### 2. 특정 테이블 용량 조회

#### 실제 텔레메트리 데이터 (`vehicle_telemetry`)
```sql
SELECT 
    pg_size_pretty(pg_total_relation_size('vehicle_telemetry')) AS total_size,
    pg_size_pretty(pg_relation_size('vehicle_telemetry')) AS table_size,
    pg_size_pretty(pg_indexes_size('vehicle_telemetry')) AS indexes_size,
    (SELECT COUNT(*) FROM vehicle_telemetry) AS row_count;
```

#### 테스트 데이터 (`write_performance_test`)
```sql
SELECT 
    pg_size_pretty(pg_total_relation_size('write_performance_test')) AS total_size,
    pg_size_pretty(pg_relation_size('write_performance_test')) AS table_size,
    pg_size_pretty(pg_indexes_size('write_performance_test')) AS indexes_size,
    (SELECT COUNT(*) FROM write_performance_test) AS row_count;
```

### 3. 모든 테이블 용량 일괄 조회
```sql
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    pg_size_pretty(pg_indexes_size(schemaname||'.'||tablename)) AS indexes_size,
    (SELECT COUNT(*) FROM information_schema.tables t2 
     WHERE t2.table_schema = t.schemaname AND t2.table_name = t.tablename) AS estimated_rows
FROM pg_tables t
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 4. 하이퍼테이블별 상세 크기 (TimescaleDB 전용)
```sql
SELECT 
    hypertable_schema AS schema_name,
    hypertable_name AS table_name,
    pg_size_pretty(total_bytes) AS total_size,
    pg_size_pretty(table_bytes) AS table_size,
    pg_size_pretty(index_bytes) AS index_size,
    pg_size_pretty(toast_bytes) AS toast_size,
    num_chunks
FROM timescaledb_information.hypertable_sizes
ORDER BY total_bytes DESC;
```

### 5. 중요 필드 설명
- **`pg_total_relation_size()`**: 테이블 + 인덱스 + TOAST의 총 크기
- **`pg_relation_size()`**: 테이블 자체의 크기 (데이터만)
- **`pg_indexes_size()`**: 인덱스가 차지하는 공간
- **`toast_size`**: 큰 데이터를 저장하는 TOAST 테이블 크기

---

## 🔄 빠른 비교 스크립트

아래 명령어로 동일한 데이터의 용량을 바로 비교할 수 있습니다.

### MongoDB (실제 데이터)
```bash
# Docker 컨테이너 내에서 실행
docker exec -it alcha-mongodb mongosh -u admin -p adminpassword --authenticationDatabase admin --eval "
use alcha_events;
var stats = db.getCollection('realtime-storage-data').stats(1024*1024);
print('=== MongoDB 실제 데이터 ===');
print('컬렉션: realtime-storage-data');
print('데이터 크기: ' + stats.size + ' MB');
print('저장 공간: ' + stats.storageSize + ' MB');
print('인덱스 크기: ' + stats.totalIndexSize + ' MB');
print('문서 수: ' + stats.count);
"
```

### TimescaleDB (실제 데이터)
```bash
# Docker 컨테이너 내에서 실행
docker exec -it alcha-timescaledb psql -U alcha -d alcha_events -c "
SELECT 
    'vehicle_telemetry' AS table_name,
    pg_size_pretty(pg_total_relation_size('vehicle_telemetry')) AS total_size,
    pg_size_pretty(pg_relation_size('vehicle_telemetry')) AS table_size,
    pg_size_pretty(pg_indexes_size('vehicle_telemetry')) AS indexes_size,
    (SELECT COUNT(*) FROM vehicle_telemetry) AS row_count;
"
```

---

## 📝 용량 비교 체크리스트

동일한 432,000개 레코드를 비교할 때:

1. ✅ MongoDB `write_performance_test` 컬렉션
2. ✅ TimescaleDB `write_performance_test` 테이블
3. ✅ 실제 운영 데이터: MongoDB `realtime-storage-data` vs TimescaleDB `vehicle_telemetry`

**참고**: MongoDB는 문서 기반이라 필드명도 저장 공간에 포함되므로, 일반적으로 같은 데이터를 저장할 때 MongoDB가 더 큰 공간을 차지할 수 있습니다.


