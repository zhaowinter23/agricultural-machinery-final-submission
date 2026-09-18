"""独立测试工程根 conftest。

核心作用：把【主系统目录】加入 sys.path，使 tracks / accounts / agricultural_machinery
可被 import。这样测试代码与主系统物理隔离，主系统目录保持干净，零测试文件混入。

模型导入放在 fixture 内部（懒加载），因为 conftest 模块级代码执行时 Django 尚未
setup（apps 未加载），在 fixture 调用时（pytest_configure 之后）才安全。
"""
import os
import sys
from datetime import datetime, timedelta

import pytest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
SYSTEM_DIR = os.path.abspath(
    os.path.join(TEST_DIR, "..", "agricultural-machinery-system")
)

for _d in (TEST_DIR, SYSTEM_DIR):
    if _d not in sys.path:
        sys.path.insert(0, _d)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_settings")
# pytest-playwright 在异步事件循环里跑测试，pytest-django 的建库是同步的，
# Django 的异步安全检查会拦截。测试环境关闭该检查（仅测试，不影响生产）。
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")


@pytest.fixture
def track_factory(db):
    """合成地块数据工厂：造小地块 + 若干轨迹点，无关字段用默认值兜底。"""
    from tracks.models import Track, TrackPoint

    counter = [0]

    def make(name=None, points=None, width=2.0, depth_standard=300):
        counter[0] += 1
        track = Track.objects.create(name=name or f"测试地块{counter[0]}")
        base_time = datetime(2022, 1, 1, 10, 0, 0)
        objs = []
        for i, p in enumerate(points or []):
            working = p.get("working", True)
            objs.append(TrackPoint(
                track=track,
                sequence=i + 1,
                gps_time=p.get("time", base_time + timedelta(seconds=i * 60)),
                longitude=p.get("lng", 131.0),
                latitude=p.get("lat", 47.0),
                x=p.get("x", 0.0),
                y=p.get("y", 0.0),
                speed=p.get("speed", 5.0),
                heading=p.get("heading", 0.0),
                working_status=working,
                width=p.get("width", width),
                depth=p.get("depth", 400.0 if working else 0.0),
                depth_standard=p.get("depth_standard", depth_standard),
            ))
        if objs:
            TrackPoint.objects.bulk_create(objs)
        return track

    return make


@pytest.fixture
def admin_user(db):
    """管理员账号（is_staff=True）。"""
    from django.contrib.auth.models import User
    return User.objects.create_user(
        username="admin_test", password="pass1234", is_staff=True
    )


@pytest.fixture
def regular_user(db):
    """普通用户账号（is_staff=False）。"""
    from django.contrib.auth.models import User
    return User.objects.create_user(
        username="user_test", password="pass1234", is_staff=False
    )
