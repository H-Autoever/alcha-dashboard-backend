# Database Comparison Monitoring with Prometheus & Grafana

MongoDB vs TimescaleDB 성능 비교 테스트 결과를 Prometheus와 Grafana를 통해 시각화합니다.

## 🚀 시작하기

### 1. Prometheus와 Grafana 서비스 시작

```bash
cd scripts/measuring_datas
docker-compose up -d prometheus grafana
```

### 2. 테스트 스크립트 실행

테스트 스크립트는 자동으로 Prometheus 메트릭을 export합니다:

```bash
cd ../..  # alcha-dashboard-backend로 이동
python scripts/measuring_datas/database_comparison_test.py
```

테스트 스크립트 실행 시:
- 포트 8000에서 Prometheus 메트릭을 HTTP 엔드포인트로 제공
- 모든 테스트 결과가 실시간으로 메트릭에 기록됨

### 3. Grafana 대시보드 확인

1. **Grafana 접속**: http://localhost:3000
   - 사용자명: `admin`
   - 비밀번호: `admin`

2. **대시보드 확인**:
   - 좌측 메뉴에서 "Dashboards" → "Database Comparison - MongoDB vs TimescaleDB" 선택
   - 또는 직접 URL: http://localhost:3000/d/db-comparison

### 4. Prometheus 메트릭 확인 (선택사항)

- **Prometheus UI**: http://localhost:9090
- **메트릭 엔드포인트**: http://localhost:8000/metrics

## 📊 대시보드 패널

대시보드는 다음 메트릭을 시각화합니다:

### 1. 쓰기 성능 비교
- **초당 처리 레코드 수**: MongoDB vs TimescaleDB
- **배치 크기별 성능**: 100, 1000, 5000, 10000 레코드 배치

### 2. 읽기 성능 비교
- **시간 범위 쿼리**: 1시간 데이터 조회 성능
- **집계 쿼리**: 평균/최대/최소 집계 성능

### 3. 실시간 모니터링
- 테스트 실행 중 실시간 성능 모니터링
- 히스토리 데이터 조회 가능

## 🔧 설정

### 메트릭 포트 변경

환경 변수로 메트릭 포트를 변경할 수 있습니다:

```bash
export METRICS_PORT=9000
python scripts/measuring_datas/database_comparison_test.py
```

그리고 `prometheus.yml`에서 해당 포트로 수정해야 합니다.

### Prometheus 스크랩 주기

`prometheus.yml`의 `scrape_interval`을 수정하여 스크랩 주기를 변경할 수 있습니다 (기본: 5초).

## 📝 메트릭 종류

### Gauge 메트릭
- `db_write_records_per_second`: 초당 쓰기 처리 레코드 수
- `db_read_query_time_gauge_seconds`: 읽기 쿼리 평균 소요 시간

### Histogram 메트릭
- `db_write_time_seconds`: 쓰기 작업 소요 시간 분포
- `db_read_query_time_seconds`: 읽기 쿼리 소요 시간 분포

## 🐛 문제 해결

### Prometheus가 메트릭을 스크랩하지 못하는 경우

Windows 환경에서 `host.docker.internal`이 작동하지 않는다면:

1. `prometheus.yml`의 target을 호스트의 실제 IP 주소로 변경
2. 또는 Prometheus를 `host` 네트워크 모드로 실행

### Grafana 대시보드가 데이터를 표시하지 않는 경우

1. Prometheus가 정상적으로 메트릭을 수집하는지 확인 (http://localhost:9090/targets)
2. Grafana 데이터소스가 Prometheus를 올바르게 가리키는지 확인
3. 테스트 스크립트가 실행 중이고 메트릭을 export하고 있는지 확인

