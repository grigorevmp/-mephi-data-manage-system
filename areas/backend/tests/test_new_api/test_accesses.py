import pytest
from tests.test_new_api.conftest_constants import casual_user_email2


class TestUserAccess:

    def add_workspace_with_file(self, app_client_user, file_name: str = 'test.txt'):
        req_data = {
            'title': 'Test add title',
            'description': 'Test add description',
            'document_name': file_name,
            'document_data': 'data:@file/plain;base64,VGVzdCBkb2N1bWVudA=='
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

    @pytest.mark.parametrize('view_only', ['true', 'false'])
    def test_add_access_2_1(self, app_client_user, casual_user_2, view_only):
        """
        Номер теста 2.1
        Наименование теста: Добавление прав пользователя на рабочее пространство с документом test.txt
        """
        file_id, branch_id, workspace_id, document_name = self.add_workspace_with_file(app_client_user)

        add_access = app_client_user.put(f'/accesses/{workspace_id}/email/{casual_user_email2}?view_only={view_only}')
        assert add_access.status_code == 200

        get_workspace_accesses = app_client_user.get(f'/accesses/{workspace_id}')
        assert get_workspace_accesses.status_code == 200
        accesses = get_workspace_accesses.json['accesses']
        assert len(accesses) == 1
        access = accesses[0]
        assert access['class'] == 'UserAccess'
        assert access['content'] == casual_user_email2
        assert access['type'] == 'View' if view_only == 'true' else 'Edit'

    def test_remove_access_2_2(self, app_client_user, casual_user_2):
        """
        Номер теста 2.2
        Наименование теста: Удаление прав пользователя на рабочее пространство с документом test.txt
        """
        file_id, branch_id, workspace_id, document_name = self.add_workspace_with_file(app_client_user)

        add_access = app_client_user.put(f'/accesses/{workspace_id}/email/{casual_user_email2}?view_only=true')
        assert add_access.status_code == 200

        get_workspace_accesses = app_client_user.get(f'/accesses/{workspace_id}')
        assert get_workspace_accesses.status_code == 200
        accesses = get_workspace_accesses.json['accesses']
        assert len(accesses) == 1
        access = accesses[0]
        assert access['class'] == 'UserAccess'
        assert access['content'] == casual_user_email2
        assert access['type'] == 'View'

        delete_access = app_client_user.delete(f'/accesses/{workspace_id}/email/{casual_user_email2}')
        assert delete_access.status_code == 200

        get_workspace_accesses = app_client_user.get(f'/accesses/{workspace_id}')
        assert get_workspace_accesses.status_code == 200
        accesses = get_workspace_accesses.json['accesses']
        assert len(accesses) == 0

    @pytest.mark.xfail(reason='No error in this case yet')
    def test_negative_add_access_2_3(self, app_client_user):
        """
        Номер теста 2.3
        Наименование теста: Негативная проверка выдачи прав несуществующему пользователю
        """
        file_id, branch_id, workspace_id, document_name = self.add_workspace_with_file(app_client_user)

        add_access = app_client_user.put(f'/accesses/{workspace_id}/email/wrong@mail.ru?view_only=true')
        assert add_access.status_code == 404

        get_workspace_accesses = app_client_user.get(f'/accesses/{workspace_id}')
        assert get_workspace_accesses.status_code == 200
        accesses = get_workspace_accesses.json['accesses']
        assert len(accesses) == 0
