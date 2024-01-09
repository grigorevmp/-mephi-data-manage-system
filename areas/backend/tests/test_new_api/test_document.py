import uuid

import pytest

from tests.test_new_api.conftest_constants import user1_workspace1_id


class TestUserDocument:

    def add_workspace_with_file(self, app_client_user):
        req_data = {
            'title': 'Test add title',
            'description': 'Test add description',
            'document_name': 'test.txt',
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
        return file_id, branch_id, workspace_id, req_data['document_name'], req_data['document_data']

    def test_view_file_1_2(self, app_client_user):
        """
        Номер теста 1.2
        Наименование теста: Просмотр текстового документа
        """
        import base64
        file_id, _, _, _, document_data = self.add_workspace_with_file(app_client_user)
        get_file = app_client_user.get(f'/file/{file_id}/view')
        assert get_file.status_code == 200
        assert get_file.text == base64.b64decode(document_data.split('base64,')[1]).decode()

    def test_update_file_1_3(self, app_client_user):
        """
        Номер теста 1.3
        Наименование теста: Редактирование документа test.txt
        """
        import base64
        file_id, branch_id, workspace_id, _, document_data = self.add_workspace_with_file(app_client_user)
        get_file = app_client_user.get(f'/file/{file_id}/view')
        assert get_file.status_code == 200
        assert get_file.text == base64.b64decode(document_data.split('base64,')[1]).decode()

        # Загружаем новый файл
        req_data = {
            "document_name": "test2.txt",
            "document_data": "data:@file/plain;base64,TmV3IHRlc3QgdGV4dA=="
        }
        upload_new_file = app_client_user.post(f'/upload_file/{file_id}', json=req_data)
        assert upload_new_file.status_code == 200
        get_branch_response = app_client_user.get(f'/workspace/{workspace_id}/view/{branch_id}')
        assert get_branch_response.status_code == 200
        file_id = get_branch_response.json['document_id']
        get_file = app_client_user.get(f'/file/{file_id}/view')
        assert get_file.status_code == 200
        assert get_file.text == base64.b64decode(req_data['document_data'].split('base64,')[1]).decode()

    def test_copy_document_1_9(self, app_client_user):
        """
        Номер теста 1.9
        Наименование теста: Копирование документа test.txt
        """
        import base64
        file_id, branch_id, workspace_id, document_name, document_data = self.add_workspace_with_file(app_client_user)

        req_data = {
            'title': 'Test Copy',
            'description': 'Test Description Copy'
        }
        copy_response = app_client_user.post(f'/workspace/{workspace_id}/copy/{branch_id}', json=req_data)
        assert copy_response.status_code == 200

        get_response = app_client_user.get(f'/get_workspaces')
        assert get_response.status_code == 200
        resp = get_response.json
        assert len(resp['workspaces']) == 3
        workspaces_id = [workspace['id'] for workspace in resp['workspaces']]
        assert user1_workspace1_id in workspaces_id
        assert workspace_id in workspaces_id
        assert copy_response.json['id'] in workspaces_id

        workspace_id = copy_response.json['id']
        get_response = app_client_user.get(f'/get_workspace/{workspace_id}')
        assert get_response.status_code == 200
        resp = get_response.json
        branch_id = resp['branches'][0]['id']
        get_branch_response = app_client_user.get(f'/workspace/{workspace_id}/view/{branch_id}')
        assert get_branch_response.status_code == 200
        file_id = get_branch_response.json['document_id']
        copy_name = document_name.split(".")
        copy_name[-2] += '_copy'
        copy_name = '.'.join(copy_name)
        assert get_branch_response.json['document'] == copy_name
        get_file = app_client_user.get(f'/file/{file_id}/view')
        assert get_file.status_code == 200
        assert get_file.text == base64.b64decode(document_data.split('base64,')[1]).decode()

    def test_rename_document_1_10(self, app_client_user):
        """
        Номер теста 1.10
        Наименование теста: Переименование документа test.txt
        """
        file_id, branch_id, workspace_id, document_name, document_data = self.add_workspace_with_file(app_client_user)

        new_filename = 'New Filename'
        rename_response = app_client_user.put(f'/rename/{file_id}?new_name={new_filename}')
        assert rename_response.status_code == 200

        get_branch_response = app_client_user.get(f'/workspace/{workspace_id}/view/{branch_id}')
        assert get_branch_response.status_code == 200
        assert get_branch_response.json['document'] == new_filename
