from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models.user import User

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            # 验证JWT令牌
            verify_jwt_in_request()
            
            # 获取用户ID
            user_id = get_jwt_identity()
            
            # 查询用户
            current_user = User.query.get(user_id)
            
            if not current_user:
                return jsonify({'message': '无效的用户令牌'}), 401
                
            # 将用户对象传递给被装饰的函数
            return f(current_user, *args, **kwargs)
            
        except Exception as e:
            return jsonify({'message': f'认证失败: {str(e)}'}), 401
            
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            # 验证JWT令牌
            verify_jwt_in_request()
            
            # 获取用户ID
            user_id = get_jwt_identity()
            
            # 查询用户
            current_user = User.query.get(user_id)
            
            if not current_user:
                return jsonify({'message': '无效的用户令牌'}), 401
                
            # 检查用户是否为医生
            if current_user.role != 'doctor':
                return jsonify({'message': '需要医生权限'}), 403
                
            # 将用户对象传递给被装饰的函数
            return f(current_user, *args, **kwargs)
            
        except Exception as e:
            return jsonify({'message': f'认证失败: {str(e)}'}), 401
            
    return decorated 