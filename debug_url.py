"""
调试视图 - 提供基本的环境和设置信息

在生产环境中，此视图仅显示有限信息且需要特定参数以提高安全性
"""

from django.http import JsonResponse
import os
from django.conf import settings
import sys
import time
import socket

def debug_info(request):
    """返回环境变量和设置信息的JSON视图，用于调试"""
    
    # 检查是否在生产环境中
    is_production = not settings.DEBUG
    
    # 在生产环境中需要提供调试令牌参数
    debug_token = request.GET.get('debug_token', '')
    expected_token = "flomo2_debug_" + time.strftime("%Y%m%d")  # 基于日期的简单令牌
    
    # 在生产环境且没有提供正确的令牌时，限制访问
    if is_production and debug_token != expected_token:
        return JsonResponse({
            "status": "受限",
            "message": "此调试视图在生产环境中需要有效的调试令牌",
            "date": time.strftime("%Y-%m-%d"),
            "debug_enabled": settings.DEBUG,
        }, status=403, json_dumps_params={"ensure_ascii": False})
    
    # 基本系统信息（无论环境如何都可以显示）
    sys_info = {
        "Python版本": sys.version.split()[0],
        "平台": sys.platform,
        "主机名": socket.gethostname(),
        "设置模块": settings.__module__,
        "时间戳": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    
    # Django设置（安全信息）
    django_settings = {
        "DEBUG": settings.DEBUG,
        "ALLOWED_HOSTS": settings.ALLOWED_HOSTS,
        "STATIC_URL": settings.STATIC_URL,
        "MIDDLEWARE_COUNT": len(settings.MIDDLEWARE),
    }
    
    # 只在开发环境或有调试令牌时显示更多详细信息
    if not is_production or debug_token == expected_token:
        # 环境变量（敏感信息已过滤）
        env_vars = {
            "RAILWAY_ENVIRONMENT": os.environ.get("RAILWAY_ENVIRONMENT", "未设置"),
            "DJANGO_SETTINGS_MODULE": os.environ.get("DJANGO_SETTINGS_MODULE", "未设置"),
            "PYTHONPATH": os.environ.get("PYTHONPATH", "未设置"),
            "DEEPSEEK_API_KEY": "已设置" if os.environ.get("DEEPSEEK_API_KEY") else "未设置",
            "DEEPSEEK_API_KEY_IN_SETTINGS": "已设置" if getattr(settings, "DEEPSEEK_API_KEY", None) else "未设置",
        }
        
        # 更多Django设置
        django_settings.update({
            "STATIC_ROOT": getattr(settings, "STATIC_ROOT", "未设置"),
            "SECURE_SSL_REDIRECT": getattr(settings, "SECURE_SSL_REDIRECT", "未设置"),
            "SECURE_PROXY_SSL_HEADER": getattr(settings, "SECURE_PROXY_SSL_HEADER", "未设置"),
        })
        
        return JsonResponse({
            "环境变量": env_vars,
            "系统信息": sys_info,
            "Django设置": django_settings,
            "请求信息": {
                "路径": request.path,
                "方法": request.method,
                "是否安全": request.is_secure(),
                "主机": request.get_host(),
                "HTTP_X_FORWARDED_PROTO": request.META.get("HTTP_X_FORWARDED_PROTO", "未设置"),
            }
        }, json_dumps_params={"ensure_ascii": False})
    
    # 在生产环境中返回有限信息
    return JsonResponse({
        "系统信息": sys_info,
        "Django设置": django_settings,
        "状态": "正常",
    }, json_dumps_params={"ensure_ascii": False}) 