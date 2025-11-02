#!/bin/bash
# MongoDB 샤딩 클러스터 설정 스크립트

set -e

echo "🚀 MongoDB 샤딩 클러스터 설정 시작..."

# Config Server Replica Set 초기화
echo "📋 Config Server Replica Set 초기화 중..."
docker exec alcha-mongodb-config-1 mongosh --eval "
rs.initiate({
  _id: 'configrs',
  configsvr: true,
  members: [
    { _id: 0, host: 'alcha-mongodb-config-1:27017' },
    { _id: 1, host: 'alcha-mongodb-config-2:27017' },
    { _id: 2, host: 'alcha-mongodb-config-3:27017' }
  ]
})
" --quiet

echo "⏳ Config Server 초기화 대기 중..."
sleep 10

# Shard 1 Replica Set 초기화
echo "📋 Shard 1 Replica Set 초기화 중..."
docker exec alcha-mongodb-shard-1-1 mongosh --eval "
rs.initiate({
  _id: 'shard1rs',
  members: [
    { _id: 0, host: 'alcha-mongodb-shard-1-1:27017' },
    { _id: 1, host: 'alcha-mongodb-shard-1-2:27017' },
    { _id: 2, host: 'alcha-mongodb-shard-1-3:27017' }
  ]
})
" --quiet

# Shard 2 Replica Set 초기화
echo "📋 Shard 2 Replica Set 초기화 중..."
docker exec alcha-mongodb-shard-2-1 mongosh --eval "
rs.initiate({
  _id: 'shard2rs',
  members: [
    { _id: 0, host: 'alcha-mongodb-shard-2-1:27017' },
    { _id: 1, host: 'alcha-mongodb-shard-2-2:27017' },
    { _id: 2, host: 'alcha-mongodb-shard-2-3:27017' }
  ]
})
" --quiet

echo "⏳ Replica Sets 초기화 대기 중..."
sleep 15

# Mongos에 Shard 추가
echo "📋 Mongos에 Shard 추가 중..."
docker exec alcha-mongodb-router mongosh --eval "
sh.addShard('shard1rs/alcha-mongodb-shard-1-1:27017,alcha-mongodb-shard-1-2:27017,alcha-mongodb-shard-1-3:27017')
sh.addShard('shard2rs/alcha-mongodb-shard-2-1:27017,alcha-mongodb-shard-2-2:27017,alcha-mongodb-shard-2-3:27017')
" --quiet

# 샤딩 활성화 및 샤드 키 설정
echo "📋 데이터베이스 샤딩 활성화 중..."
docker exec alcha-mongodb-router mongosh --eval "
use alcha_events
sh.enableSharding('alcha_events')
" --quiet

# realtime-storage-data 컬렉션 샤딩 (vehicle_id 기반 해시 샤딩)
echo "📋 realtime-storage-data 컬렉션 샤딩 설정 중..."
docker exec alcha-mongodb-router mongosh --eval "
use alcha_events
sh.shardCollection('alcha_events.realtime-storage-data', { vehicle_id: 'hashed' })
" --quiet

# periodic-storage-data 컬렉션 샤딩
echo "📋 periodic-storage-data 컬렉션 샤딩 설정 중..."
docker exec alcha-mongodb-router mongosh --eval "
use alcha_events
sh.shardCollection('alcha_events.periodic-storage-data', { vehicle_id: 'hashed' })
" --quiet

# event-* 컬렉션 샤딩
echo "📋 event-* 컬렉션 샤딩 설정 중..."
docker exec alcha-mongodb-router mongosh --eval "
use alcha_events
sh.shardCollection('alcha_events.event-collision', { vehicle_id: 'hashed' })
sh.shardCollection('alcha_events.event-sudden-acceleration', { vehicle_id: 'hashed' })
sh.shardCollection('alcha_events.event-engine-status', { vehicle_id: 'hashed' })
sh.shardCollection('alcha_events.event-warning-light', { vehicle_id: 'hashed' })
" --quiet

echo "✅ MongoDB 샤딩 클러스터 설정 완료!"

# 샤딩 상태 확인
echo "📊 샤딩 상태 확인..."
docker exec alcha-mongodb-router mongosh --eval "
sh.status()
" --quiet

