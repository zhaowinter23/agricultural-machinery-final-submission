"""冒烟测试：验证独立测试工程能拉起主系统 Django 并访问其模型。"""
import django


def test_django_booted():
    assert django.get_version()


def test_can_import_main_system(db):
    # 能创建主系统的模型对象，说明 sys.path、settings、测试库全部就绪
    from tracks.models import Track
    t = Track.objects.create(name="冒烟地块")
    assert t.pk is not None
    assert str(t) == "冒烟地块"
