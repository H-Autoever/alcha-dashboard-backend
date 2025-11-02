# TimescaleDB와 MongoDB 사용 이유 분석

## 📊 개요

Alcha Dashboard 프로젝트는 두 가지 데이터베이스를 활용하여 차량 텔레메트리 데이터를 효율적으로 관리합니다:
- **TimescaleDB**: 시계열 데이터 저장 및 분석용
- **MongoDB**: 초기 데이터 수집 및 유연한 이벤트 스키마 저장용

---

## 🗄️ TimescaleDB 사용 이유

### 1. **시계열 데이터 최적화**

TimescaleDB는 PostgreSQL 기반의 시계열 데이터베이스로, **1초 단위의 텔레메트리 데이터**를 저장하고 쿼리하는 데 최적화되어 있습니다.

#### 사용 사례:
- `vehicle_telemetry` 테이블: 차량 속도, 엔진 RPM, 스로틀 위치를 1초마다 기록
- 시간 범위 기반 쿼리: 특정 시간대의 데이터를 빠르게 조회
- 시계열 집계 연산: 시간 기반 통계 계산

#### 코드 예시:
```140:145:alcha-dashboard-backend/app/timescaledb.py
        # TimescaleDB 하이퍼테이블로 변환
        cursor.execute("SELECT create_hypertable('engine_off_events', 'timestamp', if_not_exists => TRUE);")
        cursor.execute("SELECT create_hypertable('collision_events', 'timestamp', if_not_exists => TRUE);")
        cursor.execute("SELECT create_hypertable('vehicle_telemetry', 'timestamp', if_not_exists => TRUE);")
        cursor.execute("SELECT create_hypertable('periodic_data', 'timestamp', if_not_exists => TRUE);")
        cursor.execute("SELECT create_hypertable('sudden_acceleration_events', 'timestamp', if_not_exists => TRUE);")
```

**하이퍼테이블(Hypertable)**: TimescaleDB의 핵심 기능으로, 시계열 데이터를 자동으로 파티셔닝하여 성능을 최적화합니다.

### 2. **고성능 시간 범위 쿼리**

시계열 데이터는 시간 순서로 정렬되어 저장되며, 시간 범위 기반 쿼리가 매우 빠릅니다.

#### 코드 예시:
```278:319:alcha-dashboard-backend/app/timescaledb.py
def get_telemetry_data(vehicle_id: str, start_time: str = None, end_time: str = None) -> List[Dict[str, Any]]:
    """특정 차량의 텔레메트리 데이터 조회"""
    conn = get_timescaledb_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 시간 범위 조건 설정
        time_condition = ""
        params = [vehicle_id]
        
        if start_time and end_time:
            time_condition = "AND timestamp BETWEEN %s AND %s"
            params.extend([start_time, end_time])
        elif start_time:
            time_condition = "AND timestamp >= %s"
            params.append(start_time)
        elif end_time:
            time_condition = "AND timestamp <= %s"
            params.append(end_time)
        
        query = f"""
            SELECT vehicle_id, vehicle_speed, engine_rpm, throttle_position, timestamp
            FROM vehicle_telemetry
            WHERE vehicle_id = %s {time_condition}
            ORDER BY timestamp ASC
        """
        
        cursor.execute(query, params)
        telemetry_data = []
        for row in cursor.fetchall():
            telemetry_data.append({
                "vehicle_id": row["vehicle_id"],
                "vehicle_speed": row["vehicle_speed"],
                "engine_rpm": row["engine_rpm"],
                "throttle_position": row["throttle_position"],
                "timestamp": row["timestamp"].isoformat()
            })
        
        return telemetry_data
```

### 3. **배치 삽입 성능**

TimescaleDB는 대량의 시계열 데이터 삽입에 최적화되어 있습니다.

