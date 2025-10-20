// VHC-001~010 모든 차량의 한달간 MongoDB 이벤트 데이터 추가
db = db.getSiblingDB('alcha_events');

print('=== VHC-001~010 한달간 이벤트 데이터 추가 시작 ===');

// 기존 이벤트 데이터 삭제
db.engine_off_events.deleteMany({});
db.collision_events.deleteMany({});

// VHC-001 (Hyundai IONIQ 5) 이벤트 - 한달간
db.engine_off_events.insertMany([
  // 10월 2일 - 하루에 2번 엔진오프 이벤트
  {
    vehicle_id: 'VHC-001',
    speed: 0,
    gear_status: 'P',
    gyro: 15.2,
    side: 'left',
    ignition: false,
    timestamp: new Date('2024-10-02T08:30:00Z'),
    created_at: new Date()
  },
  {
    vehicle_id: 'VHC-001',
    speed: 0,
    gear_status: 'P',
    gyro: 12.8,
    side: 'right',
    ignition: false,
    timestamp: new Date('2024-10-02T18:45:00Z'),
    created_at: new Date()
  },
  // 10월 5일
  {
    vehicle_id: 'VHC-001',
    speed: 0,
    gear_status: 'P',
    gyro: 18.5,
    side: 'left',
    ignition: false,
    timestamp: new Date('2024-10-05T14:20:00Z'),
    created_at: new Date()
  },
  // 10월 8일 - 하루에 2번 엔진오프 이벤트
  {
    vehicle_id: 'VHC-001',
    speed: 0,
    gear_status: 'P',
    gyro: 16.3,
    side: 'right',
    ignition: false,
    timestamp: new Date('2024-10-08T09:15:00Z'),
    created_at: new Date()
  },
  {
    vehicle_id: 'VHC-001',
    speed: 0,
    gear_status: 'P',
    gyro: 14.7,
    side: 'left',
    ignition: false,
    timestamp: new Date('2024-10-08T20:30:00Z'),
    created_at: new Date()
  },
  // 10월 12일
  {
    vehicle_id: 'VHC-001',
    speed: 0,
    gear_status: 'P',
    gyro: 19.2,
    side: 'right',
    ignition: false,
    timestamp: new Date('2024-10-12T11:45:00Z'),
    created_at: new Date()
  },
  // 10월 15일
  {
    vehicle_id: 'VHC-001',
    speed: 0,
    gear_status: 'P',
    gyro: 13.8,
    side: 'left',
    ignition: false,
    timestamp: new Date('2024-10-15T16:20:00Z'),
    created_at: new Date()
  },
  // 10월 18일 - 하루에 2번 엔진오프 이벤트
  {
    vehicle_id: 'VHC-001',
    speed: 0,
    gear_status: 'P',
    gyro: 17.1,
    side: 'right',
    ignition: false,
    timestamp: new Date('2024-10-18T07:30:00Z'),
    created_at: new Date()
  },
  {
    vehicle_id: 'VHC-001',
    speed: 0,
    gear_status: 'P',
    gyro: 15.9,
    side: 'left',
    ignition: false,
    timestamp: new Date('2024-10-18T19:15:00Z'),
    created_at: new Date()
  },
  // 10월 22일
  {
    vehicle_id: 'VHC-001',
    speed: 0,
    gear_status: 'P',
    gyro: 20.4,
    side: 'right',
    ignition: false,
    timestamp: new Date('2024-10-22T13:40:00Z'),
    created_at: new Date()
  },
  // 10월 25일
  {
    vehicle_id: 'VHC-001',
    speed: 0,
    gear_status: 'P',
    gyro: 11.6,
    side: 'left',
    ignition: false,
    timestamp: new Date('2024-10-25T10:25:00Z'),
    created_at: new Date()
  },
  // 10월 28일 - 하루에 2번 엔진오프 이벤트
  {
    vehicle_id: 'VHC-001',
    speed: 0,
    gear_status: 'P',
    gyro: 16.8,
    side: 'right',
    ignition: false,
    timestamp: new Date('2024-10-28T08:50:00Z'),
    created_at: new Date()
  },
  {
    vehicle_id: 'VHC-001',
    speed: 0,
    gear_status: 'P',
    gyro: 14.2,
    side: 'left',
    ignition: false,
    timestamp: new Date('2024-10-28T17:35:00Z'),
    created_at: new Date()
  }
]);

