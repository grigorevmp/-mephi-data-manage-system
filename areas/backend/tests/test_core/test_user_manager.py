import uuid

import pytest

from core.user import User
from core.user_manager import UserManager, UserNotFoundError


@pytest.fixture()
def user():
    return User(
        email="test_mail@mail.com",
        password="password",
        username="username",
    )


@pytest.fixture()
def user_manager():
    return UserManager(users=None)


class TestUserManager:

    def test_get_users(self, user_manager):
        assert user_manager.users == []

    def test_set_users(self, user_manager, user):
        user_manager.users = [user]

        with pytest.raises(TypeError):
            user_manager.users = "asd"

    def test_add_user(self, user_manager, user):
        assert user_manager.add_user(user) is None

        with pytest.raises(TypeError):
            user_manager.add_user("asd")

    def test_get_user(self, user_manager, user):
        user_manager.add_user(user)
        assert user_manager.get_user(user.get_id()) == user
        assert user_manager.get_user_by_email(user.email) == user

        with pytest.raises(UserNotFoundError):
            new_user = user_manager.get_user(uuid.uuid4())

        with pytest.raises(TypeError):
            user_manager.get_user(42)

    def test_remove_user(self, user_manager, user):
        user_manager.add_user(user)
        user_manager.remove_user_by_email(user.email)

        with pytest.raises(UserNotFoundError):
            user_manager.get_user_by_email(user.email)

        with pytest.raises(UserNotFoundError):
            user_manager.remove_user_by_email(user.email)

        with pytest.raises(TypeError):
            user_manager.remove_user_by_email(42)

        with pytest.raises(TypeError):
            user_manager.get_user_by_email(42)