#### 코드 예시:
```245:276:alcha-dashboard-backend/app/timescaledb.py
def batch_write_telemetry_data(data_list: List[Dict[str, Any]]):
    """배치로 텔레메트리 데이터 기록 (성능 최적화)"""
    conn = get_timescaledb_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # 배치 삽입
        args = [(
            d['vehicle_id'],
            d['vehicle_speed'],
            d['engine_rpm'],
            d['throttle_position'],
            d['timestamp']
        ) for d in data_list]
        
        cursor.executemany("""
            INSERT INTO vehicle_telemetry (vehicle_id, vehicle_speed, engine_rpm, throttle_position, timestamp)
            VALUES (%s, %s, %s, %s, %s)
        """, args)
        
        conn.commit()
        print(f"Successfully wrote {len(data_list)} telemetry records")
        return True
    except Exception as e:
        print(f"Failed to batch write telemetry data: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
```

### 4. **SQL 기반 복잡한 쿼리**

표준 SQL을 사용하여 복잡한 조인, 집계, 분석 쿼리를 수행할 수 있습니다.

---

## 🍃 MongoDB 사용 이유

### 1. **유연한 스키마**

MongoDB는 스키마 없는 문서형 데이터베이스로, **다양한 형태의 이벤트 데이터**를 동일한 컬렉션에 저장할 수 있습니다.

#### 사용 사례:
- `realtime-storage-data`: 실시간 텔레메트리 데이터 (초당 1개)
- `periodic-storage-data`: 주기적 데이터 (10분마다)
- `event-collision`: 충돌 이벤트
- `event-sudden-acceleration`: 급가속 이벤트
- `event-engine-status`: 엔진 상태 이벤트
- `event-warning-light`: 경고등 이벤트

#### 코드 예시:
```74:148:alcha-dashboard-backend/scripts/generate_mongodb_data.py
def generate_realtime_data():
    """실시간 텔레메트리 데이터 생성 (1시간 × 3차량 = 10,800개)"""
    print("📊 실시간 텔레메트리 데이터 생성 중...")
    
    realtime_data = []
    total_records = 0
    
    for vehicle_id in VEHICLE_IDS:
        print(f"  - {vehicle_id} 데이터 생성 중...")
        vehicle_data = []
        
        for i in range(3600):  # 1시간 = 3600초
            current_time = BASE_TIMESTAMP + timedelta(seconds=i)
            
            # 기본 차량 상태 시뮬레이션
            base_speed = random.uniform(20, 80)  # 20-80 km/h
            speed_variation = random.uniform(-5, 5)
            vehicle_speed = max(0, base_speed + speed_variation)
            
            # 엔진 RPM (속도에 비례)
            engine_rpm = int(800 + (vehicle_speed * 30) + random.uniform(-200, 200))
            engine_rpm = max(600, min(6000, engine_rpm))
            
            # 스로틀 위치 (속도 변화에 따라)
            throttle_position = random.uniform(10, 80)
            
            # 기어 상태
            gear_modes = ["P", "R", "N", "D"]
            gear_position_mode = random.choice(gear_modes)
            gear_position_current_gear = random.randint(1, 6) if gear_position_mode == "D" else 0
            
            # 자이로 센서 (차량 움직임 시뮬레이션)
            gyro_yaw_rate = random.uniform(-2, 2)
            gyro_pitch_rate = random.uniform(-1, 1)
            gyro_roll_rate = random.uniform(-1, 1)
            
            # 온도 (엔진 가동에 따라)
            engine_temp = random.uniform(75, 95)
            coolant_temp = random.uniform(78, 88)
            
            # 브레이크 상태
            side_brake_status = "ON" if vehicle_speed < 1 else "OFF"
            brake_pressure = random.uniform(5, 15)
            
            record = {
                "vehicle_id": vehicle_id,
                "vehicle_speed": round(vehicle_speed, 6),
                "engine_rpm": engine_rpm,
                "engine_status_ignition": "ON",
                "throttle_position": round(throttle_position, 6),
                "wheel_speed_front_left": round(vehicle_speed + random.uniform(-0.5, 0.5), 6),
                "wheel_speed_front_right": round(vehicle_speed + random.uniform(-0.5, 0.5), 6),
                "wheel_speed_rear_left": round(vehicle_speed + random.uniform(-0.5, 0.5), 6),
                "wheel_speed_rear_right": round(vehicle_speed + random.uniform(-0.5, 0.5), 6),
                "gear_position_mode": gear_position_mode,
                "gear_position_current_gear": gear_position_current_gear,
                "gyro_yaw_rate": round(gyro_yaw_rate, 6),
                "gyro_pitch_rate": round(gyro_pitch_rate, 6),
                "gyro_roll_rate": round(gyro_roll_rate, 6),
                "engine_temp": round(engine_temp, 6),
                "coolant_temp": round(coolant_temp, 6),
                "side_brake_status": side_brake_status,
                "brake_pressure": round(brake_pressure, 1),
                "timestamp": current_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            }
            
            vehicle_data.append(record)
        
        realtime_data.extend(vehicle_data)
        total_records += len(vehicle_data)
        print(f"    ✅ {len(vehicle_data)}개 레코드 생성 완료")
    
    print(f"✅ 총 {total_records}개 실시간 텔레메트리 데이터 생성 완료")
    return realtime_data
```

