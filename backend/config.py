import os
from datetime import timedelta

# ==================== 路径配置 ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
DOCS_DIR = os.path.join(BASE_DIR, "docs")

# ==================== 数据库配置 ====================
DATABASE_PATH = os.path.join(BASE_DIR, "portal.db")

# ==================== 服务端口配置 ====================
FLASK_PORT = 8080
FRPS_PORT = 7000           # FRP服务端口
FRPS_HTTP_PORT = 8080      # FRP HTTP代理端口
FRPS_DASHBOARD_PORT = 7500 # FRP管理面板端口

# ==================== 域名配置 ====================
BASE_DOMAIN = "nas.yourdomain.com"  # 你的基础域名
WILDCARD_DOMAIN = f"*.{BASE_DOMAIN}"

# ==================== 密钥配置 ====================
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
JWT_SECRET = os.environ.get('JWT_SECRET', 'jwt-secret-key-change-in-production')
FRP_TOKEN = os.environ.get('FRP_TOKEN', 'frp-auth-token-change-in-production')

# ==================== Flask 配置类 ====================
class FlaskConfig:
    SECRET_KEY = SECRET_KEY
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False  # 生产环境改为True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

# ==================== FRP配置模板 ====================
FRPC_CONFIG_TEMPLATE = """
[common]
server_addr = {server_addr}
server_port = {server_port}
token = {token}

[{subdomain}_web]
type = http
local_port = 5000
subdomain = {subdomain}
"""
