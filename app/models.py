from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

class JobNotice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    title = db.Column(db.String(255), nullable=False)
    link = db.Column(db.Text)
    # Location 관계 추가
    locations = db.relationship('Location', backref='job_notice', lazy=True)
    # Money 관계 추가
    salaries = db.relationship('Money', backref='job_notice', lazy=True)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    job_notice_id = db.Column(db.Integer, db.ForeignKey('job_notice.id'))
    status = db.Column(db.String(50))

class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    job_notice_id = db.Column(db.Integer, db.ForeignKey('job_notice.id'))

class Company(db.Model):
    __tablename__ = 'company'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    job_notices = db.relationship('JobNotice', backref='company', lazy=True)


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_notice_id = db.Column(db.Integer, db.ForeignKey('job_notice.id'), nullable=False)
    region = db.Column(db.String(255), nullable=False)


class Money(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_notice_id = db.Column(db.Integer, db.ForeignKey('job_notice.id'), nullable=False)
    salary = db.Column(db.String(50), nullable=False)
