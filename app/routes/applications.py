from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models import Application, db

bp = Blueprint('applications', __name__)

@bp.route('/', methods=['POST'])
@jwt_required()
def apply():
    user_id = get_jwt_identity()
    
    data = request.get_json()
    
    application = Application(
        user_id=user_id,
        job_notice_id=data['job_notice_id'],
        status="지원 완료"
    )
    
    db.session.add(application)
    db.session.commit()
    
    return jsonify({"message": "Application submitted successfully"}), 201

@bp.route('/', methods=['GET'])
@jwt_required()
def get_applications():
    user_id = get_jwt_identity()
    
    applications = Application.query.filter_by(user_id=user_id).all()
    
    result = [{"id": app.id, "job_notice_id": app.job_notice_id} for app in applications]
    
    return jsonify(result), 200