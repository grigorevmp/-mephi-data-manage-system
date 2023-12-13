import pytest


class TestUserSearch:

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

    def test_search_file_1_8(self, app_client_user):
        """
        Номер теста 1.8
        Наименование теста: Поиск документа test.txt
        """
        file_id, branch_id, workspace_id, document_name = self.add_workspace_with_file(app_client_user)

        search_response = app_client_user.get(f'search?name={document_name}')
        assert search_response.status_code == 200
        search_res = search_response.json['items']
        assert len(search_res) == 1
        assert search_res[0]['id'] == file_id
        assert search_res[0]['branch_id'] == branch_id
        assert search_res[0]['space_id'] == workspace_id
        assert search_res[0]['name'] == document_name

    def test_search_file_1_14(self, app_client_user):
        """
        Номер теста 1.14
        Наименование теста: Поиск документа различными вариантами
        """
        import urllib.parse
        file_id, branch_id, workspace_id, document_name = self.add_workspace_with_file(app_client_user,
                                                                                       file_name='test_file!#3.txt')

        search_response = app_client_user.get(f'search?name=wrong')
        assert search_response.status_code == 200
        search_res = search_response.json['items']
        assert len(search_res) == 0

        search_response = app_client_user.get(f'search?name={urllib.parse.quote(".!@#")}')
        assert search_response.status_code == 200
        search_res = search_response.json['items']
        assert len(search_res) == 0

        search_response = app_client_user.get(f'search?name={urllib.parse.quote(document_name)}')
        assert search_response.status_code == 200
        search_res = search_response.json['items']
        assert len(search_res) == 1
        assert search_res[0]['id'] == file_id
        assert search_res[0]['branch_id'] == branch_id
        assert search_res[0]['space_id'] == workspace_id
        assert search_res[0]['name'] == document_name
