FROM python:3.11-slim

# 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    cron \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# requirements.txt 복사 및 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 코드 복사
COPY app/ ./app/
COPY scripts/ ./scripts/

# crontab 파일 복사
COPY cron/crontab /etc/cron.d/migration-cron

# crontab 권한 설정
RUN chmod 0644 /etc/cron.d/migration-cron && \
    crontab /etc/cron.d/migration-cron

# 로그 디렉토리 생성
RUN mkdir -p /var/log/cron

# entrypoint 스크립트 복사
COPY cron/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# entrypoint 실행
ENTRYPOINT ["/entrypoint.sh"]

