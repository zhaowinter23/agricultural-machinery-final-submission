"""
农机作业量统计计算引擎。

计算公式严格依据《企业实训阶段要求.pdf》模块1「农机作业量统计分析」与
《第一阶段展示PPT.pptx》中的官方公式：

- 作业总时长  T_total = t_end - t_start   （含作业+非作业时间，剔除关机停歇，多段累计）
- 作业总行程  D_total = Σ √((x_{i+1}-x_i)² + (y_{i+1}-y_i)²)   （基于 x,y 大地坐标，单位 m）
- 作业面积    S_field = Σ √((x_{i+1}-x_i)² + (y_{i+1}-y_i)²) · w   （仅工作状态点，w 为作业幅宽）
- 田间平均速度 v_work = Σ v_work(P_i) / n   （工作状态点的速度均值）

数据清洗（关机停歇）：相邻点时间间隔超过阈值（默认 600 秒）视为关机停歇，
该段时间从作业总时长中剔除，跨该间隔的位置跳跃不计入作业总行程与作业面积。
"""
import math
from datetime import timedelta
from django.conf import settings
from .models import TrackPoint


def euclidean(p1, p2):
    """两点（基于 x,y 大地坐标，单位米）的欧氏距离。"""
    return math.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2)


def detect_segments(points, threshold=None):
    """
    按时间间隔将有序轨迹点切分为连续段。

    关机停歇判定：相邻两点时间间隔 > threshold 视为关机停歇，
    在此处断开新段。返回 (segments, gaps)：
    - segments: list[list[TrackPoint]]，每个子段为连续轨迹点列表
    - gaps: list[float]，每处关机停歇的时长（秒）
    """
    if threshold is None:
        threshold = getattr(settings, 'TRACK_SHUTDOWN_THRESHOLD_SECONDS', 600)

    segments = []
    gaps = []
    current = []

    for i, p in enumerate(points):
        if i > 0:
            prev = points[i - 1]
            gap = (p.gps_time - prev.gps_time).total_seconds()
            if gap > threshold:
                # 关机停歇：结束当前段，记录停歇时长，开启新段
                if current:
                    segments.append(current)
                gaps.append(gap)
                current = []
        current.append(p)

    if current:
        segments.append(current)

    return segments, gaps


def _representative_width(working_points):
    """取作业点的代表性幅宽（非零众数/最大值），用于处理个别 0 值噪声。"""
    widths = [p.width for p in working_points if p.width and p.width > 0]
    if not widths:
        return 0.0
    # 众数（数据中幅宽通常恒定，如 5.3）
    freq = {}
    for w in widths:
        freq[w] = freq.get(w, 0) + 1
    return max(freq, key=freq.get)