MongoDB는 이런 복잡한 구조를 별도 스키마 정의 없이 저장할 수 있습니다.

### 2. **빠른 쓰기 성능 (초기 수집)**

실시간 데이터 수집 단계에서는 **높은 쓰기 처리량**이 필요하며, MongoDB는 대량의 문서 삽입에 효율적입니다.

#### 코드 예시:
```350:367:alcha-dashboard-backend/scripts/generate_mongodb_data.py
def insert_data_to_mongodb(db, all_data):
    """MongoDB에 데이터 삽입"""
    print("💾 MongoDB에 데이터 삽입 중...")
    
    total_inserted = 0
    
    for collection_name, data in all_data.items():
        if data:
            try:
                result = db[collection_name].insert_many(data)
                inserted_count = len(result.inserted_ids)
                total_inserted += inserted_count
                print(f"  ✅ {collection_name}: {inserted_count}개 삽입 완료")
            except Exception as e:
                print(f"  ❌ {collection_name} 삽입 실패: {e}")
    
    print(f"✅ 총 {total_inserted}개 레코드 삽입 완료")
    return total_inserted
```

### 3. **데이터 마이그레이션 파이프라인**

MongoDB에서 수집된 데이터를 정제하여 TimescaleDB로 마이그레이션하는 구조를 사용합니다.

#### 마이그레이션 흐름:
```
실시간 데이터 수집 (MongoDB)
    ↓
데이터 검증 및 정제
    ↓
TimescaleDB 마이그레이션 (migrate_mongodb_to_timescaledb.py)
    ↓
시계열 분석 및 쿼리 (TimescaleDB)
```

#### 코드 예시:
```61:103:alcha-dashboard-backend/scripts/migrate_mongodb_to_timescaledb.py
def migrate_realtime_data(db):
    """실시간 텔레메트리 데이터 마이그레이션"""
    print("📊 실시간 텔레메트리 데이터 마이그레이션 중...")
    
    try:
        collection = db["realtime_data"]
        total_count = collection.count_documents({})
        print(f"  - 총 {total_count}개 레코드 처리 예정")
        
        # 배치 단위로 처리 (1000개씩)
        batch_size = 1000
        processed = 0
        batch_data = []
        
        for doc in collection.find().sort("timestamp", 1):
            # MongoDB 문서를 TimescaleDB 형식으로 변환
            telemetry_record = {
                "vehicle_id": convert_vehicle_id(doc["vehicle_id"]),
                "vehicle_speed": doc["vehicle_speed"],
                "engine_rpm": doc["engine_rpm"],
                "throttle_position": doc["throttle_position"],
                "timestamp": doc["timestamp"]
            }
            
            batch_data.append(telemetry_record)
            processed += 1
            
            # 배치가 가득 찼거나 마지막 레코드인 경우 삽입
            if len(batch_data) >= batch_size or processed == total_count:
                if batch_write_telemetry_data(batch_data):
                    print(f"  ✅ 배치 {processed}/{total_count} 처리 완료")
                else:
                    print(f"  ❌ 배치 {processed}/{total_count} 처리 실패")
                    return False
                batch_data = []
        
        print(f"✅ 실시간 텔레메트리 데이터 마이그레이션 완료 ({processed}개)")
        return True
        
    except Exception as e:
        print(f"❌ 실시간 텔레메트리 데이터 마이그레이션 실패: {e}")
        return False
```

