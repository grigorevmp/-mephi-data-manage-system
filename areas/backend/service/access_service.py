import uuid
from uuid import UUID

from core.accesses import UrlAccess, Access, UserAccess, DepartmentAccess, BaseAccess
from decorators.token_required import get_user_by_token
from exceptions.exceptions import NotAllowedError, SpaceNotFoundError
from service.data_store_service import DataStoreService

from areas.backend.exceptions.exceptions import UserNotFoundError, DepartmentNotFoundError
from areas.backend.service.user_service import UserService


class AccessService:

    def __init__(self):
        self.data_store_service = DataStoreService()
        self.user_service = UserService()

    def get_accesses_for_workspace(self, workspace_id: UUID) -> list[BaseAccess]:
        user = get_user_by_token()
        try:
            name, user_id, workspace = self.data_store_service.get_workspace_by_id(user.email, workspace_id, True)
        except SpaceNotFoundError:
            raise NotAllowedError()
        return workspace.get_accesses()

    def add_access_for_workspace_by_url(self, workspace_id: UUID, view_only: bool) -> str:
        user = get_user_by_token()
        try:
            name, user_id, workspace = self.data_store_service.get_workspace_by_id(user.email, workspace_id, True)
        except SpaceNotFoundError:
            raise NotAllowedError()

        if view_only:
            access_type = Access.View
        else:
            access_type = Access.Edit

        new_access = UrlAccess(
            url=str(uuid.uuid4()),
            access_type=access_type
        )
        new_access.owner = user.email

        return self.data_store_service.set_url_access_for_workspace(workspace, new_access)

    def remove_access_for_workspace_by_url(self, workspace_id: UUID) -> str:
        user = get_user_by_token()
        try:
            name, user_id, workspace = self.data_store_service.get_workspace_by_id(user.email, workspace_id, True)
        except SpaceNotFoundError:
            raise NotAllowedError()

        return self.data_store_service.remove_url_access_for_workspace(workspace)

    def add_access_for_workspace_by_email(self, workspace_id: UUID, email: str, view_only: bool) -> str:
        user = get_user_by_token()
        try:
            name, user_id, workspace = self.data_store_service.get_workspace_by_id(user.email, workspace_id, True)
        except SpaceNotFoundError:
            raise NotAllowedError()

        if view_only:
            access_type = Access.View
        else:
            access_type = Access.Edit

        if not self.user_service.is_user_exists(email):
            raise UserNotFoundError()

        new_access = UserAccess(
            email=email,
            access_type=access_type
        )
        new_access.owner = user.email

        return self.data_store_service.add_email_access_for_workspace(workspace, new_access)

    def remove_access_for_workspace_by_email(self, workspace_id: UUID, email: str) -> str:
        user = get_user_by_token()
        try:
            name, user_id, workspace = self.data_store_service.get_workspace_by_id(user.email, workspace_id, True)
        except SpaceNotFoundError:
            raise NotAllowedError()

        return self.data_store_service.remove_email_access_for_workspace(workspace, email)

    def add_access_for_workspace_by_department(self, workspace_id: UUID, department: str, view_only: bool) -> str:
        user = get_user_by_token()
        try:
            name, user_id, workspace = self.data_store_service.get_workspace_by_id(user.email, workspace_id, True)
        except SpaceNotFoundError:
            raise NotAllowedError()

        try:
            self.user_service.get_department_by_name(department)
        except DepartmentNotFoundError:
            raise DepartmentNotFoundError()

        if view_only:
            access_type = Access.View
        else:
            access_type = Access.Edit

        new_access = DepartmentAccess(
            department_name=department,
            access_type=access_type
        )
        new_access.owner = user.email

        return self.data_store_service.add_department_access_for_workspace(workspace, new_access)

    def remove_access_for_workspace_by_department(self, workspace_id: UUID, department: str) -> str:
        user = get_user_by_token()
        try:
            name, user_id, workspace = self.data_store_service.get_workspace_by_id(user.email, workspace_id, True)
        except SpaceNotFoundError:
            raise NotAllowedError()

        return self.data_store_service.remove_department_access_for_workspace(workspace, department)
