import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Track, TrackPoint
from .services import compute_track_stats, compute_all_stats, compute_summary


def is_admin(user):
    return user.is_staff


@login_required
def home(request):
    tracks = Track.objects.all()
    total_points = TrackPoint.objects.count()
    return render(request, 'tracks/home.html', {'tracks': tracks, 'total_points': total_points})


@login_required
def track_geojson(request, pk):
    """返回指定地块的GeoJSON数据"""
    track = get_object_or_404(Track, pk=pk)
    points = track.points.all().order_by('sequence')

    coordinates = [[p.longitude, p.latitude] for p in points]
    feature = {
        'type': 'Feature',
        'properties': {
            'name': track.name,
            'id': track.pk,
            'point_count': points.count(),
        },
        'geometry': {
            'type': 'LineString',
            'coordinates': coordinates,
        }
    }

    # 每个轨迹点作为Point Feature
    point_features = []
    for p in points:
        point_features.append({
            'type': 'Feature',
            'properties': {
                'sequence': p.sequence,
                'gps_time': p.gps_time.strftime('%Y/%m/%d %H:%M:%S'),
                'gps_ts': int(p.gps_time.timestamp() * 1000),
                'speed': p.speed,
                'heading': p.heading,
                'working_status': p.working_status,
                'width': p.width,
                'depth': p.depth,
                'depth_standard': p.depth_standard,
            },
            'geometry': {
                'type': 'Point',
                'coordinates': [p.longitude, p.latitude],
            }
        })

    geojson = {
        'type': 'FeatureCollection',
        'features': [feature] + point_features,
    }
    return JsonResponse(geojson)


@login_required
def all_tracks_geojson(request):
    """返回所有地块的GeoJSON数据（仅线）"""
    tracks = Track.objects.all()
    features = []
    for track in tracks:
        points = track.points.all().order_by('sequence')
        if not points.exists():
            continue
        coordinates = [[p.longitude, p.latitude] for p in points]
        features.append({
            'type': 'Feature',
            'properties': {
                'name': track.name,
                'id': track.pk,
                'point_count': points.count(),
            },
            'geometry': {
                'type': 'LineString',
                'coordinates': coordinates,
            }
        })
    return JsonResponse({'type': 'FeatureCollection', 'features': features})


@login_required
def track_query(request):
    """轨迹属性查询（支持服务端分页与过滤）"""
    tracks = Track.objects.all()
    selected_track = None
    page_obj = None
    stats = None

    track_id = request.GET.get('track_id')
    track_name = request.GET.get('track_name', '').strip()

    # track_id优先，下拉选择比输入框更精确
    if track_id:
        try:
            selected_track = Track.objects.get(pk=track_id)
        except Track.DoesNotExist:
            messages.error(request, '未找到该地块')
    elif track_name:
        try:
            selected_track = Track.objects.get(name__contains=track_name)
        except Track.DoesNotExist:
            messages.error(request, f'未找到包含"{track_name}"的地块')
        except Track.MultipleObjectsReturned:
            messages.error(request, f'找到多个包含"{track_name}"的地块，请更精确输入')

    if selected_track:
        stats = compute_track_stats(selected_track)
        points_qs = selected_track.points.all().order_by('sequence')

        # ---- 过滤 ----
        status = request.GET.get('status', '')
        if status == 'working':
            points_qs = points_qs.filter(working_status=True)
        elif status == 'idle':
            points_qs = points_qs.filter(working_status=False)

        seq = request.GET.get('seq', '').strip()
        if seq.isdigit():
            points_qs = points_qs.filter(sequence=int(seq))

        speed_min = request.GET.get('speed_min', '').strip()
        speed_max = request.GET.get('speed_max', '').strip()
        if speed_min.replace('.', '', 1).isdigit():
            points_qs = points_qs.filter(speed__gte=float(speed_min))
        if speed_max.replace('.', '', 1).isdigit():
            points_qs = points_qs.filter(speed__lte=float(speed_max))

        # ---- 分页（每页 20 条） ----
        paginator = Paginator(points_qs, 20)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

    return render(request, 'tracks/query.html', {
        'tracks': tracks,
        'selected_track': selected_track,
        'page_obj': page_obj,
        'points_total': selected_track.points.count() if selected_track else 0,
        'filtered_count': page_obj.paginator.count if page_obj else 0,
        'stats': stats,
        'track_id_param': bool(track_id),
        'filters': {
            'status': request.GET.get('status', ''),
            'seq': request.GET.get('seq', ''),
            'speed_min': request.GET.get('speed_min', ''),
            'speed_max': request.GET.get('speed_max', ''),
        },
    })