---

## 📈 데이터 흐름 비교

### MongoDB (초기 수집 단계)
- **역할**: 원본 데이터 수집 및 임시 저장
- **특징**: 
  - 빠른 쓰기 성능
  - 유연한 스키마
  - 다양한 이벤트 타입 수용
- **사용 컬렉션**:
  - `realtime-storage-data`: 실시간 텔레메트리 (초당 1개)
  - `periodic-storage-data`: 주기적 데이터 (10분마다)
  - `event-*`: 다양한 이벤트 타입

### TimescaleDB (분석 및 쿼리 단계)
- **역할**: 시계열 데이터 분석 및 고성능 쿼리
- **특징**:
  - 시계열 최적화 (하이퍼테이블)
  - 시간 범위 쿼리 성능
  - SQL 기반 복잡한 분석
- **사용 테이블**:
  - `vehicle_telemetry`: 1초 단위 텔레메트리
  - `periodic_data`: 주기적 센서 데이터
  - `*_events`: 정규화된 이벤트 테이블

---

## 🎯 결론

### 📊 핵심 요약

| 데이터베이스 | 주요 역할 | 핵심 특징 | 사용 이유 |
|------------|----------|----------|----------|
| **🍃 MongoDB** | 초기 데이터 수집 및 유연한 이벤트 스키마 저장 | • 빠른 쓰기 성능<br>• 스키마 없는 문서형<br>• 다양한 이벤트 타입 수용 | 다양한 형태의 원본 데이터를 스키마 정의 없이 빠르게 수집하고 저장 |
| **⏱️ TimescaleDB** | 시계열 데이터 분석 및 고성능 쿼리 | • 시계열 최적화 (하이퍼테이블)<br>• 시간 범위 쿼리 성능<br>• SQL 기반 복잡한 분석 | 1초 단위 대량 데이터의 효율적 저장 및 시간 기반 분석 쿼리 최적화 |

### 🔄 데이터 흐름 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                     차량 텔레메트리 데이터 수집                      │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
        ┌──────────────────────────────────────┐
        │     🍃 MongoDB (임시 저장)              │
        │  • 유연한 스키마                        │
        │  • 빠른 쓰기                           │
        │  • 다양한 이벤트 타입                    │
        └──────────────────┬───────────────────┘
                            │
                            │ 데이터 정제 및 변환
                            ▼
        ┌──────────────────────────────────────┐
        │   ⏱️ TimescaleDB (분석용)              │
        │  • 시계열 최적화                       │
        │  • 고성능 시간 범위 쿼리                │
        │  • SQL 기반 복잡한 분석                 │
        └───────────────────────────────────────┘
