from .settings import *

# 使用测试数据库
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'test_db.sqlite3',
    }
}

# 测试环境下的调试模式
DEBUG = True

# 测试环境下的媒体文件路径
MEDIA_ROOT = BASE_DIR / 'test_media' 