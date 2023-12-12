from __future__ import annotations

from typing import Optional
from uuid import UUID, uuid4

from core import department_manager
from core.role import Role
from core import workspace


class User:
    def __init__(
            self,
            email: Optional[str],
            password: Optional[str],
            username: Optional[str],
            workSpaces: list[workspace.WorkSpace] = None,
            _id: Optional[UUID] = None,
            role: Role = Role.Client,
            _department_manager: Optional[department_manager.DepartmentManager] = None
    ):
        self.__id: UUID = _id or uuid4()
        self.__email: str = email
        self.__password: str = password
        self.__username: str = username
        self.__workSpaces: list[workspace.WorkSpace] = workSpaces
        self.__role: Role = role

        self.__department_manager: department_manager.DepartmentManager = _department_manager

    def get_id(self) -> UUID:
        return self.__id

    def get_email(self) -> str:
        return self.__email

    def set_email(self, new_email: str):
        if isinstance(new_email, str):
            self.__email = new_email
        else:
            raise TypeError

    email = property(get_email, set_email)

    def get_password(self) -> str:
        return self.__password

    def set_password(self, new_password: str):
        if isinstance(new_password, str):
            self.__password = new_password
        else:
            raise TypeError

    password = property(get_password, set_password)

    def get_username(self) -> str:
        return self.__username

    def set_username(self, new_username: str):
        if isinstance(new_username, str):
            self.__username = new_username
        else:
            raise TypeError

    username = property(get_username, set_username)

    def get_role(self) -> Role:
        return self.__role

    def set_role(self, new_role: Role):
        if isinstance(new_role, Role):
            self.__role = new_role
        else:
            raise TypeError

    role = property(get_role, set_role)

    def get_workSpaces(self) -> list[workspace.WorkSpace]:
        return self.__workSpaces

    def set_workSpaces(self, new_workSpaces: list[workspace.WorkSpace]):
        if isinstance(new_workSpaces, list):
            self.__workSpaces = new_workSpaces
        else:
            raise TypeError

    workSpaces = property(get_workSpaces, set_workSpaces)

    def get_department_manager(self) -> department_manager.DepartmentManager:
        return self.__department_manager

    def set_department_manager(self, new_department_manager: department_manager.DepartmentManager):
        if isinstance(new_department_manager, department_manager.DepartmentManager):
            self.__department_manager = new_department_manager
        else:
            raise TypeError

    department_manager = property(get_department_manager, set_department_manager)
