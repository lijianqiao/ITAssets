"""
-*- coding: utf-8 -*-
 @Author: li
 @ProjectName: ITAssets
 @Email: lijianqiao2906@live.com
 @FileName: baseAdmin.py
 @DateTime: 2024/4/8 下午2:03
 @Docs:  各个app的admin基类
"""
from django.core.exceptions import PermissionDenied
from import_export.admin import ImportExportModelAdmin
from django.utils.translation import gettext_lazy as _

from assets.models import Assetsmanager


class Baseadmin(ImportExportModelAdmin):
    list_per_page = 20  # 每页显示对象的数量

    def creator_full_name(self, obj):
        return f"{obj.creator.last_name}{obj.creator.first_name}" if obj.creator else ''

    creator_full_name.short_description = _('创建人')

    # 将原有的creator从list_display中移除，并替换成creator_full_name
    def get_list_display(self, request, *args, **kwargs):
        list_display = super().get_list_display(request)
        if 'creator_full_name' not in list_display:
            if 'creator' in list_display:
                index = list_display.index('creator')
                list_display.pop(index)
            list_display.append('creator_full_name')
        return list_display

    def save_model(self, request, obj, form, change):
        """
        保存模型实例。
        :param request: HttpRequest对象
        :param obj: 要保存的对象
        :param form: 表单实例
        :param change: 布尔值，表示是新增还是修改
        :raises PermissionDenied: 如果用户没有权限，则抛出异常
        """
        if request.user.is_superuser or self._is_asset_manager_for_department(request.user, obj.department):
            obj.creator = request.user
            super().save_model(request, obj, form, change)
        else:
            raise PermissionDenied(_("无权限修改此对象"))

    def delete_model(self, request, obj):
        """
        删除模型实例。
        :param request: HttpRequest对象
        :param obj: 要删除的对象
        :raises PermissionDenied: 如果用户没有权限，则抛出异常
        """
        if request.user.is_superuser or self._is_asset_manager_for_department(request.user,
                                                                              getattr(obj, 'department', None)):
            obj.creator = request.user
            super().delete_model(request, obj)
        else:
            raise PermissionDenied(_("无权限修改此对象"))

    def get_queryset(self, request):
        """
        获得查询集时的权限过滤。
        :param request: HttpRequest对象
        :return: 过滤后的模型查询集
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(department__assetsmanager__user=request.user)

    def has_add_permission(self, request):
        """
        判断用户是否有添加对象的权限。
        :param request: HttpRequest对象
        :return: 布尔值，具有权限则为True，否则为False
        """
        return request.user.is_superuser or Assetsmanager.objects.filter(user=request.user).exists()

    def has_change_permission(self, request, obj=None):
        """
        判断用户是否有修改对象的权限。
        :param request: HttpRequest对象
        :param obj: 要修改的对象，可为空
        :return: 布尔值，具有权限则为True，否则为False
        """
        if request.user.is_superuser:
            return True
        if obj is not None and (
                obj.creator == request.user or self._is_asset_manager_for_department(request.user, obj.department)):
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        """
        判断用户是否有删除对象的权限。
        :param request: HttpRequest对象
        :param obj: 要删除的对象，可为空
        :return: 布尔值，具有权限则为True，否则为False
        """
        if request.user.is_superuser:
            return True
        if obj is not None and (
                obj.creator == request.user or self._is_asset_manager_for_department(request.user, obj.department)):
            return True
        return False

    @staticmethod
    def _is_asset_manager_for_department(user, department):
        """
        判断用户是否为指定部门的资产管理员。
        :param user: 用户对象
        :param department: 部门对象
        :return: 布尔值，是资产管理员则为True，否则为False
        """
        return Assetsmanager.objects.filter(user=user, department=department).exists()
