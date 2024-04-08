import os

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path('assets/', include('assets.urls')),
    path('repair/', include('repair.urls')),
    path('', lambda request: redirect('/admin/', permanent=False)),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 网站标签页名称
admin.site.site_title = os.getenv("ADMIN_SITE_SITE_TITLE", "资产管理系统")

# 网站名称：显示在登录页和首页
admin.site.site_header = os.getenv("ADMIN_SITE_SITE_HEADER", "IT资产管理平台")
