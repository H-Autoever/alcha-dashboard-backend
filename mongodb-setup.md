# MongoDB 설정 및 데이터 구조 가이드

## 📋 개요
이 문서는 Alcha Dashboard 프로젝트의 MongoDB 설정, 초기화 과정, 그리고 사용되는 데이터 구조에 대해 설명합니다.

## 🚀 MongoDB 컨테이너 실행

### 1. MongoDB 컨테이너 실행
```bash
docker run -d --name alcha-mongodb --network alcha-net -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=adminpassword \
  mongo:7.0
```

### 2. 연결 정보
- **호스트**: localhost (또는 alcha-mongodb)
- **포트**: 27017
- **사용자명**: admin
- **비밀번호**: adminpassword
- **인증 데이터베이스**: admin

## 🗄️ 데이터베이스 구조

### 데이터베이스: `alcha_events`
MongoDB에서 사용하는 데이터베이스명은 `alcha_events`입니다.

### 컬렉션 1: `engine_off_events`
엔진이 꺼진 상태에서 발생하는 이벤트들을 저장합니다.

#### 스키마 구조:
```javascript
{
  _id: ObjectId,                    // MongoDB 자동 생성 ID
  vehicle_id: String,               // 차량 고유 ID (예: "VHC-001")
  speed: Number,                    // 속도 (km/h, 항상 0)
  gear_status: String,              // 기어 상태 ("P", "R", "N", "D")
  gyro: Number,                     // 자이로 센서 값 (도)
  side: String,                     // 측면 ("left", "right")
  ignition: Boolean,                // 점화 상태 (항상 false)
  timestamp: Date,                  // 이벤트 발생 시간
  created_at: Date                  // 레코드 생성 시간
}
```

#### 샘플 데이터:
```javascript
{
  vehicle_id: "VHC-001",
  speed: 0,
  gear_status: "P",
  gyro: 15.2,
  side: "left",
  ignition: false,
  timestamp: ISODate("2024-10-02T14:30:00Z"),
  created_at: ISODate("2025-10-19T10:22:19.907Z")
}
```

### 컬렉션 2: `collision_events`
차량 충돌 이벤트들을 저장합니다.

#### 스키마 구조:
```javascript
{
  _id: ObjectId,                    // MongoDB 자동 생성 ID
  vehicle_id: String,               // 차량 고유 ID (예: "VHC-001")
  damage: Number,                   // 손상도 (1-5 스케일)
  timestamp: Date,                  // 충돌 발생 시간
  created_at: Date                  // 레코드 생성 시간
}
```

#### 샘플 데이터:
```javascript
{
  vehicle_id: "VHC-001",
  damage: 3,
  timestamp: ISODate("2024-10-03T16:45:00Z"),
  created_at: ISODate("2025-10-19T10:22:19.920Z")
}
```

## 🔧 초기화 스크립트

### MongoDB 초기화 스크립트 (`init_mongodb.js`)
```javascript
// MongoDB 초기화 스크립트
db = db.getSiblingDB('alcha_events');

// 기존 데이터 삭제
db.engine_off_events.deleteMany({});
db.collision_events.deleteMany({});

// Engine Off Events 삽입
db.engine_off_events.insertMany([
  {
    vehicle_id: 'VHC-001',
    speed: 0,
    gear_status: 'P',
    gyro: 15.2,
    side: 'left',
    ignition: false,
    timestamp: new Date('2024-10-02T14:30:00Z'),
    created_at: new Date()
  },
  {
    vehicle_id: 'VHC-001',
    speed: 0,
    gear_status: 'P',
    gyro: 12.8,
    side: 'right',
    ignition: false,
    timestamp: new Date('2024-10-04T09:15:00Z'),
    created_at: new Date()
  },
  {
    vehicle_id: 'VHC-002',
    speed: 0,
    gear_status: 'P',
    gyro: 18.5,
    side: 'left',
    ignition: false,
    timestamp: new Date('2024-10-03T11:20:00Z'),
    created_at: new Date()
  },
  {
    vehicle_id: 'VHC-003',
    speed: 0,
    gear_status: 'P',
    gyro: 22.1,
    side: 'right',
    ignition: false,
    timestamp: new Date('2024-10-01T16:45:00Z'),
    created_at: new Date()
  }
]);

// Collision Events 삽입
db.collision_events.insertMany([
  {
    vehicle_id: 'VHC-001',
    damage: 3,
    timestamp: new Date('2024-10-03T16:45:00Z'),
    created_at: new Date()
  },
  {
    vehicle_id: 'VHC-002',
    damage: 1,
    timestamp: new Date('2024-10-02T08:30:00Z'),
    created_at: new Date()
  },
  {
    vehicle_id: 'VHC-003',
    damage: 4,
    timestamp: new Date('2024-10-04T13:15:00Z'),
    created_at: new Date()
  }
]);

print('MongoDB 이벤트 데이터 초기화 완료!');
print('Engine Off Events 개수:', db.engine_off_events.countDocuments());
print('Collision Events 개수:', db.collision_events.countDocuments());
```

### 초기화 실행 방법:
```bash
# 1. 스크립트 파일을 컨테이너에 복사
docker cp init_mongodb.js alcha-mongodb:/tmp/init_mongodb.js

# 2. 스크립트 실행
docker exec -i alcha-mongodb mongosh --username admin --password adminpassword --authenticationDatabase admin /tmp/init_mongodb.js
```

