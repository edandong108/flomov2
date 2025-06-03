"""
生产环境Django设置
"""

import os
import dj_database_url
from .settings import *

# 安全设置
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-flomo2-production-key-change-me')

# 允许的主机
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.railway.app',  # 允许所有railway.app子域名
    'flomov2-production.up.railway.app',  # 您的具体Railway域名
    # 在这里添加您的自定义域名
]

# 数据库配置 - 使用PostgreSQL
if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }
else:
    # 保持SQLite作为后备
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# 静态文件配置
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# 媒体文件配置
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 安全中间件
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Railway代理设置
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# HTTPS设置（在生产环境中启用）
# 禁用SECURE_SSL_REDIRECT以避免重定向循环
SECURE_SSL_REDIRECT = False  # 改为False，因为Railway已经处理HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# DeepSeek API 配置
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")  # 从环境变量获取API密钥

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
} 