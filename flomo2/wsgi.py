"""
WSGI配置

它为WSGI兼容的Web服务器提供了运行Django项目的接口
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flomo2.settings')

application = get_wsgi_application() 