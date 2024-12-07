from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity  # JWT 인증 관련 모듈

from app.models import Bookmark, db

bp = Blueprint('bookmarks', __name__)

# 북마크 추가/제거 (토글)
@bp.route('/', methods=['POST'])
@jwt_required()  # JWT 인증 필요
def toggle_bookmark():
    user_id = get_jwt_identity()  # 현재 사용자 ID 가져오기
    
    data = request.get_json()
    job_notice_id = data.get('job_notice_id')

    if not job_notice_id:
        return jsonify({"error": "job_notice_id is required"}), 400

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

# 북마크 목록 조회
@bp.route('/', methods=['GET'])
@jwt_required()  # JWT 인증 필요
def get_bookmarks():
    user_id = get_jwt_identity()  # 현재 사용자 ID 가져오기

    # 쿼리 파라미터로 페이지 번호와 페이지 크기 처리 (기본값: page=1, per_page=10)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # 사용자별 북마크를 ID 기준으로 내림차순 정렬하여 페이징 처리
    bookmarks_query = Bookmark.query.filter_by(user_id=user_id).order_by(Bookmark.id.desc())
    bookmarks_paginated = bookmarks_query.paginate(page=page, per_page=per_page)

    # 결과 반환
    result = {
        "total": bookmarks_paginated.total,
        "pages": bookmarks_paginated.pages,
        "current_page": bookmarks_paginated.page,
        "per_page": bookmarks_paginated.per_page,
        "bookmarks": [
            {
                "id": bookmark.id,
                "job_notice_id": bookmark.job_notice_id
            }
            for bookmark in bookmarks_paginated.items
        ]
    }
    
    return jsonify(result), 200