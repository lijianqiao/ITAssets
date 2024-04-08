"""
-*- coding: utf-8 -*-
 @Author: li
 @ProjectName: ITAssets
 @Email: lijianqiao2906@live.com
 @FileName: urls.py
 @DateTime: 2024/4/8 上午9:48
 @Docs: 资产路由-生成资产信息玫瑰图
"""

from django.urls import path
from . import views

app_name = 'assets'

urlpatterns = [
    path('asset_chart_view/', views.asset_chart_view, name='asset_chart_view'),
]
