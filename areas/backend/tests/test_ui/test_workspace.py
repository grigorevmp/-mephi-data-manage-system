import pytest

from tests.test_ui.base_actions import BaseCase


class TestUserWorkspace(BaseCase):

    def test_add_workspace_1_1(self, auto_auth, file1_path, request):
        """
        Номер теста 1.1
        Наименование теста: Загрузка текстового документа
        """
        title = self.workspaces_page.add_workspace(file1_path, title=f'Test-{request.node.name}')
        assert title in self.driver.page_source

    def test_view_file_1_2(self, auto_auth, file1_path, request):
        """
        Номер теста 1.2
        Наименование теста: Просмотр текстового документа
        """
        title = self.workspaces_page.add_workspace(file1_path, title=f'Test-{request.node.name}')
        assert title in self.driver.page_source
        workspace_id, branch_id = self.api_client.get_workspace_by_title(title)
        self.branch_page.open_branch_page(workspace_id, branch_id)
        self.branch_page.view_file()
        assert 'Test Document' in self.driver.page_source

    def test_edit_file_1_3(self, auto_auth, file1_path, file2_path, request):
        """
        Номер теста 1.3
        Наименование теста: Редактирование документа
        """
        title = self.workspaces_page.add_workspace(file1_path, title=f'Test-{request.node.name}')
        assert title in self.driver.page_source
        workspace_id, branch_id = self.api_client.get_workspace_by_title(title)
        self.branch_page.open_branch_page(workspace_id, branch_id)
        self.branch_page.view_file()
        assert 'Test Document' in self.driver.page_source
        self.driver.refresh()
        self.branch_page.edit_file(file2_path)
        self.branch_page.view_file()
        assert 'Test Document 2' in self.driver.page_source

    def test_add_branch_1_4(self, auto_auth, file1_path, request):
        """
        Номер теста 1.4
        Наименование теста: Создания новой ветки работы с документом test.txt
        """
        title = self.workspaces_page.add_workspace(file1_path, title=f'Test-{request.node.name}')
        assert title in self.driver.page_source
        workspace_id, branch_id = self.api_client.get_workspace_by_title(title)
        self.branch_page.open_branch_page(workspace_id, branch_id)
        self.branch_page.view_file()
        assert 'Test Document' in self.driver.page_source
        self.driver.refresh()
        self.branch_page.add_branch('test_branch')
        assert 'test_branch' in self.driver.page_source
        self.branch_page.view_file()
        assert 'Test Document' in self.driver.page_source

    def test_add_request_1_5(self, auto_auth, file1_path, request):
        """
        Номер теста 1.5
        Наименование теста: Предложение согласования изменений документа test.txt
        """
        title = self.workspaces_page.add_workspace(file1_path, title=f'Test-{request.node.name}')
        assert title in self.driver.page_source
        workspace_id, branch_id = self.api_client.get_workspace_by_title(title)
        self.branch_page.open_branch_page(workspace_id, branch_id)
        self.driver.refresh()
        self.branch_page.add_branch('test_branch')
        assert 'test_branch' in self.driver.page_source
        self.branch_page.add_request('Request_title', 'Request_description')
        assert 'Request_title' in self.driver.page_source

    def test_approve_request_1_6(self, auto_auth, file1_path, request):
        """
        Номер теста 1.6
        Наименование теста: Согласование изменений документа test.txt
        """
        title = self.workspaces_page.add_workspace(file1_path, title=f'Test-{request.node.name}')
        assert title in self.driver.page_source
        workspace_id, branch_id = self.api_client.get_workspace_by_title(title)
        self.branch_page.open_branch_page(workspace_id, branch_id)
        self.driver.refresh()
        self.branch_page.add_branch('test_branch')
        assert 'test_branch' in self.driver.page_source
        self.branch_page.add_request('Request_title', 'Request_description')
        assert 'Request_title' in self.driver.page_source
