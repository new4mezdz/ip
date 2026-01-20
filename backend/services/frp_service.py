# services/frp_service.py
# -*- coding: utf-8 -*-
"""
FRP服务管理
"""

import os
import subprocess
from config import (
    BASE_DIR, FRP_TOKEN, FRPS_PORT, FRPS_HTTP_PORT,
    FRPS_DASHBOARD_PORT, BASE_DOMAIN, FRPC_CONFIG_TEMPLATE
)


class FRPService:
    """FRP服务管理类"""

    FRPS_CONFIG_PATH = os.path.join(BASE_DIR, "frps.ini")

    @staticmethod
    def generate_frps_config():
        """生成frps配置文件"""
        config = f"""[common]
bind_port = {FRPS_PORT}
vhost_http_port = {FRPS_HTTP_PORT}
dashboard_port = {FRPS_DASHBOARD_PORT}
dashboard_user = admin
dashboard_pwd = admin123
token = {FRP_TOKEN}
subdomain_host = {BASE_DOMAIN}
log_file = ./frps.log
log_level = info
log_max_days = 3
"""
        with open(FRPService.FRPS_CONFIG_PATH, 'w') as f:
            f.write(config)
        print(f"✅ frps配置已生成: {FRPService.FRPS_CONFIG_PATH}")
        return config

    @staticmethod
    def generate_frpc_config(subdomain, server_addr):
        """生成frpc配置（提供给NAS客户端）"""
        return FRPC_CONFIG_TEMPLATE.format(
            server_addr=server_addr,
            server_port=FRPS_PORT,
            token=FRP_TOKEN,
            subdomain=subdomain
        )

    @staticmethod
    def start_frps():
        """启动frps服务"""
        if not os.path.exists(FRPService.FRPS_CONFIG_PATH):
            FRPService.generate_frps_config()

        try:
            result = subprocess.run(
                ['pgrep', '-f', 'frps'],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                print("⚠️ frps已在运行")
                return None
        except:
            pass

        try:
            proc = subprocess.Popen(
                ['./frps', '-c', FRPService.FRPS_CONFIG_PATH],
                cwd=BASE_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print(f"✅ frps已启动, PID: {proc.pid}")
            return proc
        except Exception as e:
            print(f"❌ frps启动失败: {e}")
            return None

    @staticmethod
    def get_client_status():
        """获取所有连接的客户端状态"""
        import requests
        try:
            resp = requests.get(
                f"http://127.0.0.1:{FRPS_DASHBOARD_PORT}/api/proxy/http",
                auth=('admin', 'admin123'),
                timeout=3
            )
            if resp.status_code == 200:
                return resp.json()
        except:
            pass
        return None

    @staticmethod
    def check_subdomain_online(subdomain):
        """检查某个子域名是否在线"""
        clients = FRPService.get_client_status()
        if clients and 'proxies' in clients:
            for proxy in clients['proxies']:
                if proxy.get('name', '').startswith(subdomain):
                    return proxy.get('status') == 'online'
        return False