import pytest

from core.department import Department
from core.user import User
from core.user_manager import UserNotFoundError


@pytest.fixture()
def user():
    return User(
        email="test_mail@mail.com",
        password="password",
        username="username",
    )


@pytest.fixture()
def user2():
    return User(
        email="test2_mail@mail.com",
        password="password",
        username="username",
    )


@pytest.fixture()
def department():
    return Department('company1', users=None)


class TestDepartment:

    def test_get_and_set_department_name(self, department):
        department.department_name = "company1"
        assert department.department_name == "company1"

        department.department_name = "company2"
        assert department.department_name == "company2"

    def test_set_department_name_wrong(self, department):
        assert department.department_name == "company1"

        with pytest.raises(TypeError):
            department.department_name = 123

        assert department.department_name == "company1"

    def test_get_users(self, department):
        assert department.get_users() == []

    def test_set_users(self, department, user):
        department.users = [user]
        assert department.users == [user]

        with pytest.raises(TypeError):
            department.users = [user, 1234]

        with pytest.raises(TypeError):
            department.users = 123

    def test_add_user(self, department, user):
        department.add_user(user)
        assert department.users == [user]

        with pytest.raises(TypeError):
            department.add_user(13)

    def test_remove_user(self, department, user, user2):
        department.users = [user, user2]
        assert department.get_users() == [user, user2]
        with pytest.raises(TypeError):
            department.remove_user_by_email(123)

        with pytest.raises(UserNotFoundError):
            department.remove_user_by_email('2134@1231.ru')

        department.remove_user_by_email(user.email)

        assert department.get_users() == [user2]
