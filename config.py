import os

class Config:
    # Flask 기본 설정
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key')  # Flask 앱의 기본 키
    DEBUG = True

    # 데이터베이스 설정
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:easycow03@localhost/job_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT 설정
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your_jwt_secret_key')  # JWT 서명 키