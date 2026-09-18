"""E2E：登录流程。"""
import pytest
from seed_data import seed_admin, login_as_admin


@pytest.mark.e2e
@pytest.mark.django_db(transaction=True)
def test_admin_login_reaches_home(live_server, page):
    seed_admin()
    login_as_admin(page, live_server)
    # 登录成功后到达首页，导航栏出现"统计分析"入口
    assert "统计分析" in page.content()
    assert live_server.url in page.url
