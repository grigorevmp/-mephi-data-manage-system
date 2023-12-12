from __future__ import annotations

from typing import List, Optional

from core import department
from core import user
from core.user_manager import UserNotFoundError


class DepartmentNotFoundError(Exception):
    """Exception to show that department is not found"""


class DepartmentManager:
    def __init__(self, departments: Optional[List[department.Department]]):
        self.__departments = departments or list()

    def get_departments(self):
        return self.__departments

    def add_department(self, new_department: department.Department):
        if isinstance(new_department, department.Department):
            self.__departments.append(new_department)
        else:
            raise TypeError

    def get_department(self, department_name: str) -> department.Department:
        if isinstance(department_name, str):
            for department_ in self.__departments:
                if department_.department_name == department_name:
                    return department_
            raise DepartmentNotFoundError
        else:
            raise TypeError

    def remove_department_by_department_name(self, department_name: str):
        if isinstance(department_name, str):
            for department_ in self.__departments:
                if department_.department_name == department_name:
                    self.__departments.remove(department_)
                    return
            raise DepartmentNotFoundError
        else:
            raise TypeError

    def add_user(self, user_: user.User, department_name: str):
        if isinstance(user_, user.User) and isinstance(department_name, str):
            flag = False
            for department_ in self.__departments:
                if department_.department_name == department_name:
                    department_.add_user(user_)
                    flag = True
            if not flag:
                raise DepartmentNotFoundError
        else:
            raise TypeError

    def remove_user(self, user_email: str, department_name: str):
        if isinstance(user_email, str) and isinstance(department_name, str):
            flag = False
            for department_ in self.__departments:
                if department_.department_name == department_name:
                    department_.remove_user_by_email(user_email)
                    flag = True
            if not flag:
                raise DepartmentNotFoundError
        else:
            raise TypeError

    def add_users_to_department(self, users: List[user.User], department_name: str):
        for user_ in users:
            self.add_user(user_, department_name)

    def remove_users(self, users_emails: List[str], department_name: str):
        for email in users_emails:
            self.remove_user(email, department_name)

    def add_users_to_departments(self, users_emails: List[user.User], departments_names: List[str]):
        for department_ in departments_names:
            self.add_users_to_department(users_emails, department_)

    def get_department_by_user_email(self, email: str) -> List[department.Department]:
        result = []
        if isinstance(email, str):
            for department_ in self.__departments:
                for user_ in department_.users:
                    if user_.email == email:
                        result.append(department_)
            if len(result) != 0:
                return result
            raise UserNotFoundError
        else:
            raise TypeError

    def get_users_list_by_department_name(self, department_name: str) -> List[user.User]:
        if isinstance(department_name, str):
            for department_ in self.__departments:
                if department_.department_name == department_name:
                    return department_.users
            raise DepartmentNotFoundError
        else:
            raise TypeError
