"""
Django环境变量和设置调试脚本
"""

import os
import sys
import django

# 根据环境设置Django设置模块
if os.environ.get('RAILWAY_ENVIRONMENT', '') == 'production':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flomo2.settings_production')
    print("使用生产环境设置: flomo2.settings_production")
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flomo2.settings')
    print("使用开发环境设置: flomo2.settings")

try:
    django.setup()
    print("Django环境已成功加载")
except Exception as e:
    print(f"Django环境加载失败: {e}")

def check_environment():
    """检查环境变量和系统信息"""
    print("\n===== 环境变量检查 =====")
    
    # 检查Railway环境变量
    railway_env = os.environ.get("RAILWAY_ENVIRONMENT", "未设置")
    print(f"RAILWAY_ENVIRONMENT: {railway_env}")
    
    # 检查Django设置模块
    django_settings = os.environ.get("DJANGO_SETTINGS_MODULE", "未设置")
    print(f"DJANGO_SETTINGS_MODULE: {django_settings}")
    
    # 检查DeepSeek API密钥
    deepseek_key = os.environ.get("DEEPSEEK_API_KEY", "")
    print(f"DEEPSEEK_API_KEY环境变量: {'已设置' if deepseek_key else '未设置'}")
    
    # 系统信息
    print("\n===== 系统信息 =====")
    print(f"Python版本: {sys.version}")
    print(f"平台: {sys.platform}")
    print(f"当前目录: {os.getcwd()}")
    
    # 尝试导入Django设置
    try:
        from django.conf import settings
        print("\n===== Django设置 =====")
        print(f"DEBUG: {settings.DEBUG}")
        print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        print(f"DEEPSEEK_API_KEY设置: {'已设置' if hasattr(settings, 'DEEPSEEK_API_KEY') and settings.DEEPSEEK_API_KEY else '未设置'}")
        if hasattr(settings, 'DEEPSEEK_API_KEY'):
            key_source = "环境变量" if settings.DEEPSEEK_API_KEY == os.environ.get("DEEPSEEK_API_KEY", "") else "硬编码或默认值"
            print(f"DEEPSEEK_API_KEY来源: {key_source}")
    except Exception as e:
        print(f"\n无法导入Django设置: {e}")

if __name__ == "__main__":
    check_environment() 