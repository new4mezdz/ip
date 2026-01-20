# models/database.py
# -*- coding: utf-8 -*-
"""
数据库模型定义
"""

import sqlite3
import os
from datetime import datetime
from config import DATABASE_PATH


def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库表"""
    conn = get_db()
    cursor = conn.cursor()

    # 用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            email VARCHAR(100),
            phone VARCHAR(20),
            product_sn VARCHAR(50) UNIQUE,
            subdomain VARCHAR(50) UNIQUE,
            frp_port INTEGER UNIQUE,
            status VARCHAR(20) DEFAULT 'inactive',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            last_heartbeat TIMESTAMP
        )
    ''')

    # 设备表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            device_sn VARCHAR(50) UNIQUE NOT NULL,
            device_name VARCHAR(100),
            local_ip VARCHAR(50),
            public_ip VARCHAR(50),
            frp_status VARCHAR(20) DEFAULT 'offline',
            last_online TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # 域名分配记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS domain_assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            device_id INTEGER NOT NULL,
            subdomain VARCHAR(50) UNIQUE NOT NULL,
            frp_port INTEGER NOT NULL,
            status VARCHAR(20) DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (device_id) REFERENCES devices(id)
        )
    ''')

    # 下载记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS download_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            file_name VARCHAR(255),
            file_type VARCHAR(50),
            ip_address VARCHAR(50),
            downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 产品信息表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            specs TEXT,
            price DECIMAL(10,2),
            image_url VARCHAR(255),
            doc_url VARCHAR(255),
            status VARCHAR(20) DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ 数据库初始化完成")


if __name__ == '__main__':
    init_db()