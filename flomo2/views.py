"""
项目级视图
"""

from django.http import JsonResponse
import time
from django.conf import settings

def health_check(request):
    """
    简单的健康检查端点，用于监控应用状态
    返回基本系统信息和时间戳
    """
    return JsonResponse({
        'status': 'healthy',
        'timestamp': time.time(),
        'environment': 'production' if not settings.DEBUG else 'development',
    }) 