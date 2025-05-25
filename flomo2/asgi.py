"""
ASGI配置

它为ASGI兼容的Web服务器提供了运行Django项目的异步接口
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flomo2.settings')

application = get_asgi_application() 