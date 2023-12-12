import pytest

from core.accesses import UrlAccess, UserAccess, DepartmentAccess, Access


@pytest.fixture()
def url_access():
    return UrlAccess("tg.ru", Access.Edit)


@pytest.fixture()
def user_access():
    return UserAccess("name", Access.View)


@pytest.fixture()
def department_access():
    return DepartmentAccess("dep_name", Access.View)


class TestAccesses:

    def test_url_access(self, url_access):
        assert url_access.get_url() == "tg.ru"
        assert url_access.access_type == Access.Edit

        url_access.access_type = Access.View
        assert url_access.access_type == Access.View

        with pytest.raises(TypeError):
            url_access.access_type = "42"

    def test_user_access(self, user_access):
        assert user_access.get_email() == "name"
        assert user_access.access_type == Access.View

        user_access.access_type = Access.Edit
        assert user_access.access_type == Access.Edit

        with pytest.raises(TypeError):
            user_access.access_type = "42"

    def test_department_access(self, department_access):
        assert department_access.get_department_name() == "dep_name"
        assert department_access.access_type == Access.View

        department_access.access_type = Access.Edit
        assert department_access.access_type == Access.Edit

        with pytest.raises(TypeError):
            department_access.access_type = "42"
