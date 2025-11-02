# Docker로 MongoDB와 TimescaleDB 구축 가이드

## 📋 개요

이 가이드는 `docker-compose.yml`을 사용하여 MongoDB와 TimescaleDB를 구축하는 방법을 설명합니다.

## 🚀 시작하기

### 1. Docker Compose 실행

```bash
# 프로젝트 루트 디렉터리에서 실행
docker-compose up -d
```

이 명령으로 다음 서비스가 시작됩니다:
- **MongoDB**: 포트 27017
- **TimescaleDB**: 포트 5432

### 2. 서비스 상태 확인

```bash
# 실행 중인 컨테이너 확인
docker-compose ps

# 로그 확인
docker-compose logs -f

# 특정 서비스 로그 확인
docker-compose logs -f mongodb
docker-compose logs -f timescaledb
```

## 🔧 데이터베이스 설정

### MongoDB 설정

#### 연결 정보
- **호스트**: `localhost` (로컬) 또는 `mongodb` (Docker 네트워크 내)
- **포트**: `27017`
- **사용자명**: `admin`
- **비밀번호**: `adminpassword`
- **데이터베이스**: `alcha_events`
- **인증 데이터베이스**: `admin`

#### 환경 변수
`generate_mongodb_data.py` 스크립트에서 사용하는 환경 변수:
```bash
export MONGO_HOST=localhost
export MONGO_PORT=27017
export MONGO_DB=alcha_events
export MONGO_USER=admin
export MONGO_PASSWORD=adminpassword
```

#### MongoDB 연결 테스트
```bash
# MongoDB 컨테이너에 접속
docker exec -it alcha-mongodb mongosh -u admin -p adminpassword --authenticationDatabase admin

# 또는 mongosh가 설치되어 있다면
mongosh "mongodb://admin:adminpassword@localhost:27017/?authSource=admin"
```

#### MongoDB 데이터 생성
```bash
cd alcha-dashboard-backend/scripts

# 환경 변수 설정
export MONGO_HOST=localhost
export MONGO_PORT=27017
export MONGO_DB=alcha_events
export MONGO_USER=admin
export MONGO_PASSWORD=adminpassword

# MongoDB 데이터 생성
python3 generate_mongodb_data.py
```

### TimescaleDB 설정

#### 연결 정보
- **호스트**: `localhost` (로컬) 또는 `alcha-timescaledb` (Docker 네트워크 내)
- **포트**: `5432`
- **사용자명**: `alcha`
- **비밀번호**: `alcha_password`
- **데이터베이스**: `alcha_events`

#### 환경 변수
`migrate_mongodb_to_timescaledb.py` 스크립트와 `app/timescaledb.py`에서 사용하는 환경 변수:
```bash
export TIMESCALEDB_HOST=localhost
export TIMESCALEDB_PORT=5432
export TIMESCALEDB_DB=alcha_events
export TIMESCALEDB_USER=alcha
export TIMESCALEDB_PASSWORD=alcha_password
```

#### TimescaleDB 연결 테스트
```bash
# TimescaleDB 컨테이너에 접속
docker exec -it alcha-timescaledb psql -U alcha -d alcha_events

# 또는 psql이 설치되어 있다면
psql -h localhost -p 5432 -U alcha -d alcha_events
# 비밀번호: alcha_password
```

#### TimescaleDB 초기화 및 데이터 마이그레이션
```bash
cd alcha-dashboard-backend/scripts

# 환경 변수 설정
export TIMESCALEDB_HOST=localhost
export TIMESCALEDB_PORT=5432
export TIMESCALEDB_DB=alcha_events
export TIMESCALEDB_USER=alcha
export TIMESCALEDB_PASSWORD=alcha_password

# MongoDB에서 TimescaleDB로 데이터 마이그레이션
python3 migrate_mongodb_to_timescaledb.py
```

## 📊 데이터베이스 사용 순서

### 1단계: MongoDB 데이터 생성
```bash
# MongoDB에 원본 데이터 생성
python3 generate_mongodb_data.py
```

