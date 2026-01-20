# routes/device_routes.py
# -*- coding: utf-8 -*-
"""
NAS设备相关路由
"""

from flask import Blueprint, request, jsonify, g
from datetime import datetime
from models import User
from models.database import get_db
from services import FRPService, login_required
from config import BASE_DOMAIN, FRP_TOKEN, FRPS_PORT

device_bp = Blueprint('device', __name__, url_prefix='/api/device')


@device_bp.route('/register', methods=['POST'])
def device_register():
    """NAS设备注册/绑定"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    device_sn = data.get('device_sn')
    device_name = data.get('device_name')
    local_ip = data.get('local_ip')

    if not all([username, password, device_sn]):
        return jsonify({'error': '用户名、密码和设备序列号必填'}), 400

    user = User.authenticate(username, password)
    if not user:
        return jsonify({'error': '认证失败'}), 401

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM devices WHERE device_sn = ?', (device_sn,))
    existing = cursor.fetchone()

    if existing:
        cursor.execute('''
            UPDATE devices SET local_ip = ?, last_online = ? WHERE device_sn = ?
        ''', (local_ip, datetime.now(), device_sn))
    else:
        cursor.execute('''
            INSERT INTO devices (user_id, device_sn, device_name, local_ip, last_online)
            VALUES (?, ?, ?, ?, ?)
        ''', (user['id'], device_sn, device_name, local_ip, datetime.now()))

    conn.commit()
    conn.close()

    server_addr = request.host.split(':')[0]
    frpc_config = FRPService.generate_frpc_config(
        subdomain=user['subdomain'],
        server_addr=server_addr
    )

    return jsonify({
        'success': True,
        'message': '设备注册成功',
        'data': {
            'subdomain': user['subdomain'],
            'domain': f"{user['subdomain']}.{BASE_DOMAIN}",
            'frp_server': server_addr,
            'frp_port': FRPS_PORT,
            'frp_token': FRP_TOKEN,
            'frpc_config': frpc_config
        }
    })


@device_bp.route('/heartbeat', methods=['POST'])
def device_heartbeat():
    """设备心跳"""
    data = request.json
    device_sn = data.get('device_sn')
    public_ip = data.get('public_ip')

    if not device_sn:
        return jsonify({'error': '设备序列号必填'}), 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE devices 
        SET frp_status = 'online', 
            last_online = ?,
            public_ip = COALESCE(?, public_ip)
        WHERE device_sn = ?
    ''', (datetime.now(), public_ip, device_sn))

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'error': '设备未注册'}), 404

    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'message': 'heartbeat ok'
    })


@device_bp.route('/status', methods=['GET'])
@login_required
def device_status():
    """获取用户的设备状态"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM devices WHERE user_id = ?
    ''', (g.user['user_id'],))

    devices = cursor.fetchall()
    conn.close()

    result = []
    for device in devices:
        device_dict = dict(device)
        device_dict['frp_connected'] = FRPService.check_subdomain_online(
            g.user['subdomain']
        )
        result.append(device_dict)

    return jsonify({
        'success': True,
        'data': result
    })


@device_bp.route('/frp-config', methods=['GET'])
@login_required
def get_frp_config():
    """获取FRP客户端配置"""
    user = User.get_by_id(g.user['user_id'])

    server_addr = request.host.split(':')[0]
    frpc_config = FRPService.generate_frpc_config(
        subdomain=user['subdomain'],
        server_addr=server_addr
    )

    return jsonify({
        'success': True,
        'data': {
            'config': frpc_config,
            'subdomain': user['subdomain'],
            'domain': f"{user['subdomain']}.{BASE_DOMAIN}"
        }
    })