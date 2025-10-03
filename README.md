### 공통 네트워크 생성 (최초 1회)
```bash
docker network create alcha-net
```

### 1) DB 컨테이너 실행 및 스키마 적용
```bash
docker run -d --name alcha-mysql --network alcha-net -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=rootpassword \
  -e MYSQL_DATABASE=alcha \
  -e MYSQL_USER=alcha \
  -e MYSQL_PASSWORD=alcha_password \
  mysql:8.0 --default-authentication-plugin=mysql_native_password \
  --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci

# MySQL 기동 대기 (준비될 때까지 대기)
docker exec alcha-mysql sh -c 'until mysqladmin ping -h127.0.0.1 -prootpassword --silent; do sleep 1; done'

# 스키마/더미데이터 적용
docker exec -i alcha-mysql mysql -uroot -prootpassword alcha < sql/schema.sql
```

### 2) 백엔드 컨테이너 실행
```bash
cd alcha-dashboard-backend
docker build -t alcha-git-backend .
docker run -d --name alcha-backend --network alcha-net -p 8000:8000 \
  -e DATABASE_URL=mysql+pymysql://alcha:alcha_password@alcha-mysql:3306/alcha \
  -e ENV=local \
  alcha-git-backend
```

### 접속
API 문서: http://localhost:8000/docs
