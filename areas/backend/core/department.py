from __future__ import annotations

from typing import List, Optional

from core import user
from core.user_manager import UserNotFoundError


class Department:
    def __init__(self, department_name: str, users: Optional[List[user.User]]):
        self.__department_name: str = department_name
        self.__users: List[user.User] = users or list()

    def get_department_name(self) -> str:
        return self.__department_name

    def set_department_name(self, new_department_name: str):
        if isinstance(new_department_name, str):
            self.__department_name = new_department_name
        else:
            raise TypeError

    department_name = property(get_department_name, set_department_name)

    def get_users(self) -> List[user.User]:
        return self.__users

    def set_users(self, new_users: List[user.User]):
        if isinstance(new_users, list):
            if all(map(lambda new_user: isinstance(new_user, user.User), new_users)):
                self.__users = new_users
            else:
                raise TypeError
        else:
            raise TypeError

    users = property(get_users, set_users)

    def add_user(self, user_: user.User):
        if isinstance(user_, user.User):
            self.__users.append(user_)
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
