from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Bookmark, db

bp = Blueprint('bookmarks', __name__)

@bp.route('/', methods=['POST'])
@jwt_required()
def toggle_bookmark():
    """
    북마크 추가/제거 (토글)
    ---
    tags:
      - Bookmarks
    parameters:
      - name: job_notice_id
        in: body
        type: integer
        required: true
        description: Job notice ID to bookmark or unbookmark.
    responses:
      200:
        description: Bookmark toggled successfully.
      400:
        description: Invalid input.
      401:
        description: Unauthorized.
    """
    user_id = get_jwt_identity()
    
    data = request.get_json()
    job_notice_id = data.get('job_notice_id')

    if not job_notice_id:
        return jsonify({"error": "job_notice_id is required"}), 400

    bookmark = Bookmark.query.filter_by(user_id=user_id, job_notice_id=job_notice_id).first()
    
    if bookmark:
        db.session.delete(bookmark)
        db.session.commit()
        return jsonify({"message": "Bookmark removed"}), 200
    
    new_bookmark = Bookmark(user_id=user_id, job_notice_id=job_notice_id)
    db.session.add(new_bookmark)
    db.session.commit()
    
    return jsonify({"message": "Bookmark added"}), 201

@bp.route('/', methods=['GET'])
@jwt_required()
def get_bookmarks():
    """
    북마크 목록 조회
    ---
    tags:
      - Bookmarks
    parameters:
      - name: page
        in: query
        type: integer
        required: false
      - name: per_page
        in: query
        type: integer
        required: false
    responses:
      200:
        description: A list of bookmarks.
      401:
        description: Unauthorized.
     """
    
    user_id = get_jwt_identity()

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    bookmarks_query = Bookmark.query.filter_by(user_id=user_id).order_by(Bookmark.id.desc())
    
    bookmarks_paginated = bookmarks_query.paginate(page=page, per_page=per_page)

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
