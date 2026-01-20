# services/auth_service.py
# -*- coding: utf-8 -*-
"""
JWT认证服务
"""

import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, g
from config import JWT_SECRET


class AuthService:
    """认证服务"""

    TOKEN_EXPIRE_HOURS = 24 * 7  # 7天有效期

    @staticmethod
    def generate_token(user_id, username, subdomain):
        """生成JWT令牌"""
        payload = {
            'user_id': user_id,
            'username': username,
            'subdomain': subdomain,
            'exp': datetime.utcnow() + timedelta(hours=AuthService.TOKEN_EXPIRE_HOURS),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

    @staticmethod
    def verify_token(token):
        """验证JWT令牌"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @staticmethod
    def get_token_from_request():
        """从请求中获取令牌"""
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header[7:]
        return request.cookies.get('token')


def login_required(f):
    """登录验证装饰器"""

    @wraps(f)
    def decorated(*args, **kwargs):
        token = AuthService.get_token_from_request()

        if not token:
            return jsonify({'error': '未登录'}), 401

        payload = AuthService.verify_token(token)
        if not payload:
            return jsonify({'error': '令牌无效或已过期'}), 401

        g.user = payload
        return f(*args, **kwargs)

    return decorated


def admin_required(f):
    """管理员验证装饰器"""

    @wraps(f)
    def decorated(*args, **kwargs):
        token = AuthService.get_token_from_request()

        if not token:
            return jsonify({'error': '未登录'}), 401

        payload = AuthService.verify_token(token)
        if not payload:
            return jsonify({'error': '令牌无效或已过期'}), 401

        if payload.get('role') != 'admin':
            return jsonify({'error': '需要管理员权限'}), 403

        g.user = payload
        return f(*args, **kwargs)

    return decorated