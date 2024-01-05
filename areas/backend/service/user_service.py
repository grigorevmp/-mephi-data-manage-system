from typing import List
from uuid import UUID

from bcrypt import checkpw, gensalt, hashpw
from jwt import InvalidTokenError, decode, encode

from core.department import Department
from core.department_manager import DepartmentNotFoundError
from core.role import Role
from core.user import User
from core.user_manager import UserNotFoundError
from exceptions.exceptions import AlreadyExistsError, InvalidCredentialsError
from repository.user_storage_repository import UserRepository


class UserService:
    def __init__(self):
        self.user_repo = UserRepository()

    def registration(self, email: str, password: str, role: Role, username: str) -> None:
        try:
            self.user_repo.get_user_from_db_by_email(email)
            raise AlreadyExistsError
        except UserNotFoundError:
            new_user = User(
                email=email,
                password=password,
                role=role,
                username=username,
                workSpaces=[]
            )
            hash = hashpw(
                str(new_user.password).encode(), gensalt()
            )
            new_user.password = hash.decode()
            self.user_repo.add_new_user_to_db(new_user)

    def login(self, email: str, password: str) -> str:
        try:
            user = self.user_repo.get_user_from_db_by_email(email)
            if checkpw(password.encode(), str(user.password).encode()) is False:
                raise InvalidCredentialsError
            # TODO: get secret from env
            token = encode({"id": str(user.get_id())}, "SUPER-SECRET-KEY", algorithm="HS256")
            return token
        except UserNotFoundError:
            raise InvalidCredentialsError

    def authentication(self, token: str) -> User:
        try:
            payload = decode(token, "SUPER-SECRET-KEY", ["HS256"])
            _id = UUID(hex=payload["id"])
            return self.user_repo.get_user_from_db_by_id(_id)
        except Exception:
            raise InvalidTokenError

    def get_all_departments(self, page: int, limit: int) -> List[Department]:
        departments = self.user_repo.get_departments()
        output_list = []
        start_index = (page - 1) * limit
        end_index = min(len(departments), start_index + limit)
        for index in range(start_index, end_index):
            output_list.append(departments[index])
        return output_list

    def get_all_users(self, page: int, limit: int) -> List[User]:
        users = self.user_repo.get_users()
        output_list = []
        start_index = (page - 1) * limit
        end_index = min(len(users), start_index + limit)
        for index in range(start_index, end_index):
            output_list.append(users[index])
        return output_list

    def get_user_info(self, user: User) -> list[str]:
        departments = self.user_repo.get_user_departments_by_id(user.get_id())
        return departments

    def is_user_exists(self, email: str) -> bool:
        return self.user_repo.is_user_exists(email)

    def add_new_department(self, new_department: Department) -> None:
        try:
            self.user_repo.get_department_by_name(new_department.department_name)
            raise AlreadyExistsError
        except DepartmentNotFoundError:
            self.user_repo.add_new_department(new_department)

    def delete_department_by_name(self, department_name: str) -> None:
        self.user_repo.delete_department_by_name(department_name)

    def get_department_by_name(self, department_name: str) -> Department:
        return self.user_repo.get_department_by_name(department_name)

    def add_users_to_department(self, department_name: str, users: List[str]) -> Department:
        new_department = self.user_repo.add_users_to_department(department_name, users)
        return new_department

    def delete_users_from_department(self, department_name: str, users: List[str]) -> Department:
        new_department = self.user_repo.delete_users_from_department(department_name, users)
        return new_department

    def delete_user(self, user_id: UUID):
        self.user_repo.delete_user(user_id)
