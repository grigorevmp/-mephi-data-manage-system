from typing import Optional
from uuid import UUID, uuid4

import areas
from areas.backend.core.document import Document
from areas.backend.core.branch_status import BranchStatus


class Branch:
    def __init__(
            self,
            name: Optional[str],
            author: UUID,
            parent: UUID,
            status: BranchStatus,
            document: Document,
            _id: Optional[UUID] = None,
    ):
        self.__id: UUID = _id or uuid4()
        self.__name: str = name
        self.__author: UUID = author
        self.__parent: UUID = parent
        self.__status: BranchStatus = status
        self.__document: Document = document
    def get_id(self) -> UUID:
        return self.__id

    def get_parent_id(self) -> UUID:
        return self.__parent

    def get_status(self) -> BranchStatus:
        return self.__status

    def set_status(self, new_status: BranchStatus):
        if isinstance(new_status, BranchStatus):
            self.__status = new_status
        else:
            raise TypeError

    status = property(get_status, set_status)

    def get_document(self) -> Document:
        return self.__document

    def set_document(self, new_document: Document):
        if isinstance(new_document, Document):
            self.__document = new_document
        else:
            raise TypeError

    document = property(get_document, set_document)

    def get_author(self) -> UUID:
        return self.__author

    def set_author(self, new_author: UUID):
        if isinstance(new_author, UUID):
            self.__author = new_author
        else:
            raise TypeError

    author = property(get_author, set_author)

    def get_name(self) -> str:
        return self.__name

    def set_name(self, new_name: str):
        if isinstance(new_name, str):
            self.__name = new_name
        else:
            raise TypeError

    name = property(get_name, set_name)
