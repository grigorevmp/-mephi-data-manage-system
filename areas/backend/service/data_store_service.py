import datetime
from typing import Optional, BinaryIO
import uuid
from uuid import UUID

from core.accesses import BaseAccess, DepartmentAccess, UserAccess, UrlAccess, AccessType
from core.branch import Branch
from core.document import Document
from core.request import Request
from core.workspace import WorkSpace
from exceptions.exceptions import ItemNotFoundError, AlreadyExistsError, SpaceNotFoundError
from repository.data_store_storage_repository import DataStoreStorageRepository

from core.workspace_status import WorkSpaceStatus


class DataStoreService:
    def __init__(self):
        self.data_store_storage_repo = DataStoreStorageRepository()

    #############
    # SEARCH
    #############

    def search_in_cloud(self, user_mail: str, document_name: str) -> list[tuple[Document, str, str]]:
        """
        @param user_mail: user email
        @param document_name: query name
        """
        return self.data_store_storage_repo.get_workspaces_document_by_name(user_mail, document_name)

    #############
    # WORKSPACES
    #############

    def get_workspaces(self, user_mail: str, archived: bool) -> list[WorkSpace]:
        return self.data_store_storage_repo.get_workspaces(user_mail, archived)

    def get_workspaces_access(self, user_mail: str) -> list[tuple[WorkSpace, AccessType]]:
        return self.data_store_storage_repo.get_workspaces_access(user_mail)

    def get_workspaces_open(self) -> list[WorkSpace]:
        return self.data_store_storage_repo.get_workspaces_open()

    def change_workspace_status(self, user_mail: str, space_id: uuid.UUID, status: str):
        self.data_store_storage_repo.change_workspace_status(user_mail=user_mail, space_id=space_id, status=status)

    def get_workspace_by_id(self, user_mail: str, space_id: UUID, archived) -> Optional[tuple[str, str, WorkSpace]]:
        name, user_id, space = self.data_store_storage_repo.get_workspace_by_id(user_mail, space_id, archived)

        if space is None:
            raise SpaceNotFoundError

        return name, user_id, space

    def create_workspace(self, user_mail: str, workspace: WorkSpace, document_name: str, document_data: str):
        return self.data_store_storage_repo.create_workspace(user_mail, workspace, document_name, document_data)

    def get_all_workspaces(self, page: int, limit: int, deleted: bool) -> list[(str, WorkSpace)]:
        workspaces = self.data_store_storage_repo.get_all_workspaces(deleted)
        output_list = []
        start_index = (page - 1) * limit
        end_index = min(len(workspaces), start_index + limit) if limit != 0 else len(workspaces)
        for index in range(start_index, end_index):
            output_list.append(workspaces[index])
        return output_list

    def update_workspace(self, space_id: uuid.UUID | None, new_status: WorkSpaceStatus | None, new_owner: UUID | None):
        self.data_store_storage_repo.get_workspace_by_id_admin(space_id=space_id)
        if new_status is not None:
            self.data_store_storage_repo.change_workspace_status(space_id=space_id, status=new_status.value, admin=True)
        if new_owner is not None:
            self.data_store_storage_repo.change_workspace_owner(space_id=space_id, owner=new_owner)
        return self.data_store_storage_repo.get_workspace_by_id_admin(space_id=space_id)

    #############
    # BRANCHES
    #############

    # Delete branch

    def delete_branch(self, user_mail: str, space_id: uuid.UUID, branch_id: uuid.UUID):
        self.data_store_storage_repo.delete_branch_from_workspace_by_id(user_mail, space_id, branch_id)

    # View branch

    def get_branch_in_workspace_by_id(
            self, user_mail: str, space_id: uuid.UUID, branch_id: uuid.UUID
    ) -> tuple[Optional[Branch], str, str, list[Request]]:
        return self.data_store_storage_repo.get_branch_in_workspace_by_id(user_mail, space_id, branch_id)

    # List of branches in workspace
    def get_branches_in_workspace(
            self, user_mail: str, space_id: uuid.UUID
    ) -> list[Branch]:
        return self.data_store_storage_repo.get_branches_in_workspace(user_mail, space_id)

    # Master branch in workspace
    def get_master_branch_in_workspace(
            self, user_mail: str, space_id: uuid.UUID
    ) -> Branch:
        return self.data_store_storage_repo.get_master_branch_in_workspace(user_mail, space_id)

    # Create new branch from current

    def create_branch_for_workspace(self, user_mail: str, workspace_id: UUID, branch: Branch):
        return self.data_store_storage_repo.create_branch_for_workspace(user_mail, workspace_id, branch)

    #############
    # REQUESTS
    #############

    # Add Request

    def create_request_for_branch(self, user_mail: str, workspace_id: UUID, request: Request):
        return self.data_store_storage_repo.create_request_for_branch(user_mail, workspace_id, request)

    # View Request

    def get_request_in_workspace_by_id(
            self, user_mail: str, space_id: uuid.UUID, request_id: uuid.UUID
    ) -> Optional[Request]:
        return self.data_store_storage_repo.get_request_in_workspace_by_id(user_mail, space_id, request_id)

    # Change Request status

    def change_request_status(self, user_mail: str, workspace_id: UUID, request_id: uuid.UUID, status: str):
        self.data_store_storage_repo.change_request_status(user_mail, workspace_id, request_id, status)

    # Merge Request

    def force_merge(self, user_mail: str, workspace_id: UUID, request_id: UUID):
        self.data_store_storage_repo.force_merge(user_mail, workspace_id, request_id)

    # Create Document

    def add_new_document(self, user_email: str, workspace_id: uuid.UUID, new_document_name: str, new_document_type: str,
                         new_file_data: str) -> UUID:
        try:
            name, user_id, workspace = self.get_workspace_by_id(user_email, workspace_id)
        except SpaceNotFoundError:
            raise ItemNotFoundError
        # TODO тут нужно проверять, есть ли файл с таким названием в воркспейсе

        full_file_name = f"{new_document_name}{new_document_type}"

        try:
            branches = self.get_branches_in_workspace(user_email, workspace.get_id())
        except SpaceNotFoundError:
            raise ItemNotFoundError

        for branch in branches:
            document_from_branch = branch.get_document()
            if document_from_branch:
                if branch.document.get_name() == full_file_name:
                    raise AlreadyExistsError

        new_document = Document(name=full_file_name, file=uuid.uuid4(), task_id=uuid.uuid4(),
                                time=datetime.datetime.now(), _id=uuid.uuid4())
        return self.data_store_storage_repo.add_new_document(workspace, new_document, new_file_data)

    # Create Document

    def update_document(self, user_mail: str, document_id: uuid.UUID, document_name: str, new_file_data: str) -> UUID:
        return self.data_store_storage_repo.update_document(user_mail, document_id, document_name, new_file_data)

    def download_item(self, user_mail: str, item_id: UUID) -> [BinaryIO, Document]:
        try:
            item = self.get_file_by_id(user_mail=user_mail, item_id=item_id)
        except FileNotFoundError:
            raise FileNotFoundError

        if item is not None:
            if isinstance(item, Document):
                # result = self.data_store_storage_repo.get_binary_file_from_cloud_by_id(item.get_name())
                result = self.data_store_storage_repo.get_binary_io_file_from_cache(str(item.get_id()) + item.get_name())
                return [result, item]
        else:
            raise ItemNotFoundError  # pragma: no cover reason: We never get this error

    def get_file_by_id(self, user_mail: str, item_id: UUID) -> Document:
        return self.data_store_storage_repo.get_document_by_id(user_mail, item_id)

    def get_item_in_workspace_by_id(self, user_mail: str, space_id: UUID, item_id: UUID) -> Document:
        workspaces = self.get_workspaces(user_mail)

        for workspace in workspaces:
            if workspace.get_id() == space_id:
                branches = self.get_branches_in_workspace(user_mail, workspace.get_id())
                for branch in branches:
                    document_from_branch = branch.get_document()
                    document_id = branch.document.get_id()
                    if document_from_branch:
                        if document_id == str(item_id):
                            return document_from_branch

        raise FileNotFoundError  # pragma: no cover reason: We never get this error

    def get_binary_file_from_cloud_by_id(self, file_name: str) -> Optional[BinaryIO]:
        return self.data_store_storage_repo.get_binary_file_from_cloud_by_id(file_name)

    def get_base64_file_from_cloud_by_id(self, file_name: str) -> Optional[str]:
        return self.data_store_storage_repo.get_base64_file_from_cloud_by_id(file_name)

    def rename_item_by_id(self, user_mail: str, item_id: UUID, new_name: str):
        try:
            item = self.data_store_storage_repo.get_document_by_id(user_mail, item_id)
        except FileNotFoundError:
            raise FileNotFoundError

        if item is not None:
            self.data_store_storage_repo.rename_file(user_mail, item_id, new_name)
            return item.name
        else:
            return None

    #############
    # LEGACY
    #############
    #
    # def get_directory_in_space(self, user_mail: str, space_id: UUID, dir_id: UUID) -> Optional[Directory]:
    #     space = self.data_store_storage_repo.get_user_space_content(user_mail, space_id)
    #     possible_shared_url_space = self.data_store_storage_repo.get_url_space_content(space_id)
    #
    #     if space is None:
    #         directory, _ = self.get_dir_in_url_shared_space(possible_shared_url_space, dir_id)
    #     else:
    #         directory, _ = self.get_user_dir_in_space(space, dir_id)
    #
    #     if directory is None:
    #         return None
    #     return directory
    #
    # def add_new_directory(
    #         self,
    #         user_email: str,
    #         space_id: UUID,
    #         parent_dir_id: uuid.UUID,
    #         new_directory_name: str
    # ) -> UUID:
    #     items, _, _ = self.get_dir_content(user_email, parent_dir_id)
    #     for item in items:
    #         if item.get_name() == new_directory_name:
    #             raise AlreadyExistsError
    #     new_directory = Directory(name=new_directory_name, _id=uuid.uuid4())
    #     return self.data_store_storage_repo.add_new_directory(new_directory, parent_dir_id)
    #
    # def get_dir_content(self, user_mail: str, dir_id: UUID) -> tuple[list[BaseStorageItem], list[tuple[str, str]], str]:
    #     spaces = self.data_store_storage_repo.get_root_dir_by_user_mail(user_mail).get_spaces()
    #     directory = None
    #     path = []
    #
    #     for space in spaces:
    #         directory, path = self.get_user_dir_in_space(space, dir_id)
    #         if directory is not None:
    #             break
    #
    #     if directory is None:
    #         possible_shared_url_space_id = self.data_store_storage_repo.find_possible_url_access(dir_id)
    #         if possible_shared_url_space_id is None:
    #             raise ItemNotFoundError
    #
    #         possible_shared_url_space = self.data_store_storage_repo.get_url_space_content(possible_shared_url_space_id)
    #
    #         directory, path = self.get_dir_in_url_shared_space(possible_shared_url_space, dir_id)
    #
    #     items: list[BaseStorageItem] = []
    #     items.extend(directory.get_directory_manager().items)
    #     items.extend(directory.get_directory_manager().file_manager.items)
    #
    #     return items, path, directory.name
    #
    # def get_user_dir_in_space(self, space: UserCloudSpace, dir_id: UUID) -> tuple[
    #     Optional[Directory], list[tuple[str, str]]]:
    #     for directory in space.get_directory_manager().items:
    #         if str(directory.id) == str(dir_id):
    #             return directory, []
    #         else:
    #             possible_dir, path = self.get_user_dir_in_another_dir(directory, dir_id)
    #             if possible_dir is not None:
    #                 return possible_dir, [(str(directory.id), directory.name)] + path
    #
    #     return None, []
    #
    # def get_dir_in_url_shared_space(self, root_directory, dir_id: UUID) -> tuple[
    #     Optional[Directory], list[tuple[str, str]]]:
    #     if root_directory.id == dir_id:
    #         return root_directory, []
    #     else:
    #         dir_, path = self.get_user_dir_in_another_dir(root_directory, dir_id)
    #         return dir_, [str(root_directory.id), root_directory.name] + path
    #
    # def get_user_dir_in_another_dir(self, directory: Directory, dir_id: UUID) -> tuple[
    #     Optional[Directory], list[tuple[str, str]]]:
    #     for directory in directory.get_directory_manager().items:
    #         if str(directory.id) == str(dir_id):
    #             return directory, []
    #         else:
    #             possible_dir, path = self.get_user_dir_in_another_dir(directory, dir_id)
    #             if possible_dir is not None:
    #                 return possible_dir, [(str(directory.id), directory.name)] + path
    #
    #     return None, []
    #
    # @private
    # def search_in_spaces(self, space_manager: SpaceManager, query: str) -> list[tuple[BaseStorageItem, str]]:
    #     file_and_directories_with_paths = list[tuple[BaseStorageItem, str]]()
    #     for space in space_manager.get_spaces():
    #         for directory in space.get_directory_manager().items:
    #             file_and_directories_with_paths.extend(
    #                 self.search_in_directory(directory=directory, query=query, path=f"{space.get_id()}/root/")
    #             )
    #             file_and_directories_with_paths.extend(
    #                 self.search_for_file_in_directory(
    #                     file_manager=space.get_directory_manager().file_manager,
    #                     query=query,
    #                     path=f"{space.get_id()}/root/"
    #                 )
    #             )
    #     return file_and_directories_with_paths
    #
    # @private
    # def search_in_directory(self, directory: Directory, query: str, path="/", self_check=True) -> list[
    #     tuple[BaseStorageItem, str]]:
    #     file_and_directories_with_paths = list[tuple[BaseStorageItem, str]]()
    #
    #     if self_check and query in directory.name:
    #         file_and_directories_with_paths.append((directory, path + directory.name + "/"))
    #
    #     directory_manager = directory.directory_manager
    #
    #     for directory_ in directory_manager.items:
    #         if query in directory_.name:
    #             file_and_directories_with_paths.append((directory_, path))
    #         file_and_directories_with_paths.extend(
    #             self.search_in_directory(
    #                 directory=directory_,
    #                 query=query,
    #                 path=path + directory_.name + "/",
    #                 self_check=False
    #             )
    #         )
    #
    #     file_and_directories_with_paths.extend(
    #         self.search_for_file_in_directory(
    #             file_manager=directory.directory_manager.file_manager,
    #             query=query,
    #             path=path
    #         )
    #     )
    #
    #     logging.log(
    #         level=logging.DEBUG,
    #         msg=f"For {query} found next items: {[item.name for (item, path) in file_and_directories_with_paths]}"
    #     )
    #
    #     return file_and_directories_with_paths
    #
    # @private
    # def search_for_file_in_directory(
    #         self,
    #         file_manager: FileManager,
    #         query: str,
    #         path: str
    # ) -> list[tuple[BaseStorageItem, str]]:
    #     files_with_path = [(file, path + file.name + file.type) for file in file_manager.items if query in file.name]
    #     return files_with_path
    #
    # def get_item_in_directory_by_id(self, directory: Directory, id_: UUID, recursive=True) -> Optional[BaseStorageItem]:
    #     if str(directory.id) == str(id_):
    #         return directory
    #
    #     directory_manager = directory.directory_manager
    #
    #     for directory_ in directory_manager.items:
    #         if str(directory_.id) == str(id_):
    #             return directory_
    #
    #         if recursive:
    #             item = self.get_item_in_directory_by_id(directory=directory_, id_=id_, recursive=recursive)
    #             if item is not None:
    #                 return item
    #
    #     file = self.get_file_in_directory_by_id(file_manager=directory.directory_manager.file_manager, id_=id_)
    #     if file is not None:
    #         return file
    #
    #     return None
    #
    # @private
    # def get_file_in_directory_by_id(
    #         self,
    #         file_manager: FileManager,
    #         id_: UUID
    # ) -> Optional[File]:
    #     for file in file_manager.items:
    #         if str(file.id) == str(id_):
    #             return file
    #     return None
    #
    # def add_new_file(self, user_email: str, space_id: uuid.UUID, dir_id: uuid.UUID, new_file_name: str,
    #                  new_file_type: str, new_file_data: str) -> UUID:
    #     if not (self.is_user_item(user_email, dir_id)):
    #         raise ItemNotFoundError
    #
    #     dir_content, _, _ = self.get_dir_content(user_email, dir_id)
    #     for _item in dir_content:
    #         if _item.name == new_file_name:
    #             raise AlreadyExistsError
    #     new_file = File(new_file_name, new_file_type, _id=uuid.uuid4())
    #     return self.data_store_storage_repo.add_new_file(dir_id, new_file, new_file_data)
    #
    # def get_file_by_id(self, user_mail: str, item_id: UUID) -> File:
    #     spaces = self.data_store_storage_repo.get_root_dir_by_user_mail(user_mail).get_spaces()
    #
    #     for space in spaces:
    #         for directory in space.get_directory_manager().items:
    #             file = self.get_item_in_directory_by_id(directory=directory, id_=item_id)
    #             if file is not None:
    #                 return file
    #
    #     possible_shared_url_space_id = self.data_store_storage_repo.find_possible_url_access_for_file(item_id)
    #     if possible_shared_url_space_id is None:
    #         raise FileNotFoundError
    #
    #     possible_shared_url_space = self.data_store_storage_repo.get_url_space_content(possible_shared_url_space_id)
    #
    #     file = self.get_file_in_directory_by_id(
    #         file_manager=possible_shared_url_space.get_directory_manager().file_manager,
    #         id_=item_id
    #     )
    #     if file is not None:
    #         return file
    #
    #     raise FileNotFoundError  # pragma: no cover reason: We never get this error
    #
    # def get_item_in_space_by_id(self, user_mail: str, space_id: UUID, item_id: UUID) -> Optional[BaseStorageItem]:
    #     space = self.data_store_storage_repo.get_user_space_content(user_mail, space_id)
    #     possible_shared_url_space = self.data_store_storage_repo.get_url_space_content(space_id)
    #
    #     if space is None and possible_shared_url_space is None:
    #         return None
    #     elif space is None:
    #         space = possible_shared_url_space
    #
    #     for directory in space.get_directory_manager().items:
    #         item = self.get_item_in_directory_by_id(directory=directory, id_=item_id)
    #         if item is not None:
    #             return item
    #         file = self.get_file_in_directory_by_id(
    #             file_manager=space.get_directory_manager().file_manager,
    #             id_=item_id
    #         )
    #         if file is not None:
    #             return file
    #
    #     return None

    def set_url_access_for_workspace(self, workspace: WorkSpace, new_access: BaseAccess) -> str:
        add_new_access = True
        another_access_id = None

        for access in workspace.accesses:
            if isinstance(access, UrlAccess):
                another_access_id = access.get_url()
                if access.access_type != new_access.access_type:
                    access.access_type = new_access.access_type
                    add_new_access = False
                else:
                    return f"nothing changed: {another_access_id}"

        if add_new_access:
            workspace.add_access(new_access)
            return_text = f"new access added for workspace {workspace.get_id()}"
        else:
            return_text = f"accesses updated for workspace {workspace.get_id()}"
        self.data_store_storage_repo.update_workspace_access(workspace)
        return return_text

    def remove_url_access_for_workspace(self, workspace: WorkSpace) -> str:
        for access in workspace.accesses:
            if isinstance(access, UrlAccess):
                workspace.remove_access(access)
                self.data_store_storage_repo.update_workspace_access(workspace)
                return "access removed"
        return "nothing to remove"

    def add_email_access_for_workspace(self, workspace: WorkSpace, new_access: UserAccess) -> str:
        add_new_access = True

        for access in workspace.accesses:
            if isinstance(access, UserAccess):
                if access.get_email() == new_access.get_email():
                    if access.access_type != new_access.access_type:
                        access.access_type = new_access.access_type
                        add_new_access = False
                    else:
                        return "nothing changed"

        if add_new_access:
            workspace.add_access(new_access)
            return_text = f"new access added for workspace {workspace.get_id()}"
        else:
            return_text = f"accesses updated for workspace {workspace.get_id()}"
        self.data_store_storage_repo.update_workspace_access(workspace)
        return return_text

    def remove_email_access_for_workspace(self, workspace: WorkSpace, email: str) -> str:
        for access in workspace.accesses:
            if isinstance(access, UserAccess):
                if access.get_email() == email:
                    workspace.remove_access(access)
                    self.data_store_storage_repo.update_workspace_access(workspace)
                    return "access removed"
        return "nothing to remove"

    def add_department_access_for_workspace(self, workspace: WorkSpace, new_access: DepartmentAccess):
        add_new_access = True

        for access in workspace.accesses:
            if isinstance(access, DepartmentAccess):
                if access.get_department_name() == new_access.get_department_name():
                    if access.access_type != new_access.access_type:
                        access.access_type = new_access.access_type
                        add_new_access = False
                    else:
                        return "nothing changed"

        if add_new_access:
            workspace.add_access(new_access)
            return_text = f"new access added for workspace {workspace.get_id()}"
        else:
            return_text = f"accesses updated for workspace {workspace.get_id()}"
        self.data_store_storage_repo.update_workspace_access(workspace)
        return return_text

    def remove_department_access_for_workspace(self, workspace: WorkSpace, department_name: str):
        for access in workspace.accesses:
            if isinstance(access, DepartmentAccess):
                if access.get_department_name() == department_name:
                    workspace.remove_access(access)
                    self.data_store_storage_repo.update_workspace_access(workspace)
                    return "access removed"
        return "nothing to remove"

    # def get_accesses_for_item(self, item: BaseStorageItem) -> list[BaseAccess]:
    #     return item.accesses
    #
    #
    # def move_item(self, user_mail: str, space_id: UUID, item_id: UUID, target_directory_id: UUID, target_space: UUID):
    #     item = self.get_item_in_space_by_id(user_mail, space_id, item_id)
    #     if item is not None:
    #         if not self.check_edit_access(user_mail, space_id, item):
    #             raise AccessError
    #         target_directory = self.get_directory_in_space(user_mail, target_space, target_directory_id)
    #         if not self.check_edit_access(user_mail, target_space, target_directory):
    #             raise AccessError
    #         if target_directory is not None and isinstance(target_directory, Directory):
    #             self.data_store_storage_repo.move_item_in_db(item, target_directory)
    #             return target_directory.name
    #     else:
    #         raise ItemNotFoundError
    #
    # def download_item(self, user_mail: str, item_id: UUID) -> [BinaryIO, File]:
    #     try:
    #         item = self.get_file_by_id(user_mail=user_mail, item_id=item_id)
    #     except FileNotFoundError:
    #         item = self.get_dir_content(user_mail=user_mail, dir_id=item_id)
    #
    #     if item is not None:
    #         if isinstance(item, File):
    #             result = self.data_store_storage_repo.get_binary_file_from_cloud_by_id(item.id, item.type)
    #             return [result, item]
    #         if isinstance(item, Directory):
    #             result = self.data_store_storage_repo.get_binary_dir_by_id(item)
    #             return [result, item]
    #     else:
    #         raise ItemNotFoundError  # pragma: no cover reason: We never get this error
    #
    #
    # def delete_item(self, user_mail: str, space_id: UUID, item_id: UUID) -> True:
    #     item = self.get_user_item_by_id(user_mail, item_id)
    #     if item is not None:
    #         if not self.check_edit_access(user_mail, space_id, item):
    #             raise AccessError
    #         if isinstance(item, File):
    #             self.data_store_storage_repo.delete_item_from_db(item)
    #             return True
    #         elif isinstance(item, Directory):
    #             if item.name == "Root":
    #                 raise AccessError
    #             del_file_manager = item.directory_manager.file_manager
    #             for file in del_file_manager.items:
    #                 self.data_store_storage_repo.delete_item_from_db(file)
    #             for subdirectory in item.directory_manager.items:
    #                 self.delete_item(user_mail, space_id, item_id=subdirectory.id)
    #             self.data_store_storage_repo.delete_item_from_db(item)
    #             return True
    #     else:
    #         raise ItemNotFoundError
    #
    # def copy_item(self, user_mail: str, space_id: UUID, item_id: UUID, target_space: UUID, target_directory_id: UUID):
    #     item = self.get_item_in_space_by_id(user_mail, space_id, item_id)
    #     if item is not None:
    #         target_directory = self.get_item_in_space_by_id(user_mail, target_space, target_directory_id)
    #         if target_directory is not None:
    #             if not self.check_edit_access(user_mail, target_space, target_directory):
    #                 raise AccessError
    #             if isinstance(target_directory, Directory):
    #                 if isinstance(item, Directory):
    #                     new_directory = deepcopy(item)
    #                     new_directory.id = self.copy_directory(new_directory, target_directory.id)
    #                     target_directory.directory_manager.add_items([new_directory])
    #                 elif isinstance(item, File):
    #                     new_item = deepcopy(item)
    #                     new_item.id = self.data_store_storage_repo.copy_file(item, target_directory.id)
    #                     target_directory.directory_manager.file_manager.add_item(new_item)
    #                 return target_directory.name
    #     raise ItemNotFoundError
    #
    # def copy_directory(self, directory: Directory, target_directory_id):
    #     new_dir_id = self.data_store_storage_repo.copy_directory(directory, target_directory_id)
    #     for file in directory.directory_manager.file_manager.items:
    #         _id = self.data_store_storage_repo.copy_file(file, new_dir_id)
    #         file.id = _id
    #     for subdirectory in directory.directory_manager.items:
    #         self.copy_directory(subdirectory, new_dir_id)
    #     return new_dir_id
    #
    # @private
    # def check_edit_access(self, user_mail, space_id, item):
    #     space = self.data_store_storage_repo.get_user_space(user_mail, space_id)
    #     if space is None:
    #         space = self.data_store_storage_repo.get_url_space(space_id)
    #     if isinstance(space, UrlSpaceModel):
    #         return self.data_store_storage_repo.get_url_access(space.id) == Access.Edit
    #     elif space.space_type == SpaceType.Regular:
    #         return True
    #     elif space.space_type == SpaceType.Shared:
    #         return self.data_store_storage_repo.get_shared_access(user_mail, item) == Access.Edit
