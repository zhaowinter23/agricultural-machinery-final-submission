"""计算引擎 services.py 的单元测试。

【最重要的原则】所有期望值按 PPT/PDF 官方公式手算，绝不跑实现拿值——
避免"用实现验证实现"的同义反复测试。

被测公式：
  作业总时长  T = t_end - t_start，剔除关机停歇(间隔>阈值)，含段内非作业时间
  作业总行程  D = Σ √((x_{i+1}-x_i)² + (y_{i+1}-y_i)²)   基于 x,y 大地坐标
  作业面积    S = Σ(相邻工作点距离) × 幅宽
  田间平均速度 v = 工作点速度均值
"""
from datetime import datetime, timedelta
import pytest
from tracks.services import compute_track_stats


# ========== 作业面积：行程 × 幅宽 ==========
def test_area_is_working_distance_times_width(track_factory):
    t = track_factory(points=[{"x": 0, "y": 0}, {"x": 10, "y": 0}, {"x": 20, "y": 0}], width=2)
    stats = compute_track_stats(t)
    # 工作行程 = 10 + 10 = 20m；面积 = 20 × 2 = 40 m²
    assert stats["area"] == pytest.approx(40, abs=0.01)
    assert stats["area_mu"] == pytest.approx(40 / 666.667, abs=0.01)
    # 直接断言工作行程（变异测试发现：之前没查 working_distance，相关 bug 抓不到）
    assert stats["working_distance"] == pytest.approx(20, abs=0.01)


def test_area_only_counts_consecutive_working_pairs(track_factory):
    # 工作点、工作点、非工作、工作 —— 只有第 1-2 点是"相邻且都工作"
    t = track_factory(
        points=[{"x": 0, "y": 0, "working": True},
                {"x": 10, "y": 0, "working": True},
                {"x": 20, "y": 0, "working": False},
                {"x": 30, "y": 0, "working": True}],
        width=2,
    )
    stats = compute_track_stats(t)
    # 只有第1-2点计入：10m × 2 = 20 m²
    assert stats["area"] == pytest.approx(20, abs=0.01)


# ========== 作业总行程：x,y 欧氏距离（不是经纬度 haversine）==========
def test_total_distance_uses_xy_euclidean(track_factory):
    # 经典 3-4-5 直角三角形：欧氏距离应为 5m
    t = track_factory(points=[{"x": 0, "y": 0}, {"x": 3, "y": 4}])
    stats = compute_track_stats(t)
    assert stats["total_distance"] == pytest.approx(5, abs=0.01)


# ========== 作业总时长：剔除关机停歇，但保留段内非作业时间 ==========
def test_duration_excludes_shutdown_gap(track_factory):
    base = datetime(2022, 1, 1, 10, 0, 0)
    t = track_factory(points=[
        {"time": base},
        {"time": base + timedelta(seconds=60)},
        {"time": base + timedelta(seconds=60 + 5340)},  # +89min，关机停歇
    ])
    stats = compute_track_stats(t)
    assert stats["total_duration_hours"] == pytest.approx(1 / 60, abs=0.001)
    assert stats["shutdown_count"] == 1
    assert stats["shutdown_time_hours"] == pytest.approx(89 / 60, abs=0.001)
    # 3 个点被 1 处停歇切成 2 段（变异测试发现：之前没查 segments）
    assert stats["segments"] == 2


def test_duration_includes_idle_within_segment(track_factory):
    base = datetime(2022, 1, 1, 10, 0, 0)
    t = track_factory(points=[
        {"time": base, "working": True},
        {"time": base + timedelta(seconds=60), "working": True},
        {"time": base + timedelta(seconds=120), "working": False},  # 非作业，但连续
        {"time": base + timedelta(seconds=180), "working": True},
    ])
    stats = compute_track_stats(t)
    # 总时长 = 180s = 3min（含中间那段非作业时间）
    assert stats["total_duration_hours"] == pytest.approx(3 / 60, abs=0.001)
    # 有效作业时长：第1-2点 60s；第4点单点 0 → 共 60s = 1min
    assert stats["working_time_hours"] == pytest.approx(1 / 60, abs=0.001)
    # 段内非作业时长 = 总3min - 有效1min = 2min（变异测试发现：之前没查 idle_time）
    assert stats["idle_time_hours"] == pytest.approx(2 / 60, abs=0.001)


# ========== 关机停歇阈值边界（参数化）==========
@pytest.mark.parametrize("gap_seconds,expect_shutdown", [
    (600, False),  # 恰好等于阈值：不算关机（判定是 > 阈值）
    (601, True),   # 刚超阈值：算关机
])
def test_shutdown_threshold_boundary(track_factory, settings, gap_seconds, expect_shutdown):
    settings.TRACK_SHUTDOWN_THRESHOLD_SECONDS = 600
    base = datetime(2022, 1, 1, 10, 0, 0)
    t = track_factory(points=[
        {"time": base},
        {"time": base + timedelta(seconds=gap_seconds)},
    ])
    stats = compute_track_stats(t)
    assert stats["shutdown_count"] == (1 if expect_shutdown else 0)


# ========== 田间平均速度：工作点速度均值 ==========
def test_avg_speed_is_mean_of_working_points(track_factory):
    t = track_factory(points=[{"speed": 4}, {"speed": 6}, {"speed": 8}])
    stats = compute_track_stats(t)
    assert stats["avg_working_speed"] == pytest.approx(6, abs=0.01)


def test_avg_speed_ignores_non_working_points(track_factory):
    t = track_factory(points=[
        {"speed": 4, "working": True},
        {"speed": 100, "working": False},
        {"speed": 6, "working": True},
    ])
    stats = compute_track_stats(t)
    assert stats["avg_working_speed"] == pytest.approx(5, abs=0.01)


# ========== 边界用例 ==========
def test_empty_track_returns_none(track_factory):
    t = track_factory(points=[])
    assert compute_track_stats(t) is None


def test_single_point_zero_everything(track_factory):
    t = track_factory(points=[{"x": 5, "y": 5, "speed": 7}])
    stats = compute_track_stats(t)
    assert stats["total_duration_hours"] == 0
    assert stats["total_distance"] == 0
    assert stats["area"] == 0
    assert stats["avg_working_speed"] == pytest.approx(7, abs=0.01)


def test_all_non_working_zero_area_and_speed(track_factory):
    t = track_factory(points=[
        {"x": 0, "y": 0, "working": False},
        {"x": 10, "y": 0, "working": False},
    ])
    stats = compute_track_stats(t)
    assert stats["area"] == 0
    assert stats["working_distance"] == 0
    assert stats["avg_working_speed"] == 0
    # 但总行程仍统计（行程不区分工作状态）
    assert stats["total_distance"] == pytest.approx(10, abs=0.01)
