from datetime import datetime

from auditlog.models import AuditlogHistoryField
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from assets.models import Assets, Department, Supplier
from auditlog.registry import auditlog


class BaseModel(models.Model):
    """模型抽象基类"""
    history = AuditlogHistoryField()
    id = models.AutoField(primary_key=True, verbose_name='ID')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='创建人')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    remake = models.TextField(null=True, blank=True, verbose_name='备注')

    class Meta:
        abstract = True


class SparePartType(BaseModel):
    """备件类型"""
    name = models.CharField(max_length=255, verbose_name='备件类型')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'spare_part_type'
        verbose_name = '备件类型'
        verbose_name_plural = verbose_name


class SparePart(BaseModel):
    """备件"""
    type = models.ForeignKey(SparePartType, on_delete=models.CASCADE, verbose_name='备件类型')
    name = models.CharField(max_length=255, verbose_name='备件名称')
    sn = models.CharField(max_length=255, unique=True, verbose_name='备件序列号')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name='供应商')
    warranty = models.IntegerField(verbose_name='保修期限')

    def __str__(self):
        return f"{self.type.name}-{self.name}({self.sn})"

    class Meta:
        db_table = 'spare_part'
        verbose_name = '备件'
        verbose_name_plural = verbose_name


class RepairRecord(BaseModel):
    """维修记录"""
    REPAIR_TYPE_CHOICES = [
        (0, '供应商维修'),
        (1, '信息部维修'),
        (2, '供应商保修'),
        (3, '其他维修'),
    ]

    REPAIR_STATUS_CHOICES = [
        (0, '移送至信息部'),
        (1, '移送至供应商'),
        (2, '已维修'),
        (3, '不为修'),
        (4, '废弃'),
    ]
    repair_number = models.CharField(max_length=50, verbose_name='维修单号', blank=True)
    asset = models.ForeignKey(Assets, on_delete=models.CASCADE, verbose_name='资产名称')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='维修部门')
    applicant = models.CharField(max_length=50, verbose_name='申请维修人')
    fault_description = models.TextField(verbose_name='故障描述')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name='维修供应商')
    repair_type = models.SmallIntegerField(choices=REPAIR_TYPE_CHOICES, default=0, verbose_name='维修类别')
    spare_part = models.ManyToManyField(SparePart, verbose_name='选择维修备件')
    repair_status = models.SmallIntegerField(choices=REPAIR_STATUS_CHOICES, default=0, verbose_name='维修状态')
    repair_start_time = models.DateTimeField(auto_now_add=True, verbose_name='维修开始时间', null=True, blank=True)
    repair_duration = models.DurationField(verbose_name='维修持续周期', null=True, blank=True)

    def __str__(self):
        return f"{self.repair_number}-{self.asset.name}"

    class Meta:
        db_table = 'repair_record'
        verbose_name = '维修记录'
        verbose_name_plural = verbose_name

    def clean(self):
        super().clean()
        if self.repair_start_time and self.repair_start_time > timezone.now():
            raise ValidationError({'repair_start_time': '维修开始时间不能大于当前时间'})

    def save(self, *args, **kwargs):
        # 如果是新的维修记录
        if not self.pk:
            # 生成维修单号
            today = datetime.today().strftime('%Y%m%d')
            last_repair_record = RepairRecord.objects.filter(repair_number__startswith=f'WX{today}').order_by(
                '-repair_number').first()
            if last_repair_record:
                last_number = int(last_repair_record.repair_number[-4:])
                new_number = last_number + 1
            else:
                new_number = 1
            self.repair_number = f'WX{today}{new_number:04d}'

            # 更新维修状态
            self.asset.repair_count += 1
            self.asset.save()

        if self.repair_status in [2, 3, 4] and self.repair_start_time:
            # 计算维修持续周期
            self.repair_duration = timezone.now() - self.repair_start_time

        super().save(*args, **kwargs)


auditlog.register(SparePartType)
auditlog.register(SparePart)
auditlog.register(RepairRecord, m2m_fields={"spare_part"})
