"""E2E：地图页 —— 点击地块后侧栏信息面板出现（JS 交互）。

注：依赖 Leaflet（CDN）加载，需联网。无网环境下本用例可能超时。
"""
import pytest
from seed_data import seed_admin, seed_track, login_as_admin


@pytest.mark.e2e
@pytest.mark.django_db(transaction=True)
def test_map_click_track_shows_info_panel(live_server, page):
    seed_admin()
    seed_track()
    login_as_admin(page, live_server)

    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: errors.append(f"[{m.type}] {m.text}") if m.type in ("error", "warning") else None)

    page.wait_for_selector(".track-list li")
    # 先等 Leaflet(CDN) 加载完，否则 map 未初始化、点击会报错（降低 flaky）
    page.wait_for_function("typeof L !== 'undefined'", timeout=15000)
    leaflet_loaded = page.evaluate("typeof L")
    page.click(".track-list li:first-child")
    try:
        page.wait_for_selector("#trackInfoPanel .tip-title", timeout=15000)
    except Exception:
        page.screenshot(path="/tmp/map_debug.png")
        pytest.fail(
            f"信息面板未出现。Leaflet typeof L = {leaflet_loaded!r}；控制台错误:\n"
            + "\n".join(errors[:20])
        )
    assert "作业总时长" in page.locator("#trackInfoPanel").inner_text()
