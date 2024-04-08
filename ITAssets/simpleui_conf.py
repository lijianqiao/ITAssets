"""
-*- coding: utf-8 -*-
 @Author: lee
 @ProjectName: ITAssets
 @Email: lijianqiao2906@live.com
 @FileName: simpleui_conf.py.py
 @DateTime: 2024/3/29 09:36
 @Docs:  simpleui配置文件
"""
# 隐藏首页服务器信息
SIMPLEUI_HOME_INFO = False
# 使用分析，默认开启，统计分析信息只是为了更好的帮助simpleui改进，并不会读取敏感信息。并且分析数据不会分享至任何第三方。
SIMPLEUI_ANALYSIS = False
# 离线模式
SIMPLEUI_STATIC_OFFLINE = True
# 关闭Loading遮罩层，默认开启
# SIMPLEUI_LOADING = False
# 默认主题
SIMPLEUI_DEFAULT_THEME = 'orange.css'
SIMPLEUI_CONFIG = {
    'system_keep': True,
    'dynamic': False,
    # 'menus': [{
    #     'name': '社区',
    #     'icon': 'fas fa-code',
    #     'url': 'https://simpleui.72wo.com',
    #     'codename': 'community'
    # }, {
    #     'name': '产品',
    #     'icon': 'fa fa-file',
    #     'codename': 'product',
    #     'models': [{
    #         'name': 'SimplePro',
    #         'codename': 'SimplePro',
    #         'icon': 'far fa-surprise',
    #         'models': [{
    #             'name': 'Pro文档',
    #             'url': 'https://simpleui.72wo.com/docs/simplepro'
    #         }, {
    #             'name': '购买Pro',
    #             'url': 'https://simpleui.72wo.com/simplepro'
    #         }]
    #     }, {
    #         'name': 'SimpleUI',
    #         'url': 'https://github.com/newpanjing/simpleui',
    #         'icon': 'fab fa-github',
    #         'codename': 'simpleui',
    #         'newTab': True
    #     }, {
    #         'name': '图片转换器',
    #         'url': 'https://convert.72wo.com',
    #         'icon': 'fab fa-github',
    #         'codename': 'convert',
    #         'newTab': True
    #     }, {
    #         'name': '全文检索',
    #         'url': 'https://github.com/sea-team/gofound',
    #         'icon': 'fab fa-github',
    #         'codename': 'gofound',
    #         'newTab': True
    #     }]
    # }]
}
# 关闭默认图标.
SIMPLEUI_DEFAULT_ICON = False
# 自定义图标
# SIMPLEUI_ICON = {
#     '系统管理': 'fab fa-apple',
#     '员工管理': 'fas fa-user-tie'
# }


# 登录页 & 首页logo
SIMPLEUI_LOGO = '/static/img/logo.png'

# 富文本编辑器

MEDITOR_DEFAULT_CONFIG = {
    'width': '90%',
    'height': 500,
    'toolbar': ["undo", "redo", "|",
                "bold", "del", "italic", "quote", "ucwords", "uppercase", "lowercase", "|",
                "h1", "h2", "h3", "h5", "h6", "|",
                "list-ul", "list-ol", "hr", "|",
                "link", "reference-link", "image", "code", "preformatted-text", "code-block", "table", "datetime",
                "emoji", "html-entities", "pagebreak", "goto-line", "|",
                "help", "info",
                "||", "preview", "watch", "fullscreen"],
    'upload_image_formats': ["jpg", "JPG", "jpeg", "JPEG", "gif", "GIF", "png",
                             "PNG", "bmp", "BMP", "webp", "WEBP"],
    'image_floder': 'editor',
    'theme': 'default',  # dark / default
    'preview_theme': 'default',  # dark / default
    'editor_theme': 'default',  # pastel-on-dark / default
    'toolbar_autofixed': True,
    'search_replace': True,
    'emoji': True,
    'tex': True,
    'flow_chart': True,
    'sequence': True,
    'language': 'zh'  # zh / en
}
