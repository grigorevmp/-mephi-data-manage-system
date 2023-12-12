from typing import Optional
from uuid import UUID, uuid4

from core.request_status import RequestStatus


class Request:
    def __init__(
            self,
            title: Optional[str],
            description: Optional[str],
            status: RequestStatus,
            source_branch_id: UUID,
            target_branch_id: UUID,
            _id: Optional[UUID] = None,
    ):
        self.__id: UUID = _id or uuid4()
        self.__title: str = title
        self.__description: str = description
        self.__status: RequestStatus = status
        self.__source_branch_id: UUID = source_branch_id
        self.__target_branch_id: UUID = target_branch_id

    def get_id(self) -> UUID:
        return self.__id

    def get_source_branch_id(self) -> UUID:
        return self.__source_branch_id

    def set_source_branch_id(self, source_branch_id: UUID):
        if isinstance(source_branch_id, UUID):
            self.__source_branch_id = source_branch_id
        else:
            raise TypeError

    source_branch_id = property(get_source_branch_id, set_source_branch_id)

    def get_target_branch_id(self) -> UUID:
        return self.__target_branch_id

    def set_target_branch_id(self, target_branch_id: UUID):
        if isinstance(target_branch_id, UUID):
            self.__target_branch_id = target_branch_id
        else:
            raise TypeError

    target_branch_id = property(get_target_branch_id, set_target_branch_id)

    def get_status(self) -> RequestStatus:
        return self.__status

    def set_status(self, new_status: RequestStatus):
        if isinstance(new_status, RequestStatus):
            self.__status = new_status
        else:
            raise TypeError

    status = property(get_status, set_status)

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
