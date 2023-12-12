import pytest

from core.department import Department
from core.department_manager import DepartmentManager, DepartmentNotFoundError
from core.user import User
from core.user_manager import UserNotFoundError


@pytest.fixture()
def department_manager():
    return DepartmentManager(
        departments=None
    )


@pytest.fixture()
def user():
    return User(
        email="test_mail@mail.com",
        password="password",
        username="username",
    )


@pytest.fixture()
def department(user):
    return Department(
        department_name="test",
        users=None
    )


@pytest.fixture()
def department2(user):
    return Department(
        department_name="test2",
        users=None
    )


@pytest.fixture()
def department_manager_with_departments(department_manager, department, department2):
    department_manager.add_department(department)
    department_manager.add_department(department2)
    return department_manager


@pytest.fixture()
def user1():
    return User(
        email="test_mail@mail.com",
        password="password",
        username="username",
    )


@pytest.fixture()
def user2():
    return User(
        email="test_mail2@mail.com",
        password="password",
        username="username",
    )


@pytest.fixture()
def department_manager_with_departments_and_users(department_manager_with_departments, user1, user2, department):
    department_manager_with_departments.add_users_to_department([user1, user2], department.department_name)
    return department_manager_with_departments


class TestDepartmentManager:

    def test_add_department(self, department_manager, department):
        department_manager.add_department(department)

        with pytest.raises(TypeError):
            department_manager.add_department(231)

        dp = department_manager.get_department(department.department_name)
        assert dp == department

    def test_get_department(self, department_manager, department):
        department_manager.add_department(department)

        with pytest.raises(TypeError):
            department_manager.get_department(1234)

        with pytest.raises(DepartmentNotFoundError):
            department_manager.get_department('V2')

        dp = department_manager.get_department(department.department_name)
        assert dp == department

    def test_remove_department_by_department_name(self, department_manager_with_departments, department):
        assert department_manager_with_departments.get_department(department.department_name) == department

        with pytest.raises(TypeError):
            department_manager_with_departments.remove_department_by_department_name(123)

        with pytest.raises(DepartmentNotFoundError):
            department_manager_with_departments.remove_department_by_department_name('Test4')

        department_manager_with_departments.remove_department_by_department_name(department.department_name)

        with pytest.raises(DepartmentNotFoundError):
            department_manager_with_departments.get_department(department.department_name)

    def test_add_user(self, department_manager_with_departments, user, department):
        assert department_manager_with_departments.add_user(user, department.department_name) is None

        with pytest.raises(TypeError):
            department_manager_with_departments.add_user(123, "abc")

        with pytest.raises(TypeError):
            department_manager_with_departments.add_user("abc", 123)

        with pytest.raises(DepartmentNotFoundError):
            department_manager_with_departments.add_user(user, "abc")

    def test_remove_user(self, department_manager_with_departments, department, user):
        department_manager_with_departments.add_user(user, department.department_name)
        assert department_manager_with_departments.remove_user(user.email, department.department_name) is None
        assert department_manager_with_departments.get_users_list_by_department_name(department.department_name) == []

        with pytest.raises(UserNotFoundError):
            assert department_manager_with_departments.remove_user(user.email, department.department_name) is None

        with pytest.raises(TypeError):
            assert department_manager_with_departments.remove_user(234532, department.department_name) is None

    def test_remove_user_wrong_department(self, department_manager_with_departments, department, user):
        department_manager_with_departments.add_user(user, department.department_name)
        with pytest.raises(DepartmentNotFoundError):
            assert department_manager_with_departments.remove_user(user.email,
                                                                   department.department_name + "_WRONG") is None

    def test_add_users_to_department(self, department_manager_with_departments, user, user2, department):
        assert department_manager_with_departments.add_users_to_department(
            [user, user2],
            department.department_name
        ) is None

        assert department_manager_with_departments.get_users_list_by_department_name(department.department_name) == [
            user, user2]

        with pytest.raises(TypeError):
            department_manager_with_departments.add_users_to_department(123, "abc")

        with pytest.raises(TypeError):
            department_manager_with_departments.add_users_to_department(["abc"], 123)

    def test_remove_users(self, department_manager_with_departments, user, user2, department):
        assert department_manager_with_departments.add_users_to_department(
            [user, user2],
            department.department_name
        ) is None

        assert department_manager_with_departments.get_users_list_by_department_name(department.department_name) == [
            user, user2]

        assert department_manager_with_departments.remove_users([user.email, user2.email],
                                                                department.department_name) is None
        assert department_manager_with_departments.get_users_list_by_department_name(department.department_name) == []

        with pytest.raises(TypeError):
            department_manager_with_departments.remove_users(123, "abc")

        with pytest.raises(TypeError):
            department_manager_with_departments.remove_users(["abc"], 123)

    def test_add_users_to_departments(self, department_manager_with_departments, user, user2, department, department2):
        assert department_manager_with_departments.add_users_to_departments(
            [user, user2],
            [department.department_name, department2.department_name]
        ) is None

        assert department_manager_with_departments.get_users_list_by_department_name(department.department_name) == [
            user, user2]
        assert department_manager_with_departments.get_users_list_by_department_name(department2.department_name) == [
            user, user2]

        with pytest.raises(TypeError):
            department_manager_with_departments.add_users_to_departments(123, ["abc"])

        with pytest.raises(TypeError):
            department_manager_with_departments.add_users_to_departments(["abc"], 123)

    def test_get_department_by_user_email(self, department_manager_with_departments_and_users, user1, user2,
                                          department2):
        with pytest.raises(UserNotFoundError):
            department_manager_with_departments_and_users.get_department_by_user_email('test3_mail@mail.com')
        with pytest.raises(TypeError):
            department_manager_with_departments_and_users.get_department_by_user_email(123)

        assert len(
            department_manager_with_departments_and_users.get_department_by_user_email(user1.email)) == 1

        department_manager_with_departments_and_users.add_users_to_department([user1, user2],
                                                                              department2.department_name)

        assert len(
            department_manager_with_departments_and_users.get_department_by_user_email(user2.email)) == 2

    def test_get_users_list_by_department_name(self, department_manager_with_departments_and_users, department):
        with pytest.raises(DepartmentNotFoundError):
            department_manager_with_departments_and_users.get_users_list_by_department_name('test3')
        with pytest.raises(TypeError):
            department_manager_with_departments_and_users.get_users_list_by_department_name(123)

        assert len(department_manager_with_departments_and_users.get_users_list_by_department_name(
            department.department_name)) == 2

    def test_get_departments(self, department_manager_with_departments):
        assert len(department_manager_with_departments.get_departments()) == 2
