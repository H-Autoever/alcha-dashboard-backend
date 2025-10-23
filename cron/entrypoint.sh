#!/bin/bash

# 환경 변수를 cron에서 사용할 수 있도록 설정
printenv | grep -E '^(MONGO_|MYSQL_|TIMESCALEDB_)' > /etc/environment

# 초기 실행 (즉시 한 번 실행)
echo "🚀 초기 마이그레이션 실행 중..."
cd /app && python /app/scripts/migrate_mongodb_to_timescaledb.py

# cron 시작
echo "⏰ Cron 서비스 시작 (3분마다 마이그레이션 실행)..."
cron

# 로그 출력 (컨테이너가 계속 실행되도록)
echo "📋 마이그레이션 로그를 실시간으로 표시합니다..."
touch /var/log/cron/migration.log
tail -f /var/log/cron/migration.log

