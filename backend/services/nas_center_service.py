# services/nas_center_service.py
# -*- coding: utf-8 -*-
"""
NAS 管理端通信服务
"""

import requests
from config import NAS_CENTER_URL, NAS_SHARED_SECRET


class NASCenterService:
    """NAS 管理端服务"""

    @staticmethod
    def get_stats():
        """获取节点统计信息（不需要认证）"""
        try:
            resp = requests.get(
                f"{NAS_CENTER_URL}/api/stats",
                timeout=5
            )
            if resp.status_code == 200:
                return resp.json()
            return None
        except Exception as e:
            print(f"[NAS Center] 获取统计失败: {e}")
            return None

    @staticmethod
    def get_system_status():
        """获取系统整体状态"""
        stats = NASCenterService.get_stats()
        if stats:
            return {
                'online': True,
                'total_nodes': stats.get('total_nodes', 0),
                'online_nodes': stats.get('online_nodes', 0),
                'offline_nodes': stats.get('offline_nodes', 0)
            }
        return {
            'online': False,
            'total_nodes': 0,
            'online_nodes': 0,
            'offline_nodes': 0
        }