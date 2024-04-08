from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ITAssets.baseAdmin import Baseadmin
from assets.models import Assets, Supplier
from utils.resource import RepairRecordResource
from .models import RepairRecord, SparePartType, SparePart


@admin.register(SparePartType)
class SparePartTypeAdmin(Baseadmin):
    """
    备件类型管理界面的自定义配置。
    """
    list_display = ['name', 'create_time', 'update_time', 'remake']
    search_fields = ['name']
    list_filter = ['create_time', 'update_time']
    fields = ['name', 'remake']


@admin.register(SparePart)
class SparePartAdmin(Baseadmin):
    """
    备件管理界面的自定义配置。
    """
    list_display = ['type', 'name', 'sn', 'supplier', 'warranty', 'create_time', 'update_time', 'remake']
    search_fields = ['name', 'sn']
    list_filter = ['type', 'supplier', 'warranty', 'create_time', 'update_time']
    fields = ['type', 'name', 'sn', 'supplier', 'warranty', 'remake']


@admin.register(RepairRecord)
class RepairRecordAdmin(Baseadmin):
    """
    维修记录管理界面的自定义配置。
    """
    resource_class = RepairRecordResource

    list_display = ['repair_number', 'asset', 'department', 'applicant', 'fault_description', 'supplier', 'repair_type',
                    'repair_status', 'repair_start_time', 'get_repair_duration_display']
    search_fields = ['asset__name', 'fault_description']
    list_filter = ['repair_start_time', 'department', 'supplier', 'repair_type', 'repair_status']
    fieldsets = (
        (_('主要信息'), {
            'fields': (
                'asset', 'department', 'supplier')
        }),
        (_('维修信息'), {
            'fields': ('applicant', 'fault_description', 'repair_type')
        }),
        (_('维修详情'), {
            'fields': ('spare_part',)
        }),
        (_('其他信息'), {
            'fields': ('repair_status', 'remake')
        }),
    )
    readonly_fields = ('repair_number', 'get_repair_duration_display')
    filter_horizontal = ('spare_part',)
    actions = ['department_to_spare', 'supplier_to_spare']

    def department_to_spare(self, request, queryset):
        """
        部门各备件类型维修按钮的动作。
        :param request:
        :param queryset:
        :return:
        """
        pass

    department_to_spare.short_description = _(' 部门各备件类型维修图标')
    department_to_spare.icon = "fa-solid fa-hammer"

    department_to_spare.type = 'success'

    department_to_spare.style = 'color:black;'
    department_to_spare.action_type = 1
    department_to_spare.action_url = '/repair/department_to_spare/'

    def supplier_to_spare(self, request, queryset):
        """
        供应商各备件类型维修按钮的动作。
        :param request:
        :param queryset:
        :return:
        """
        pass

    supplier_to_spare.short_description = _(' 供应商各备件类型维修图标')
    supplier_to_spare.icon = "fa-solid fa-screwdriver-wrench"

    supplier_to_spare.type = 'success'

    supplier_to_spare.style = 'color:black;'
    supplier_to_spare.action_type = 1
    supplier_to_spare.action_url = '/repair/supplier_to_spare/'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        重写外键字段的显示内容 - 不显示已报废的资产和不显示已禁止的供应商。。
        """
        if db_field.name == 'asset':
            kwargs['queryset'] = Assets.objects.exclude(status=2)
        if db_field.name == 'supplier':
            kwargs['queryset'] = Supplier.objects.exclude(is_active=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_repair_duration_display(self, obj):
        """
        获取维修持续时间的显示格式。
        :param obj: 维修记录对象
        :return: 维修持续时间的显示格式
        """
        if obj.repair_duration:
            days = obj.repair_duration.days
            hours, remainder = divmod(obj.repair_duration.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{days}天{hours}小时{minutes}分{seconds}秒"
        else:
            return "维修中"

    get_repair_duration_display.short_description = _('维修持续时间')

    def get_readonly_fields(self, request, obj=None):
        """
        当资产维修记录为“已维修”、“不为修”、“废弃”的时候，将所有字段都设置为只读。
        :param request: HttpRequest对象
        :param obj: 资产对象
        :return: 只读字段列表
        """
        if obj and obj.repair_status in [2, 3, 4] and not request.user.is_superuser:
            return [f.name for f in self.model._meta.fields if f.name != 'get_repair_duration_display']
        return super().get_readonly_fields(request, obj)
