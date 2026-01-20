# app.py
# -*- coding: utf-8 -*-
"""
IP分发端主程序
"""

import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from config import FlaskConfig, FLASK_PORT, BASE_DIR
from models import init_db
from routes import auth_bp, device_bp, public_bp
from services import FRPService


def create_app():
    """创建Flask应用"""
    app = Flask(__name__, static_folder='static')
    app.config.from_object(FlaskConfig)

    CORS(app, supports_credentials=True)

    app.register_blueprint(auth_bp)
    app.register_blueprint(device_bp)
    app.register_blueprint(public_bp)

    @app.route('/health')
    def health():
        return jsonify({'status': 'ok'})

    @app.route('/')
    def index():
        return send_from_directory('static', 'index.html')

    @app.route('/<path:path>')
    def static_files(path):
        return send_from_directory('static', path)

    return app


def main():
    """主函数"""
    print("=" * 50)
    print("🚀 IP分发端启动中...")
    print("=" * 50)

    init_db()

    os.makedirs(os.path.join(BASE_DIR, 'docs'), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, 'uploads'), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, 'static'), exist_ok=True)

    FRPService.generate_frps_config()

    app = create_app()

    print(f"📡 服务地址: http://0.0.0.0:{FLASK_PORT}")
    print("=" * 50)

    app.run(host='0.0.0.0', port=FLASK_PORT, debug=True)


if __name__ == '__main__':
    main()