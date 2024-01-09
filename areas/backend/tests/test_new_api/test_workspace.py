import uuid

import pytest

from core.workspace_status import WorkSpaceStatus
from database.database import WorkspaceModel
from tests.test_new_api.conftest_constants import user1_workspace1_id, user1_workspace2_id, user1_workspace3_id, \
    casual_user_id


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

    def test_add_workspace_1_1(self, app_client_user):
        """
        Номер теста 1.1
        Наименование теста: Загрузка текстового документа
        """
        from database.database import DocumentModel
        req_data = {
            'title': 'Test add title',
            'description': 'Test add description',
            'document_name': 'test.txt',
            'document_data': 'data:@file/plain;base64,VGVzdCBkb2N1bWVudA==',
            'task': str(uuid.uuid4())
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
        assert DocumentModel.query.filter_by(name=req_data['document_name']).first()

    def test_add_workspace_invalid_body(self, app_client_user):
        req_data = {'title': 'Test add title'}
        response = app_client_user.post(f'/workspace/add', json=req_data)
        assert response.status_code == 400
        assert response.json['error'] == 'Invalid request body'

    def test_archive_workspace_1_11(self, app_client_user):
        """
        Номер теста 1.11
        Наименование теста: Архивирование рабочего пространства с документом test.txt
        """
        workspace_id = user1_workspace1_id
        response = app_client_user.post(f'/workspace/{workspace_id}/archive')
        assert response.status_code == 200
        assert response.json['status'] == "ok"
        get_response = app_client_user.get(f'/get_workspaces')
        assert get_response.status_code == 200
        resp = get_response.json
        assert len(resp['workspaces']) == 0
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

    def add_workspace_with_file(self, app_client_user, file_name: str = 'test.txt'):
        req_data = {
            'title': 'Test add title',
            'description': 'Test add description',
            'document_name': file_name,
            'document_data': 'data:@file/plain;base64,VGVzdCBkb2N1bWVudA==',
            'task': str(uuid.uuid4())
        }
        response = app_client_user.post(f'/workspace/add', json=req_data)
        assert response.status_code == 200
        workspace_id = response.json['id']
        get_response = app_client_user.get(f'/get_workspace/{workspace_id}')
        assert get_response.status_code == 200
        resp = get_response.json
        branch_id = resp['branches'][0]['id']
        get_branch_response = app_client_user.get(f'/workspace/{workspace_id}/view/{branch_id}')
        assert get_branch_response.status_code == 200
        file_id = get_branch_response.json['document_id']
        return file_id, branch_id, workspace_id, req_data['document_name']

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

    def test_delete_workspace_3_1(self, app_client_admin):
        """
        Номер теста 3.1
        Наименование теста: Удаление рабочего пространства с документом test.txt
        """
        file_id, branch_id, workspace_id, document_name = self.add_workspace_with_file(app_client_admin)

        delete_workspace = app_client_admin.delete(f'/workspace/{workspace_id}')
        assert delete_workspace.status_code == 200

        db_workspace = WorkspaceModel.query.filter_by(id=workspace_id).first()
        assert db_workspace.status == str(WorkSpaceStatus.Deleted.value)

        response = app_client_admin.get(f'/all_workspaces?deleted=true')
        assert response.status_code == 200
        resp = response.json
        assert len(resp['workspaces']) == 4
        workspaces_ids = [ws['id'] for ws in response.json['workspaces']]
        assert user1_workspace1_id in workspaces_ids
        assert user1_workspace2_id in workspaces_ids
        assert user1_workspace3_id in workspaces_ids
        assert workspace_id in workspaces_ids

    def test_unarchive_workspace_3_2(self, app_client_admin):
        """
        Номер теста 3.2
        Наименование теста: Разархивирование рабочего пространства с документом test.txt
        """
        workspace_id = user1_workspace2_id

        req_data = {
            "new_status": str(WorkSpaceStatus.Active.value),
            "new_owner": 'user'
        }
        unarchive_workspace = app_client_admin.put(f'/workspace/{workspace_id}', json=req_data)
        assert unarchive_workspace.status_code == 200

        response = app_client_admin.get(f'/all_workspaces')
        assert response.status_code == 200
        resp = response.json
        assert len(resp['workspaces']) == 2
        unarchived_workspace = [ws for ws in response.json['workspaces'] if ws['id'] == workspace_id]
        assert unarchived_workspace[0]['status'] == str(WorkSpaceStatus.Active.value)
