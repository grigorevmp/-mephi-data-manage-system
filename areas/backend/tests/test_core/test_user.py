import uuid
from datetime import datetime
from uuid import uuid4

import pytest

from core.branch import Branch
from core.branch_status import BranchStatus
from core.department_manager import DepartmentManager
from core.document import Document
from core.role import Role
from core.user import User
from core.workspace import WorkSpace
from core.workspace_status import WorkSpaceStatus


@pytest.fixture()
def user(space_manager):
    return User(
        email="test_mail@mail.com",
        password="password",
        username="username",
        workSpaces=[space_manager]
    )


@pytest.fixture(scope='function')
def department_manager():
    return DepartmentManager(
        departments=None
    )


@pytest.fixture()
def file():
    return Document(
        name="Test Document",
        task_id=uuid.uuid4(),
        file=uuid.uuid4(),
        time=datetime.now(),
    )


@pytest.fixture(scope='function')
def branch(file):
    return Branch(
        name="test_space",
        author=uuid4(),
        parent=uuid4(),
        status=BranchStatus.Active.value,
        document=file,
    )


@pytest.fixture()
def space_manager(branch):
    return WorkSpace(
        title="test_space",
        description="test desc",
        branches=[],
        requests=[],
        main_branch=branch,
        status=WorkSpaceStatus.Active,
        accesses=[],
    )


class TestUser:

    def test_get_email(self, user):
        user.email = "asd@asd.asd"
        assert user.email == "asd@asd.asd"

    def test_set_email(self, user):
        user.email = "asd@asd.asd"
        assert user.email == "asd@asd.asd"
        try:
            user.email = 123
        except TypeError:
            pass

    def test_get_password(self, user):
        user.password = "pass123"
        assert user.get_password() == "pass123"

    def test_set_password(self, user):
        user.password = "pass123"
        assert user.password == "pass123"
        try:
            user.password = 123
        except TypeError:
            pass

    def test_get_username(self, user):
        user.username = "user1"
        assert user.username == "user1"

    def test_set_username(self, user):
        user.username = "user1"
        assert user.username == "user1"
        try:
            user.username = 123
        except TypeError:
            pass

    def test_get_role(self, user):
        assert user.role == Role.Client

    def test_set_role(self, user):
        user.role = Role.Admin
        assert user.role == Role.Admin

        try:
            user.role = 123
        except TypeError:
            pass

    def test_get_default_space_manager(self, user):
        assert user.workSpaces[0].title == "test_space"

    def test_set_space_manager(self, user, space_manager):
        user.space_manager = space_manager
        assert user.space_manager == space_manager
        try:
            user.space_manager = 123
        except TypeError:
            pass

    def test_get_department_manager(self, user):
        assert user.get_department_manager() is None

    def test_set_department_manager(self, user, department_manager):
        user.department_manager = department_manager
        assert user.department_manager == department_manager
        try:
            user.department_manager = 123
        except TypeError:
            pass
