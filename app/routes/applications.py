from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from app.models import Application, db

bp = Blueprint('applications', __name__)

@bp.route('/', methods=['POST'])
@jwt_required()
def apply():
    """
    지원하기
    ---
    tags:
      - Applications
    parameters:
      - name: job_notice_id
        in: body
        type: integer
        required: true
        description: "지원하려는 채용 공고 ID"
    responses:
      201:
        description: "지원 성공"
      400:
        description: "잘못된 입력 또는 중복 지원 시 발생"
      500:
        description: "서버 오류 발생"
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data or 'job_notice_id' not in data:
        return jsonify({"error": "job_notice_id is required"}), 400

    existing_application = Application.query.filter_by(user_id=user_id, job_notice_id=data['job_notice_id']).first()
    if existing_application:
        return jsonify({"error": "You have already applied for this job"}), 400

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


@bp.route('/', methods=['GET'])
@jwt_required()
def get_applications():
    """
    지원 내역 조회
    ---
    tags:
      - Applications
    parameters:
      - name: status_filter
        in: query
        type: string
        required: false
        description: "필터링할 상태 (예: '지원 완료', '취소됨')"
    responses:
      200:
        description: "지원 내역 반환 성공"
      401:
        description: "인증 실패 (유효하지 않은 JWT 토큰)"
    """
    user_id = get_jwt_identity()

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


@bp.route('/<int:application_id>', methods=['DELETE'])
@jwt_required()
def cancel_application(application_id):
    """
    지원 취소하기
    ---
    tags:
      - Applications
    parameters:
      - name: application_id
        in: path
        type: integer
        required: true
        description: "취소하려는 지원 ID"
    responses:
      200:
        description: "지원 취소 성공적으로 완료됨."
      400:
        description: "잘못된 요청 또는 취소 불가능한 상태일 경우."
      404:
        description: "해당 지원 정보를 찾을 수 없음."
      500:
        description: "서버 오류 발생."
    """
    user_id = get_jwt_identity()

    application = Application.query.filter_by(id=application_id, user_id=user_id).first()

    if not application:
        return jsonify({"error": "Application not found"}), 404

    if application.status != "지원 완료":
        return jsonify({"error": "Application cannot be canceled"}), 400

    application.status = "취소됨"
    
    try:
        db.session.commit()
        return jsonify({"message": "Application canceled successfully"}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Failed to cancel application"}), 500
