from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from app.models import Application, db

bp = Blueprint('applications', __name__)

# 지원하기
@bp.route('/', methods=['POST'])
@jwt_required()
def apply():
    user_id = get_jwt_identity()
    data = request.get_json()

    # 필수 데이터 체크
    if not data or 'job_notice_id' not in data:
        return jsonify({"error": "job_notice_id is required"}), 400

    # 중복 지원 방지
    existing_application = Application.query.filter_by(user_id=user_id, job_notice_id=data['job_notice_id']).first()
    if existing_application:
        return jsonify({"error": "You have already applied for this job"}), 400

    # 새로운 지원 생성
    application = Application(
        user_id=user_id,
        job_notice_id=data['job_notice_id'],
        status="지원 완료"
    )

    try:
        db.session.add(application)
        db.session.commit()
        return jsonify({"message": "Application submitted successfully"}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Failed to submit application"}), 500

# 지원 내역 조회
@bp.route('/', methods=['GET'])
@jwt_required()
def get_applications():
    user_id = get_jwt_identity()

    # 쿼리 파라미터로 상태 처리
    status_filter = request.args.get('status', None)

    query = Application.query.filter_by(user_id=user_id)
    
    if status_filter:
        query = query.filter_by(status=status_filter)

    applications = query.all()

    result = [
        {
            "id": app.id,
            "job_notice_id": app.job_notice_id,
            "status": app.status
        }
        for app in applications
    ]
    
    return jsonify(result), 200

# 지원 취소
@bp.route('/<int:application_id>', methods=['DELETE'])
@jwt_required()
def cancel_application(application_id):
    user_id = get_jwt_identity()

    # 지원 정보 가져오기
    application = Application.query.filter_by(id=application_id, user_id=user_id).first()

    if not application:
        return jsonify({"error": "Application not found"}), 404

    # 취소 가능 여부 확인 (예: 상태가 '지원 완료'일 때만 취소 가능)
    if application.status != "지원 완료":
        return jsonify({"error": "Application cannot be canceled"}), 400

    # 상태 업데이트
    application.status = "취소됨"
    
    try:
        db.session.commit()
        return jsonify({"message": "Application canceled successfully"}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Failed to cancel application"}), 500