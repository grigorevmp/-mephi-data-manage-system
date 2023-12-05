import pytest

from core.workspace_status import WorkSpaceStatus
from tests.test_new_api.conftest_constants import user1_workspace1_id, user1_workspace2_id, user1_workspace3_id


class TestUserWorkspace:

    def test_get_workspace_by_id(self, app_client_user):
        workspace_id = user1_workspace1_id
        response = app_client_user.get(f'/get_workspace/{workspace_id}')
        assert response.status_code == 200
        resp = response.json
        assert resp['id'] == user1_workspace1_id
        assert resp["status"] == str(WorkSpaceStatus.Active.value)

    def test_get_archived_workspace_by_id(self, app_client_user):
        workspace_id = user1_workspace2_id
        response = app_client_user.get(f'/get_workspace/{workspace_id}?archived=true')
        assert response.status_code == 200
        resp = response.json
        assert resp['id'] == user1_workspace2_id
        assert resp["status"] == str(WorkSpaceStatus.Archived.value)

    def test_get_archived_workspace_by_id_wout_query(self, app_client_user):
        workspace_id = user1_workspace2_id
        response = app_client_user.get(f'/get_workspace/{workspace_id}')
        assert response.status_code == 404
        resp = response.json
        assert resp == "Can't find space with ID"

    def test_get_all_user_workspaces(self, app_client_user):
        response = app_client_user.get(f'/get_workspaces')
        assert response.status_code == 200
        resp = response.json
        assert len(resp['workspaces']) == 1
        assert resp['workspaces'][0]['id'] == user1_workspace1_id

    def test_get_all_user_workspaces_with_archived(self, app_client_user):
        response = app_client_user.get(f'/get_workspaces?archived=true')
        assert response.status_code == 200
        resp = response.json
        assert len(resp['workspaces']) == 2
        workspaces_id = [workspace['id'] for workspace in resp['workspaces']]
        assert user1_workspace1_id in workspaces_id
        assert user1_workspace2_id in workspaces_id

    def test_add_workspace(self, app_client_user):
        req_data = {
            'title': 'Test add title',
            'description': 'Test add description',
            'document_name': 'test.txt',
            'document_data': 'Test add description',
        }
        response = app_client_user.post(f'/workspace/add', json=req_data)
        assert response.status_code == 200
        get_response = app_client_user.get(f'/get_workspaces')
        assert get_response.status_code == 200
        resp = get_response.json
        assert len(resp['workspaces']) == 2
        workspaces_id = [workspace['id'] for workspace in resp['workspaces']]
        assert user1_workspace1_id in workspaces_id
        assert response.json['id'] in workspaces_id

    def test_add_workspace_invalid_body(self, app_client_user):
        req_data = {'title': 'Test add title'}
        response = app_client_user.post(f'/workspace/add', json=req_data)
        assert response.status_code == 400
        assert response.json['error'] == 'Invalid request body'

    def test_archive_workspace(self, app_client_user):
        workspace_id = user1_workspace1_id
        response = app_client_user.post(f'/workspace/{workspace_id}/archive')
        assert response.status_code == 200
        assert response.json['status'] == "ok"
        response = app_client_user.get(f'/get_workspace/{workspace_id}?archived=true')
        assert response.status_code == 200
        resp = response.json
        assert resp['id'] == user1_workspace1_id
        assert resp["status"] == str(WorkSpaceStatus.Archived.value)

    def test_archive_workspace_negative(self, app_client_user):
        workspace_id = user1_workspace2_id
        response = app_client_user.post(f'/workspace/{workspace_id}/archive')
        assert response.status_code == 401


class TestAdminWorkspace:

    def test_get_all_workspaces(self, app_client_admin):
        response = app_client_admin.get(f'/all_workspaces')
        assert response.status_code == 200
        resp = response.json
        assert len(resp['workspaces']) == 2
        workspaces_ids = [ws['id'] for ws in response.json['workspaces']]
        assert user1_workspace1_id in workspaces_ids
        assert user1_workspace2_id in workspaces_ids
        assert user1_workspace3_id not in workspaces_ids

    def test_get_all_workspaces_deleted(self, app_client_admin):
        response = app_client_admin.get(f'/all_workspaces?deleted=true')
        assert response.status_code == 200
        resp = response.json
        assert len(resp['workspaces']) == 3
        workspaces_ids = [ws['id'] for ws in response.json['workspaces']]
        assert user1_workspace1_id in workspaces_ids
        assert user1_workspace2_id in workspaces_ids
        assert user1_workspace3_id in workspaces_ids

    def test_get_all_workspaces_limit(self, app_client_admin):
        response = app_client_admin.get(f'/all_workspaces?deleted=true&limit=1')
        assert response.status_code == 200
        resp = response.json
        assert len(resp['workspaces']) == 1