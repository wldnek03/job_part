import os
from sqlalchemy import create_engine

class Config:
    # Flask 기본 설정
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key')  # Flask 앱의 기본 키
    DEBUG = True

    SECRET_KEY = "your_secret_key"
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:easycow0304@10.0.0.251:3306/job"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SQLAlchemy 엔진 생성
    ENGINE = create_engine(
        SQLALCHEMY_DATABASE_URI,
        pool_pre_ping=True,
        pool_recycle=3600
    )

    # JWT 설정
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your_jwt_secret_key')  # JWT 서명 키