이 스크립트는 다음 컬렉션을 생성합니다:
- `realtime-storage-data`: 실시간 텔레메트리 데이터 (초당 1개)
- `periodic-storage-data`: 주기적 데이터 (10분마다)
- `event-collision`: 충돌 이벤트
- `event-sudden-acceleration`: 급가속 이벤트
- `event-engine-status`: 엔진 상태 이벤트
- `event-warning-light`: 경고등 이벤트

### 2단계: TimescaleDB 초기화 및 마이그레이션
```bash
# MongoDB 데이터를 TimescaleDB로 마이그레이션
python3 migrate_mongodb_to_timescaledb.py
```

이 스크립트는:
1. TimescaleDB 초기화 (테이블 생성 및 하이퍼테이블 설정)
2. MongoDB 데이터를 TimescaleDB로 변환 및 삽입

## 🛠️ 유용한 명령어

### 서비스 관리
```bash
# 서비스 시작
docker-compose up -d

# 서비스 중지
docker-compose stop

# 서비스 중지 및 제거
docker-compose down

# 볼륨까지 삭제 (데이터 초기화)
docker-compose down -v

# 서비스 재시작
docker-compose restart

# 특정 서비스만 재시작
docker-compose restart mongodb
docker-compose restart timescaledb
```

### 데이터베이스 백업
```bash
# MongoDB 백업
docker exec alcha-mongodb mongodump --out /backup --username admin --password adminpassword --authenticationDatabase admin

# TimescaleDB 백업
docker exec alcha-timescaledb pg_dump -U alcha alcha_events > backup.sql
```

### 데이터베이스 복원
```bash
# MongoDB 복원
docker exec -i alcha-mongodb mongorestore --username admin --password adminpassword --authenticationDatabase admin /backup

# TimescaleDB 복원
docker exec -i alcha-timescaledb psql -U alcha alcha_events < backup.sql
```

## 🔍 문제 해결

### MongoDB 연결 실패
```bash
# MongoDB 상태 확인
docker-compose logs mongodb

# MongoDB 컨테이너 재시작
docker-compose restart mongodb
```

### TimescaleDB 연결 실패
```bash
# TimescaleDB 상태 확인
docker-compose logs timescaledb

# TimescaleDB 컨테이너 재시작
docker-compose restart timescaledb
```

### 포트 충돌
다른 서비스가 이미 포트를 사용 중인 경우:
```bash
# 포트 사용 확인
lsof -i :27017  # MongoDB
lsof -i :5432   # TimescaleDB

# docker-compose.yml에서 포트 변경
# ports:
#   - "27018:27017"  # MongoDB
#   - "5433:5432"    # TimescaleDB
```

## 📝 주의사항

1. **데이터 영속성**: 볼륨을 사용하여 데이터가 영구적으로 저장됩니다.
2. **네트워크**: 두 데이터베이스는 `alcha-net` 네트워크를 통해 통신합니다.
3. **환경 변수**: 로컬 개발 시 `localhost`를 사용하고, Docker 네트워크 내에서는 서비스 이름을 사용합니다.
4. **초기화**: TimescaleDB는 처음 실행 시 자동으로 초기화되지 않으므로, `migrate_mongodb_to_timescaledb.py` 스크립트를 실행해야 합니다.

## 🎯 다음 단계

1. MongoDB에 데이터 생성 (`generate_mongodb_data.py`)
2. TimescaleDB 초기화 및 마이그레이션 (`migrate_mongodb_to_timescaledb.py`)
3. 백엔드 애플리케이션 실행 (FastAPI)
4. 프론트엔드 애플리케이션 실행 (React)

## 🔗 관련 문서

- [TimescaleDB와 MongoDB 사용 이유 분석](./DATABASE_ANALYSIS.md)
- [MongoDB 설정 가이드](./alcha-dashboard-backend/mongodb-setup.md)
- [백엔드 README](./alcha-dashboard-backend/README.md)

