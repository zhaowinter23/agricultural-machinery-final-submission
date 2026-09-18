"""
初始化/重置默认账号。

用法：
    python manage.py init_accounts

默认账号（可在 settings.py 中通过 DEFAULT_* 配置覆盖）：
    管理员： admin   / admin123   （is_staff=True, is_superuser=True）
    普通用户： user   / user123    （普通登录）

命令幂等：已存在则重置密码与角色，不存在则创建。直接 set_password 绕过
密码校验器，保证账号一定可登录。
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings


class Command(BaseCommand):
    help = '初始化/重置默认管理员与普通用户账号'

    def handle(self, *args, **options):
        admin_user = getattr(settings, 'DEFAULT_ADMIN_USERNAME', 'admin')
        admin_pwd = getattr(settings, 'DEFAULT_ADMIN_PASSWORD', 'admin123')
        norm_user = getattr(settings, 'DEFAULT_USER_USERNAME', 'user')
        norm_pwd = getattr(settings, 'DEFAULT_USER_PASSWORD', 'user123')

        # 管理员
        obj, created = User.objects.get_or_create(username=admin_user, defaults={'email': ''})
        obj.set_password(admin_pwd)
        obj.is_staff = True
        obj.is_superuser = True
        obj.is_active = True
        obj.save()
        self.stdout.write(self.style.SUCCESS(
            f'[{"创建" if created else "重置"}] 管理员账号 → 用户名: {admin_user}  密码: {admin_pwd}'
        ))

        # 普通用户
        obj, created = User.objects.get_or_create(username=norm_user, defaults={'email': ''})
        obj.set_password(norm_pwd)
        obj.is_staff = False
        obj.is_superuser = False
        obj.is_active = True
        obj.save()
        self.stdout.write(self.style.SUCCESS(
            f'[{"创建" if created else "重置"}] 普通用户 → 用户名: {norm_user}  密码: {norm_pwd}'
        ))

        self.stdout.write(self.style.WARNING(
            '\n登录方式：登录页选择「用户登录」用 user/user123，'
            '选择「管理员登录」用 admin/admin123。'
        ))
