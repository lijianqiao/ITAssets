"""
-*- coding: utf-8 -*-
 @Author: li
 @ProjectName: ITAssets
 @Email: lijianqiao2906@live.com
 @FileName: sunburst_chart.py
 @DateTime: 2024/4/8 下午2:07
 @Docs: 
"""

from pyecharts.charts import Sunburst
from pyecharts import options as opts


def generate_sunburst_chart(data, title):
    """
    生成旭日图的通用函数。

    参数:
    - data: 旭日图的数据。
    - title: 旭日图的标题。

    返回值:
    - 旭日图的HTML代码。
    """
    sunburst = (
        Sunburst()
        .add(series_name="", data_pair=data, radius=[0, "90%"])
        .set_global_opts(title_opts=opts.TitleOpts(title=title),
                         toolbox_opts=opts.ToolboxOpts(is_show=True))
    )

    # 渲染图表
    chart = sunburst.render_embed()

    return chart
