"""E2E：统计分析页真实渲染。"""
import pytest
from seed_data import seed_admin, seed_track, login_as_admin


@pytest.mark.e2e
@pytest.mark.django_db(transaction=True)
def test_statistics_page_shows_track_and_summary(live_server, page):
    seed_admin()
    seed_track()
    login_as_admin(page, live_server)

    page.goto(f"{live_server.url}/tracks/statistics/")
    page.wait_for_selector(".stat-card")
    body = page.content()
    # 汇总卡片 + 导出按钮
    assert "作业总面积" in body
    assert "导出Excel" in body
    # 表格里有刚导入的地块
    assert "地块e2e" in body
