from enum import Enum
from typing import Optional, BinaryIO
from uuid import UUID

from areas.backend.core.accesses import BaseAccess, AccessType
from areas.backend.core.branch import Branch
from areas.backend.core.document import Document
from areas.backend.core.request import Request
from areas.backend.core.request_status import RequestStatus
from areas.backend.core.workspace import WorkSpace
from areas.backend.core.workspace_status import WorkSpaceStatus
from areas.backend.exceptions.exceptions import NotAllowedError
from areas.backend.service.access_service import AccessService
from areas.backend.service.data_store_service import DataStoreService


class AccessEditTypeEnum(Enum):
    Add = 1
    Remove = 2


class AccessClassEnum(Enum):
    Url = 1
    UserEmail = 2
    Department = 3


class DataStoreController:

    def __init__(self):
        self.data_store_service = DataStoreService()
        self.access_service = AccessService()

    """
        ==================
        Data Store Service
        ==================
    """

    #############
    # SEARCH
    #############

    # TODO UPDATE
    def search_in_cloud(self, user_mail: str, file_name: str) -> list[tuple[Document, str]]:
        return self.data_store_service.search_in_cloud(user_mail, file_name)

    #############
    # WORKSPACES
    #############

    def get_workspaces(self, user_mail: str, archived: bool) -> list[WorkSpace]:
        return self.data_store_service.get_workspaces(user_mail, archived)

    def get_workspaces_access(self, user_mail: str) -> list[tuple[WorkSpace, AccessType]]:
        return self.data_store_service.get_workspaces_access(user_mail)

    def get_workspaces_open(self) -> list[WorkSpace]:
        return self.data_store_service.get_workspaces_open()

    def get_workspace_by_id(self, user_mail: str, space_id: UUID, archived) -> Optional[tuple[str, str, WorkSpace]]:
        return self.data_store_service.get_workspace_by_id(user_mail, space_id, archived)

    def archive_workspace(self, user_mail: str,  space_id: UUID):
        self.data_store_service.change_workspace_status(user_mail, space_id, WorkSpaceStatus.Archived.value)

    def update_workspace(self, space_id: UUID, new_status: str | None = None, new_owner: UUID | None = None):
        new_status = WorkSpaceStatus.get_enum_from_value(new_status) if new_status is not None else None
        return self.data_store_service.update_workspace(space_id, new_status, new_owner)

    def create_workspace(self, user_mail: str, workspace: WorkSpace, document_name: str, document_data: str):
        return self.data_store_service.create_workspace(user_mail, workspace, document_name, document_data)

    def get_all_workspaces(self, page: int, limit: int, deleted: bool) -> list[(str, WorkSpace)]:
        return self.data_store_service.get_all_workspaces(page, limit, deleted)

    #############
    # BRANCHES
    #############

    # Delete branch

    def delete_branch(self, user_mail: str, space_id: UUID, branch_id: UUID):
        self.data_store_service.delete_branch(user_mail, space_id, branch_id)

    # View branch

    def get_branch_in_workspace_by_id(
            self, user_mail: str, space_id: UUID, branch_id: UUID
    ) -> tuple[Optional[Branch], str, str, list[Request]]:
        return self.data_store_service.get_branch_in_workspace_by_id(user_mail, space_id, branch_id)

    # Create new branch from current

    def create_branch_for_workspace(self, user_mail: str, workspace_id: UUID, branch: Branch):
        return self.data_store_service.create_branch_for_workspace(user_mail, workspace_id, branch)

    # Add Request

    def create_request_for_branch(self, user_mail: str, workspace_id: UUID, request: Request):
        return self.data_store_service.create_request_for_branch(user_mail, workspace_id, request)

    #############
    # REQUESTS
    #############

    # Delete Request

    def close_request(self, user_mail: str, workspace_id: UUID, request_id: UUID):
        self.data_store_service.change_request_status(user_mail, workspace_id, request_id, RequestStatus.Closed.value)

    # Merge Request

    def force_merge(self, user_mail: str, workspace_id: UUID, request_id: UUID):
        self.data_store_service.force_merge(user_mail, workspace_id, request_id)

    # View Request

    def get_request_in_workspace_by_id(
            self, user_mail: str, space_id: UUID, request_id: UUID
    ) -> Optional[Request]:
        return self.data_store_service.get_request_in_workspace_by_id(user_mail, space_id, request_id)

    # Change Request status

    def change_request_status(self, user_mail: str, workspace_id: UUID, request_id: UUID, status: str):
        self.data_store_service.change_request_status(user_mail, workspace_id, request_id, status)

    # Create Document

    def add_new_document(self, user_email: str, workspace_id: UUID, new_document_name: str, new_document_type: str,
                     new_document_data: str) -> UUID:
        return self.data_store_service.add_new_document(user_email, workspace_id, new_document_name, new_document_type,
                                                    new_document_data)

    def download_item(self, user_mail: str, item_id: UUID) -> [BinaryIO, Document]:
        return self.data_store_service.download_item(user_mail=user_mail, item_id=item_id)

    def get_file_by_id(self, user_mail: str, item_id: UUID) -> Document:
        return self.data_store_service.get_file_by_id(user_mail, item_id)

    def get_binary_file_from_cloud_by_id(self, file_name: str):
        return self.data_store_service.get_binary_file_from_cloud_by_id(file_name)

    def get_base64_file_from_cloud_by_id(self, file_name: str):
        return self.data_store_service.get_base64_file_from_cloud_by_id(f"{file_name}")

    def rename_item(self, user_mail: str, item_id: UUID, new_name: str):
        return self.data_store_service.rename_item_by_id(item_id=item_id, user_mail=user_mail, new_name=new_name)

    def update_document(self, user_mail: str, document_id: UUID, document_name: str, new_file_data: str) -> UUID:
        return self.data_store_service.update_document(user_mail, document_id, document_name, new_file_data)

    #############
    # LEGACY
    #############
    #
    # def add_new_directory(self, user_email: str, space_id: UUID, parent_id: UUID, new_directory_name: str) -> UUID:
    #     return self.data_store_service.add_new_directory(user_email, space_id, parent_id, new_directory_name)
    #
    # def get_dir_content(self, user_mail: str, dir_id: UUID) -> tuple[list[BaseStorageItem], list[tuple[str, str]], str]:
    #     return self.data_store_service.get_dir_content(user_mail, dir_id)
    #
    #
    #
    #
    # def move_item(self, user_mail: str, space_id: UUID, item_id: UUID, target_space: UUID, target_directory_id: UUID):
    #     return self.data_store_service.move_item(item_id=item_id, space_id=space_id, user_mail=user_mail,
    #                                              target_space=target_space, target_directory_id=target_directory_id)
    #
    #
    #
    # def delete_item(self, user_mail: str, space_id, item_id: UUID) -> bool:
    #     return self.data_store_service.delete_item(user_mail=user_mail, space_id=space_id, item_id=item_id)
    #
    # def copy_item(self, user_mail: str, space_id: UUID, item_id: UUID, target_space: UUID, target_directory_id: UUID):
    #     return self.data_store_service.copy_item(item_id=item_id, user_mail=user_mail, space_id=space_id,
    #                                              target_space=target_space, target_directory_id=target_directory_id)
    #
    """
        ==============
        Access Service
        ==============
    """

    def get_accesses(self, workspace_id: UUID) -> list[BaseAccess]:
        return self.access_service.get_accesses_for_workspace(workspace_id)

    def edit_access(
            self,
            space_id: UUID,
            edit_type: AccessEditTypeEnum,
            access_class: AccessClassEnum,
            view_only: Optional[bool] = True,
            value: Optional[str] = None,
    ) -> str:
        try:
            if edit_type == AccessEditTypeEnum.Add:
                if access_class == AccessClassEnum.Url:
                    return self.access_service.add_access_for_workspace_by_url(space_id, view_only)
                if access_class == AccessClassEnum.UserEmail:
                    return self.access_service.add_access_for_workspace_by_email(space_id, value, view_only)
                if access_class == AccessClassEnum.Department:
                    return self.access_service.add_access_for_workspace_by_department(space_id, value, view_only)
            elif edit_type == AccessEditTypeEnum.Remove:
                if access_class == AccessClassEnum.Url:
                    return self.access_service.remove_access_for_workspace_by_url(space_id)
                if access_class == AccessClassEnum.UserEmail:
                    return self.access_service.remove_access_for_workspace_by_email(space_id, value)
                if access_class == AccessClassEnum.Department:
                    return self.access_service.remove_access_for_workspace_by_department(space_id, value)
        except NotAllowedError:
            raise NotAllowedError
