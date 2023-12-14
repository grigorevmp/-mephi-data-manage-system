from urllib.parse import urljoin

import pytest
import requests

from core.role import Role


class APIClient:
    def __init__(self, base_url: str, login: str, password: str, logger):
        self.base_url = base_url.split('3000')[0] + '5000'
        self.login = login
        self.password = password
        self.session = requests.Session()
        self.logger = logger

    def _request(self, method, location, headers=None, data=None, files=None, json=None):
        url = urljoin(self.base_url, location)
        response = self.session.request(method=method, url=url, headers=headers, data=data, files=files, json=json)
        self.logger.debug(response.status_code)
        return response

    def post_login(self):
        location = 'login'
        req_data = {
            'email': self.login,
            'password': self.password
        }
        res = self._request('PUT', location=location, json=req_data)
        return res

    def post_registration(self):
        location = 'registration'
        req_data = {
            'email': self.login,
            'password': self.password,
            'username': 'test_user',
            'role': str(Role.Client.value)
        }
        res = self._request('POST', location=location, json=req_data)

    def get_workspaces(self):
        location = f'/get_workspaces'
        res = self._request('GET', location=location)
        assert res.status_code == 200
        return res.json

    def get_workspace_by_title(self, title):
        location = f'/get_workspaces'
        res = self._request('GET', location=location)
        assert res.status_code == 200
        workspace_id = [workspace['id'] for workspace in res.json()['workspaces'] if workspace['title'] == title][0]

        location = f'/get_workspace/{workspace_id}'
        res = self._request('GET', location=location)
        assert res.status_code == 200
        return workspace_id, res.json()['main_branch']
