"""数据导入集成测试 —— 锁定"防重复导入"修复。

回归场景：之前导入已存在的地块会静默覆盖、无提示。修复后应"跳过 + 提示"。
"""
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from tracks.models import Track, TrackPoint

CSV_LINE = ("序列号,GPS时间,经度,纬度,x,y,速度(km/h),航向,工作状态,幅宽(m),深度(mm),深度标准值\n"
            "1,2022/01/01 10:00:00,131.0,47.0,0,0,5.0,0,TRUE,2,400,300\n")


@pytest.mark.django_db
def test_duplicate_import_is_skipped_not_overwritten(client, admin_user, track_factory):
    existing = track_factory(name="地块dup", points=[{"x": 0, "y": 0}])
    before_track_count = Track.objects.count()
    before_point_count = existing.points.count()

    client.force_login(admin_user)
    f = SimpleUploadedFile("dup.csv", CSV_LINE.encode("gbk"), content_type="text/csv")
    resp = client.post("/tracks/import/", {"files": f})

    assert Track.objects.count() == before_track_count
    assert Track.objects.get(name="地块dup").points.count() == before_point_count
    assert "已存在" in resp.content.decode()
    assert "跳过" in resp.content.decode()


@pytest.mark.django_db
def test_new_import_creates_track(client, admin_user):
    before = Track.objects.count()
    client.force_login(admin_user)
    f = SimpleUploadedFile("newplot.csv", CSV_LINE.encode("gbk"), content_type="text/csv")
    client.post("/tracks/import/", {"files": f})
    assert Track.objects.count() == before + 1
    assert Track.objects.filter(name="地块newplot").exists()
    assert TrackPoint.objects.filter(track__name="地块newplot").count() == 1
