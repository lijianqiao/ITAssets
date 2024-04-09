from django.db import models
from django.http import HttpResponse
from pyecharts import options as opts

from assets.models import Assetsmanager
from repair.models import RepairRecord
from utils.sunburst_chart import generate_sunburst_chart


def department_to_spare(request):
    """
        根据资产管理员权限展示部门各备件类型资产维修记录的旭日图。

        参数:
        - request: HttpRequest对象，包含客户端请求的信息。

        返回值:
        - HttpResponse对象，包含渲染的旭日图HTML代码。
        """
    user = request.user
    if user.is_superuser:
        # 超级用户，获取所有部门的维修记录数据
        records = RepairRecord.objects.values('department__name', 'spare_part__type__name').annotate(
            count=models.Count('id'))
    else:
        # 资产管理员，只获取其管理的部门的维修记录数据
        department = Assetsmanager.objects.get(user=user).department
        records = (RepairRecord.objects.filter(department=department)
                   .values('department__name', 'spare_part__type__name').annotate(count=models.Count('id')))

    # 处理维修记录数据，生成部门和备件类型的统计字典
    data_dict = {}
    total_count = 0
    for record in records:
        if record['department__name'] not in data_dict:
            data_dict[record['department__name']] = {}
        data_dict[record['department__name']][record['spare_part__type__name']] = record['count']
        total_count += record['count']

    # 将部门和备件类型统计数据转换为旭日图所需的格式
    data = []
    for department, spare_part_types in data_dict.items():
        children = []
        for spare_part_type, count in spare_part_types.items():
            children.append(opts.SunburstItem(name=spare_part_type, value=count))
        data.append(opts.SunburstItem(name=department, children=children))

    # 创建旭日图对象

    chart = generate_sunburst_chart(data, f"部门各备件类型资产维修记录 (总记录数: {total_count})")

    return HttpResponse(chart)


def supplier_to_spare(request):
    """
    根据资产管理员权限展示供应商各备件类型资产维修记录的旭日图。
    """
    user = request.user
    if user.is_superuser:
        # 超级用户，获取所有供应商的维修记录数据
        records = RepairRecord.objects.values('supplier__name', 'spare_part__type__name').annotate(
            count=models.Count('id'))
    else:
        # 资产管理员，只获取其管理的部门的维修记录数据
        department = Assetsmanager.objects.get(user=user).department
        records = (RepairRecord.objects.filter(department=department)
                   .values('supplier__name', 'spare_part__type__name').annotate(count=models.Count('id')))

    data_dict = {}
    total_count = 0
    for record in records:
        if record['supplier__name'] not in data_dict:
            data_dict[record['supplier__name']] = {}
        data_dict[record['supplier__name']][record['spare_part__type__name']] = record['count']
        total_count += record['count']

    data = []
    for supplier, spare_part_types in data_dict.items():
        children = []
        for spare_part_type, count in spare_part_types.items():
            children.append(opts.SunburstItem(name=spare_part_type, value=count))
        data.append(opts.SunburstItem(name=supplier, children=children))

    chart = generate_sunburst_chart(data, f"供应商各备件类型资产维修记录 (总记录数: {total_count})")

    return HttpResponse(chart)
