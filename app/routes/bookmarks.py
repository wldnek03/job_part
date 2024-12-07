from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity  # jwt_required와 get_jwt_identity 가져오기

from app.models import Bookmark, db

bp = Blueprint('bookmarks', __name__)

@bp.route('/', methods=['POST'])
@jwt_required()  # JWT 인증 필요
def toggle_bookmark():
    user_id = get_jwt_identity()  # 현재 사용자 ID 가져오기
    
    data = request.get_json()
    job_notice_id = data.get('job_notice_id')

    # 북마크 상태 확인 및 토글 처리
    bookmark = Bookmark.query.filter_by(user_id=user_id, job_notice_id=job_notice_id).first()
    if bookmark:
        db.session.delete(bookmark)
        db.session.commit()
        return jsonify({"message": "Bookmark removed"}), 200
    else:
        new_bookmark = Bookmark(user_id=user_id, job_notice_id=job_notice_id)
        db.session.add(new_bookmark)
        db.session.commit()
        return jsonify({"message": "Bookmark added"}), 201