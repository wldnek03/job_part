from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)
from app.models import User, db
import re  # 이메일 검증을 위한 정규식

bp = Blueprint('auth', __name__)

# 이메일 형식 검증 함수
def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email)

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # 요청 데이터 검증
    if not data or 'username' not in data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Missing required fields: username, email, and password"}), 400

    # 이메일 형식 검증
    if not is_valid_email(data['email']):
        return jsonify({"error": "Invalid email format"}), 400

    # 중복 회원 검사
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already exists"}), 400

    # 비밀번호 암호화 (pbkdf2:sha256 사용)
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')

    # 사용자 저장
    new_user = User(username=data['username'], email=data['email'], password=hashed_password)
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    # 요청 데이터 검증
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Missing required fields: email and password"}), 400

    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid credentials"}), 401

    # JWT 토큰 생성 (Access Token 및 Refresh Token)
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    # 로그인 이력 저장 (예시)
    user.last_login = db.func.now()
    db.session.commit()

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 200

@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    
    # 새로운 Access Token 생성
    new_access_token = create_access_token(identity=current_user_id)
    
    return jsonify({"access_token": new_access_token}), 200

@bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()  # 현재 사용자 ID 가져오기
    return jsonify({"message": f"Hello user {current_user_id}!"}), 200

@bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()

    # 비밀번호 변경
    if 'password' in data:
        user.password = generate_password_hash(data['password'], method='pbkdf2:sha256')

    # 프로필 정보 수정
    if 'username' in data:
        user.username = data['username']
    
    db.session.commit()
    
    return jsonify({"message": "Profile updated successfully"}), 200