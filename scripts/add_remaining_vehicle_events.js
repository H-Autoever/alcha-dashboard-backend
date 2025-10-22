// VHC-004~010 차량들에 MongoDB 이벤트 데이터 추가
db = db.getSiblingDB('alcha_events');

print('=== VHC-004~010 이벤트 데이터 추가 시작 ===');

// VHC-004 (Tesla Model Y) - 이벤트 데이터 없음 (의도적으로 비워둠)

// VHC-005 (BMW iX3) 이벤트 추가
db.engine_off_events.insertMany([
  {
    vehicle_id: 'VHC-005',
    speed: 0,
    gear_status: 'P',
    gyro: 19.5,
    side: 'left',
    ignition: false,
    timestamp: new Date('2024-10-06T14:15:00Z'),
    created_at: new Date()
  }
]);

db.collision_events.insertMany([
  {
    vehicle_id: 'VHC-005',
    damage: 4,
    timestamp: new Date('2024-10-10T09:30:00Z'),
    created_at: new Date()
  },
  {
    vehicle_id: 'VHC-005',
    damage: 1,
    timestamp: new Date('2024-10-18T16:20:00Z'),
    created_at: new Date()
  }
]);

// VHC-006 (Mercedes EQC) 이벤트 추가
db.engine_off_events.insertMany([
  {
    vehicle_id: 'VHC-006',
    speed: 0,
    gear_status: 'P',
    gyro: 13.7,
    side: 'right',
    ignition: false,
    timestamp: new Date('2024-10-07T11:45:00Z'),
    created_at: new Date()
  },
  {
    vehicle_id: 'VHC-006',
    speed: 0,
    gear_status: 'P',
    gyro: 15.3,
    side: 'left',
    ignition: false,
    timestamp: new Date('2024-10-15T13:30:00Z'),
    created_at: new Date()
  }
]);

// VHC-007 (Audi e-tron) 이벤트 추가
db.engine_off_events.insertMany([
  {
    vehicle_id: 'VHC-007',
    speed: 0,
    gear_status: 'P',
    gyro: 17.8,
    side: 'left',
    ignition: false,
    timestamp: new Date('2024-10-09T08:20:00Z'),
    created_at: new Date()
  }
]);

db.collision_events.insertMany([
  {
    vehicle_id: 'VHC-007',
    damage: 3,
    timestamp: new Date('2024-10-14T17:10:00Z'),
    created_at: new Date()
  }
]);

// VHC-008 (Volkswagen ID.4) 이벤트 추가
db.engine_off_events.insertMany([
  {
    vehicle_id: 'VHC-008',
    speed: 0,
    gear_status: 'P',
    gyro: 12.4,
    side: 'right',
    ignition: false,
    timestamp: new Date('2024-10-11T16:30:00Z'),
    created_at: new Date()
  },
  {
    vehicle_id: 'VHC-008',
    speed: 0,
    gear_status: 'P',
    gyro: 14.1,
    side: 'left',
    ignition: false,
    timestamp: new Date('2024-10-19T10:15:00Z'),
    created_at: new Date()
  }
]);

// VHC-009 (Nissan Ariya) 이벤트 추가
db.engine_off_events.insertMany([
  {
    vehicle_id: 'VHC-009',
    speed: 0,
    gear_status: 'P',
    gyro: 16.9,
    side: 'left',
    ignition: false,
    timestamp: new Date('2024-10-13T12:45:00Z'),
    created_at: new Date()
  }
]);

db.collision_events.insertMany([
  {
    vehicle_id: 'VHC-009',
    damage: 2,
    timestamp: new Date('2024-10-17T14:25:00Z'),
    created_at: new Date()
  }
]);

// VHC-010 (Ford Mustang Mach-E) 이벤트 추가
db.engine_off_events.insertMany([
  {
    vehicle_id: 'VHC-010',
    speed: 0,
    gear_status: 'P',
    gyro: 20.3,
    side: 'right',
    ignition: false,
    timestamp: new Date('2024-10-16T11:20:00Z'),
    created_at: new Date()
  },
  {
    vehicle_id: 'VHC-010',
    speed: 0,
    gear_status: 'P',
    gyro: 18.7,
    side: 'left',
    ignition: false,
    timestamp: new Date('2024-10-25T09:40:00Z'),
    created_at: new Date()
  }
]);

db.collision_events.insertMany([
  {
    vehicle_id: 'VHC-010',
    damage: 5,
    timestamp: new Date('2024-10-22T13:50:00Z'),
    created_at: new Date()
  }
]);

print('=== VHC-004~010 이벤트 데이터 추가 완료 ===');
print('Engine Off Events 총 개수:', db.engine_off_events.countDocuments());
print('Collision Events 총 개수:', db.collision_events.countDocuments());

// 차량별 이벤트 개수 확인
print('\n=== 차량별 이벤트 개수 ===');
for (let i = 4; i <= 10; i++) {
  const vehicleId = 'VHC-' + String(i).padStart(3, '0');
  const engineOffCount = db.engine_off_events.find({vehicle_id: vehicleId}).count();
  const collisionCount = db.collision_events.find({vehicle_id: vehicleId}).count();
  print(`${vehicleId}: Engine Off ${engineOffCount}개, Collision ${collisionCount}개`);
}

print('\n=== 참고 ===');
print('VHC-004는 의도적으로 이벤트 데이터가 없습니다.');
print('"이벤트 데이터가 없습니다" 메시지 테스트용입니다.');