## 📊 데이터 상세 정보

### 차량별 이벤트 데이터 요약:

#### VHC-001 (Hyundai Ioniq 5)
- **Engine Off Events**: 2개
  - 2024-10-02 14:30:00: 자이로 15.2°, 왼쪽
  - 2024-10-04 09:15:00: 자이로 12.8°, 오른쪽
- **Collision Events**: 1개
  - 2024-10-03 16:45:00: 손상도 3/5

#### VHC-002 (Kia EV6)
- **Engine Off Events**: 1개
  - 2024-10-03 11:20:00: 자이로 18.5°, 왼쪽
- **Collision Events**: 1개
  - 2024-10-02 08:30:00: 손상도 1/5

#### VHC-003 (Genesis GV60)
- **Engine Off Events**: 1개
  - 2024-10-01 16:45:00: 자이로 22.1°, 오른쪽
- **Collision Events**: 1개
  - 2024-10-04 13:15:00: 손상도 4/5

## 🔌 API 엔드포인트

### 1. 특정 차량의 모든 이벤트 조회
```
GET /api/events/{vehicle_id}
```

**응답 예시:**
```json
{
  "vehicle_id": "VHC-001",
  "engine_off_events": [
    {
      "_id": "68f4bbdb348e61a5ac4f87fe",
      "vehicle_id": "VHC-001",
      "speed": 0,
      "gear_status": "P",
      "gyro": 15.2,
      "side": "left",
      "ignition": false,
      "timestamp": "2024-10-02T14:30:00",
      "created_at": "2025-10-19T10:22:19.907000"
    }
  ],
  "collision_events": [
    {
      "_id": "68f4bbdb348e61a5ac4f8802",
      "vehicle_id": "VHC-001",
      "damage": 3,
      "timestamp": "2024-10-03T16:45:00",
      "created_at": "2025-10-19T10:22:19.920000"
    }
  ]
}
```

### 2. 특정 차량의 이벤트 요약 정보
```
GET /api/events/{vehicle_id}/summary
```

**응답 예시:**
```json
{
  "vehicle_id": "VHC-001",
  "total_engine_off_events": 2,
  "total_collision_events": 1,
  "total_events": 3
}
```

## 🛠️ 백엔드 설정

### MongoDB 연결 설정 (`app/mongodb.py`)
```python
from motor.motor_asyncio import AsyncIOMotorClient
import os
from typing import Optional

class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    database = None

mongodb = MongoDB()

async def get_mongodb() -> AsyncIOMotorClient:
    return mongodb.client

async def connect_to_mongo():
    """MongoDB 연결"""
    mongodb.client = AsyncIOMotorClient(
        f"mongodb://admin:adminpassword@alcha-mongodb:27017/?authSource=admin"
    )
    mongodb.database = mongodb.client.alcha_events
    print("MongoDB 연결 성공!")

async def close_mongo_connection():
    """MongoDB 연결 종료"""
    if mongodb.client:
        mongodb.client.close()
        print("MongoDB 연결 종료!")
```

### 의존성 (`requirements.txt`)
```
pymongo==4.6.1
motor==3.3.2
```

## 🔍 데이터 조회 예시

### MongoDB 셸에서 직접 조회:
```javascript
// 데이터베이스 선택
use alcha_events

// 모든 Engine Off Events 조회
db.engine_off_events.find().pretty()

// 특정 차량의 충돌 이벤트 조회
db.collision_events.find({vehicle_id: "VHC-001"}).pretty()

// 날짜 범위로 이벤트 조회
db.engine_off_events.find({
  timestamp: {
    $gte: new Date("2024-10-01"),
    $lte: new Date("2024-10-05")
  }
}).pretty()

// 손상도가 높은 충돌 이벤트 조회
db.collision_events.find({damage: {$gte: 3}}).pretty()
```

## 📈 프론트엔드 시각화

### X-Y축 차트 구조:
- **X축**: 날짜 (시간 순서)
- **Y축**: 이벤트 타입
  - 상단 라인: 충돌 이벤트 (빨간색)
  - 하단 라인: 엔진 오프 이벤트 (주황색)

### 이벤트 포인트:
- **원형 마커**: 각 이벤트를 원으로 표시
- **색상 구분**: 
  - 빨간색 (#ef4444): 충돌 이벤트
  - 주황색 (#f59e0b): 엔진 오프 이벤트
- **호버 효과**: 마우스 오버 시 상세 정보 툴팁

## 🚨 주의사항

1. **데이터 일관성**: `vehicle_id`는 MySQL의 `basic_info` 테이블과 일치해야 합니다.
2. **타임스탬프**: 모든 시간은 UTC 기준으로 저장됩니다.
3. **인덱스**: 대용량 데이터의 경우 `vehicle_id`와 `timestamp`에 인덱스를 생성하는 것을 권장합니다.
4. **백업**: 운영 환경에서는 정기적인 MongoDB 백업을 설정해야 합니다.

## 🔄 데이터 업데이트

실제 운영 환경에서는 Airflow를 통해 일일 데이터 업데이트가 이루어집니다:
- **Engine Off Events**: 차량 센서 데이터에서 실시간 수집
- **Collision Events**: 충돌 감지 시스템에서 발생 시 즉시 기록
- **데이터 보존**: 필요에 따라 오래된 데이터 아카이빙 정책 수립
