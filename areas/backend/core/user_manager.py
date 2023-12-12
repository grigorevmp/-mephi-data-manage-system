from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from core import user


class UserNotFoundError(Exception):
    """Exception to show that user is not found"""


class UserManager:
    def __init__(self, users: Optional[List[user.User]]):
        self.__users = users or list()

    def get_users(self) -> list:
        return self.__users

    def set_users(self, new_users: list):
        if all(map(lambda new_user: isinstance(new_user, user.User), new_users)):
            self.__users = new_users
        else:
            raise TypeError

    users = property(get_users, set_users)

    def add_user(self, new_user: user.User):
        if isinstance(new_user, user.User):
            self.__users.append(new_user)
        else:
            raise TypeError

    def get_user(self, id: UUID) -> user.User:
        if isinstance(id, UUID):
            for user_ in self.__users:
                if user_.get_id() == id:
                    return user_
            raise UserNotFoundError
        else:
            raise TypeError

    def get_user_by_email(self, email: str) -> user.User:
        if isinstance(email, str):
            for user_ in self.__users:
                if user_.email == email:
                    return user_
            raise UserNotFoundError
        else:
            raise TypeError

    def remove_user_by_email(self, email: str):
        if isinstance(email, str):
            for user_ in self.__users:
                if user_.email == email:
                    self.__users.remove(user_)
                    return
            raise UserNotFoundError
        else:
            raise TypeError