@login_required
def statistics(request):
    """作业量统计分析（含全局汇总）"""
    all_stats = compute_all_stats()
    summary = compute_summary(all_stats)
    return render(request, 'tracks/statistics.html', {
        'all_stats': all_stats,
        'summary': summary,
    })


@login_required
def track_analysis(request, pk):
    """单地块作业量详情分析"""
    track = get_object_or_404(Track, pk=pk)
    stats = compute_track_stats(track)
    if not stats:
        messages.error(request, '该地块暂无轨迹点数据')
        return redirect('statistics')

    points = track.points.all().order_by('sequence')

    # 速度分布（工作点）直方图：0~12 km/h，每 2 km/h 一档
    speed_bins = [0, 2, 4, 6, 8, 10, 12]
    speed_labels = ['0-2', '2-4', '4-6', '6-8', '8-10', '10-12', '12+']
    speed_counts = [0] * len(speed_labels)
    for p in points:
        if p.working_status:
            v = p.speed
            idx = min(int(v // 2), len(speed_labels) - 1)
            speed_counts[idx] += 1

    # 深度分布（工作点）直方图：0~500 mm，每 100 mm 一档
    depth_labels = ['<300', '300-350', '350-400', '400-450', '450-500', '500+']
    depth_counts = [0] * len(depth_labels)
    for p in points:
        if p.working_status:
            d = p.depth
            if d < 300:
                depth_counts[0] += 1
            elif d < 350:
                depth_counts[1] += 1
            elif d < 400:
                depth_counts[2] += 1
            elif d < 450:
                depth_counts[3] += 1
            elif d < 500:
                depth_counts[4] += 1
            else:
                depth_counts[5] += 1

    # 时间构成：有效作业 / 段内非作业 / 关机停歇
    time_composition = {
        'labels': ['有效作业', '段内非作业', '关机停歇'],
        'data': [
            round(stats['working_time_hours'], 2),
            round(stats['idle_time_hours'], 2),
            round(stats['shutdown_time_hours'], 2),
        ],
    }

    # 关机停歇明细（各停歇段时长，分钟）
    from .services import detect_segments
    pts_list = list(points)
    _, gaps = detect_segments(pts_list)
    gap_minutes = [round(g / 60, 1) for g in gaps]

    chart_data = {
        'speed_labels': speed_labels,
        'speed_counts': speed_counts,
        'depth_labels': depth_labels,
        'depth_counts': depth_counts,
        'time_composition': time_composition,
        'gap_minutes': gap_minutes,
    }

    return render(request, 'tracks/analysis.html', {
        'track': track,
        'stats': stats,
        'chart_data': json.dumps(chart_data, ensure_ascii=False),
    })


@login_required
def track_stats_api(request, pk):
    """返回单地块统计 JSON（供地图侧栏信息面板使用）"""
    track = get_object_or_404(Track, pk=pk)
    stats = compute_track_stats(track)
    if not stats:
        return JsonResponse({'error': 'no data'}, status=404)
    # 仅返回可序列化字段
    return JsonResponse({
        'name': track.name,
        'id': track.pk,
        'total_duration_hours': round(stats['total_duration_hours'], 2),
        'raw_duration_hours': round(stats['raw_duration_hours'], 2),
        'shutdown_count': stats['shutdown_count'],
        'shutdown_time_hours': round(stats['shutdown_time_hours'], 2),
        'working_time_hours': round(stats['working_time_hours'], 2),
        'total_distance_km': round(stats['total_distance_km'], 2),
        'area_mu': round(stats['area_mu'], 2),
        'avg_working_speed': round(stats['avg_working_speed'], 2),
        'point_count': stats['point_count'],
        'working_point_count': stats['working_point_count'],
        'width': round(stats['width'], 2),
    })


@user_passes_test(is_admin)
def track_import(request):
    """导入地块轨迹数据"""
    if request.method == 'POST':
        import pandas as pd
        from datetime import datetime
        from django.core.files.storage import default_storage

        files = request.FILES.getlist('files')
        imported_count = 0
        skipped_tracks = []   # 已存在、被跳过未重复添加的地块

        for f in files:
            if not f.name.endswith('.csv'):
                messages.warning(request, f'{f.name} 不是CSV文件，已跳过')
                continue

            # 从文件名提取地块编号
            track_name = f.name.rsplit('.', 1)[0]
            full_name = f'地块{track_name}'

            # 防重复添加：地块已存在则跳过，不覆盖原有数据
            if Track.objects.filter(name=full_name).exists():
                skipped_tracks.append(full_name)
                continue

            # 保存临时文件
            path = default_storage.save(f'tmp/{f.name}', f)
            file_path = default_storage.path(path)

            try:
                df = pd.read_csv(file_path, encoding='gbk')
                track = Track.objects.create(name=full_name)

                # 批量创建轨迹点
                point_objects = []
                for _, row in df.iterrows():
                    gps_time = row.get('GPS时间')
                    if isinstance(gps_time, str):
                        for fmt in ('%Y/%m/%d %H:%M:%S', '%Y/%m/%d %H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'):
                            try:
                                gps_time = datetime.strptime(gps_time, fmt)
                                break
                            except ValueError:
                                continue
                    elif isinstance(gps_time, pd.Timestamp):
                        gps_time = gps_time.to_pydatetime()

                    point_objects.append(TrackPoint(
                        track=track,
                        sequence=int(row.get('序列号', 0)),
                        gps_time=gps_time,
                        longitude=float(row.get('经度', 0)),
                        latitude=float(row.get('纬度', 0)),
                        x=float(row.get('x', 0)),
                        y=float(row.get('y', 0)),
                        speed=float(row.get('速度(km/h)', 0)),
                        heading=float(row.get('航向', 0)),
                        working_status=str(row.get('工作状态', '')).upper() == 'TRUE',
                        width=float(row.get('幅宽(m)', 0)),
                        depth=float(row.get('深度(mm)', 0)),
                        depth_standard=float(row.get('深度标准值', 0)),
                    ))

                TrackPoint.objects.bulk_create(point_objects, batch_size=500)
                imported_count += 1
            except Exception as e:
                # 导入失败则回滚刚刚创建的空地块，避免残留
                Track.objects.filter(name=full_name).delete()
                messages.error(request, f'导入 {f.name} 失败：{str(e)}')
            finally:
                default_storage.delete(path)

        if imported_count > 0:
            messages.success(request, f'成功导入 {imported_count} 个地块数据')
        if skipped_tracks:
            messages.warning(
                request,
                f'以下地块已存在，已跳过未重复添加（如需更新数据请先在列表中删除原地块）：{"、".join(skipped_tracks)}'
            )

    return render(request, 'tracks/import.html', {'tracks': Track.objects.all()})


@user_passes_test(is_admin)
def track_delete(request, pk):
    """删除地块"""
    track = get_object_or_404(Track, pk=pk)
    if request.method == 'POST':
        track.delete()
        messages.success(request, f'已删除地块 {track.name}')
    return redirect('track_import')


@user_passes_test(is_admin)
def user_management(request):
    """用户账号管理"""
    users = User.objects.all().order_by('-date_joined')
    if request.method == 'POST':
        user_id = request.POST.get('delete_user_id')
        if user_id:
            user = get_object_or_404(User, pk=user_id)
            if user != request.user:
                user.delete()
                messages.success(request, f'已删除用户 {user.username}')
            else:
                messages.error(request, '不能删除当前登录的用户')
        return redirect('user_management')

    return render(request, 'tracks/user_management.html', {'users': users})


@login_required
def stats_chart_data(request):
    """返回统计图表数据API"""
    all_stats = compute_all_stats()
    labels = [s['track'].name for s in all_stats]
    data = {
        'labels': labels,
        'total_distance': [round(s['total_distance_km'], 2) for s in all_stats],
        'area': [round(s['area_mu'], 2) for s in all_stats],
        'avg_speed': [round(s['avg_working_speed'], 2) for s in all_stats],
        'duration': [round(s['total_duration_hours'], 2) for s in all_stats],
        'raw_duration': [round(s['raw_duration_hours'], 2) for s in all_stats],
    }
    return JsonResponse(data)


@login_required
def export_statistics(request):
    """导出各地块作业量统计为 Excel(.xlsx)"""
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

    all_stats = compute_all_stats()
    summary = compute_summary(all_stats)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = '农机作业量统计'

    # 标题行
    title_font = Font(bold=True, color='FFFFFF', size=12)
    title_fill = PatternFill('solid', fgColor='2D6A4F')
    thin = Side(style='thin', color='BBBBBB')
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    center = Alignment(horizontal='center', vertical='center')

    headers = ['地块名称', '作业总时长(h)', '关机停歇剔除(h)', '有效作业时长(h)',
               '作业总行程(km)', '作业面积(亩)', '田间平均速度(km/h)',
               '轨迹点数', '工作点数', '作业幅宽(m)']
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.font = title_font
        cell.fill = title_fill
        cell.alignment = center
        cell.border = border

    for r, s in enumerate(all_stats, 2):
        row = [
            s['track'].name,
            round(s['total_duration_hours'], 2),
            round(s['shutdown_time_hours'], 2),
            round(s['working_time_hours'], 2),
            round(s['total_distance_km'], 2),
            round(s['area_mu'], 2),
            round(s['avg_working_speed'], 2),
            s['point_count'],
            s['working_point_count'],
            round(s['width'], 2),
        ]
        for c, v in enumerate(row, 1):
            cell = ws.cell(row=r, column=c, value=v)
            cell.alignment = center
            cell.border = border

    # 汇总行：时长/行程/面积/点数为各列合计；速度列为全部工作点的加权整体均值
    if summary:
        sr = len(all_stats) + 3
        sum_row = ['合计',
                   round(summary['total_duration_hours'], 2),
                   round(summary['total_shutdown_hours'], 2),
                   round(summary['total_working_hours'], 2),
                   round(summary['total_distance_km'], 2),
                   round(summary['total_area_mu'], 2),
                   round(summary['avg_speed'], 2),
                   summary['total_points'],
                   summary['total_working_points'],
                   '']
        for c, v in enumerate(sum_row, 1):
            cell = ws.cell(row=sr, column=c, value=v)
            cell.font = Font(bold=True)
            cell.fill = PatternFill('solid', fgColor='E8F5E9')
            cell.alignment = center
            cell.border = border

        # 脚注：说明速度列口径与幅宽列留空原因，避免歧义
        note = ws.cell(
            row=sr + 1, column=1,
            value='注：田间平均速度为全部地块工作点按点数加权的整体均值；作业幅宽为地块固有参数，不参与合计。'
        )
        note.font = Font(italic=True, size=9, color='777777')

    # 列宽
    widths = [14, 14, 16, 16, 14, 14, 18, 10, 10, 12]
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="农机作业量统计.xlsx"'
    wb.save(response)
    return response
