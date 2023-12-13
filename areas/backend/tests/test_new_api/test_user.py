import pytest

from core.workspace_status import WorkSpaceStatus
from tests.test_new_api.conftest_constants import casual_user_id, casual_user_id2, user1_workspace1_id, \
    user1_workspace2_id, user1_workspace3_id


class TestAdminUserManagement:

    def test_delete_user_3_7(self, app_client_admin, casual_user_2):
        """
        Номер теста 3.7
        Наименование теста: Удаление пользователя
        """
        response = app_client_admin.get(f'/all_workspaces')
        assert response.status_code == 200
        resp = response.json
        assert len(resp['workspaces']) == 2
        workspaces_ids = [ws['id'] for ws in response.json['workspaces']]
        assert user1_workspace1_id in workspaces_ids
        assert user1_workspace2_id in workspaces_ids
        assert user1_workspace3_id not in workspaces_ids
        active_ws = [ws for ws in response.json['workspaces'] if ws['id'] == user1_workspace1_id]
        assert active_ws[0]['status'] == str(WorkSpaceStatus.Active.value)

        delete_user = app_client_admin.delete(f'/user/{casual_user_id}')
        assert delete_user.status_code == 200

        get_users = app_client_admin.get(f'/user')
        assert get_users.status_code == 200
        assert len(get_users.json['users']) == 2
        deleted_user = [usr for usr in get_users.json['users'] if usr['id'] == casual_user_id]
        assert not deleted_user

        response = app_client_admin.get(f'/all_workspaces')
        assert response.status_code == 200
        resp = response.json
        assert len(resp['workspaces']) == 2
        workspaces_ids = [ws['id'] for ws in response.json['workspaces']]
        assert user1_workspace1_id in workspaces_ids
        assert user1_workspace2_id in workspaces_ids
        assert user1_workspace3_id not in workspaces_ids
        archived_ws = [ws for ws in response.json['workspaces'] if ws['id'] == user1_workspace1_id]
        assert archived_ws[0]['status'] == str(WorkSpaceStatus.Archived.value)
