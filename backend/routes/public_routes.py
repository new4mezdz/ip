# routes/public_routes.py
# -*- coding: utf-8 -*-
"""
公开页面路由
"""

import os
import re
from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
from models.database import get_db
from config import DOCS_DIR

public_bp = Blueprint('public', __name__, url_prefix='/api/public')


@public_bp.route('/products', methods=['GET'])
def list_products():
    """获取产品列表"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, name, description, specs, price, image_url, doc_url
        FROM products WHERE status = 'active'
        ORDER BY id DESC
    ''')

    products = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify({
        'success': True,
        'data': products
    })


@public_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """获取单个产品详情"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM products WHERE id = ? AND status = 'active'
    ''', (product_id,))

    product = cursor.fetchone()
    conn.close()

    if not product:
        return jsonify({'error': '产品不存在'}), 404

    return jsonify({
        'success': True,
        'data': dict(product)
    })


@public_bp.route('/docs', methods=['GET'])
def list_docs():
    """获取可下载的文档列表"""
    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR)
        return jsonify({'success': True, 'data': []})

    docs = []
    for filename in os.listdir(DOCS_DIR):
        filepath = os.path.join(DOCS_DIR, filename)
        if os.path.isfile(filepath):
            stat = os.stat(filepath)
            docs.append({
                'name': filename,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
            })

    return jsonify({
        'success': True,
        'data': docs
    })


@public_bp.route('/docs/download/<filename>', methods=['GET'])
def download_doc(filename):
    """下载文档"""
    if '..' in filename or filename.startswith('/'):
        return jsonify({'error': '非法文件名'}), 400

    filepath = os.path.join(DOCS_DIR, filename)

    if not os.path.exists(filepath):
        return jsonify({'error': '文件不存在'}), 404

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO download_logs (file_name, file_type, ip_address)
            VALUES (?, ?, ?)
        ''', (filename, 'doc', request.remote_addr))
        conn.commit()
        conn.close()
    except:
        pass

    return send_file(
        filepath,
        as_attachment=True,
        download_name=filename
    )


@public_bp.route('/check-subdomain', methods=['GET'])
def check_subdomain():
    """检查子域名是否可用"""
    subdomain = request.args.get('subdomain', '').lower().strip()

    if not subdomain:
        return jsonify({'error': '子域名不能为空'}), 400

    if len(subdomain) < 3 or len(subdomain) > 20:
        return jsonify({'error': '子域名长度需要3-20个字符'}), 400

    if not re.match(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$', subdomain):
        return jsonify({'error': '子域名只能包含字母、数字和连字符'}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE subdomain = ?', (subdomain,))
    exists = cursor.fetchone() is not None
    conn.close()

    return jsonify({
        'success': True,
        'available': not exists,
        'subdomain': subdomain
    })