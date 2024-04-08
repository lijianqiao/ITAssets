from _pydatetime import datetime

from auditlog.models import AuditlogHistoryField
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.files import File
from django.db import models

from auditlog.registry import auditlog
from django.utils import timezone


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


class Bussline(BaseModel):
    """业务线"""
    name = models.CharField(max_length=32, unique=True, verbose_name='业务线名称')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'bussline'
        verbose_name = '业务线'
        verbose_name_plural = verbose_name


class Department(BaseModel):
    """部门"""
    bussline = models.ForeignKey(Bussline, on_delete=models.CASCADE, verbose_name='业务线')
    name = models.CharField(max_length=32, unique=True, verbose_name='部门名称')

    def __str__(self):
        return f"{self.bussline.name}-{self.name}"

    class Meta:
        db_table = 'department'
        verbose_name = '部门'
        verbose_name_plural = verbose_name


class Supplier(BaseModel):
    """供应商"""
    name = models.CharField(max_length=32, unique=True, verbose_name='供应商名称')
    contact = models.CharField(max_length=32, null=True, blank=True, verbose_name='联系人')
    phone = models.CharField(max_length=32, null=True, blank=True, verbose_name='联系电话')
    email = models.EmailField(null=True, blank=True, verbose_name='邮箱')
    address = models.CharField(max_length=128, null=True, blank=True, verbose_name='地址')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'supplier'
        verbose_name = '供应商'
        verbose_name_plural = verbose_name


class Assetsmanager(BaseModel):
    """资产管理员"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='assets_manager', verbose_name='姓名')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True, verbose_name='部门')
    employee_id = models.CharField(max_length=32, null=True, blank=True, verbose_name='工号')
    phone = models.CharField(max_length=32, null=True, blank=True, verbose_name='联系电话')
    email = models.EmailField(null=True, blank=True, verbose_name='邮箱')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')

    def __str__(self):
        return f"{self.user.last_name}{self.user.first_name}-{self.department}"

    class Meta:
        db_table = 'assetsmanager'
        verbose_name = '资产管理员'
        verbose_name_plural = verbose_name


def department_path(instance, filename):
    """保存部门二维码路径，在 media/业务线/部门/文件名 下"""
    return '{0}/{1}/{2}'.format(instance.department.bussline.name, instance.department.name, filename)


class Assets(BaseModel):
    """资产信息"""
    ASSET_STATUS = [
        (0, '未使用'),
        (1, '使用中'),
        (2, '已报废'),
    ]
    ASSET_TYPE = [
        (0, '服务器'),
        (1, '网络设备'),
        (2, '存储设备'),
        (3, '安全设备'),
        (4, '电脑设备'),
        (5, '办公设备'),
        (6, '其他'),
    ]
    name = models.CharField(max_length=32, verbose_name='资产名称')
    sn = models.CharField(max_length=32, unique=True, verbose_name='资产编号')
    asset_type = models.SmallIntegerField(choices=ASSET_TYPE, default=4, verbose_name='资产类型')
    asset_location = models.CharField(max_length=80, null=True, blank=True, verbose_name='资产位置')
    bussline = models.ForeignKey(Bussline, on_delete=models.CASCADE, related_name='assets', verbose_name='业务线')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='assets', verbose_name='部门')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name='供应商')
    purchase_date = models.DateField(verbose_name='购买日期')
    expire_date = models.PositiveIntegerField(verbose_name='过保期限(月份)')
    price = models.FloatField(null=True, blank=True, verbose_name='价格')
    status = models.SmallIntegerField(choices=ASSET_STATUS, default=1, verbose_name='资产状态')
    qr_code = models.ImageField(upload_to=department_path, null=True, blank=True, verbose_name='二维码')
    repair_count = models.PositiveIntegerField(default=0, verbose_name='维修次数')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')

    def __str__(self):
        return f"{self.name}-{self.sn}"

    class Meta:
        db_table = 'assets'
        verbose_name = '资产信息'
        verbose_name_plural = verbose_name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.qr_code:
            self.generate_qr_code()
        if self.status == 2:  # 已报废
            self.is_active = False
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()  # 调用父级 clean 方法
        if self.purchase_date and self.purchase_date > timezone.now().date():
            raise ValidationError({'purchase_date': '购买日期不能大于当前时间'})
        if self.price and self.price < 0:
            raise ValidationError({'price': '采购价格不能小于0'})

    def generate_qr_code(self):
        """生成资产二维码"""
        import qrcode
        import io
        qr_content = f"{settings.PUBLIC_URL}/admin/assets/assets/{self.pk}/change/"

        qr = qrcode.main.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        # 添加内容到二维码
        qr.add_data(qr_content)
        qr.make(fit=True)
        # 将二维码保存为图片
        img = qr.make_image()
        img_io = io.BytesIO()
        img.save(img_io)
        img_io.seek(0)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{self.name}_{self.sn}_{timestamp}.png"
        self.qr_code.save(filename, File(img_io), save=False)

    def get_asset_type_display(self):
        return dict(self.ASSET_TYPE)[self.asset_type]


@receiver(post_delete, sender=Assets)
def delete_qr_code(sender, instance, **kwargs):
    """删除资产时删除本地二维码"""
    if instance.qr_code:
        instance.qr_code.delete(save=False)


auditlog.register(Bussline)
auditlog.register(Department)
auditlog.register(Supplier)
auditlog.register(Assetsmanager)
auditlog.register(Assets)
