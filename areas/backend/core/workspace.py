from typing import Optional
from uuid import UUID, uuid4

from core.accesses import BaseAccess
from core.branch import Branch
from core.request import Request
from core.request_status import RequestStatus
from core.workspace_status import WorkSpaceStatus


class WorkSpace:
    def __init__(
            self,
            title: Optional[str],
            description: Optional[str],
            branches: list[Branch],
            requests: list[Request],
            main_branch: Optional[Branch],
            status: WorkSpaceStatus,
            accesses: list[BaseAccess],

            _id: Optional[UUID] = None,

    ):
        self.__id: UUID = _id or uuid4()
        self.__title: str = title
        self.__description: str = description
        self.__branches: list[Branch] = branches
        self.__requests: list[Request] = requests
        self.__main_branch: Optional[Branch] = main_branch
        self.__status: WorkSpaceStatus = status
        self.__accesses: list[BaseAccess] = accesses

    def get_id(self) -> UUID:
        return self.__id

    def add_access(self, new_access: BaseAccess):
        self.__accesses.append(new_access)

    def remove_access(self, access: BaseAccess):
        self.__accesses.remove(access)

    def get_accesses(self) -> list[BaseAccess]:
        return self.__accesses

    def set_accesses(self, new_accesses: list[BaseAccess]):
        if isinstance(new_accesses, list):
            self.__accesses = new_accesses
        else:
            raise TypeError

    accesses = property(get_accesses, set_accesses)

    def get_status(self) -> WorkSpaceStatus:
        return self.__status

    def set_status(self, new_status: WorkSpaceStatus):
        if isinstance(new_status, WorkSpaceStatus):
            self.__status = new_status
        else:
            raise TypeError

    def archive(self):
        self.__status = WorkSpaceStatus.Deleted

    def unArchive(self):
        self.__status = WorkSpaceStatus.Active

    def delete(self):
        self.__status = WorkSpaceStatus.Deleted

    status = property(get_status, set_status)

    def get_main_branch(self) -> Optional[Branch]:
        return self.__main_branch

    def set_main_branch(self, new_main_branch: Branch):
        if isinstance(new_main_branch, Branch):
            self.__main_branch = new_main_branch
        else:
            raise TypeError

    main_branch = property(get_main_branch, set_main_branch)

    def get_requests(self) -> list[Request]:
        return self.__requests

    def set_requests(self, new_requests: list[Request]):
        if isinstance(new_requests, list):
            self.__requests = new_requests
        else:
            raise TypeError

    requests = property(get_requests, set_requests)

    def get_branches(self) -> list[Branch]:
        return self.__branches

    def get_branch_by_id(self, _id: UUID) -> Branch:
        return next((x for x in self.__branches if x.get_id() == _id), None)

    def set_branches(self, new_branches: list[Branch]):
        if isinstance(new_branches, list):
            self.__branches = new_branches
        else:
            raise TypeError

    branches = property(get_branches, set_branches)

    def get_description(self) -> str:
        return self.__description

    def set_description(self, new_description: str):
        if isinstance(new_description, str):
            self.__description = new_description
        else:
            raise TypeError

    description = property(get_description, set_description)

    def get_title(self) -> str:
        return self.__title

    def set_title(self, new_title: str):
        if isinstance(new_title, str):
            self.__title = new_title
        else:
            raise TypeError

    title = property(get_title, set_title)

    def delete_branch(self, branch: Branch):
        self.branches = self.branches.remove(branch)

    def merge(self, branch: Branch):
        source_branch = self.get_branch_by_id(branch.get_parent_id())
        source_branch.document = branch.document
        self.branches = self.branches.remove(branch)

    def create_request(
            self,
            title: str,
            description: str,
            branch: Branch
    ):
        self.requests.append(
            Request(
                title=title,
                description=description,
                status=RequestStatus.Open,
                source_branch_id=branch.get_id(),
                target_branch_id=branch.get_parent_id(),
            )
        )