def compute_track_stats(track):
    """
    计算单个地块的作业量统计指标（按官方公式）。

    返回字典保留旧键以兼容现有模板：
        total_duration / total_duration_hours     作业总时长（剔除关机停歇）
        total_distance / total_distance_km        作业总行程
        working_distance / working_distance_km    工作状态行程（用于面积）
        area / area_mu                            作业面积
        avg_working_speed                         田间平均作业速度
        point_count / working_point_count         轨迹点 / 工作点计数
    新增键：
        raw_duration_hours                        未清洗时长（首尾时间差）
        shutdown_count                            关机停歇次数
        shutdown_time_hours                       剔除的停歇时长
        working_time_hours                        有效作业时长（连续工作段时间之和）
        idle_time_hours                           段内非作业时长（=总时长-有效作业）
        segments                                  连续段数
        width                                     代表性作业幅宽
    """
    points = list(track.points.all().order_by('sequence'))
    if not points:
        return None

    threshold = getattr(settings, 'TRACK_SHUTDOWN_THRESHOLD_SECONDS', 600)
    segments, gaps = detect_segments(points, threshold)

    # ---- 作业总时长 T_total：累加各连续段时长（剔除关机停歇） ----
    total_duration = timedelta()
    for seg in segments:
        if len(seg) >= 2:
            total_duration += seg[-1].gps_time - seg[0].gps_time

    # 未清洗时长（首尾时间差），用于展示清洗价值
    raw_duration = points[-1].gps_time - points[0].gps_time
    shutdown_time = raw_duration - total_duration

    # ---- 作业总行程 D_total：段内相邻点 x,y 欧氏距离之和（跨停歇跳跃不计） ----
    total_distance = 0.0
    for seg in segments:
        for i in range(1, len(seg)):
            total_distance += euclidean(seg[i - 1], seg[i])

    # ---- 工作点相关 ----
    working_points = [p for p in points if p.working_status]
    working_speeds = [p.speed for p in working_points]
    rep_width = _representative_width(working_points)

    # ---- 作业面积 S_field：相邻工作点距离 × 幅宽之和 ----
    # 仅统计“相邻且均为工作状态”的点对；跨停歇或跨非作业状态的不计入。
    working_distance = 0.0
    area = 0.0
    for seg in segments:
        for i in range(1, len(seg)):
            cur, prev = seg[i], seg[i - 1]
            if cur.working_status and prev.working_status:
                d = euclidean(prev, cur)
                working_distance += d
                w = cur.width if cur.width and cur.width > 0 else rep_width
                area += d * w

    # ---- 有效作业时长 T_work：连续工作段（极大连续工作点）时长之和 ----
    # 每段为 首个工作点时间 ~ 末个工作点时间。
    working_time = timedelta()
    run_start = None
    run_last = None
    for p in points:
        if p.working_status:
            if run_start is None:
                run_start = p.gps_time
            run_last = p.gps_time
        else:
            if run_start is not None:
                working_time += run_last - run_start
                run_start = None
                run_last = None
    # 收尾：若最后一段为工作状态
    if run_start is not None:
        working_time += run_last - run_start

    # 段内非作业时长（地头转弯/停歇维护）= 总时长 - 有效作业时长
    idle_time = total_duration - working_time

    avg_working_speed = sum(working_speeds) / len(working_speeds) if working_speeds else 0.0

    return {
        # 旧键（兼容模板），值已按官方公式修正
        'total_duration': total_duration,
        'total_duration_hours': total_duration.total_seconds() / 3600 if total_duration else 0,
        'total_distance': total_distance,
        'total_distance_km': total_distance / 1000,
        'working_distance': working_distance,
        'working_distance_km': working_distance / 1000,
        'area': area,
        'area_mu': area / 666.667,  # 平方米 → 亩
        'avg_working_speed': avg_working_speed,
        'point_count': len(points),
        'working_point_count': len(working_points),
        # 新增键：清洗与时间构成明细
        'raw_duration_hours': raw_duration.total_seconds() / 3600 if raw_duration else 0,
        'shutdown_count': len(gaps),
        'shutdown_time_hours': shutdown_time.total_seconds() / 3600 if shutdown_time else 0,
        'working_time_hours': working_time.total_seconds() / 3600 if working_time else 0,
        'idle_time_hours': idle_time.total_seconds() / 3600 if idle_time else 0,
        'segments': len(segments),
        'width': rep_width,
    }


def compute_all_stats():
    """计算所有地块的统计指标，并附带全局汇总。"""
    from .models import Track
    results = []
    for track in Track.objects.all():
        stats = compute_track_stats(track)
        if stats:
            stats['track'] = track
            results.append(stats)
    return results


def compute_summary(all_stats):
    """基于 compute_all_stats 的结果计算全局汇总（用于统计页顶部卡片）。"""
    if not all_stats:
        return None
    total_duration = sum(s['total_duration_hours'] for s in all_stats)
    total_distance = sum(s['total_distance_km'] for s in all_stats)
    total_area = sum(s['area_mu'] for s in all_stats)
    total_points = sum(s['point_count'] for s in all_stats)
    total_working = sum(s['working_point_count'] for s in all_stats)
    total_shutdown = sum(s['shutdown_time_hours'] for s in all_stats)
    total_working_time = sum(s['working_time_hours'] for s in all_stats)
    raw_total = sum(s['raw_duration_hours'] for s in all_stats)
    # 平均速度：按工作点数加权
    wsum = sum(s['avg_working_speed'] * s['working_point_count'] for s in all_stats)
    avg_speed = wsum / total_working if total_working else 0
    return {
        'track_count': len(all_stats),
        'total_duration_hours': total_duration,
        'total_distance_km': total_distance,
        'total_area_mu': total_area,
        'total_points': total_points,
        'total_working_points': total_working,
        'total_shutdown_hours': total_shutdown,
        'total_working_hours': total_working_time,
        'raw_duration_hours': raw_total,
        'avg_speed': avg_speed,
    }
