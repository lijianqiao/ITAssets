"""
-*- coding: utf-8 -*-
 @Author: li
 @ProjectName: ITAssets
 @Email: lijianqiao2906@live.com
 @FileName: urls.py
 @DateTime: 2024/4/8 上午11:22
 @Docs: 
"""

from django.urls import path
from . import views

app_name = 'repair'

urlpatterns = [
    path('department_to_spare/', views.department_to_spare, name='department_to_spare'),
    path('supplier_to_spare/', views.supplier_to_spare, name='supplier_to_spare'),
]
