import uuid
from uuid import UUID

from areas.backend.core.accesses import UrlAccess, Access, UserAccess, DepartmentAccess, BaseAccess
from areas.backend.decorators.token_required import get_user_by_token
from areas.backend.exceptions.exceptions import NotAllowedError, SpaceNotFoundError
from areas.backend.service.data_store_service import DataStoreService


class AccessService:

    def __init__(self):
        self.data_store_service = DataStoreService()

    def get_accesses_for_workspace(self, workspace_id: UUID) -> list[BaseAccess]:
        user = get_user_by_token()
        try:
            workspace = self.data_store_service.get_workspace_by_id(user.email, workspace_id)
        except SpaceNotFoundError:
            raise NotAllowedError()
        return workspace.get_accesses()

    def add_access_for_workspace_by_url(self, workspace_id: UUID, view_only: bool) -> str:
        user = get_user_by_token()
        try:
            workspace = self.data_store_service.get_workspace_by_id(user.email, workspace_id)
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
            workspace = self.data_store_service.get_workspace_by_id(user.email, workspace_id)
        except SpaceNotFoundError:
            raise NotAllowedError()

        return self.data_store_service.remove_url_access_for_workspace(workspace)

    def add_access_for_workspace_by_email(self, workspace_id: UUID, email: str, view_only: bool) -> str:
        user = get_user_by_token()
        try:
            workspace = self.data_store_service.get_workspace_by_id(user.email, workspace_id)
        except SpaceNotFoundError:
            raise NotAllowedError()

        if view_only:
            access_type = Access.View
        else:
            access_type = Access.Edit

        new_access = UserAccess(
            email=email,
            access_type=access_type
        )
        new_access.owner = user.email

        return self.data_store_service.add_email_access_for_workspace(workspace, new_access)

    def remove_access_for_workspace_by_email(self, workspace_id: UUID, email: str) -> str:
        user = get_user_by_token()
        try:
            workspace = self.data_store_service.get_workspace_by_id(user.email, workspace_id)
        except SpaceNotFoundError:
            raise NotAllowedError()

        return self.data_store_service.remove_email_access_for_workspace(workspace, email)

    def add_access_for_workspace_by_department(self, workspace_id: UUID, department: str, view_only: bool) -> str:
        user = get_user_by_token()
        try:
            workspace = self.data_store_service.get_workspace_by_id(user.email, workspace_id)
        except SpaceNotFoundError:
            raise NotAllowedError()

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
            workspace = self.data_store_service.get_workspace_by_id(user.email, workspace_id)
        except SpaceNotFoundError:
            raise NotAllowedError()

        return self.data_store_service.remove_department_access_for_workspace(workspace, department)
