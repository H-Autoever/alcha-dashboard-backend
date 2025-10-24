# MongoDB → TimescaleDB 자동 마이그레이션 Cron 서비스

3분마다 MongoDB에서 TimescaleDB로 데이터를 자동으로 마이그레이션하는 Docker 컨테이너입니다.

## 빌드 및 실행

### 1. Docker 이미지 빌드

```bash
cd /Users/xxng/Desktop/alcha-dashboard/alcha-dashboard-backend
docker build -f cron/Dockerfile -t alcha-cron .
```

### 2. Docker 컨테이너 실행

```bash
docker run -d \
  --name alcha-cron \
  --network alcha-net \
  -e MONGO_HOST=alcha-mongodb \
  -e MONGO_PORT=27017 \
  -e MONGO_DB=alcha_events \
  -e TIMESCALEDB_HOST=alcha-timescaledb \
  -e TIMESCALEDB_PORT=5432 \
  -e TIMESCALEDB_DB=alcha_events \
  -e TIMESCALEDB_USER=alcha \
  -e TIMESCALEDB_PASSWORD=alcha_password \
  alcha-cron
```

### 3. 로그 확인

```bash
# 실시간 로그 확인
docker logs -f alcha-cron

# 최근 로그만 확인
docker logs --tail 100 alcha-cron
```

### 4. 중지 및 제거

```bash
docker stop alcha-cron
docker rm alcha-cron
```

## 동작 방식

1. **초기 실행**: 컨테이너 시작 시 즉시 한 번 마이그레이션을 실행합니다.
2. **주기적 실행**: 이후 3분마다 자동으로 마이그레이션을 실행합니다.
3. **로그 기록**: 모든 실행 결과는 `/var/log/cron/migration.log`에 기록됩니다.

## Cron 스케줄 변경

`cron/crontab` 파일에서 실행 주기를 변경할 수 있습니다:

```cron
# 현재: 3분마다
*/3 * * * * ...

# 예시: 5분마다
*/5 * * * * ...

# 예시: 10분마다
*/10 * * * * ...

# 예시: 1시간마다
0 * * * * ...
```

