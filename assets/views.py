from django.db import models
from django.http import HttpResponse
from pyecharts import options as opts

from assets.models import Assets
from utils.sunburst_chart import generate_sunburst_chart


def asset_chart_view(request):
    """
    根据资产管理员权限展示资产分布的旭日图。

    参数:
    - request: HttpRequest对象，包含客户端请求的信息。

    返回值:
    - HttpResponse对象，包含渲染的旭日图HTML代码。
    """
    user = request.user
    if user.is_superuser:
        # 超级用户，获取所有部门的资产数据
        assets = Assets.objects.values('department__name', 'asset_type').annotate(count=models.Count('id'))
    else:
        # 资产管理员，只获取其管理的部门的资产数据
        assets = (Assets.objects.filter(department__assetsmanager__user=user)
                  .values('department__name', 'asset_type').annotate(count=models.Count('id')))

    # 处理资产数据，生成部门和资产类型的统计字典
    data_dict = {}
    total_count = 0
    for asset in assets:
        asset_type_display = Assets(asset_type=asset['asset_type']).get_asset_type_display()
        if asset['department__name'] not in data_dict:
            data_dict[asset['department__name']] = {}
        data_dict[asset['department__name']][asset_type_display] = asset['count']
        total_count += asset['count']

    # 将部门和资产类型统计数据转换为旭日图所需的格式
    data = []
    for department, asset_types in data_dict.items():
        children = []
        for asset_type, count in asset_types.items():
            children.append(opts.SunburstItem(name=asset_type, value=count))
        data.append(opts.SunburstItem(name=department, children=children))

    # 创建旭日图对象
    chart = generate_sunburst_chart(data, f"资产信息图 (总资产数: {total_count})")

    return HttpResponse(chart)
