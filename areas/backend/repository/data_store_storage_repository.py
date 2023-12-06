import base64
import datetime
import os
import uuid
from io import BytesIO
from typing import BinaryIO, Optional

from flask import current_app
from minio import Minio
from sqlalchemy import delete, or_
from sqlalchemy import update

from areas.backend.app_db import get_current_db
from areas.backend.config import endpoint, secret_key, access_key
from areas.backend.core.accesses import UrlAccess, AccessType, DepartmentAccess, UserAccess
from areas.backend.core.branch import Branch
from areas.backend.core.document import Document
from areas.backend.core.request import Request
from areas.backend.core.request_status import RequestStatus
from areas.backend.core.workspace import WorkSpace
from areas.backend.core.workspace_status import WorkSpaceStatus
from areas.backend.database.database import UserModel, WorkspaceModel, RequestModel, BranchModel, DepartmentModel, \
    BaseAccessModel, DocumentModel
from areas.backend.exceptions.exceptions import UserNotFoundError, SpaceNotFoundError, NotAllowedError


class DataStoreStorageRepository:
    def __init__(self):
        self.db = get_current_db(current_app)
        self.minio_client = DataStoreStorageRepository.get_minio_client()

    @staticmethod
    def get_minio_client():
        client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
        )

        found = client.bucket_exists("sud")
        if not found:  # pragma: no cover
            client.make_bucket("sud")  # pragma: no cover
        else:  # pragma: no cover
            pass  # pragma: no cover

        return client

    #############
    # ACCESSES
    #############

    def has_access_to_workspace(self, workspace: WorkSpace, user: UserModel):
        accesses: list[BaseAccessModel] = BaseAccessModel.query.filter_by(workspace_id=workspace.get_id()).all()

        if self.is_author_of_workspace(user.email, workspace.get_id()):
            return True

        for access in accesses:
            if access.access_type == AccessType.Url:
                return True
            if access.access_type == AccessType.User:
                if user.email == access.value:
                    return True
            if access.access_type == AccessType.Department:
                department: DepartmentModel = DepartmentModel.query.filter_by(name=access.value).first()

                for user_ in department.users:
                    if user_.email == user.email:
                        return True
        return False

    def is_author_of_workspace(self, user_mail: str, space_id: uuid.UUID):
        spaces: list[WorkSpace] = self.get_workspaces(user_mail)
        for space in spaces:
            if str(space.get_id()) == str(space_id):
                return True

        return False

    #############
    # WORKSPACES
    #############

    @staticmethod
    def get_workspaces(user_mail: str, archived: bool = False) -> list[WorkSpace]:
        user: UserModel = UserModel.query.filter_by(email=user_mail).first()
        workspaces: list[WorkspaceModel] = WorkspaceModel.query.filter(
            WorkspaceModel.user_id == user.id,
            or_(WorkspaceModel.status == WorkSpaceStatus.Active.value,
                WorkspaceModel.status == WorkSpaceStatus.Archived.value
                )
        ).all() if archived else WorkspaceModel.query.filter(
            WorkspaceModel.user_id == user.id,
            WorkspaceModel.status == WorkSpaceStatus.Active.value
        ).all()

        workspaces_final = []

        for workspace in workspaces:
            branches: list[BranchModel] = BranchModel.query.filter_by(workspace_id=workspace.id).all()
            accesses: list[BaseAccessModel] = BaseAccessModel.query.filter_by(workspace_id=workspace.id).all()

            all_branches = []
            all_requests = []
            all_accesses = []
            indexes = []

            accesses: list[BaseAccessModel] = BaseAccessModel.query.filter_by(workspace_id=workspace.id).all()

            for access in accesses:

                if access.access_type == AccessType.User:
                    all_accesses.append(
                        UserAccess(
                            email=access.value,
                            access_type=access.access_level,
                        )
                    )

                if access.access_type == AccessType.Url:
                    all_accesses.append(
                        UrlAccess(
                            url=access.value,
                            access_type=access.access_level,
                        )
                    )

                if access.access_type == AccessType.Department:
                    all_accesses.append(
                        DepartmentAccess(
                            department_name=access.value,
                            access_type=access.access_level,
                        )
                    )

            for br in branches:
                documentModel: DocumentModel = DocumentModel.query.filter_by(id=br.document_id).first()
                document = None

                if documentModel is not None:
                    document = Document(
                        name=documentModel.name,
                        task_id=documentModel.task_id,
                        file=documentModel.file_id,
                        time=documentModel.modification_time,
                        _id=documentModel.id,
                    )

                all_branches.append(
                    Branch(
                        name=br.name,
                        author=br.author,
                        parent=br.parent_branch_id,
                        document=document,
                        _id=br.id,
                    )
                )

                requests: list[RequestModel] = RequestModel.query.filter_by(source_branch_id=br.id).all()
                requests2: list[RequestModel] = RequestModel.query.filter_by(target_branch_id=br.id).all()

                for req in requests:
                    req_ = Request(
                        title=req.title,
                        description=req.description,
                        status=req.status,
                        source_branch_id=req.source_branch_id,
                        target_branch_id=req.target_branch_id,
                        _id=req.id,
                    )
                    if req.id not in indexes:
                        all_requests.append(req_)
                        indexes.append(req.id)
                for req in requests2:
                    req_ = Request(
                        title=req.title,
                        description=req.description,
                        status=req.status,
                        source_branch_id=req.source_branch_id,
                        target_branch_id=req.target_branch_id,
                        _id=req.id,
                    )
                    if req.id not in indexes:
                        all_requests.append(req_)
                        indexes.append(req.id)

            workspaces_final.append(
                WorkSpace(
                    title=workspace.title,
                    description=workspace.description,
                    branches=all_branches,
                    requests=all_requests,
                    accesses=all_accesses,
                    main_branch=workspace.main_branch,
                    status=workspace.status,
                    _id=workspace.id,
                )
            )

        return workspaces_final

    @staticmethod
    def get_workspaces_access(user_mail: str) -> list[tuple[WorkSpace, AccessType]]:
        user: UserModel = UserModel.query.filter_by(email=user_mail).first()

        workspaces_final: list[tuple[WorkSpace, AccessType]] = []

        workspaces: list[tuple[WorkspaceModel, AccessType]] = []
        if user.department_id is not None:
            department: DepartmentModel = DepartmentModel.query.filter_by(id=user.department_id).first()

            accesses: list[BaseAccessModel] = BaseAccessModel.query.filter(
                BaseAccessModel.access_type == AccessType.Department,
                BaseAccessModel.value == department.name).all()

            for access in accesses:
                workspace: WorkspaceModel = WorkspaceModel.query.filter(WorkspaceModel.id == access.workspace_id,
                                                                        WorkspaceModel.status == WorkSpaceStatus.Active.value).first()
                if workspace is not None:
                    workspaces.append((workspace, access.access_type))

        accesses: list[BaseAccessModel] = BaseAccessModel.query.filter(BaseAccessModel.access_type == AccessType.User,
                                                                       BaseAccessModel.value == user.email).all()

        for access in accesses:
            workspace: WorkspaceModel = WorkspaceModel.query.filter(WorkspaceModel.id == access.workspace_id,
                                                                    WorkspaceModel.status == WorkSpaceStatus.Active.value).first()

            if workspace is not None:
                workspaces.append((workspace, access.access_type))

        for (workspace, access_type) in workspaces:
            branches: list[BranchModel] = BranchModel.query.filter_by(workspace_id=workspace.id).all()

            all_branches = []
            all_requests = []
            indexes = []

            for br in branches:
                documentModel: DocumentModel = DocumentModel.query.filter_by(id=br.document_id).first()
                document = None

                if documentModel is not None:
                    document = Document(
                        name=documentModel.name,
                        task_id=documentModel.task_id,
                        file=documentModel.file_id,
                        time=documentModel.modification_time,
                        _id=documentModel.id,
                    )

                all_branches.append(
                    Branch(
                        name=br.name,
                        author=br.author,
                        parent=br.parent_branch_id,
                        document=document,
                        _id=br.id,
                    )
                )

                requests: list[RequestModel] = RequestModel.query.filter_by(source_branch_id=br.id).all()
                requests2: list[RequestModel] = RequestModel.query.filter_by(target_branch_id=br.id).all()

                for req in requests:
                    req_ = Request(
                        title=req.title,
                        description=req.description,
                        status=req.status,
                        source_branch_id=req.source_branch_id,
                        target_branch_id=req.target_branch_id,
                        _id=req.id,
                    )
                    if req.id not in indexes:
                        all_requests.append(req_)
                        indexes.append(req.id)
                for req in requests2:
                    req_ = Request(
                        title=req.title,
                        description=req.description,
                        status=req.status,
                        source_branch_id=req.source_branch_id,
                        target_branch_id=req.target_branch_id,
                        _id=req.id,
                    )
                    if req.id not in indexes:
                        all_requests.append(req_)
                        indexes.append(req.id)

            workspaces_final.append(
                (WorkSpace(
                    title=workspace.title,
                    description=workspace.description,
                    branches=all_branches,
                    requests=all_requests,
                    accesses=[],
                    main_branch=workspace.main_branch,
                    status=workspace.status,
                    _id=workspace.id,
                ), access_type)
            )

        return workspaces_final

    @staticmethod
    def get_workspaces_open() -> list[WorkSpace]:
        accesses: list[BaseAccessModel] = BaseAccessModel.query.filter(
            BaseAccessModel.access_type == AccessType.Url).all()

        workspaces_final: list[WorkSpace] = []
        workspaces: list[WorkspaceModel] = []

        for access in accesses:
            workspace: WorkspaceModel = WorkspaceModel.query.filter(WorkspaceModel.id == access.workspace_id,
                                                                    WorkspaceModel.status == WorkSpaceStatus.Active.value).first()
            if workspace is not None:
                workspaces.append(workspace)

        for workspace in workspaces:
            branches: list[BranchModel] = BranchModel.query.filter_by(workspace_id=workspace.id).all()

            all_branches = []
            all_requests = []
            indexes = []

            for br in branches:
                documentModel: DocumentModel = DocumentModel.query.filter_by(id=br.document_id).first()
                document = None

                if documentModel is not None:
                    document = Document(
                        name=documentModel.name,
                        task_id=documentModel.task_id,
                        file=documentModel.file_id,
                        time=documentModel.modification_time,
                        _id=documentModel.id,
                    )

                all_branches.append(
                    Branch(
                        name=br.name,
                        author=br.author,
                        parent=br.parent_branch_id,
                        document=document,
                        _id=br.id,
                    )
                )

                requests: list[RequestModel] = RequestModel.query.filter_by(source_branch_id=br.id).all()
                requests2: list[RequestModel] = RequestModel.query.filter_by(target_branch_id=br.id).all()

                for req in requests:
                    req_ = Request(
                        title=req.title,
                        description=req.description,
                        status=req.status,
                        source_branch_id=req.source_branch_id,
                        target_branch_id=req.target_branch_id,
                        _id=req.id,
                    )
                    if req.id not in indexes:
                        all_requests.append(req_)
                        indexes.append(req.id)
                for req in requests2:
                    req_ = Request(
                        title=req.title,
                        description=req.description,
                        status=req.status,
                        source_branch_id=req.source_branch_id,
                        target_branch_id=req.target_branch_id,
                        _id=req.id,
                    )
                    if req.id not in indexes:
                        all_requests.append(req_)
                        indexes.append(req.id)

            workspaces_final.append(
                WorkSpace(
                    title=workspace.title,
                    description=workspace.description,
                    branches=all_branches,
                    requests=all_requests,
                    accesses=[],
                    main_branch=workspace.main_branch,
                    status=workspace.status,
                    _id=workspace.id,
                )
            )

        return workspaces_final

    @staticmethod
    def get_all_workspaces(deleted: bool = False) -> list[(str, WorkSpace)]:
        workspaces: list[WorkspaceModel] = WorkspaceModel.query.filter(
            WorkspaceModel.status != WorkSpaceStatus.Deleted.value
        ).all() if not deleted else WorkspaceModel.query.all()
        workspaces_list = [
            (UserModel.query.filter_by(id=workspace.user_id).first().username, workspace.user_id, WorkSpace(
                title=workspace.title,
                description=workspace.description,
                branches=[],
                requests=[],
                accesses=[],
                main_branch=None,
                status=workspace.status,
                _id=workspace.id,
            )) for workspace in workspaces]
        return workspaces_list

    @staticmethod
    def get_workspace_by_id_admin(space_id: uuid.UUID) -> (str, WorkSpace):
        workspace: WorkspaceModel = WorkspaceModel.query.filter_by(id=str(space_id)).first()
        if workspace is None:
            raise SpaceNotFoundError
        return (UserModel.query.filter_by(id=workspace.user_id).first().username, workspace.user_id, WorkSpace(
            title=workspace.title,
            description=workspace.description,
            branches=[],
            requests=[],
            accesses=[],
            main_branch=None,
            status=workspace.status,
            _id=workspace.id,
        ))

    def create_workspace(self, user_mail: str, workspace: WorkSpace, document_name: str, document_data: str):
        user: UserModel = UserModel.query.filter_by(email=user_mail).first()

        workspace_id = str(uuid.uuid4())

        file_id = uuid.uuid4()

        _branch = BranchModel(
            id=str(uuid.uuid4()),
            name="master",
            author=user.id,
            document_id=str(file_id),
            parent_branch_id=-1,
            workspace_id=workspace_id
        )

        self.db.session.add(_branch)
        self.db.session.commit()

        _workspace = WorkspaceModel(
            id=workspace_id,
            title=workspace.title,
            description=workspace.description,
            main_branch=_branch.id,
            status=WorkSpaceStatus.Active.value,
            user_id=user.id,
        )

        self.db.session.add(_workspace)
        self.db.session.commit()

        document = Document(name=document_name, file=file_id, task_id=uuid.uuid4(),
                            time=datetime.datetime.now(), _id=file_id)
        self.add_new_document(document, document_data, _branch)

        return _workspace.id

    def get_workspace_by_id(self, user_mail: str, space_id: uuid.UUID, archived: bool = False) -> Optional[
        tuple[str, str, WorkSpace]]:
        user: UserModel = UserModel.query.filter_by(email=user_mail).first()

        spaces: list[WorkSpace] = self.get_workspaces(user_mail, archived)
        print(len(spaces))
        for space in spaces:
            print(space.get_id())
            if str(space.get_id()) == str(space_id):
                return UserModel.query.filter_by(id=user.id).first().username, user.id, space

        space: WorkspaceModel = WorkspaceModel.query.filter_by(id=str(space_id)).first()
        if space is not None and str(space.status) == str(WorkSpaceStatus.Active.value):
            branches: list[BranchModel] = BranchModel.query.filter_by(workspace_id=space.id).all()

            all_branches = []
            all_requests = []
            all_accesses = []
            indexes = []

            accesses: list[BaseAccessModel] = BaseAccessModel.query.filter_by(workspace_id=space.id).all()

            for access in accesses:

                if access.access_type == AccessType.User:
                    all_accesses.append(
                        UserAccess(
                            email=access.value,
                            access_type=access.access_level,
                        )
                    )

                if access.access_type == AccessType.Url:
                    all_accesses.append(
                        UrlAccess(
                            url=access.value,
                            access_type=access.access_level,
                        )
                    )

                if access.access_type == AccessType.Department:
                    all_accesses.append(
                        DepartmentAccess(
                            department_name=access.value,
                            access_type=access.access_level,
                        )
                    )

            for br in branches:
                documentModel: DocumentModel = DocumentModel.query.filter_by(id=br.document_id).first()
                document = None

                if documentModel is not None:
                    document = Document(
                        name=documentModel.name,
                        task_id=documentModel.task_id,
                        file=documentModel.file_id,
                        time=documentModel.modification_time,
                        _id=documentModel.id,
                    )

                all_branches.append(
                    Branch(
                        name=br.name,
                        author=br.author,
                        parent=br.parent_branch_id,
                        document=document,
                        _id=br.id,
                    )
                )

                requests: list[RequestModel] = RequestModel.query.filter_by(source_branch_id=br.id).all()
                requests2: list[RequestModel] = RequestModel.query.filter_by(target_branch_id=br.id).all()

                for req in requests:
                    req_ = Request(
                        title=req.title,
                        description=req.description,
                        status=req.status,
                        source_branch_id=req.source_branch_id,
                        target_branch_id=req.target_branch_id,
                        _id=req.id,
                    )
                    if req.id not in indexes:
                        all_requests.append(req_)
                        indexes.append(req.id)
                for req in requests2:
                    req_ = Request(
                        title=req.title,
                        description=req.description,
                        status=req.status,
                        source_branch_id=req.source_branch_id,
                        target_branch_id=req.target_branch_id,
                        _id=req.id,
                    )
                    if req.id not in indexes:
                        all_requests.append(req_)
                        indexes.append(req.id)

            workspace: WorkSpace = WorkSpace(
                title=space.title,
                description=space.description,
                main_branch=space.main_branch,
                status=space.status,
                _id=space.id,
                branches=all_branches,
                requests=all_requests,
                accesses=all_accesses,
            )
            if self.has_access_to_workspace(workspace, user):
                return UserModel.query.filter_by(id=space.user_id).first().username, space.user_id, workspace
            else:
                raise NotAllowedError()

        raise SpaceNotFoundError()

    def change_workspace_status(self, space_id: uuid.UUID, status: str, user_mail: str | None = None, admin=False):
        if admin or self.is_author_of_workspace(user_mail, space_id):
            if admin or self.is_author_of_workspace(user_mail, space_id):
                self.db.session.execute(update(WorkspaceModel).where(WorkspaceModel.id == str(space_id)).values(
                    status=status
                ))
                self.db.session.commit()
                return None
            else:
                raise NotAllowedError()

    def change_workspace_owner(self, space_id: uuid.UUID, owner: uuid.UUID):
        from areas.backend.database.database import UserModel
        user: UserModel = UserModel.query.filter_by(id=str(owner)).first()
        if user is None:
            raise UserNotFoundError
        self.db.session.execute(update(WorkspaceModel).where(WorkspaceModel.id == str(space_id)).values(
            user_id=str(owner)
        ))
        self.db.session.commit()
        return None

    #############
    # BRANCHES
    #############

    def get_branch_in_workspace_by_id(
            self, user_mail: str, space_id: uuid.UUID, branch_id: uuid.UUID
    ) -> tuple[Optional[Branch], str, str, list[Request]]:
        user: UserModel = UserModel.query.filter_by(email=user_mail).first()
        username, user_id, workspace = self.get_workspace_by_id(user_mail, space_id)

        if self.has_access_to_workspace(workspace, user):
            for branch in workspace.branches:
                if str(branch.get_id()) == str(branch_id):
                    user: UserModel = UserModel.query.filter_by(id=branch.author).first()

                    original_branch_name: str = "" if str(
                        branch.get_parent_id()) == "-1" else BranchModel.query.filter_by(
                        id=branch.get_parent_id()).first().name

                    all_requests = []
                    requests: list[RequestModel] = RequestModel.query.filter_by(source_branch_id=branch.get_id()).all()

                    for req in requests:
                        all_requests.append(
                            Request(
                                title=req.title,
                                description=req.description,
                                status=req.status,
                                source_branch_id=req.source_branch_id,
                                target_branch_id=req.target_branch_id,
                                _id=req.id,
                            )
                        )

                    return branch, user.username, original_branch_name, requests

        raise SpaceNotFoundError()

    def get_branches_in_workspace(
            self, user_mail: str, space_id: uuid.UUID
    ) -> list[Branch]:
        user: UserModel = UserModel.query.filter_by(email=user_mail).first()
        username, user_id, workspace = self.get_workspace_by_id(user_mail, space_id)
        list_of_branches = []

        if self.has_access_to_workspace(workspace, user):
            for branch in workspace.branches:
                list_of_branches.append(branch)

                return list_of_branches

        raise SpaceNotFoundError()

    def get_master_branch_in_workspace(
            self, user_mail: str, space_id: uuid.UUID
    ) -> Branch:
        user: UserModel = UserModel.query.filter_by(email=user_mail).first()
        username, user_id, workspace = self.get_workspace_by_id(user_mail, space_id)

        if self.has_access_to_workspace(workspace, user):
            master = workspace.get_main_branch()
            return master

        raise SpaceNotFoundError()

    def delete_branch_from_workspace_by_id(self, user_mail: str, space_id: uuid.UUID, branch_id: uuid.UUID):
        branch: BranchModel = BranchModel.query.filter_by(id=branch_id).first()
        user: UserModel = UserModel.query.filter_by(email=user_mail).first()

        if self.is_author_of_workspace(user_mail, space_id) or branch.author == user.id:
            self.db.session.execute(delete(BranchModel).where(BranchModel.id == branch_id))
            self.db.session.commit()
        else:
            raise NotAllowedError()

    def create_branch_for_workspace(self, user_mail: str, workspace_id: uuid.UUID, branch: Branch):
        user: UserModel = UserModel.query.filter_by(email=user_mail).first()
        username, user_id, workspace = self.get_workspace_by_id(user_mail, workspace_id)

        document_id = uuid.uuid4()

        if self.has_access_to_workspace(workspace, user):
            _branch = BranchModel(
                id=str(uuid.uuid4()),
                name=branch.name,
                author=str(branch.author),
                workspace_id=str(workspace_id),
                document_id=str(document_id),
                parent_branch_id=str(branch.get_parent_id()),
            )

            self.db.session.add(_branch)
            workspace.branches.append(_branch)

            self.db.session.commit()

            old_document: DocumentModel = DocumentModel.query.filter_by(id=branch.document).first()

            document_data = BytesIO(self.get_file_from_cloud(old_document.id + "_" + old_document.name)).read()

            document = Document(name=old_document.name, file=old_document.file_id, task_id=uuid.uuid4(),
                                time=datetime.datetime.now(), _id=document_id)

            base64_bytes = base64.b64encode(document_data).decode('ascii')

            self.add_new_document(document, base64_bytes, _branch)

            return _branch.id
        else:
            raise NotAllowedError()

    #############
    # REQUESTS
    #############

    def get_request_in_workspace_by_id(
            self, user_mail: str, space_id: uuid.UUID, request_id: uuid.UUID
    ) -> Optional[Request]:
        user: UserModel = UserModel.query.filter_by(email=user_mail).first()
        username, user_id, workspace = self.get_workspace_by_id(user_mail, space_id)

        if self.has_access_to_workspace(workspace, user):
            for request in workspace.requests:
                if str(request.get_id()) == str(request_id):
                    return request
        else:
            raise NotAllowedError()

    def change_request_status(self, user_mail: str, workspace_id: uuid.UUID, request_id: uuid.UUID, status: str):
        user: UserModel = UserModel.query.filter_by(email=user_mail).first()
        username, user_id, workspace = self.get_workspace_by_id(user_mail, workspace_id)
        request: RequestModel = RequestModel.query.filter_by(id=request_id).first()
        branch: BranchModel = BranchModel.query.filter_by(id=request.source_branch_id).first()

        if self.has_access_to_workspace(workspace, user) or branch.author == user.id:
            self.db.session.execute(update(RequestModel).where(RequestModel.id == str(request_id)).values(
                status=status
            ))

            self.db.session.commit()
        else:
            raise NotAllowedError()

    def create_request_for_branch(self, user_mail: str, workspace_id: uuid.UUID, request: Request):
        user: UserModel = UserModel.query.filter_by(email=user_mail).first()
        username, user_id, workspace = self.get_workspace_by_id(user_mail, workspace_id)

        if self.has_access_to_workspace(workspace, user):
            _request = RequestModel(
                id=str(uuid.uuid4()),
                title=request.title,
                description=request.description,
                status=request.status,
                source_branch_id=request.get_source_branch_id(),
                target_branch_id=request.get_target_branch_id(),
            )

            self.db.session.add(_request)
            workspace.requests.append(_request)

            self.db.session.commit()

            return _request.id
        else:
            raise NotAllowedError()

    def force_merge(self, user_mail: str, workspace_id: uuid.UUID, request_id: uuid.UUID, ):
        username, user_id, workspace = self.get_workspace_by_id(user_mail, workspace_id)

        if self.is_author_of_workspace(user_mail, workspace_id):

            current_request: Optional[Request] = None

            for request in workspace.requests:
                if str(request.get_id()) == str(request_id):
                    current_request = request
                    break

            if current_request is None:
                raise FileNotFoundError

            branch = self.get_branch_in_workspace_by_id(user_mail, workspace_id, current_request.get_source_branch_id())

            self.db.session.execute(
                update(BranchModel).where(BranchModel.id == str(current_request.get_target_branch_id())).values(
                    document_id=branch.document.get_id()
                ))

            self.delete_branch_from_workspace_by_id(user_mail, workspace_id, branch.get_id())
            self.change_request_status(user_mail, workspace_id, request_id, RequestStatus.Merged.value)
        else:
            raise NotAllowedError()

    def add_new_document(self, new_document: Document, new_file_data: str, branch: BranchModel) -> uuid.UUID:
        print("new_file_data:", new_file_data)

        doc = DocumentModel(
            id=str(new_document.get_id()),
            name=new_document.name,
            task_id=str(new_document.task_id),
            modification_time=datetime.datetime.now(),
            file_id=str(new_document.file),
        )

        self.db.session.add(doc)

        self.db.session.execute(update(BranchModel).where(BranchModel.id == str(branch.id)).values(
            document_id=doc.id
        ))

        self.db.session.commit()

        fn = str(new_document.get_id()) + "_" + new_document.name
        with open(f'cache/{fn}', "wb") as fh:
            fh.write(base64.decodebytes(str.encode(new_file_data)))

        self.save_file_to_cloud(fn)
        return new_document.get_id()

    def save_file_to_cloud(self, file_name):
        self.minio_client.fput_object("sud", file_name, f"cache/{file_name}")
        print(f"'cache/{file_name}' is successfully uploaded as object 'test_file.py' to bucket 'cloud_storage'.")
        # os.remove(f"cache/{file_name}")

    def get_binary_file_from_cloud_by_id(self, file_name: str) -> BinaryIO:
        return BytesIO(self.get_file_from_cloud(f"{file_name}"))

    @staticmethod
    def get_binary_io_file_from_cache(file_name: str) -> BinaryIO:
        with open(file_name, 'rb') as binary_file:
            file_contents = binary_file.read()

            print(file_contents)

            binary_file.seek(0)

            return BytesIO(binary_file.read())

    def get_file_from_cloud(self, file_name):
        print("file_name:" + file_name)
        try:
            cloud_file_request = self.minio_client.get_object("sud", file_name)
            return cloud_file_request.data
        except:
            raise FileNotFoundError

    def edit_item_name(self, item):
        if isinstance(item, Document):
            self.db.session.execute(update(DocumentModel).where(DocumentModel.id ==
                                                                str(item.get_id())).values(name=item.get_name()))
        self.db.session.commit()

    def get_document_by_id(self, user_mail, document_id) -> Document:
        branch: BranchModel = BranchModel.query.filter_by(document_id=str(document_id)).first()

        user: UserModel = UserModel.query.filter_by(email=user_mail).first()
        username, user_id, workspace = self.get_workspace_by_id(user_mail, branch.workspace_id)

        if self.has_access_to_workspace(workspace, user):
            doc: DocumentModel = DocumentModel.query.filter_by(id=str(document_id)).first()

            return Document(
                name=doc.name,
                task_id=doc.task_id,
                file=doc.file_id,
                time=doc.modification_time,
            )
        else:
            raise NotAllowedError()

    #############
    # LEGACY
    #############
    #
    # def find_possible_url_access(self, dir_id: uuid.UUID) -> Optional[uuid.UUID]:
    #     parent_id = dir_id
    #     while parent_id is not None:
    #         url_space = UrlSpaceModel.query.filter_by(root_directory_id=str(parent_id)).first()
    #         if url_space is not None:
    #             return url_space.id
    #
    #         directory: DirectoryModel = DirectoryModel.query.filter_by(id=str(parent_id)).first()
    #
    #         if directory is None:
    #             return None
    #
    #         parent_id = directory.parent_id
    #
    # def find_possible_url_access_for_file(self, file_id: uuid.UUID) -> Optional[uuid.UUID]:
    #     file: FileModel = FileModel.query.filter_by(id=str(file_id)).first()
    #
    #     if file is None:
    #         return None
    #
    #     parent_dir = file.directory[0]
    #
    #     return self.find_possible_url_access(parent_dir.id)
    #
    # def get_url_space_content(self, space_id: uuid.UUID) -> Optional[Directory]:
    #     url_space: UrlSpaceModel = UrlSpaceModel.query.filter_by(id=str(space_id)).first()
    #
    #     if url_space is None:
    #         return None
    #
    #     directory: DirectoryModel = url_space.root_directory
    #     root_directory: Directory = self.fill_directory_with_data(directory)
    #
    #     return root_directory
    #
    # def get_url_space(self, space_id: uuid.UUID) -> Optional[UrlSpaceModel]:
    #     return UrlSpaceModel.query.filter_by(id=str(space_id)).first()
    #
    # def get_user_space(self, user_mail, space_id) -> Optional[UserSpaceModel]:
    #     user: UserModel = UserModel.query.filter_by(email=user_mail).first()
    #     user_space_models: list[UserSpaceModel] = UserSpaceModel.query.filter_by(user_id=user.id).all()
    #     for space in user_space_models:
    #         if str(space.id) == str(space_id):
    #             return space
    #     return None
    #
    # def get_user_space_content(self, user_mail: str, space_id: uuid.UUID) -> Optional[UserCloudSpace]:
    #     spaces: list[UserCloudSpace] = self.get_user_spaces(user_mail)
    #     for space in spaces:
    #         if str(space.get_id()) == str(space_id):
    #             return space
    #
    # def get_root_user_space_content(self, user_mail: str) -> Optional[UserCloudSpace]:
    #     spaces: list[UserCloudSpace] = self.get_user_spaces(user_mail)
    #     for space in spaces:
    #         if space.get_space_type() == SpaceType.Regular:
    #             return space
    #
    #
    #
    # def get_dir_from_cloud(self, dir, zip_name=None, begin_dir_id=None):
    #     if zip_name is None:
    #         zip_name = dir.name
    #         begin_dir_id = dir.id
    #     os.mkdir(f"cache/{zip_name}")
    #     for file in dir.directory_manager.file_manager.items:
    #         file_name = f'{file.id}{file.get_type()}'
    #         with open(f'cache/{zip_name}/{file_name}', "wb") as fh:
    #             fh.write(self.get_file_from_cloud(file_name))
    #     for directory in dir.directory_manager.items:
    #         zip_name_dir = f"{zip_name}/{directory.name}"
    #         self.get_dir_from_cloud(directory, zip_name=zip_name_dir, begin_dir_id=begin_dir_id)
    #     if dir.id == begin_dir_id:
    #         zip_file = shutil.make_archive(format='zip', root_dir="cache/", base_dir=f'{zip_name}',
    #                                        base_name=f"cache/{zip_name}")
    #         shutil.rmtree(f"cache/{zip_name}")
    #         return zip_file
    #     else:
    #         return None
    #
    # def remove_files_from_cloud(self, file_name):
    #     self.minio_client.remove_object("sud", file_name)
    #
    #
    #
    # def get_binary_dir_by_id(self, dir: Directory) -> BinaryIO:
    #     zip_file = self.get_dir_from_cloud(dir)
    #     with open(f'{zip_file}', 'rb') as fz:
    #         data = fz.read()
    #     os.remove(f'{zip_file}')
    #     return BytesIO(data)
    #
    # def add_new_directory(self, new_directory: Directory, parent_id: uuid.UUID) -> uuid.UUID:
    #     new_directory_model = DirectoryModel(
    #         id=str(new_directory.get_id()),
    #         name=new_directory.get_name(),
    #     )
    #
    #     parent_directory = DirectoryModel.query.filter_by(id=str(parent_id)).first()
    #     parent_directory.inner_directories.append(new_directory_model)
    #
    #     self.db.session.commit()
    #
    #     return new_directory.get_id()
    #
    # def fill_directory_with_data(self, directory: DirectoryModel) -> Directory:
    #     partly_root_directory = Directory(
    #         _id=uuid.UUID(directory.id),
    #         name=directory.name,
    #     )
    #
    #     accesses: list[BaseAccess] = []
    #     for access in directory.accesses:
    #         if access.access_type == AccessType.Url:
    #             new_access = UrlAccess(
    #                 url=access.value,
    #                 access_type=access.access_level
    #             )
    #             new_access.owner = access.owner
    #             accesses.append(new_access)
    #         if access.access_type == AccessType.User:
    #             new_access = UserAccess(
    #                 email=access.value,
    #                 access_type=access.access_level
    #             )
    #             new_access.owner = access.owner
    #             accesses.append(new_access)
    #         if access.access_type == AccessType.Department:
    #             new_access = DepartmentAccess(
    #                 department_name=access.value,
    #                 access_type=access.access_level
    #             )
    #             new_access.owner = access.owner
    #             accesses.append(new_access)
    #     partly_root_directory.accesses = accesses
    #
    #     files_in_directory: list[File] = []
    #     for file in directory.files:
    #
    #         accesses: list[BaseAccess] = []
    #         for access in file.accesses:
    #             if access.access_type == AccessType.Url:
    #                 new_access = UrlAccess(
    #                     url=access.value,
    #                     access_type=access.access_level
    #                 )
    #                 new_access.owner = access.owner
    #                 accesses.append(new_access)
    #             if access.access_type == AccessType.User:
    #                 new_access = UserAccess(
    #                     email=access.value,
    #                     access_type=access.access_level
    #                 )
    #                 new_access.owner = access.owner
    #                 accesses.append(new_access)
    #             if access.access_type == AccessType.Department:
    #                 new_access = DepartmentAccess(
    #                     department_name=access.value,
    #                     access_type=access.access_level
    #                 )
    #                 new_access.owner = access.owner
    #                 accesses.append(new_access)
    #
    #         files_in_directory.append(
    #             File(
    #                 name=file.name,
    #                 _id=file.id,
    #                 _type=file.type,
    #                 accesses=accesses
    #             )
    #         )
    #
    #     inner_directories: list[Directory] = []
    #     for inner_directory in directory.inner_directories:
    #         inner_directories.append(self.fill_directory_with_data(inner_directory))
    #
    #     partly_root_directory.get_directory_manager().items = inner_directories
    #     partly_root_directory.get_directory_manager().file_manager.items = files_in_directory
    #
    #     return partly_root_directory
    #
    # def copy_file(self, file, directory_id):
    #     new_id = uuid.uuid4()
    #     old_file_model: FileModel = FileModel.query.filter_by(id=str(file.id)).first()
    #     old_file_dir_model: FileDirectory = FileDirectory.query.filter_by(file_id=str(file.id)).first()
    #     new_file_model = FileModel(
    #         id=str(new_id),
    #         name=old_file_model.name + '_copy' if old_file_dir_model.directory_id == str(
    #             directory_id) else old_file_model.name,
    #         type=old_file_model.type
    #     )
    #     new_file_dir_model = FileDirectory(
    #         file_id=str(new_id),
    #         directory_id=str(directory_id)
    #     )
    #
    #     file_name = f'{old_file_model.id}{old_file_model.type}'
    #     new_file_name = f'{str(new_id)}{old_file_model.type}'
    #     file_data = self.get_binary_file_from_cloud_by_id(old_file_model.id, old_file_model.type)
    #
    #     with open(f'cache/{file_name}', "wb") as fh:
    #         fh.write(BytesIO(file_data.read()).getbuffer())
    #     src = f'cache/{file_name}'
    #     dst = f'cache/{new_file_name}'
    #     shutil.copyfile(src, dst)
    #
    #     self.save_file_to_cloud(new_file_name)
    #     os.remove(src)
    #
    #     self.db.session.add(new_file_model)
    #     self.db.session.add(new_file_dir_model)
    #     self.db.session.commit()
    #     return new_id
    #
    # def copy_directory(self, directory, target_directory_id):
    #     new_id = uuid.uuid4()
    #     old_directory_model: DirectoryModel = DirectoryModel.query.filter_by(id=str(directory.id)).first()
    #     new_directory_model = DirectoryModel(
    #         id=str(new_id),
    #         name=old_directory_model.name + '_copy' if old_directory_model.parent_id == str(
    #             target_directory_id) else old_directory_model.name,
    #         is_root=False,
    #         parent_id=str(target_directory_id)
    #     )
    #     self.db.session.add(new_directory_model)
    #     self.db.session.commit()
    #     return new_id
    #
    # def edit_item_name(self, item):
    #     if isinstance(item, File):
    #         self.db.session.execute(update(FileModel).where(FileModel.id == str(item.id)).values(name=item.name))
    #     elif isinstance(item, Directory):
    #         self.db.session.execute(
    #             update(DirectoryModel).where(DirectoryModel.id == str(item.id)).values(name=item.name))
    #     self.db.session.commit()
    #
    # def remove_shared_space_by_email(self, item: BaseStorageItem, email: str):
    #     user: UserModel = UserModel.query.filter_by(email=email).first()
    #
    #     if isinstance(item, File):
    #         for space in user.spaces:
    #             if space.space_type == SpaceType.Shared:
    #                 if space.root_directory.files[0].id == str(item.id):
    #                     user.spaces.remove(space)
    #                     if space is not None:
    #                         self.db.session.execute(delete(UserSpaceModel).where(UserSpaceModel.id == space.id))
    #     elif isinstance(item, Directory):
    #         for space in user.spaces:
    #             if space.space_type == SpaceType.Shared:
    #                 print(space)
    #                 print(space.root_directory)
    #                 print(item)
    #                 if space.root_directory.id == str(item.id):
    #                     user.spaces.remove(space)
    #                     if space is not None:
    #                         self.db.session.execute(delete(UserSpaceModel).where(UserSpaceModel.id == space.id))
    #     self.db.session.commit()
    #
    # def remove_shared_space_by_url(self, item: BaseStorageItem):
    #     url_spaces: list[UrlSpaceModel] = UrlSpaceModel.query.all()
    #
    #     if isinstance(item, File):
    #         for space in url_spaces:
    #             if len(space.root_directory.files):
    #                 if space.root_directory.files[0].id == str(item.id):
    #                     url_spaces.remove(space)
    #                     if space is not None:
    #                         self.db.session.execute(delete(UrlSpaceModel).where(UrlSpaceModel.id == space.id))
    #     elif isinstance(item, Directory):
    #         for space in url_spaces:
    #             if space.root_directory.id == str(item.id):
    #                 url_spaces.remove(space)
    #                 if space is not None:
    #                     self.db.session.execute(delete(UrlSpaceModel).where(UrlSpaceModel.id == space.id))
    #     self.db.session.commit()
    #
    # def remove_shared_space_by_department(self, item: BaseStorageItem, department_name: str):
    #     department: DepartmentModel = DepartmentModel.query.filter_by(name=department_name).first()
    #
    #     for user in department.users:
    #         self.remove_shared_space_by_email(item, user.email)
    #
    # def add_shared_space_for_file_model_by_email(self, item: FileModel, email: str):
    #     user: UserModel = UserModel.query.filter_by(email=email).first()
    #
    #     new_space = UserSpaceModel(
    #         id=str(uuid.uuid4()),
    #         space_type=SpaceType.Shared,
    #     )
    #     self.db.session.add(new_space)
    #
    #     file: FileModel = FileModel.query.filter_by(id=item.id).first()
    #     directory = DirectoryModel(
    #         id=str(uuid.uuid4()),
    #         name="Root",
    #         is_root=True,
    #     )
    #     self.db.session.add(directory)
    #     new_space.root_directory = directory
    #     new_space.root_directory.files = [file]
    #
    #     user.spaces.append(new_space)
    #     self.db.session.commit()
    #
    # def add_shared_space_for_directory_model_by_email(self, item: DirectoryModel, email: str):
    #     user: UserModel = UserModel.query.filter_by(email=email).first()
    #
    #     new_space = UserSpaceModel(
    #         id=str(uuid.uuid4()),
    #         space_type=SpaceType.Shared,
    #     )
    #     self.db.session.add(new_space)
    #
    #     directory: DirectoryModel = DirectoryModel.query.filter_by(id=item.id).first()
    #     new_space.root_directory = directory
    #
    #     user.spaces.append(new_space)
    #     self.db.session.commit()
    #
    # def add_shared_space_by_email(self, item: BaseStorageItem, email: str):
    #     user: UserModel = UserModel.query.filter_by(email=email).first()
    #
    #     if user is None:
    #         raise UserNotFoundError
    #
    #     new_space = UserSpaceModel(
    #         id=str(uuid.uuid4()),
    #         space_type=SpaceType.Shared,
    #     )
    #     self.db.session.add(new_space)
    #
    #     if isinstance(item, File):
    #         file: FileModel = FileModel.query.filter_by(id=str(item.id)).first()
    #         directory = DirectoryModel(
    #             id=str(uuid.uuid4()),
    #             name="Root",
    #             is_root=True,
    #         )
    #         self.db.session.add(directory)
    #         new_space.root_directory = directory
    #         new_space.root_directory.files = [file]
    #     elif isinstance(item, Directory):
    #         directory: DirectoryModel = DirectoryModel.query.filter_by(id=str(item.id)).first()
    #         new_space.root_directory = directory
    #     user.spaces.append(new_space)
    #     self.db.session.commit()
    #
    # def add_shared_space_by_type(self, item: BaseStorageItem, access: BaseAccess):
    #     if type(access) is UrlAccess:
    #         url_space = UrlSpaceModel(
    #             id=access.get_url()
    #         )
    #
    #         if isinstance(item, File):
    #             file: FileModel = FileModel.query.filter_by(id=str(item.id)).first()
    #             directory = DirectoryModel(
    #                 id=str(uuid.uuid4()),
    #                 name="Root",
    #                 is_root=True
    #             )
    #             self.db.session.add(directory)
    #             url_space.root_directory = directory
    #             url_space.root_directory.files = [file]
    #         elif isinstance(item, Directory):
    #             directory: DirectoryModel = DirectoryModel.query.filter_by(id=str(item.id)).first()
    #             url_space.root_directory = directory
    #
    #         self.db.session.add(url_space)
    #
    #     elif type(access) is UserAccess:
    #         self.add_shared_space_by_email(item, access.get_email())
    #
    #     elif type(access) is DepartmentAccess:
    #         department: DepartmentModel = DepartmentModel.query.filter_by(name=access.get_department_name()).first()
    #
    #         if department is None:
    #             raise DepartmentNotFoundError
    #
    #         for user in department.users:
    #             self.add_shared_space_by_email(item, user.email)
    #
    #     self.db.session.commit()
    #
    def update_workspace_access(self, workspace: WorkSpace):
        accesses: list[BaseAccessModel] = []

        for access in workspace.accesses:
            if isinstance(access, UrlAccess):
                accesses.append(
                    BaseAccessModel(
                        access_level=access.access_type,
                        access_type=AccessType.Url,
                        value=access.get_url()
                    )
                )
            elif isinstance(access, UserAccess):
                accesses.append(
                    BaseAccessModel(
                        access_level=access.access_type,
                        access_type=AccessType.User,
                        value=access.get_email()
                    )
                )
            elif isinstance(access, DepartmentAccess):
                accesses.append(
                    BaseAccessModel(
                        access_level=access.access_type,
                        access_type=AccessType.Department,
                        value=access.get_department_name()
                    )
                )

        workspace_model: WorkspaceModel = WorkspaceModel.query.filter_by(id=str(workspace.get_id())).first()
        for access in workspace_model.accesses:
            workspace_model.accesses.remove(access)
            self.db.session.execute(delete(BaseAccessModel).where(BaseAccessModel.id == access.id))
        workspace_model.accesses = accesses
        self.db.session.commit()

    # def delete_item_from_db(self, item):
    #     if isinstance(item, File):
    #         self.db.session.execute(delete(FileModel).where(FileModel.id == str(item.id)))
    #         self.db.session.execute(delete(FileDirectory).where(FileDirectory.file_id == str(item.id)))
    #         self.remove_files_from_cloud(f"{item.id}{item.type}")
    #     elif isinstance(item, Directory):
    #         self.db.session.execute(
    #             delete(DirectoryModel).where(DirectoryModel.id == str(item.id)))
    #     self.db.session.commit()
    #
    # def move_item_in_db(self, item, target_directory):
    #     if isinstance(item, File):
    #         self.db.session.execute(update(FileDirectory).where(FileDirectory.file_id == str(item.id)).values(
    #             directory_id=str(target_directory.id)))
    #     elif isinstance(item, Directory):
    #         self.db.session.execute(update(DirectoryModel).where(DirectoryModel.id == str(item.id)).values(
    #             parent_id=str(target_directory.id)))
    #     self.db.session.commit()
    #
    # def get_url_access(self, url_space_id):
    #     access: AccessModel = AccessModel.query.filter_by(value=str(url_space_id)).first()
    #     return access.access_level
    #
    # def get_shared_access(self, user_mail, item):
    #     item_id = str(item.id)
    #
    #     if isinstance(item, Directory):
    #         item_type = 'Directory'
    #     else:
    #         item_type = 'File'
    #
    #     if item_type == 'File':
    #         user_access: AccessModel = AccessModel.query.filter_by(value=user_mail, parent_file_id=item_id).first()
    #     else:
    #         user_access: AccessModel = AccessModel.query.filter_by(value=user_mail, parent_id=item_id).first()
    #
    #     if user_access is not None:
    #         return user_access.access_level
    #
    #     user_id = UserModel.query.filter_by(email=user_mail).first().id
    #     departments: list[UserDepartment] = UserDepartment.query.filter_by(user_id=user_id).all()
    #     dep_names = []
    #     for department in departments:
    #         dep_names.append(DepartmentModel.query.filter_by(id=department.department_id).first())
    #     if item_type == 'File':
    #         for department in dep_names:
    #             dep_access: AccessModel = AccessModel.query.filter_by(value=department.name,
    #                                                                   parent_file_id=item_id).first()
    #             if dep_access.access_level == Access.Edit:
    #                 return dep_access.access_level
    #     else:
    #         for department in dep_names:
    #             dep_access: AccessModel = AccessModel.query.filter_by(value=department.name, parent_id=item_id).first()
    #             if dep_access.access_level == Access.Edit:
    #                 return dep_access.access_level
