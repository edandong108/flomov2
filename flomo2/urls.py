"""项目URL配置文件"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import health_check
from debug_url import debug_info

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('notes.urls')),  # 默认路径使用notes应用的URL配置
    path('health-check/', health_check, name='health_check'),  # 简单的健康检查端点
    path('debug-info/', debug_info, name='debug_info'),  # 调试信息端点
]

# 在开发环境中添加媒体文件的URL
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 