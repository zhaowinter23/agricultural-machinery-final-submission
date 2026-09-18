"""认证与权限集成测试。

测试分层思路：用 Django test client 在 HTTP 层验证"流程通不通、权限对不对"。
- 测"登录流程本身"：POST 登录表单，看重定向/停留；
- 测"权限"：用 force_login 跳过登录，直接验证授权（测什么就隔离什么）。
"""
import pytest


@pytest.mark.django_db
def test_login_success_redirects_home(client, admin_user):
    resp = client.post("/accounts/login/", {
        "username": "admin_test", "password": "pass1234", "role": "admin"
    })
    assert resp.status_code == 302
    assert resp.url == "/"


@pytest.mark.django_db
def test_login_wrong_password_stays_on_page(client, admin_user):
    resp = client.post("/accounts/login/", {
        "username": "admin_test", "password": "wrong", "role": "admin"
    })
    assert resp.status_code == 200


@pytest.mark.django_db
def test_admin_with_user_role_is_rejected(client, admin_user):
    # 回归：管理员账号选"用户登录"应被拒（角色不匹配）
    resp = client.post("/accounts/login/", {
        "username": "admin_test", "password": "pass1234", "role": "user"
    })
    assert resp.status_code == 200


@pytest.mark.django_db
def test_regular_user_blocked_from_admin_pages(client, regular_user):
    client.force_login(regular_user)
    resp = client.get("/tracks/import/")
    assert resp.status_code == 302
    assert "/accounts/login/" in resp.url


@pytest.mark.django_db
def test_admin_can_access_admin_pages(client, admin_user):
    client.force_login(admin_user)
    assert client.get("/tracks/import/").status_code == 200
    assert client.get("/tracks/users/").status_code == 200


@pytest.mark.django_db
def test_unauthenticated_redirected_to_login(client):
    resp = client.get("/")
    assert resp.status_code == 302
    assert "/accounts/login/" in resp.url
