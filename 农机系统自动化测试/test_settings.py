"""测试专用 settings。

继承主系统的全部配置（INSTALLED_APPS、MIDDLEWARE、TEMPLATES 等），仅覆盖数据库：
让测试库 test_db.sqlite3 写在本测试工程目录内，主系统目录完全不沾测试产物。
"""
import os
from agricultural_machinery.settings import *  # noqa: F401,F403,F405

_TEST_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(_TEST_DIR, "test_db.sqlite3"),
    }
}
