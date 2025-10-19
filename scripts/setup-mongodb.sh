#!/bin/bash

# MongoDB 초기화 스크립트
# 사용법: ./scripts/setup-mongodb.sh

echo "🚀 MongoDB 초기화 시작..."

# MongoDB 컨테이너가 실행 중인지 확인
if ! docker ps | grep -q alcha-mongodb; then
    echo "❌ MongoDB 컨테이너가 실행 중이지 않습니다."
    echo "다음 명령어로 MongoDB 컨테이너를 먼저 실행하세요:"
    echo "docker run -d --name alcha-mongodb --network alcha-net -p 27017:27017 \\"
    echo "  -e MONGO_INITDB_ROOT_USERNAME=admin \\"
    echo "  -e MONGO_INITDB_ROOT_PASSWORD=adminpassword \\"
    echo "  mongo:7.0"
    exit 1
fi

echo "✅ MongoDB 컨테이너 확인 완료"

# MongoDB가 완전히 시작될 때까지 대기
echo "⏳ MongoDB 시작 대기 중..."
sleep 5

# 초기화 스크립트를 컨테이너에 복사
echo "📁 초기화 스크립트 복사 중..."
docker cp scripts/init-mongodb.js alcha-mongodb:/tmp/init-mongodb.js

# 초기화 스크립트 실행
echo "🔄 MongoDB 데이터 초기화 중..."
docker exec -i alcha-mongodb mongosh --username admin --password adminpassword --authenticationDatabase admin /tmp/init-mongodb.js

if [ $? -eq 0 ]; then
    echo "✅ MongoDB 초기화 완료!"
    echo ""
    echo "📊 데이터 요약:"
    echo "  - Engine Off Events: 4개"
    echo "  - Collision Events: 3개"
    echo "  - 차량: VHC-001, VHC-002, VHC-003"
    echo ""
    echo "🔗 API 테스트:"
    echo "  curl http://localhost:8000/api/events/VHC-001"
    echo "  curl http://localhost:8000/api/events/VHC-002"
    echo "  curl http://localhost:8000/api/events/VHC-003"
else
    echo "❌ MongoDB 초기화 실패"
    exit 1
fi
