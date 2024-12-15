from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flasgger import Swagger

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    @app.route('/')
    def home():
        return "Hello, World!"
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:easycow0304@10.0.0.251/job"

    # 데이터베이스 초기화
    db.init_app(app)

    # JWT 초기화
    jwt.init_app(app)

    # Swagger 설정
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/swagger/"
    }

    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Job Notice API",
            "description": "채용 공고 API 문서입니다.",
            "version": "1.0.0",
            "contact": {
                "name": "API Support",
                "url": "http://www.example.com/support",
                "email": "support@example.com"
            }
        },
        "host": "113.198.66.75:13251",  # 실제 배포 시 변경
        "basePath": "/",
        "securityDefinitions": {
            "BearerAuth": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header"
            }
        },
         # 기본 보안 적용
        "security": [
             {"BearerAuth": []}
    ]
    }

    Swagger(app, config=swagger_config, template=swagger_template)

    with app.app_context():
        from app.routes import auth, jobs, applications, bookmarks

        app.register_blueprint(auth.bp, url_prefix='/auth')
        app.register_blueprint(jobs.bp, url_prefix='/jobs')
        app.register_blueprint(applications.bp, url_prefix='/applications')
        app.register_blueprint(bookmarks.bp, url_prefix='/bookmarks')

        db.create_all()

    return app

if __name__ == '__main__':
    create_app().run(host='0.0.0.0', port=3000, debug=True)
