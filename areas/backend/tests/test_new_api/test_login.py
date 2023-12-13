import pytest

from tests.test_new_api.conftest_constants import invalid_token


class TestLogin:

    def test_wrong_json(self, client):
        wrong_json = {
            "my_email": "test_email@gmail.com",
            "password": "test_pass"
        }
        response = client.put(f'/login', json=wrong_json)
        assert response.status_code == 400
        resp = response.json
        assert resp['error'] == "Invalid request body"

    def test_user_not_found(self, client):
        wrong_json = {
            "email": "test_email@gmail.com",
            "password": "test_pass"
        }
        response = client.put(f'/login', json=wrong_json)
        assert response.status_code == 403
        resp = response.json
        assert resp['error'] == "Invalid email or password"

    def test_invalid_credential(self, client):
        data = {
            "email": "admin@mail.com",
            "password": "password1"
        }
        response = client.put(f'/login', json=data)
        assert response.status_code == 403
        resp = response.json
        all_headers = dict(response.headers.items())
        assert "Set-Cookie" not in all_headers
        assert resp['error'] == "Invalid email or password"

    def test_success(self, client):
        data = {
            "email": "admin@mail.com",
            "password": "password"
        }
        response = client.put(f'/login', json=data)
        assert response.status_code == 200
        all_headers = dict(response.headers.items())
        assert "Set-Cookie" in all_headers

    def test_unauthorised(self, client):
        response = client.get(f'/get_workspaces')
        assert response.status_code == 401
        resp = response.json
        assert resp['error'] == "Unauthorised"

    def test_unauthorised_admin(self, app_client_user):
        response = app_client_user.get(f'/all_workspaces')
        assert response.status_code == 403
        resp = response.json
        assert resp['error'] == "access denied"

    def test_invalid_token(self, app_client_user):
        app_client_user.set_cookie(key='token', value=invalid_token)
        response = app_client_user.get(f'/get_workspaces')
        assert response.status_code == 403
        resp = response.json
        assert resp['error'] == "Invalid token"

    def test_invalid_token_admin(self, app_client_admin):
        app_client_admin.set_cookie(key='token', value=invalid_token)
        response = app_client_admin.get(f'/all_workspaces')
        assert response.status_code == 403
        resp = response.json
        assert resp['error'] == "Invalid token"