// VHC-001 충돌 이벤트
db.collision_events.insertMany([
  // 10월 3일 - 하루에 2번 충돌 이벤트
  {
    vehicle_id: 'VHC-001',
    damage: 3,
    timestamp: new Date('2024-10-03T09:20:00Z'),
    created_at: new Date()
  },
  {
    vehicle_id: 'VHC-001',
    damage: 2,
    timestamp: new Date('2024-10-03T15:45:00Z'),
    created_at: new Date()
  },
  // 10월 7일
  {
    vehicle_id: 'VHC-001',
    damage: 4,
    timestamp: new Date('2024-10-07T12:30:00Z'),
    created_at: new Date()
  },
  // 10월 11일
  {
    vehicle_id: 'VHC-001',
    damage: 1,
    timestamp: new Date('2024-10-11T14:15:00Z'),
    created_at: new Date()
  },
  // 10월 16일 - 하루에 2번 충돌 이벤트
  {
    vehicle_id: 'VHC-001',
    damage: 2,
    timestamp: new Date('2024-10-16T10:40:00Z'),
    created_at: new Date()
  },
  {
    vehicle_id: 'VHC-001',
    damage: 3,
    timestamp: new Date('2024-10-16T18:20:00Z'),
    created_at: new Date()
  },
  // 10월 20일
  {
    vehicle_id: 'VHC-001',
    damage: 5,
    timestamp: new Date('2024-10-20T11:55:00Z'),
    created_at: new Date()
  },
  // 10월 24일
  {
    vehicle_id: 'VHC-001',
    damage: 1,
    timestamp: new Date('2024-10-24T16:10:00Z'),
    created_at: new Date()
  },
  // 10월 27일 - 하루에 2번 충돌 이벤트
  {
    vehicle_id: 'VHC-001',
    damage: 2,
    timestamp: new Date('2024-10-27T08:25:00Z'),
    created_at: new Date()
  },
  {
    vehicle_id: 'VHC-001',
    damage: 4,
    timestamp: new Date('2024-10-27T20:15:00Z'),
    created_at: new Date()
  },
  // 10월 30일
  {
    vehicle_id: 'VHC-001',
    damage: 3,
    timestamp: new Date('2024-10-30T13:30:00Z'),
    created_at: new Date()
  }
]);

// VHC-002 (Kia EV6) 이벤트
db.engine_off_events.insertMany([
  {
    vehicle_id: 'VHC-002',
    speed: 0,
    gear_status: 'P',
    gyro: 18.5,
    side: 'left',
    ignition: false,
    timestamp: new Date('2024-10-04T11:20:00Z'),
    created_at: new Date()
  },
  {
    vehicle_id: 'VHC-002',
    speed: 0,
    gear_status: 'P',
    gyro: 22.1,
    side: 'right',
    ignition: false,
    timestamp: new Date('2024-10-12T15:30:00Z'),
    created_at: new Date()
  },
  {
    vehicle_id: 'VHC-002',
    speed: 0,
    gear_status: 'P',
    gyro: 19.8,
    side: 'left',
    ignition: false,
    timestamp: new Date('2024-10-20T09:45:00Z'),
    created_at: new Date()
  },
  {
    vehicle_id: 'VHC-002',
    speed: 0,
    gear_status: 'P',
    gyro: 16.3,
    side: 'right',
    ignition: false,
    timestamp: new Date('2024-10-26T14:15:00Z'),
    created_at: new Date()
  }
]);

db.collision_events.insertMany([
  {
    vehicle_id: 'VHC-002',
    damage: 2,
    timestamp: new Date('2024-10-06T14:20:00Z'),
    created_at: new Date()
  },
  {
    vehicle_id: 'VHC-002',
    damage: 4,
    timestamp: new Date('2024-10-18T16:50:00Z'),
    created_at: new Date()
  },
  {
    vehicle_id: 'VHC-002',
    damage: 1,
    timestamp: new Date('2024-10-29T11:30:00Z'),
    created_at: new Date()
  }
]);

// VHC-003 (Genesis GV60) 이벤트
db.engine_off_events.insertMany([
  {
    vehicle_id: 'VHC-003',
    speed: 0,
    gear_status: 'P',
    gyro: 16.7,
    side: 'right',
    ignition: false,
    timestamp: new Date('2024-10-09T12:15:00Z'),
    created_at: new Date()
  },
  {
    vehicle_id: 'VHC-003',
    speed: 0,
    gear_status: 'P',
    gyro: 14.3,
    side: 'left',
    ignition: false,
    timestamp: new Date('2024-10-21T17:25:00Z'),
    created_at: new Date()
  },
  {
    vehicle_id: 'VHC-003',
    speed: 0,
    gear_status: 'P',
    gyro: 17.9,
    side: 'right',
    ignition: false,
    timestamp: new Date('2024-10-30T08:40:00Z'),
    created_at: new Date()
  }
]);

db.collision_events.insertMany([
  {
    vehicle_id: 'VHC-003',
    damage: 3,
    timestamp: new Date('2024-10-14T10:35:00Z'),
    created_at: new Date()
  },
  {
    vehicle_id: 'VHC-003',
    damage: 1,
    timestamp: new Date('2024-10-26T13:40:00Z'),
    created_at: new Date()
  }
]);

