from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from models.user import User, db  # 🚀 修复核心：从这里导入 db，打破循环导入！
import traceback
from utils.auth import token_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not all(k in data for k in ['username', 'password', 'role']):
            return jsonify({'message': '缺少必要字段: username, password, role'}), 400

        if data['role'].lower() not in ['user', 'doctor']:
            return jsonify({'message': '角色必须是user或doctor'}), 400

        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': '用户名已存在'}), 400

        user = User(
            username=data['username'],
            role=data['role'].lower()
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        return jsonify({
            'message': '注册成功',
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role
            }
        }), 201

    except Exception as e:
        traceback.print_exc()
        return jsonify({'message': '注册失败', 'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not all(k in data for k in ['username', 'password', 'role']):
            return jsonify({'message': '缺少必要字段: username, password, role'}), 400

        if data['role'].lower() not in ['user', 'doctor']:
            return jsonify({'message': '角色必须是user或doctor'}), 400

        user = User.query.filter_by(username=data['username']).first()

        if user and user.check_password(data['password']) and user.role == data['role'].lower():
            additional_claims = {"role": user.role}
            access_token = create_access_token(
                identity=user.id,
                additional_claims=additional_claims
            )
            refresh_token = create_refresh_token(
                identity=user.id,
                additional_claims=additional_claims
            )

            return jsonify({
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token': access_token,  # 兼容前端直接拿 token 的逻辑
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'role': user.role
                }
            }), 200

        if not user:
            return jsonify({'message': '用户名不存在'}), 401
        elif not user.check_password(data['password']):
            return jsonify({'message': '密码错误'}), 401
        else:
            return jsonify({'message': '角色不匹配'}), 401

    except Exception as e:
        traceback.print_exc()
        return jsonify({'message': '登录失败', 'error': str(e)}), 500


# ================= 🚀 修改密码接口 =================
@auth_bp.route('/change-password', methods=['PUT'])
@token_required
def change_password(current_user):
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not old_password or not new_password:
        return jsonify({'message': '请提供旧密码和新密码'}), 400

    # 使用你模型里自带的 check_password 方法，极其优雅！
    if not current_user.check_password(old_password):
        return jsonify({'message': '旧密码输入错误，请重试'}), 401

    if old_password == new_password:
        return jsonify({'message': '新密码不能与旧密码相同'}), 400

    # 使用你模型里自带的 set_password 方法加密新密码
    current_user.set_password(new_password)
    db.session.commit()

    return jsonify({'message': '密码修改成功，请重新登录'}), 200