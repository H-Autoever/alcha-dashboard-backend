import os

# 환경 변수에서 MySQL 설정 읽기
mysql_host = os.getenv("MYSQL_HOST", "localhost")
mysql_port = os.getenv("MYSQL_PORT", "3306")
mysql_db = os.getenv("MYSQL_DATABASE", "alcha")
mysql_user = os.getenv("MYSQL_USER", "alcha_user")
mysql_password = os.getenv("MYSQL_PASSWORD", "alcha_password")

DATABASE_URL = f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db}"

class Settings:
    database_url: str = DATABASE_URL
    env: str = os.getenv("ENV", "local")

settings = Settings()


