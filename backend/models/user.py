# models/user.py
# -*- coding: utf-8 -*-
"""
用户模型
"""

import sqlite3
import hashlib
import secrets
from datetime import datetime
from .database import get_db


class User:
    @staticmethod
    def hash_password(password):
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def generate_initial_password():
        """生成初始密码"""
        return secrets.token_urlsafe(8)

    @staticmethod
    def generate_subdomain(username):
        """生成子域名"""
        return username.lower().replace(' ', '-')

    @staticmethod
    def get_next_frp_port():
        """获取下一个可用的FRP端口"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT MAX(frp_port) FROM users')
        result = cursor.fetchone()[0]
        conn.close()
        return (result or 9999) + 1

    @staticmethod
    def create(username, password, product_sn, email=None, phone=None):
        """创建用户"""
        conn = get_db()
        cursor = conn.cursor()

        subdomain = User.generate_subdomain(username)
        frp_port = User.get_next_frp_port()
        password_hash = User.hash_password(password)

        try:
            cursor.execute('''
                INSERT INTO users (username, password_hash, email, phone, product_sn, subdomain, frp_port, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'active')
            ''', (username, password_hash, email, phone, product_sn, subdomain, frp_port))
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return {
                'id': user_id,
                'username': username,
                'subdomain': subdomain,
                'frp_port': frp_port
            }
        except sqlite3.IntegrityError as e:
            conn.close()
            raise ValueError(f"用户创建失败: {str(e)}")

    @staticmethod
    def authenticate(username, password):
        """用户认证"""
        conn = get_db()
        cursor = conn.cursor()
        password_hash = User.hash_password(password)

        cursor.execute('''
            SELECT id, username, subdomain, frp_port, status, custom_domain
            FROM users WHERE username = ? AND password_hash = ?
        ''', (username, password_hash))

        user = cursor.fetchone()

        if user:
            cursor.execute('''
                UPDATE users SET last_login = ? WHERE id = ?
            ''', (datetime.now(), user['id']))
            conn.commit()

        conn.close()
        return dict(user) if user else None

    @staticmethod
    def get_by_id(user_id):
        """根据ID获取用户"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None

    @staticmethod
    def get_by_subdomain(subdomain):
        """根据子域名获取用户"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE subdomain = ?', (subdomain,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None

    @staticmethod
    def update_heartbeat(user_id):
        """更新心跳时间"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET last_heartbeat = ? WHERE id = ?
        ''', (datetime.now(), user_id))
        conn.commit()
        conn.close()