from django.contrib import admin
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from ITAssets.baseAdmin import Baseadmin
from assets.models import Bussline, Department, Supplier, Assetsmanager, Assets
from utils.resource import AssetsResource


@admin.register(Bussline)
class BusslineAdmin(Baseadmin):
    # 定义事业线管理界面的展示字段、搜索字段、过滤器和编辑字段
    list_display = ['name', 'create_time', 'update_time', 'remake']
    search_fields = ['name']
    list_filter = ['create_time', 'update_time']
    fields = ['name', 'remake']


@admin.register(Department)
class DepartmentAdmin(Baseadmin):
    # 定义部门管理界面的展示字段、搜索字段、过滤器和编辑字段
    list_display = ['bussline', 'name', 'create_time', 'update_time', 'remake']
    search_fields = ['name']
    list_filter = ['bussline', 'create_time', 'update_time']
    fields = ['bussline', 'name', 'remake']


@admin.register(Supplier)
class SupplierAdmin(Baseadmin):
    # 定义供应商管理界面的展示字段、搜索字段、过滤器和编辑字段
    list_display = ['name', 'contact', 'phone', 'email', 'address', 'is_active', 'create_time',
                    'update_time', 'remake']
    search_fields = ['name']
    list_filter = ['is_active', 'create_time', 'update_time']
    fields = ['name', 'contact', 'phone', 'email', 'address', 'is_active', 'remake']


@admin.register(Assetsmanager)
class AssetsmanagerAdmin(Baseadmin):
    # 定义资产管理员管理界面的展示字段、搜索字段、过滤器和编辑字段
    list_display = ['user', 'department', 'phone', 'email', 'employee_id', 'is_active',
                    'create_time', 'update_time', 'remake']
    search_fields = ['user']
    list_filter = ['is_active', 'create_time', 'update_time']
    fields = ['user', 'department', 'phone', 'email', 'employee_id', 'is_active', 'remake']


@admin.register(Assets)
class AssetsAdmin(Baseadmin):
    """
    资产管理的模型注册类，定义了资产管理界面的展示字段、搜索字段、过滤器、字段分组和批量操作。
    """
    resource_class = AssetsResource

    list_display = ['name', 'sn', 'qr_code_preview', 'supplier', 'status', 'repair_count_link', 'is_active',
                    'create_time', 'update_time']
    search_fields = ['name', 'sn', 'asset_location']
    # autocomplete_fields = ['supplier']
    list_editable = ['status', 'is_active']
    list_select_related = ['supplier', 'department']
    list_filter = ['asset_type', 'supplier', 'bussline', 'department', 'status', 'is_active']
    fieldsets = (
        (_('主要信息'), {
            'fields': ('name', 'sn', 'asset_type', 'bussline', 'department', 'asset_location')
        }),
        (_('采购信息'), {
            'fields': ('supplier', 'purchase_date', 'expire_date', 'price')
        }),
        (_('状态信息'), {
            'fields': ('status', 'repair_count', 'is_active', 'remake')
        }),
    )
    actions = ['mark_as_active', 'mark_as_inactive', 'rose_diagram']
    readonly_fields = ['repair_count']
    ordering = ['-create_time']

    def mark_as_active(self, request, queryset):
        """
        批量将资产标记为启用状态。
        :param request: HttpRequest对象
        :param queryset: 被选中的资产对象列表
        """
        queryset.update(is_active=True, update_time=timezone.now())

    mark_as_active.short_description = _('标记为启用')

    def mark_as_inactive(self, request, queryset):
        """
        批量将资产标记为禁用状态。
        :param request: HttpRequest对象
        :param queryset: 被选中的资产对象列表
        """
        queryset.update(is_active=False, update_time=timezone.now())

    mark_as_inactive.short_description = _('标记为禁用')

    def rose_diagram(self, request, queryset):
        """
        资产信息图的按钮动作。
        :param request:
        :param queryset:
        :return:
        """
        pass

    rose_diagram.short_description = ' 资产信息图'
    rose_diagram.icon = "fa-brands fa-sellsy"
    rose_diagram.type = 'success'
    rose_diagram.style = 'color:black;'
    rose_diagram.action_type = 1
    rose_diagram.action_url = '/assets/asset_chart_view/'

    def qr_code_preview(self, obj):
        """
        生成二维码预览的HTML代码。
        :param obj: 资产对象
        :return: HTML代码
        """
        if obj.qr_code:
            return format_html(f'<img src="{obj.qr_code.url}" width="100" height="100">')
        return _('二维码未生成')

    qr_code_preview.short_description = _('二维码预览')

    def repair_count_link(self, obj):
        url = reverse('admin:repair_repairrecord_changelist')
        return format_html('<a href="{}?asset={}" target="_blank">{}</a>', url, obj.id,
                           obj.repair_count)

    repair_count_link.short_description = _('维修次数')

    def get_readonly_fields(self, request, obj=None):
        """
        当资产报废的时候，将所有字段都设置为只读。
        :param request: HttpRequest对象
        :param obj: 资产对象
        :return: 只读字段列表
        """
        if obj and obj.status == 2 and not request.user.is_superuser:
            return [f.name for f in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        重写外键字段的显示内容 - 不显示已禁止的供应商。
        """
        if db_field.name == 'supplier':
            kwargs['queryset'] = Supplier.objects.exclude(is_active=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
