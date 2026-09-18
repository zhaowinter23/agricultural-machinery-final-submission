"""E2E 测试数据播种与登录辅助（函数，非 fixture）。

为什么用函数不用 fixture：E2E 用 live_server，需 transaction=True 的数据库，
数据要在测试内创建并提交，才能被 live_server 线程看到。函数由测试在标记授权下
直接调用，避开 fixture 的 db/transaction_db 模式冲突，最稳。
"""
from datetime import datetime, timedelta


def seed_admin(username="e2e_admin", password="pass1234"):
    from django.contrib.auth.models import User
    return User.objects.create_user(
        username=username, password=password, is_staff=True
    )


def seed_track(name="地块e2e", n=20, width=2.0):
    from tracks.models import Track, TrackPoint
    t = Track.objects.create(name=name)
    base = datetime(2022, 1, 1, 10, 0, 0)
    objs = [
        TrackPoint(
            track=t, sequence=i + 1, gps_time=base + timedelta(seconds=i * 60),
            longitude=131.0 + i * 0.001, latitude=47.0,
            x=float(i * 10), y=0.0, speed=5.0, heading=0.0,
            working_status=True, width=width, depth=400.0, depth_standard=300.0,
        )
        for i in range(n)
    ]
    TrackPoint.objects.bulk_create(objs)
    return t


def login_as_admin(page, live_server):
    """以管理员身份走完登录流程，到达首页。"""
    page.goto(f"{live_server.url}/accounts/login/")
    page.fill('input[name="username"]', "e2e_admin")
    page.fill('input[name="password"]', "pass1234")
    page.click("#tabAdmin")
    page.click("button.login-btn")
    page.wait_for_selector(".navbar-brand")
