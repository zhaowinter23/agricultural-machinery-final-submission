"""
PythonAnywhere 部署用的 WSGI 配置模板。

用法：登录 PythonAnywhere → Web 页面 → 点开 WSGI configuration file 编辑器，
把里面的默认内容全部删除，粘贴本文件内容，然后只改下面两处「用户名」，
保存后点 Reload 即可。
"""


# ===== 只需要改这两行：把「你的用户名」换成你注册 PythonAnywhere 时的用户名 =====
PA_USERNAME = '你的用户名'
PA_DOMAIN = '你的用户名.pythonanywhere.com'
# ============================================================================

import os
import sys

# 项目所在目录（上传解压后位于 /home/用户名/agri_system）
path = f'/home/{PA_USERNAME}/agri_system'
if path not in sys.path:
    sys.path.insert(0, path)

# 部署环境变量：允许你的专属域名访问
os.environ['DJANGO_ALLOWED_HOSTS'] = PA_DOMAIN

# 指向 Django 项目的 settings 模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agricultural_machinery.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
