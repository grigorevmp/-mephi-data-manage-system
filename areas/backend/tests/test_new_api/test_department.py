import pytest
from tests.test_new_api.conftest_constants import casual_user_id, casual_user_id2


class TestAdminDepartment:

    def test_add_department_3_3(self, app_client_admin):
        """
        Номер теста 3.3
        Наименование теста: Создание отдела пользователей Department12
        """
        req_data = {"department_name": "Department12"}
        add_department = app_client_admin.post(f'/department', json=req_data)
        assert add_department.status_code == 200

        get_department = app_client_admin.get(f'/department')
        assert get_department.status_code == 200
        assert len(get_department.json['departments']) == 2
        department = [dep for dep in get_department.json['departments'] if dep['department_name'] == 'Department12']
        assert len(department) == 1

    def test_add_user_to_department_3_4(self, app_client_admin, casual_user_2):
        """
        Номер теста 3.4
        Наименование теста: Добавление пользователя в отдел Department12
        """
        req_data = {"department_name": "Department12"}
        add_department = app_client_admin.post(f'/department', json=req_data)
        assert add_department.status_code == 200

        get_department = app_client_admin.get(f'/department')
        assert get_department.status_code == 200
        assert len(get_department.json['departments']) == 2
        department = [dep for dep in get_department.json['departments'] if dep['department_name'] == req_data["department_name"]]
        assert len(department) == 1

        req_data2 = {"users": [casual_user_id, casual_user_id2]}
        add_user_to_department = app_client_admin.post(f'/department/users?name={req_data["department_name"]}',
                                                       json=req_data2)
        assert add_user_to_department.status_code == 200

        get_department_users = app_client_admin.get(f'/department/users?name={req_data["department_name"]}')
        assert get_department_users.status_code == 200
        assert len(get_department_users.json['users']) == 2
        user_ids = [user['id'] for user in get_department_users.json['users']]
        assert casual_user_id in user_ids
        assert casual_user_id2 in user_ids

    def test_remove_user_from_department_3_5(self, app_client_admin, casual_user_2):
        """
        Номер теста 3.5
        Наименование теста: Удаление пользователя из отдела Department12
        """
        req_data = {"department_name": "Department12"}
        add_department = app_client_admin.post(f'/department', json=req_data)
        assert add_department.status_code == 200

        get_department = app_client_admin.get(f'/department')
        assert get_department.status_code == 200
        assert len(get_department.json['departments']) == 2
        department = [dep for dep in get_department.json['departments'] if dep['department_name'] == req_data["department_name"]]
        assert len(department) == 1

        req_data2 = {"users": [casual_user_id, casual_user_id2]}
        add_user_to_department = app_client_admin.post(f'/department/users?name={req_data["department_name"]}',
                                                       json=req_data2)
        assert add_user_to_department.status_code == 200

        req_data2 = {"users": [casual_user_id]}
        add_user_to_department = app_client_admin.delete(f'/department/users?name={req_data["department_name"]}',
                                                         json=req_data2)
        assert add_user_to_department.status_code == 200

        get_department_users = app_client_admin.get(f'/department/users?name={req_data["department_name"]}')
        assert get_department_users.status_code == 200
        assert len(get_department_users.json['users']) == 1
        user_ids = [user['id'] for user in get_department_users.json['users']]
        assert casual_user_id2 in user_ids

    def test_delete_department_3_6(self, app_client_admin, casual_user_2):
        """
        Номер теста 3.6
        Наименование теста: Удаление отдела Department12
        """
        req_data = {"department_name": "Department12"}
        add_department = app_client_admin.post(f'/department', json=req_data)
        assert add_department.status_code == 200

        get_department = app_client_admin.get(f'/department')
        assert get_department.status_code == 200
        assert len(get_department.json['departments']) == 2
        department = [dep for dep in get_department.json['departments'] if
                      dep['department_name'] == req_data["department_name"]]
        assert len(department) == 1

        add_department = app_client_admin.delete(f'/department', json=req_data)
        assert add_department.status_code == 200
        get_department = app_client_admin.get(f'/department')
        assert get_department.status_code == 200
        assert len(get_department.json['departments']) == 1
        department = [dep for dep in get_department.json['departments'] if
                      dep['department_name'] == req_data["department_name"]]
        assert len(department) == 0

    def test_negative_add_user_to_department_3_8(self, app_client_admin):
        """
        Номер теста 3.8
        Наименование теста: Негативная проверка добавление пользователя в отдел
        """
        from database.database import UserModel
        get_department = app_client_admin.get(f'/department')
        assert get_department.status_code == 200
        assert len(get_department.json['departments']) == 1

        req_data2 = {"users": [casual_user_id]}
        add_user_to_department = app_client_admin.post(f'/department/users?name=WrongDepartment',
                                                       json=req_data2)
        assert add_user_to_department.status_code == 404

        db_user = UserModel.query.filter_by(id=casual_user_id).first()
        assert db_user.department_id is None
