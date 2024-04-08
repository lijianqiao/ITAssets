# -*- coding: utf-8 -*-
# @Author: li
# @ProjectName: ITAssets
# @Email: lijianqiao2906@live.com
# @FileName: resource.py
# @DateTime: 2024/4/2 13:43
# @Docs: django-import-export 导出
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from import_export import resources
from import_export.fields import Field
from import_export.widgets import DateWidget, ForeignKeyWidget, ManyToManyWidget
from assets.models import Assets, Bussline, Department, Supplier
from repair.models import SparePart, RepairRecord


class AssetsResource(resources.ModelResource):
    """
    资产资源类，用于django-import-export库，定义了资产数据的导出行为。
    """
    id = Field(column_name='ID', attribute='id')
    bussline = Field(attribute='bussline', column_name=_('业务线'),
                     widget=ForeignKeyWidget(Bussline, 'name'))
    department = Field(attribute='department', column_name=_('部门'),
                       widget=ForeignKeyWidget(Department, 'name'))
    supplier = Field(attribute='supplier', column_name=_('供应商'),
                     widget=ForeignKeyWidget(Supplier, 'name'))
    purchase_date = Field(attribute='purchase_date', column_name=_('购入日期'),
                          widget=DateWidget(format='%Y/%m/%d'))
    name = Field(column_name=_('资产名称'), attribute='name')
    sn = Field(column_name=_('资产编号'), attribute='sn')
    expire_date = Field(column_name=_('过保期限(月份)'), attribute='expire_date')
    price = Field(column_name=_('价格'), attribute='price')
    repair_count = Field(column_name=_('维修次数'), attribute='repair_count')
    remake = Field(column_name=_('备注'), attribute='remake')
    creator = Field(column_name=_('创建人'), attribute='creator', widget=ForeignKeyWidget(User, 'username'))
    create_time = Field(column_name=_('创建时间'), attribute='create_time',
                        widget=DateWidget(format='%Y/%m/%d %H:%M:%S'))
    update_time = Field(column_name=_('更新时间'), attribute='update_time',
                        widget=DateWidget(format='%Y/%m/%d %H:%M:%S'))
    qr_code = Field(column_name=_('二维码路径'), attribute='qr_code')

    class Meta:
        model = Assets
        skip_unchanged = True
        report_skipped = False
        import_id_fields = ('sn',)
        export_formats = ['xlsx']

    def before_import_row(self, row, row_number=None, **kwargs):
        """
        在导入行之前执行的操作，用于将导入的数据转换为数据库中的数据。
        """
        bussline, created = Bussline.objects.get_or_create(name=row['业务线'])
        department, created = Department.objects.get_or_create(name=row['部门'], bussline=bussline)
        supplier, created = Supplier.objects.get_or_create(name=row['供应商'])
        row['bussline'] = bussline.id
        row['department'] = department.id
        row['supplier'] = supplier.id
        self._validate_and_set_default_values(row)

    @staticmethod
    def _validate_and_set_default_values(row):
        """
        验证并设置默认值。
        """
        row['repair_count'] = 0  # 维修次数默认为0

        price = row.get(_('price'))
        if isinstance(price, (int, float)) and price >= 0:
            row['price'] = price
        else:
            row['price'] = 0

        asset_type_display = row.get(_('资产类型'))
        if asset_type_display:
            for code, asset_type in Assets.ASSET_TYPE:
                if asset_type == asset_type_display:
                    row['asset_type'] = code
                    break
            else:
                raise ValidationError(f"无效的资产类型: {asset_type_display}")
        else:
            raise ValidationError("资产类型不能为空")

        status_display = row.get(_('状态'))
        if status_display:
            for code, status in Assets.ASSET_STATUS:
                if status == status_display:
                    row['status'] = code
                    break
            else:
                raise ValidationError(f"无效的状态: {status_display}")
        else:
            raise ValidationError("状态不能为空")

        is_active_display = row.get(_('是否启用'))
        is_active_dict = {_('是'): True, _('否'): False}
        if is_active_display in is_active_dict.keys():
            row['is_active'] = is_active_dict[is_active_display]
        else:
            raise ValidationError(_("是否启用不能为空"))

    @staticmethod
    def dehydrate_status(assets):
        """
        用于将状态字段转换为可读性更好的显示名称。
        """
        return assets.get_status_display()

    @staticmethod
    def dehydrate_asset_type(assets):
        """
        用于将资产类型字段转换为可读性更好的显示名称。
        """
        return assets.get_asset_type_display()

    @staticmethod
    def dehydrate_is_active(assets):
        """
        用于将是否启用字段转换为更友好的显示名称。
        """
        return _('是') if assets.is_active else _('否')


class RepairRecordResource(resources.ModelResource):
    id = Field(column_name='ID', attribute='id')
    repair_number = Field(attribute='repair_number', column_name=_('维修单号'))
    asset = Field(attribute='asset', column_name=_('资产SN'),
                  widget=ForeignKeyWidget(Assets, 'sn'))
    department = Field(attribute='department', column_name=_('部门'),
                       widget=ForeignKeyWidget(Department, 'name'))
    applicant = Field(attribute='applicant', column_name=_('申请人'))
    fault_description = Field(attribute='fault_description', column_name=_('故障描述'))
    supplier = Field(attribute='supplier', column_name=_('维修供应商'),
                     widget=ForeignKeyWidget(Supplier, 'name'))
    # repair_type = Field(attribute='repair_type', column_name=_('维修类别'))
    spare_part = Field(attribute='spare_part', column_name=_('维修备件'),
                       widget=ManyToManyWidget(SparePart, separator='|', field='sn'))
    # repair_status = Field(attribute='repair_status', column_name=_('维修状态'))
    repair_start_time = Field(attribute='repair_start_time', column_name=_('维修开始时间'),
                              widget=DateWidget(format='%Y/%m/%d %H:%M:%S'))
    repair_duration = Field(attribute='repair_duration', column_name=_('维修持续周期'))
    creator = Field(column_name=_('创建人'), attribute='creator', widget=ForeignKeyWidget(User, 'username'))
    create_time = Field(column_name=_('创建时间'), attribute='create_time',
                        widget=DateWidget(format='%Y/%m/%d %H:%M:%S'))
    update_time = Field(column_name=_('更新时间'), attribute='update_time',
                        widget=DateWidget(format='%Y/%m/%d %H:%M:%S'))

    class Meta:
        model = RepairRecord
        skip_unchanged = True
        report_skipped = False
        import_id_fields = ('repair_number',)
        export_formats = ['xlsx']

    @staticmethod
    def dehydrate_repair_type(repair):
        """
        用于将状态字段转换为可读性更好的显示名称。
        """
        return repair.get_repair_type_display()

    @staticmethod
    def dehydrate_repair_status(repair):
        """
        用于将状态字段转换为可读性更好的显示名称。
        """
        return repair.get_repair_status_display()
