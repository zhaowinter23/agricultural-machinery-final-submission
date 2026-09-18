"""E2E：轨迹查询页 —— 选地块、看概览与点表。"""
import pytest
from seed_data import seed_admin, seed_track, login_as_admin


@pytest.mark.e2e
@pytest.mark.django_db(transaction=True)
def test_query_select_track_shows_overview(live_server, page):
    seed_admin()
    t = seed_track()
    login_as_admin(page, live_server)

    page.goto(f"{live_server.url}/tracks/query/")
    page.wait_for_selector("#trackSelect")
    page.select_option("#trackSelect", str(t.pk))
    page.click('button[type="submit"]')
    page.wait_for_selector(".stat-card")

    body = page.content()
    assert "地块e2e" in body
    assert "作业总时长" in body          # 统计概览
    assert "轨迹点数据" in body          # 点表
