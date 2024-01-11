from typing import List
from uuid import UUID

from sqlalchemy import update

from core.accesses import AccessType
from core.department_manager import DepartmentManager, DepartmentNotFoundError
from core.user import User
from core.department import Department
from flask import current_app
from core.user_manager import UserNotFoundError
from app_db import get_current_db
from database.database import UserModel, DepartmentModel
from repository.data_store_storage_repository import DataStoreStorageRepository

db = get_current_db(current_app)


class UserRepository:
    """
        New methods
    """

    def __init__(self):
        self.data_storage_repo = DataStoreStorageRepository()

    def get_user_from_db_by_id(self, _id: UUID):
        from database.database import UserModel
        user: UserModel = UserModel.query.filter_by(id=str(_id)).first()
        if user is None:
            raise UserNotFoundError
        return User(
            _id=UUID(hex=user.id),
            email=user.email,
            username=user.username,
            password=user.passwordHash,
            role=user.role
        )

    def get_user_from_db_by_id(self, _id: UUID):
        from database.database import UserModel, DepartmentModel
        user: UserModel = UserModel.query.filter_by(id=str(_id)).first()
        if user is None:
            raise UserNotFoundError
        current_user = User(
            _id=UUID(hex=user.id),
            email=user.email,
            username=user.username,
            password=user.passwordHash,
            role=user.role,
            _department_manager=DepartmentManager([])
        )

        department: DepartmentModel = DepartmentModel.query.filter_by(id=user.department_id).first()
        if department is not None:
            current_user.department_manager.add_department(
                Department(
                    department_name=department.name,
                    head_of_department=department.head_of_department,
                    users=[]
                )
            )

        return current_user

    def is_user_exists(self, email: str) -> bool:
        from database.database import UserModel
        user: UserModel = UserModel.query.filter_by(email=email).first()
        return user is not None


    def get_user_departments_by_id(self, _id: UUID) -> list[str]:
        from database.database import UserModel
        user: UserModel = UserModel.query.filter_by(id=str(_id)).first()
        department: DepartmentModel = DepartmentModel.query.filter_by(id=user.department_id).first()
        if department is not None:
            return [department.name]
        else:
            return []

    def get_user_from_db_by_email(self, email: str) -> User:
        from database.database import UserModel
        user: UserModel = UserModel.query.filter_by(email=email).first()
        if user is None:
            raise UserNotFoundError
        return User(
            _id=UUID(hex=user.id),
            email=user.email,
            username=user.username,
            password=user.passwordHash,
            role=user.role
        )

    def get_user_from_db_by_username(self, username: str) -> User:
        from database.database import UserModel
        user: UserModel = UserModel.query.filter_by(username=username).first()
        if user is None:
            raise UserNotFoundError
        return User(
            _id=UUID(hex=user.id),
            email=user.email,
            username=user.username,
            password=user.passwordHash,
            role=user.role
        )

    @staticmethod
    def add_new_user_to_db(new_user: User) -> None:
        from database.database import UserModel

        user: UserModel = UserModel(
            id=str(new_user.get_id()),
            email=new_user.email,
            username=new_user.username,
            passwordHash=new_user.password,
            role=new_user.role
        )

        db.session.add(user)
        db.session.commit()

    """
        Old methods
    """

    def get_departments(self) -> List[Department]:
        from database.database import DepartmentModel
        departments: List[DepartmentModel] = DepartmentModel.query.all()
        departments_list = [Department(i.name, i.head_of_department, []) for i in departments]
        return departments_list

    def get_users(self) -> List[User]:
        from database.database import UserModel
        users: List[UserModel] = UserModel.query.all()
        all_users = [
            User(
                _id=UUID(hex=user.id),
                email=user.email,
                username=user.username,
                password=user.passwordHash,
                role=user.role
            )
            for user in users
        ]
        return all_users

    def get_department_by_name(self, department_name) -> Department:
        from database.database import DepartmentModel
        from core.department_manager import DepartmentNotFoundError
        department: DepartmentModel = DepartmentModel.query.filter_by(name=department_name).first()
        if department is None:
            raise DepartmentNotFoundError
        users = [
            User(
                _id=UUID(hex=user.id),
                email=user.email,
                username=user.username,
                password=user.passwordHash,
                role=user.role
            )
            for user in UserModel.query.filter_by(department_id=department.id).all()
        ]
        return Department(
            department_name=department.name,
            head_of_department=department.head_of_department,
            users=users
        )

    def add_new_department(self, new_department: Department) -> None:
        from database.database import DepartmentModel
        department: DepartmentModel = DepartmentModel(name=new_department.department_name, head_of_department=str(new_department.head_of_department))
        db.session.add(department)
        db.session.commit()

    def delete_department_by_name(self, department_name: str) -> None:
        from database.database import DepartmentModel
        from core.department_manager import DepartmentNotFoundError
        department: DepartmentModel = DepartmentModel.query.filter_by(name=department_name).first()
        if department is None:
            raise DepartmentNotFoundError

        # Clear department from users
        users: List[UserModel] = UserModel.query.filter_by(department_id=department.id).all()

        for user in users:
            db.session.execute(update(UserModel).where(UserModel.id == str(user.id)).values(
                department_id=None
            ))

        db.session.delete(department)
        db.session.commit()

    def add_users_to_department(self, department_name: str, users: List[str]) -> Department:
        from database.database import DepartmentModel, UserModel
        department_model: DepartmentModel = DepartmentModel.query.filter_by(name=department_name).first()
        if department_model is None:
            raise DepartmentNotFoundError
        for user in users:
            user_model: UserModel = UserModel.query.filter_by(id=str(user)).first()

            db.session.execute(update(UserModel).where(UserModel.id == str(user)).values(
                department_id=department_model.id
            ))

            db.session.commit()

    def delete_users_from_department(self, department_name: str, users: List[str]) -> Department:
        from database.database import DepartmentModel, UserModel
        department_model: DepartmentModel = DepartmentModel.query.filter_by(name=department_name).first()

        for user in users:
            user_model: UserModel = UserModel.query.filter_by(id=str(user)).first()

            db.session.execute(update(UserModel).where(UserModel.id == str(user)).values(
                department_id=None
            ))

            db.session.commit()

    def update_department_users(self, department: Department) -> Department:
        from database.database import DepartmentModel, UserModel
        department_model: DepartmentModel = DepartmentModel.query.filter_by(name=department.department_name).first()
        users = []
        for user in department.users:
            user_model: UserModel = UserModel.query.filter_by(id=str(user.get_id())).first()
            users.append(user_model)
        department_model.users = users
        db.session.commit()
        return self.get_department_by_name(department.department_name)

    def get_root_user_space_content(self, user_email: str):
        return self.data_storage_repo.get_root_user_space_content(user_email)

    @staticmethod
    def delete_user(user_id: UUID):
        from exceptions.exceptions import UserNotFoundError
        from database.database import UserModel
        user: UserModel = UserModel.query.filter_by(id=str(user_id)).first()
        if user is None:
            raise UserNotFoundError
        UserModel.query.filter_by(id=str(user_id)).delete()
        db.session.commit()
