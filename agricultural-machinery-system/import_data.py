"""预加载CSV数据到数据库的脚本"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agricultural_machinery.settings')
django.setup()

import pandas as pd
from datetime import datetime
from tracks.models import Track, TrackPoint

DATA_DIR = os.path.join(os.path.dirname(__file__), '单个地块轨迹数据-8个地块', '单个地块轨迹数据-8个地块', 'csv')

if not os.path.exists(DATA_DIR):
    print(f'数据目录不存在: {DATA_DIR}')
    sys.exit(1)

files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith('.csv')])
print(f'找到 {len(files)} 个CSV文件')

for fname in files:
    track_name = f'地块{fname.rsplit(".", 1)[0]}'
    fpath = os.path.join(DATA_DIR, fname)

    track, created = Track.objects.get_or_create(name=track_name)
    if not created:
        track.points.all().delete()

    try:
        df = pd.read_csv(fpath, encoding='gbk')
        print(f'  读取 {fname}: {len(df)} 行')

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
        print(f'  导入 {track_name}: {len(point_objects)} 个轨迹点')
    except Exception as e:
        print(f'  导入 {fname} 失败: {e}')

print('数据导入完成！')
