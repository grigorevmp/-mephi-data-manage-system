import uuid

import pytest

from core.branch_status import BranchStatus
from core.request_status import RequestStatus


class TestUserBranch:

    def add_branch(self, app_client_user):
        import base64
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

        # Добавляем новую ветку
        req_data_1 = {
            'name': 'new_branch',
            'document_id': file_id,
            'parent_branch_id': branch_id
        }
        add_branch = app_client_user.post(f'/workspace/{workspace_id}/add_branch', json=req_data_1)
        assert add_branch.status_code == 200

        get_response = app_client_user.get(f'/get_workspace/{workspace_id}')
        assert get_response.status_code == 200
        resp = get_response.json
        assert len(resp['branches']) == 2
        branch_id = resp['branches'][1]['id']
        get_branch_response = app_client_user.get(f'/workspace/{workspace_id}/view/{branch_id}')
        assert get_branch_response.status_code == 200
        new_file_id = get_branch_response.json['document_id']
        assert new_file_id != file_id
        get_file = app_client_user.get(f'/file/{file_id}/view')
        assert get_file.status_code == 200
        assert get_file.text == base64.b64decode(req_data['document_data'].split('base64,')[1]).decode()
        return resp, workspace_id, branch_id

    def add_request(self, app_client_user, last_workspace, workspace_id, branch_id):
        request_data = {
            "title": "Test Request",
            "description": "Test Description",
            "source_branch_id": last_workspace['branches'][1]['id'],
            "target_branch_id": last_workspace['branches'][0]['id']
        }
        add_request = app_client_user.post(f'/workspace/{workspace_id}/request', json=request_data)
        assert add_request.status_code == 200

        get_branch_response = app_client_user.get(f'/workspace/{workspace_id}/view/{branch_id}')
        assert get_branch_response.status_code == 200
        request_id = get_branch_response.json['requests'][0]['id']

        get_request = app_client_user.get(f'/workspace/{workspace_id}/request/{request_id}')
        assert get_request.status_code == 200
        request = get_request.json
        assert request['description'] == request_data['description']
        assert request['source_branch_id'] == request_data['source_branch_id']
        assert request['target_branch_id'] == request_data['target_branch_id']
        assert request['title'] == request_data['title']
        assert request['status'] == RequestStatus.Open.value
        return request, request_id

    def test_add_branch_1_4(self, app_client_user):
        """
        Номер теста 1.4
        Наименование теста: Создания новой ветки работы с документом test.txt
        """
        self.add_branch(app_client_user)

    def test_add_request_1_5(self, app_client_user):
        """
        Номер теста 1.5
        Наименование теста: Предложение согласования изменений документа test.txt
        """
        last_workspace, workspace_id, branch_id = self.add_branch(app_client_user)

        self.add_request(app_client_user, last_workspace, workspace_id, branch_id)

    def test_approve_request_1_6(self, app_client_user):
        """
        Номер теста 1.6
        Наименование теста: Согласование изменений документа test.txt
        """
        last_workspace, workspace_id, branch_id = self.add_branch(app_client_user)

        request, request_id = self.add_request(app_client_user, last_workspace, workspace_id, branch_id)

        merge_request = app_client_user.post(f'/workspace/{workspace_id}/request/{request_id}/force_merge')
        assert merge_request.status_code == 200
        get_request = app_client_user.get(f'/workspace/{workspace_id}/request/{request_id}')
        assert get_request.status_code == 200
        request = get_request.json
        assert request['status'] == RequestStatus.Merged.value
        get_response = app_client_user.get(f'/get_workspace/{workspace_id}')
        assert get_response.status_code == 200
        resp = get_response.json
        assert len(resp['branches']) == 2
        assert resp['branches'][1]['status'] == str(BranchStatus.Merged.value)

    def test_decline_request_1_7(self, app_client_user):
        """
        Номер теста 1.7
        Наименование теста: Отклонение изменений документа
        """
        last_workspace, workspace_id, branch_id = self.add_branch(app_client_user)

        request, request_id = self.add_request(app_client_user, last_workspace, workspace_id, branch_id)

        decline_request = app_client_user.post(f'/workspace/{workspace_id}/request/{request_id}/close')
        assert decline_request.status_code == 200
        get_request = app_client_user.get(f'/workspace/{workspace_id}/request/{request_id}')
        assert get_request.status_code == 200
        request = get_request.json
        assert request['status'] == RequestStatus.Closed.value
        get_response = app_client_user.get(f'/get_workspace/{workspace_id}')
        assert get_response.status_code == 200
        resp = get_response.json
        assert len(resp['branches']) == 2
        assert resp['branches'][1]['status'] == str(BranchStatus.Active.value)
