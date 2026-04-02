# routes/auth_routes.py
# -*- coding: utf-8 -*-
"""
用户认证相关路由
"""

from flask import Blueprint, request, jsonify, g
from models import User
from models.database import get_db
from services import AuthService, login_required, FRPService
from config import BASE_DOMAIN

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册（通过产品序列号激活）"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    product_sn = data.get('product_sn')
    email = data.get('email')
    phone = data.get('phone')

    if not all([username, password, product_sn]):
        return jsonify({'error': '用户名、密码和产品序列号必填'}), 400

    try:
        user = User.create(
            username=username,
            password=password,
            product_sn=product_sn,
            email=email,
            phone=phone
        )

        token = AuthService.generate_token(
            user['id'],
            user['username'],
            user['subdomain']
        )

        return jsonify({
            'success': True,
            'message': '注册成功',
            'data': {
                'user_id': user['id'],
                'username': user['username'],
                'subdomain': user['subdomain'],
                'domain': f"{user['subdomain']}.{BASE_DOMAIN}",
                'frp_port': user['frp_port'],
                'token': token
            }
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not all([username, password]):
        return jsonify({'error': '用户名和密码必填'}), 400

    user = User.authenticate(username, password)

    if not user:
        return jsonify({'error': '用户名或密码错误'}), 401

    if user['status'] != 'active':
        return jsonify({'error': '账户已禁用'}), 403

    token = AuthService.generate_token(
        user['id'],
        user['username'],
        user['subdomain']
    )

    return jsonify({
        'success': True,
        'message': '登录成功',
        'data': {
            'user_id': user['id'],
            'username': user['username'],
            'subdomain': user['subdomain'],
            'domain': user.get('custom_domain') or f"{user['subdomain']}.{BASE_DOMAIN}",
            'token': token
        }
    })


@auth_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """获取当前用户信息"""
    user = User.get_by_id(g.user['user_id'])

    if not user:
        return jsonify({'error': '用户不存在'}), 404

    is_online = FRPService.check_subdomain_online(user['subdomain'])

    return jsonify({
        'success': True,
        'data': {
            'user_id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'phone': user['phone'],
            'subdomain': user['subdomain'],
            'domain': user.get('custom_domain') or f"{user['subdomain']}.{BASE_DOMAIN}",
            'nas_online': is_online,
            'created_at': user['created_at'],
            'last_login': user['last_login']
        }
    })


@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """修改密码"""
    data = request.json
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not all([old_password, new_password]):
        return jsonify({'error': '旧密码和新密码必填'}), 400

    user = User.authenticate(g.user['username'], old_password)
    if not user:
        return jsonify({'error': '旧密码错误'}), 401

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users SET password_hash = ? WHERE id = ?
    ''', (User.hash_password(new_password), g.user['user_id']))
    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'message': '密码修改成功'
    })