import pytest


class TestDeleteController:

    def test_delete_file(self, app_client):
        response = app_client.delete(path='/delete/abd9cd7f-9ffd-42b0-bce4-eb14b51a1fd1')
        assert response.status_code == 200

    def test_delete_directory(self, app_client):
        response = app_client.delete(path='/delete/4c3b76d1-fe24-4fdf-afdf-7c38adbdab14')
        assert response.status_code == 200

    def test_delete_not_found(self, app_client):
        response = app_client.delete(path='/delete/4c3b76d1-fe24-4fdf-afdf-7c38adb')
        assert response.status_code == 404
