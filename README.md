
# 프로젝트 이름

이 프로젝트는 Flask를 사용하여 개발된 웹 애플리케이션입니다. Anaconda 환경에서 관리되며, Flask-Swagger를 통해 API 문서를 제공합니다.

## 요구 사항

이 프로젝트를 실행하기 위해서는 다음의 Python 패키지가 필요합니다. `requirements.txt` 파일을 사용하여 설치할 수 있습니다.

```plaintext
aniso8601==9.0.1
beautifulsoup4==4.12.3
blinker==1.8.2
certifi==2024.8.30
cffi==1.17.1
charset-normalizer==3.4.0
click==8.1.7
colorama==0.4.6
cryptography==44.0.0
Flask==3.0.3
Flask-JWT-Extended==4.6.0
Flask-RESTful==0.3.10
Flask-SQLAlchemy==3.1.1
flask-swagger==0.2.14
greenlet==3.1.1
idna==3.10
importlib_metadata==8.5.0
itsdangerous==2.2.0
Jinja2==3.1.4
MarkupSafe==2.1.5
mysql-connector-python==9.0.0
pycparser==2.22
PyJWT==2.9.0
PyMySQL==1.1.1
pytz==2024.2
PyYAML==6.0.2
requests==2.32.3
six==1.17.0
soupsieve==2.6
SQLAlchemy==2.0.36
typing_extensions==4.12.2
urllib3==2.2.3
Werkzeug==3.0.6
zipp==3.20.2
```

## 설치 및 실행

### 1단계: 환경 설정

Anaconda를 사용하여 새로운 환경을 생성하고 필요한 패키지를 설치합니다.

```bash
conda create -n myenv python=3.x  
conda activate myenv

pip install -r requirements.txt  
```

### 2단계: 애플리케이션 실행

```bash
python run.py
```

## 주요 기능

- **Flask**: 웹 서버 프레임워크로, RESTful API를 제공합니다.
- **Flask-JWT-Extended**: JWT 인증을 지원합니다.
- **Flask-SQLAlchemy**: 데이터베이스 ORM으로 사용됩니다.
- **Flask-Swagger**: API 문서화를 위한 Swagger 지원을 제공합니다.

## 사용 방법

애플리케이션이 실행되면, Swagger UI를 통해 API 문서를 확인할 수 있습니다.



---