// VHC-004 (Tesla Model Y) 이벤트 - 의도적으로 이벤트 없음 (테스트용)

// VHC-005 (BMW iX3) 이벤트
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
  },
  {
    vehicle_id: 'VHC-005',
    speed: 0,
    gear_status: 'P',
    gyro: 21.2,
    side: 'right',
    ignition: false,
    timestamp: new Date('2024-10-19T10:30:00Z'),
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
  },
  {
    vehicle_id: 'VHC-005',
    damage: 2,
    timestamp: new Date('2024-10-25T13:45:00Z'),
    created_at: new Date()
  }
]);

// VHC-006 (Mercedes EQC) 이벤트
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
  },
  {
    vehicle_id: 'VHC-006',
    speed: 0,
    gear_status: 'P',
    gyro: 18.1,
    side: 'right',
    ignition: false,
    timestamp: new Date('2024-10-23T16:20:00Z'),
    created_at: new Date()
  }
]);

// VHC-007 (Audi e-tron) 이벤트
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
  },
  {
    vehicle_id: 'VHC-007',
    speed: 0,
    gear_status: 'P',
    gyro: 14.6,
    side: 'right',
    ignition: false,
    timestamp: new Date('2024-10-17T12:10:00Z'),
    created_at: new Date()
  }
]);

db.collision_events.insertMany([
  {
    vehicle_id: 'VHC-007',
    damage: 3,
    timestamp: new Date('2024-10-14T17:10:00Z'),
    created_at: new Date()
  },
  {
    vehicle_id: 'VHC-007',
    damage: 2,
    timestamp: new Date('2024-10-28T09:25:00Z'),
    created_at: new Date()
  }
]);

// VHC-008 (Volkswagen ID.4) 이벤트
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
  },
  {
    vehicle_id: 'VHC-008',
    speed: 0,
    gear_status: 'P',
    gyro: 16.8,
    side: 'right',
    ignition: false,
    timestamp: new Date('2024-10-27T14:50:00Z'),
    created_at: new Date()
  }
]);

// VHC-009 (Nissan Ariya) 이벤트
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
  },
  {
    vehicle_id: 'VHC-009',
    speed: 0,
    gear_status: 'P',
    gyro: 19.3,
    side: 'right',
    ignition: false,
    timestamp: new Date('2024-10-24T11:20:00Z'),
    created_at: new Date()
  }
]);

db.collision_events.insertMany([
  {
    vehicle_id: 'VHC-009',
    damage: 2,
    timestamp: new Date('2024-10-17T14:25:00Z'),
    created_at: new Date()
  },
  {
    vehicle_id: 'VHC-009',
    damage: 4,
    timestamp: new Date('2024-10-29T16:15:00Z'),
    created_at: new Date()
  }
]);

// VHC-010 (Ford Mustang Mach-E) 이벤트
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
  },
  {
    vehicle_id: 'VHC-010',
    speed: 0,
    gear_status: 'P',
    gyro: 22.5,
    side: 'right',
    ignition: false,
    timestamp: new Date('2024-10-30T15:30:00Z'),
    created_at: new Date()
  }
]);

db.collision_events.insertMany([
  {
    vehicle_id: 'VHC-010',
    damage: 5,
    timestamp: new Date('2024-10-22T13:50:00Z'),
    created_at: new Date()
  },
  {
    vehicle_id: 'VHC-010',
    damage: 3,
    timestamp: new Date('2024-10-30T10:20:00Z'),
    created_at: new Date()
  }
]);

print('=== VHC-001~010 한달간 이벤트 데이터 추가 완료 ===');
print('Engine Off Events 총 개수:', db.engine_off_events.countDocuments());
print('Collision Events 총 개수:', db.collision_events.countDocuments());

// 하루에 2번 같은 이벤트가 발생한 날짜들 확인
print('\n=== 하루에 2번 같은 이벤트 발생 날짜 ===');
print('VHC-001 엔진오프 2번: 10/2, 10/8, 10/18, 10/28');
print('VHC-001 충돌 2번: 10/3, 10/16, 10/27');

// 차량별 이벤트 개수 확인
print('\n=== 차량별 이벤트 개수 ===');
for (let i = 1; i <= 10; i++) {
  const vehicleId = 'VHC-' + String(i).padStart(3, '0');
  const engineOffCount = db.engine_off_events.find({vehicle_id: vehicleId}).count();
  const collisionCount = db.collision_events.find({vehicle_id: vehicleId}).count();
  print(`${vehicleId}: Engine Off ${engineOffCount}개, Collision ${collisionCount}개`);
}

print('\n=== 참고 ===');
print('VHC-004는 의도적으로 이벤트 데이터가 없습니다.');
print('"이벤트 데이터가 없습니다" 메시지 테스트용입니다.');
