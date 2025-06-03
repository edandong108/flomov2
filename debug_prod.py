"""
用于测试生产环境设置的调试脚本
"""

import os
import sys
import django

# 设置为生产环境
os.environ['RAILWAY_ENVIRONMENT'] = 'production'
os.environ['DJANGO_SETTINGS_MODULE'] = 'flomo2.settings_production'

# 模拟生产环境的DeepSeek API密钥
test_api_key = "test_api_key_for_debugging_only"
os.environ['DEEPSEEK_API_KEY'] = test_api_key

print("已设置环境为生产环境")
print(f"RAILWAY_ENVIRONMENT: {os.environ.get('RAILWAY_ENVIRONMENT')}")
print(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")

try:
    django.setup()
    print("Django环境已成功加载")
except Exception as e:
    print(f"Django环境加载失败: {e}")

# 检查设置
try:
    from django.conf import settings
    print("\n===== 生产环境Django设置 =====")
    print(f"DEBUG: {settings.DEBUG}")
    print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print(f"DEEPSEEK_API_KEY设置: {'已设置' if hasattr(settings, 'DEEPSEEK_API_KEY') and settings.DEEPSEEK_API_KEY else '未设置'}")
    
    if hasattr(settings, 'DEEPSEEK_API_KEY'):
        key_value = settings.DEEPSEEK_API_KEY
        key_source = "环境变量" if key_value == test_api_key else "其他来源"
        print(f"DEEPSEEK_API_KEY来源: {key_source}")
        print(f"API密钥长度: {len(key_value)} 字符")
        
    # 检查其他重要的生产设置
    print(f"SECURE_SSL_REDIRECT: {getattr(settings, 'SECURE_SSL_REDIRECT', '未设置')}")
    print(f"SECURE_PROXY_SSL_HEADER: {getattr(settings, 'SECURE_PROXY_SSL_HEADER', '未设置')}")
    
except Exception as e:
    print(f"\n无法导入Django设置: {e}") 