// MongoDB 초기화 스크립트
// 사용법: docker exec -i alcha-mongodb mongosh --username admin --password adminpassword --authenticationDatabase admin /tmp/init-mongodb.js

db = db.getSiblingDB('alcha_events');

print('=== MongoDB 이벤트 데이터 초기화 시작 ===');

// 기존 데이터 삭제
print('기존 데이터 삭제 중...');
db.engine_off_events.deleteMany({});
db.collision_events.deleteMany({});

// Engine Off Events 삽입
print('Engine Off Events 데이터 삽입 중...');
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
print('Collision Events 데이터 삽입 중...');
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

print('=== 초기화 완료 ===');
print('Engine Off Events 개수:', db.engine_off_events.countDocuments());
print('Collision Events 개수:', db.collision_events.countDocuments());

// 데이터 검증
print('\n=== 데이터 검증 ===');
print('VHC-001 이벤트:');
print('  - Engine Off:', db.engine_off_events.find({vehicle_id: 'VHC-001'}).count());
print('  - Collision:', db.collision_events.find({vehicle_id: 'VHC-001'}).count());

print('VHC-002 이벤트:');
print('  - Engine Off:', db.engine_off_events.find({vehicle_id: 'VHC-002'}).count());
print('  - Collision:', db.collision_events.find({vehicle_id: 'VHC-002'}).count());

print('VHC-003 이벤트:');
print('  - Engine Off:', db.engine_off_events.find({vehicle_id: 'VHC-003'}).count());
print('  - Collision:', db.collision_events.find({vehicle_id: 'VHC-003'}).count());
