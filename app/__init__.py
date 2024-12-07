from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'

    # 데이터베이스 초기화
    db.init_app(app)

    # JWT 초기화
    jwt.init_app(app)

    with app.app_context():
        from app.routes import auth, jobs, applications, bookmarks

        app.register_blueprint(auth.bp, url_prefix='/auth')
        app.register_blueprint(jobs.bp, url_prefix='/jobs')
        app.register_blueprint(applications.bp, url_prefix='/applications')
        app.register_blueprint(bookmarks.bp, url_prefix='/bookmarks')

        db.create_all()

    return app