```

### ✅ 각 데이터베이스의 핵심 가치

#### 🍃 MongoDB - "유연성과 빠른 수집"
- ✅ **다양한 형태의 데이터를 빠르게 수집**
  - 초당 수천 건의 텔레메트리 데이터 수집
  - 다양한 센서 데이터를 동일한 컬렉션에 저장
  - 구조 변경 없이 새로운 이벤트 타입 추가 가능
  
- ✅ **스키마 변경 없이 새로운 이벤트 타입 추가 가능**
  - 실시간 데이터 수집 단계에서 스키마 정의 불필요
  - 유연한 문서 구조로 다양한 데이터 구조 수용
  - 빠른 프로토타이핑 및 개발 반복 가능

#### ⏱️ TimescaleDB - "시계열 분석의 최적화"
- ✅ **1초 단위 대량 데이터의 효율적 저장 및 조회**
  - 하이퍼테이블을 통한 자동 파티셔닝
  - 대량 데이터 삽입 시 성능 최적화
  - 시간 기반 인덱싱으로 빠른 조회

- ✅ **시간 기반 분석 쿼리 최적화**
  - 시간 범위 쿼리 성능 최적화
  - 집계 연산 및 통계 분석 효율화
  - 시계열 전용 함수 및 연산 지원

- ✅ **SQL을 통한 복잡한 분석 작업 지원**
  - 표준 SQL을 통한 복잡한 조인 및 집계
  - 기존 PostgreSQL 생태계 활용 가능
  - 다양한 분석 도구 및 라이브러리 호환

### 🏗️ 하이브리드 아키텍처의 장점

이러한 **하이브리드 아키텍처**를 통해 각 데이터베이스의 장점을 최대한 활용하고 있습니다:

1. **역할 분리**: 수집 단계(MongoDB)와 분석 단계(TimescaleDB)의 명확한 역할 분리
2. **성능 최적화**: 각 단계에서 가장 적합한 데이터베이스 사용
3. **확장성**: 각 데이터베이스를 독립적으로 스케일링 가능
4. **유연성**: MongoDB의 유연한 스키마와 TimescaleDB의 구조화된 분석 결합

---

## 🔍 다른 데이터베이스와의 비교

### 1. MySQL vs MongoDB (초기 수집 단계)

#### MySQL을 사용하지 않은 이유

| 항목 | MySQL | MongoDB (선택) |
|-----|------|---------------|
| **스키마 유연성** | ❌ 고정 스키마 필요 | ✅ 스키마 없는 문서형 |
| **초기 수집 성능** | ⚠️ 스키마 변경 필요 시 성능 저하 | ✅ 빠른 쓰기 성능 |
| **이벤트 타입 추가** | ❌ ALTER TABLE 필요 | ✅ 스키마 변경 불필요 |
| **복잡한 중첩 구조** | ❌ 정규화 필요 | ✅ JSON 문서로 자연스럽게 저장 |

**결론**: 실시간 데이터 수집 단계에서는 **스키마 유연성**이 중요하며, MySQL은 고정 스키마로 인해 다양한 형태의 이벤트를 빠르게 수집하기 어렵습니다.

### 2. PostgreSQL vs TimescaleDB (시계열 분석 단계)

#### PostgreSQL을 사용하지 않은 이유

| 항목 | PostgreSQL (일반) | TimescaleDB (선택) |
|-----|------------------|-------------------|
| **시계열 최적화** | ❌ 일반 RDBMS | ✅ 시계열 전용 최적화 |
| **하이퍼테이블** | ❌ 수동 파티셔닝 필요 | ✅ 자동 파티셔닝 |
| **시간 범위 쿼리** | ⚠️ 인덱스 최적화 필요 | ✅ 시간 기반 인덱싱 최적화 |
| **대량 데이터 삽입** | ⚠️ 성능 튜닝 필요 | ✅ 배치 삽입 최적화 |

**결론**: PostgreSQL은 강력하지만, **1초 단위의 대량 시계열 데이터**를 처리하기 위해서는 TimescaleDB의 시계열 최적화 기능이 필수적입니다.

**참고**: TimescaleDB는 PostgreSQL 확장(Extension)이므로 PostgreSQL의 모든 기능을 사용할 수 있습니다.

### 3. InfluxDB vs TimescaleDB (시계열 데이터베이스)

#### InfluxDB를 사용하지 않은 이유

| 항목 | InfluxDB | TimescaleDB (선택) |
|-----|----------|-------------------|
| **SQL 지원** | ❌ InfluxQL (비표준) | ✅ 표준 SQL |
| **복잡한 조인** | ❌ 제한적 | ✅ 완전한 SQL 조인 지원 |
| **PostgreSQL 호환성** | ❌ 별도 학습 필요 | ✅ PostgreSQL 기반 |
| **시계열 최적화** | ✅ 매우 우수 | ✅ 우수 |
| **트랜잭션** | ❌ 제한적 | ✅ ACID 트랜잭션 |

**결론**: **표준 SQL과 PostgreSQL 생태계**를 활용하기 위해 TimescaleDB를 선택했습니다. 복잡한 조인 및 분석 쿼리가 필요한 경우 TimescaleDB가 더 적합합니다.

### 4. Redis vs MongoDB (임시 저장)

#### Redis를 사용하지 않은 이유

| 항목 | Redis (인메모리) | MongoDB (선택) |
|-----|----------------|--------------|
| **데이터 영속성** | ⚠️ 주로 인메모리 | ✅ 디스크 저장 |
| **대용량 데이터** | ❌ 메모리 제한 | ✅ 디스크 기반 확장 |
| **복잡한 구조** | ❌ 단순 키-값 | ✅ 복잡한 문서 구조 |
| **장기 저장** | ❌ 부적합 | ✅ 적합 |

**결론**: **장기 저장 및 대용량 데이터** 처리가 필요하므로 MongoDB를 선택했습니다. Redis는 캐싱이나 세션 저장에 적합하지만, 텔레메트리 데이터 저장에는 부적합합니다.

### 5. MySQL + Redis vs MongoDB + TimescaleDB (전체 아키텍처)

#### 다른 옵션과의 비교

| 아키텍처 옵션 | 장점 | 단점 |
|-------------|------|------|
| **MySQL + Redis** | • 안정성<br>• 널리 사용됨 | • 시계열 최적화 부족<br>• 복잡한 스키마 관리 필요 |
| **PostgreSQL + Redis** | • 강력한 RDBMS<br>• 캐싱 가능 | • 시계열 최적화 부족<br>• 별도 캐시 관리 필요 |
| **MongoDB + TimescaleDB** ✅ | • 유연한 수집<br>• 시계열 최적화<br>• 역할 분리 명확 | • 두 시스템 관리 필요 |

**결론**: **MongoDB + TimescaleDB 조합**이 텔레메트리 데이터의 수집과 분석이라는 두 가지 목적을 가장 효율적으로 달성할 수 있습니다.

---

## 📋 선택 기준 요약

### MongoDB 선택 기준 ✅
1. ✅ **유연한 스키마**: 다양한 형태의 이벤트 데이터 수집
2. ✅ **빠른 쓰기 성능**: 초당 수천 건의 데이터 수집
3. ✅ **스키마 변경 없이 확장**: 새로운 이벤트 타입 추가 용이

### TimescaleDB 선택 기준 ✅
1. ✅ **시계열 최적화**: 하이퍼테이블 및 시간 기반 인덱싱
2. ✅ **표준 SQL**: 복잡한 분석 쿼리 작성 용이
3. ✅ **PostgreSQL 기반**: 기존 도구 및 생태계 활용 가능
4. ✅ **고성능 시간 범위 쿼리**: 대량 시계열 데이터 조회 최적화

### 사용하지 않은 데이터베이스 선택 불가 이유 ❌
- **MySQL**: 고정 스키마로 유연한 이벤트 수집 어려움
- **PostgreSQL (일반)**: 시계열 최적화 기능 부족
- **InfluxDB**: 비표준 쿼리 언어 및 복잡한 조인 제한
- **Redis**: 메모리 제한 및 장기 저장 부적합

이러한 비교를 통해 **MongoDB + TimescaleDB 하이브리드 아키텍처**가 이 프로젝트에 가장 적합한 선택임을 확인할 수 있습니다.
