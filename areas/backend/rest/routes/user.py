"""The Endpoints to manage the USER_REQUESTS"""
import uuid
from typing import Optional

from flask import jsonify, Blueprint, make_response, request, send_file

from controller.data_store_controller import DataStoreController, AccessEditTypeEnum, AccessClassEnum
from controller.user_controller import UserController
from core.accesses import BaseAccess, UrlAccess, UserAccess, DepartmentAccess, AccessType
from core.branch import Branch
from core.branch_status import BranchStatus
from core.document import Document
from core.request import Request
from core.request_status import RequestStatus
from core.role import Role
from core.workspace import WorkSpace
from core.workspace_status import WorkSpaceStatus
from decorators.token_required import token_required, get_user_by_token
from exceptions.exceptions import AlreadyExistsError, InvalidCredentialsError, ItemNotFoundError, \
    NotAllowedError, UserNotFoundError, DepartmentNotFoundError, AccessError, SpaceNotFoundError

USER_REQUEST_API = Blueprint('request_user_api', __name__)

dataStoreController = DataStoreController()
userController = UserController()


def get_blueprint():
    """Return the blueprint for the main app module"""
    return USER_REQUEST_API


@USER_REQUEST_API.route('/registration', methods=['POST'])
def registration():
    request_data = request.get_json()
    try:
        email = request_data['email']
        password = request_data['password']
        role = Role.get_enum_from_value(request_data['role'])
        username = request_data['username']
    except KeyError:
        return jsonify({'error': 'Invalid request body'}), 400
    try:
        userController.registration(email, password, role, username)
    except AlreadyExistsError:
        return jsonify({'error': 'Email already exists'}), 403
    return jsonify({}), 200


@USER_REQUEST_API.route('/login', methods=['PUT'])
def login():
    request_data = request.get_json()
    try:
        email = request_data['email']
        password = request_data['password']
    except KeyError:
        return jsonify({'error': 'Invalid request body'}), 400
    try:
        token = userController.login(email, password)
        response = make_response()
        response.set_cookie('token', token)
        return response
    except InvalidCredentialsError:
        return jsonify({'error': 'Invalid email or password'}), 403


@USER_REQUEST_API.route('/logout', methods=['GET'])
def logout():
    response = make_response()
    response.delete_cookie('token')
    return response


"""
    ===================
    Block with Files
    ===================
"""


@USER_REQUEST_API.route('/search', methods=['GET'])
@token_required
def search_for():
    """
    Query:
        - query: file/dir name to search for
        - user_mail
    Result:
        {
            items: [{
              name: string,
              path: string,
              type: string
            }]
        }
    """

    # query date
    user = get_user_by_token()
    name = request.args.get('name', default=".", type=str)

    items: list[tuple[Document, str, str]] = dataStoreController.search_in_cloud(user.email, name)
    items_content = []
    for item, branch_id, space_id in items:
        items_content.append(
            {
                "name": item.name,
                "id": str(item.get_id()),
                "branch_id": branch_id,
                "space_id": space_id,
            }
        )

    return jsonify(
        {
            "items": items_content
        }
    ), 200


"""
    ===================
    Block with Workspaces
    ===================
"""


@USER_REQUEST_API.route('/get_workspaces', methods=['GET'])
@token_required
def get_workspaces():
    """
    Query:
        - query: get all workspaces
        - archive: flag to show archived workspaces
    Result:
        {
            workspaces: [{
              workspace
            }]
        }
    """

    # query date
    user = get_user_by_token()
    archived = request.args.get('archived', default=False, type=bool)

    items: list[WorkSpace] = dataStoreController.get_workspaces(user.email, archived)

    workspaces_content = []
    for item in items:
        workspaces_content.append(
            {
                "branches_num": len(item.branches),
                "title": item.title,
                "description": item.description,
                "status": item.status,
                "id": str(item.get_id()),
            }
        )

    return jsonify(
        {
            "workspaces": workspaces_content
        }
    ), 200


@USER_REQUEST_API.route('/get_workspaces_access', methods=['GET'])
@token_required
def get_workspaces_access():
    """
    Query:
        - query: get all workspaces
    Result:
        {
            workspaces: [{
              workspace
            }]
        }
    """

    # query date
    user = get_user_by_token()

    items: list[tuple[WorkSpace, AccessType]] = dataStoreController.get_workspaces_access(user.email)

    workspaces_content = []
    for (item, access_type) in items:
        workspaces_content.append(
            {
                "branches_num": len(item.branches),
                "title": item.title,
                "description": item.description,
                "status": item.status,
                "access_type": access_type.value,
                "id": str(item.get_id()),
            }
        )

    return jsonify(
        {
            "workspaces": workspaces_content
        }
    ), 200


@USER_REQUEST_API.route('/get_workspaces_open', methods=['GET'])
@token_required
def get_workspaces_open():
    """
    Query:
        - query: get all workspaces
    Result:
        {
            workspaces: [{
              workspace
            }]
        }
    """

    # query date
    user = get_user_by_token()

    items: list[WorkSpace] = dataStoreController.get_workspaces_open()

    workspaces_content = []
    for item in items:
        workspaces_content.append(
            {
                "branches_num": len(item.branches),
                "title": item.title,
                "description": item.description,
                "status": item.status,
                "access_type": 1,
                "id": str(item.get_id()),
            }
        )

    return jsonify(
        {
            "workspaces": workspaces_content
        }
    ), 200


@USER_REQUEST_API.route('/get_workspace/<space_id>', methods=['GET'])
@token_required
def get_workspace_content(space_id):
    """
    Query:
        - space_id: id of space to view
        - archived: flag to show archived workspaces
    Result:
        {
            workspace: [{
              files and dirs in space
            }]
        }
    """

    # query date
    user = get_user_by_token()
    archived = request.args.get('archived', default=False, type=bool)

    try:
        username, user_id, item = dataStoreController.get_workspace_by_id(user.email, uuid.UUID(space_id), archived)

        requests = []
        for merge_request in item.requests:
            requests.append(
                {
                    "title": merge_request.title,
                    "description": merge_request.description,
                    "source_branch_id": merge_request.source_branch_id,
                    "target_branch_id": merge_request.target_branch_id,
                    "status": merge_request.status,
                    "id": merge_request.get_id(),
                }
            )

        branches = []
        for branch in item.branches:
            branches.append(
                {
                    "name": branch.name,
                    "status": branch.status,
                    "id": branch.get_id(),
                }
            )

        return jsonify(
            {
                "branches_num": len(item.branches),
                "title": item.title,
                "description": item.description,
                "status": item.status,
                "main_branch": item.main_branch,
                "branches": branches,
                "requests": requests,
                "username": username,
                "user_id": user_id,
                "id": str(item.get_id()),
            }
        ), 200
    except SpaceNotFoundError:
        return jsonify("Can't find space with ID"), 404
    except NotAllowedError:
        return jsonify("No access to this space"), 401


@USER_REQUEST_API.route('/workspace/add', methods=['POST'])
def add_workspace():
    request_data = request.get_json()
    try:
        title = request_data['title']
        document_name = request_data['document_name']
        task = request_data['task']
        document_data = request_data['document_data'].split("base64,")[1]

        description = request_data['description']
    except KeyError:
        return jsonify({'error': 'Invalid request body'}), 400

    try:
        user = get_user_by_token()

        workspace = WorkSpace(
            title=title,
            description=description,
            branches=[],
            requests=[],
            accesses=[],
            main_branch=None,
            status=WorkSpaceStatus.Active.value,
        )

        new_file_id = dataStoreController.create_workspace(user.email, workspace, document_name, document_data, task)
    except ItemNotFoundError:
        return jsonify({'error': 'Incorrect directory'}), 404
    except NotAllowedError:
        return jsonify("No access to this space"), 401
    return jsonify({'id': new_file_id}), 200


@USER_REQUEST_API.route('/workspace/<space_id>/archive', methods=['POST'])
def archive_workspace(space_id):
    try:
        user = get_user_by_token()

        dataStoreController.archive_workspace(user.email, uuid.UUID(space_id))
    except ItemNotFoundError:
        return jsonify({'error': 'Incorrect directory'}), 404
    except NotAllowedError:
        return jsonify("No access to this space"), 401
    return jsonify({'status': "ok"}), 200


"""
    ===================
    Block with Branches
    ===================
"""


@USER_REQUEST_API.route('/workspace/<space_id>/view/<branch_id>', methods=['GET'])
@token_required
def get_branch_in_workspace_by_id(space_id, branch_id):
    """
    Query:
        - space_id: id of space to view
        - branch_id: id of branch to view
    Result:
        {
            branch: [{
              files and dirs in space
            }]
        }
    """

    # query date
    user = get_user_by_token()

    try:
        (item, userName, parentName, merge_requests) = dataStoreController.get_branch_in_workspace_by_id(
            user.email, uuid.UUID(space_id),
            uuid.UUID(branch_id)
        )

        requests = []
        for merge_request in merge_requests:
            requests.append(
                {
                    "title": merge_request.title,
                    "id": merge_request.id,
                }
            )

        return jsonify(
            {
                "id": item.get_id(),
                "name": item.name,
                "author": item.author,
                "requests": requests,
                "authorName": userName,
                "parent": item.get_parent_id(),
                "parentName": parentName,
                "document": item.document.name if item.document is not None else "",
                "document_id": item.document.get_id() if item.document is not None else "",
                "task_id": item.document.task_id if item.document is not None else "",
                "file": item.document.file if item.document is not None else "",
            }
        ), 200
    except SpaceNotFoundError:
        return jsonify("Can't find space with ID"), 404
    except NotAllowedError:
        return jsonify("No access to this space"), 401


@USER_REQUEST_API.route('/workspace/<space_id>/add_branch', methods=['POST'])
def add_branch(space_id):
    request_data = request.get_json()
    try:
        name = request_data['name']
        document_id = request_data['document_id']
        parent_branch_id = request_data['parent_branch_id']
    except KeyError:
        return jsonify({'error': 'Invalid request body'}), 400

    try:
        user = get_user_by_token()

        branch = Branch(
            name=name,
            author=user.get_id(),
            document=document_id,
            status=BranchStatus.Active.value,
            parent=parent_branch_id,
        )

        new_file_id = dataStoreController.create_branch_for_workspace(user.email, space_id, branch)
    except ItemNotFoundError:
        return jsonify({'error': 'Incorrect directory'}), 404
    except NotAllowedError:
        return jsonify("No access to this space"), 401
    except SpaceNotFoundError:
        return jsonify({'error': 'Incorrect workspace'}), 404
    return jsonify({'id': new_file_id}), 200


@USER_REQUEST_API.route('/workspace/<space_id>/branch/<branch_id>', methods=['DELETE'])
def delete_branch(space_id, branch_id):
    try:
        user = get_user_by_token()
        removed = dataStoreController.delete_branch(user.email, space_id, branch_id)
    except ItemNotFoundError:
        return jsonify({'error': 'Incorrect directory'}), 404
    except NotAllowedError:
        return jsonify("No access to this space"), 401
    return jsonify({'removed': removed}), 200


@USER_REQUEST_API.route('/workspace/<space_id>/request', methods=['POST'])
def add_request_for_branch(space_id):
    request_data = request.get_json()
    try:
        title = request_data['title']
        description = request_data['description']
        source_branch_id = request_data['source_branch_id']
        target_branch_id = request_data['target_branch_id']
    except KeyError:
        return jsonify({'error': 'Invalid request body'}), 400

    try:
        user = get_user_by_token()

        merge_request = Request(
            title=title,
            description=description,
            status=RequestStatus.Open.value,
            source_branch_id=source_branch_id,
            target_branch_id=target_branch_id,
        )

        new_file_id = dataStoreController.create_request_for_branch(user.email, space_id, merge_request)
    except ItemNotFoundError:
        return jsonify({'error': 'Incorrect directory'}), 404
    except NotAllowedError:
        return jsonify("No access to this space"), 401
    return jsonify({'id': new_file_id}), 200


@USER_REQUEST_API.route('/workspace/<space_id>/copy/<branch_id>', methods=['POST'])
def copy_document(space_id, branch_id):
    # Getting information about old branch
    user = get_user_by_token()

    try:
        (item, _, _, _) = dataStoreController.get_branch_in_workspace_by_id(
            user.email, uuid.UUID(space_id),
            uuid.UUID(branch_id)
        )

        copy_name = item.document.name.split(".") if item.document is not None else ""
        copy_name[-2] += '_copy'
        copy_name = '.'.join(copy_name)

        doc_id = str(item.document.get_id())
        doc_name = item.document.name
        doc_full_name = doc_id + '_' + doc_name
        print(doc_full_name)
        try:
            file: Optional[Document] = dataStoreController.get_base64_file_from_cloud_by_id(doc_full_name)
        except FileNotFoundError:
            return jsonify({'error': 'File not found'}), 404

        item = {
            "document": copy_name,
            "file": file if item.document is not None else "",
        }
    except SpaceNotFoundError:
        return jsonify("Can't find space with ID"), 404
    except NotAllowedError:
        return jsonify("No access to this space"), 401

    request_data = request.get_json()
    try:
        title = request_data['title']
        description = request_data['description']
    except KeyError:
        return jsonify({'error': 'Invalid request body'}), 400

    try:
        user = get_user_by_token()

        workspace = WorkSpace(
            title=title,
            description=description,
            branches=[],
            requests=[],
            accesses=[],
            main_branch=None,
            status=WorkSpaceStatus.Active.value,
        )
        new_workspace = dataStoreController.create_workspace(user.email, workspace, item['document'], item["file"])
    except ItemNotFoundError:
        return jsonify({'error': 'Incorrect directory'}), 404
    except NotAllowedError:
        return jsonify("No access to this space"), 401
    return jsonify({'id': new_workspace}), 200


"""
    ===================
    Block with Request
    ===================
"""


@USER_REQUEST_API.route('/workspace/<space_id>/request/<request_id>', methods=['GET'])
@token_required
def get_request_in_workspace_by_id(space_id, request_id):
    """
    Query:
        - space_id: id of space to view
        - request_id: id of request to view
    Result:
        {
            branch: [{
              files and dirs in space
            }]
        }
    """

    # query date
    user = get_user_by_token()

    try:
        item: Request = dataStoreController.get_request_in_workspace_by_id(user.email, uuid.UUID(hex=space_id),
                                                                           uuid.UUID(hex=request_id))

        return jsonify(
            {
                "title": item.title,
                "description": item.description,
                "status": item.status,
                "source_branch_id": item.get_source_branch_id(),
                "target_branch_id": item.get_target_branch_id(),
            }
        ), 200
    except SpaceNotFoundError:
        return jsonify("Can't find space with ID"), 404
    except NotAllowedError:
        return jsonify("No access to this space"), 401


@USER_REQUEST_API.route('/workspace/<space_id>/request/<request_id>/change_status', methods=['POST'])
def change_request_status(space_id, request_id):
    user = get_user_by_token()
    request_data = request.get_json()
    try:
        status = request_data['status']
    except KeyError:
        return jsonify({'error': 'Invalid request body'}), 400

    try:
        new_file_id = dataStoreController.change_request_status(user.email, space_id, request_id, status)
    except ItemNotFoundError:
        return jsonify({'error': 'Incorrect directory'}), 404
    except NotAllowedError:
        return jsonify("No access to this space"), 401
    return jsonify({'id': new_file_id}), 200


@USER_REQUEST_API.route('/workspace/<space_id>/request/<request_id>/close', methods=['POST'])
def close_request(space_id, request_id):
    user = get_user_by_token()
    try:
        new_file_id = dataStoreController.close_request(user.email, space_id, request_id)
    except ItemNotFoundError:
        return jsonify({'error': 'Incorrect directory'}), 404
    except NotAllowedError:
        return jsonify("No access to this space"), 401
    return jsonify({'id': new_file_id}), 200


@USER_REQUEST_API.route('/workspace/<space_id>/request/<request_id>/force_merge', methods=['POST'])
def force_merge(space_id, request_id):
    user = get_user_by_token()
    try:
        new_file_id = dataStoreController.force_merge(user.email, space_id, request_id)
    except ItemNotFoundError:
        return jsonify({'error': 'Incorrect directory'}), 404
    except NotAllowedError:
        return jsonify("No access to this space"), 401
    return jsonify({'id': new_file_id}), 200


"""
    ===================
    Block with Files
    ===================
"""


@USER_REQUEST_API.route('/document', methods=['POST'])
def add_new_file():
    request_data = request.get_json()
    try:
        workspace_id = request_data['workspace_id']
        new_document_name = request_data['new_document_name']
        new_document_type = request_data['new_document_type']
        new_document_data = request_data['new_document_data']
    except KeyError:
        return jsonify({'error': 'Invalid request body'}), 400
    try:
        user = get_user_by_token()
        new_document_id = dataStoreController.add_new_document(user.email, uuid.UUID(workspace_id), new_document_name,
                                                               new_document_type, new_document_data)
    except ItemNotFoundError:
        return jsonify({'error': 'Incorrect workspace'}), 404
    except AlreadyExistsError:
        return jsonify({'error': 'File name already exists'}), 409
    return jsonify({'id': new_document_id}), 200


# TODO REFACTOR OLD
@USER_REQUEST_API.route('/file/<file_id>/view', methods=['GET'])
@token_required
def view_file_by_id(file_id):
    """
    Path:
        - file_id: id of file to view
    Result:
        file to view
    """
    user = get_user_by_token()

    print("Request to get file with id = " + file_id)

    try:
        file: Optional[Document] = dataStoreController.get_file_by_id(user.email, uuid.UUID(hex=file_id))
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

    file_name = file.get_name()
    file_type = file_name[-4:]
    if file_type == "jpeg":
        file_type = ".jpeg"

    allowed_file_type_to_view = ['.png', '.pdf',
                                 '.jpeg', 'jpg', '.svg', '.mp4', '.txt']

    mimetype_dict = {
        '.png': 'image/png',
        '.pdf': 'application/pdf',
        '.jpeg': 'image/jpeg',
        '.jpg': 'image/jpeg',
        '.svg': 'image/svg+xml',
        '.mp4': 'video/mp4',
        '.txt': 'text/plain'
    }
    if file_type not in allowed_file_type_to_view:
        return jsonify({'error': 'Cannot view such type of file'}), 403

    try:
        binary_file = dataStoreController.get_binary_file_from_cloud_by_id(file_id + "_" + file.get_name())
        return send_file(binary_file, mimetype_dict[file_type])
    except FileNotFoundError:
        return jsonify({'error': 'File is damaged'}), 404


"""
    ===================
    Block with Accesses
    ===================
"""


@USER_REQUEST_API.route('/accesses/<workspace_id>', methods=['GET'])
@token_required
def get_accesses_for_space(workspace_id):
    """
    Path:
        - space_id: id of workspace to get information
    Result:
        information about all accesses
    """
    try:
        accesses: Optional[list[BaseAccess]] = dataStoreController.get_accesses(workspace_id) or list()

        accesses_content = []
        for access in accesses:

            content = "undefined"

            if isinstance(access, UrlAccess):
                content = access.get_url()
            elif isinstance(access, UserAccess):
                content = access.get_email()
            elif isinstance(access, DepartmentAccess):
                content = access.get_department_name()

            accesses_content.append(
                {
                    "class": access.__class__.__name__,
                    "type": access.access_type.name,
                    "content": content
                }
            )

        return jsonify(
            {
                "accesses": accesses_content
            }
        ), 200

    except NotAllowedError:
        return jsonify({'error': 'Not allowed to do this action'}), 401


@USER_REQUEST_API.route('/accesses/<space_id>/url', methods=['PUT'])
@token_required
def set_access_by_url(space_id):
    """
    Path:
        - space_id: id of space to change access
    Result:
        status of the change
    """

    view_only = request.args.get('view_only', default="true")
    if view_only == "true":
        view_only_bool: bool = True
    else:
        view_only_bool: bool = False

    try:
        result = dataStoreController.edit_access(
            space_id=space_id,
            edit_type=AccessEditTypeEnum.Add,
            access_class=AccessClassEnum.Url,
            view_only=view_only_bool,
        )
        return jsonify({"status": result}), 200

    except NotAllowedError:
        return jsonify({'error': 'Not allowed to do this action'}), 401


@USER_REQUEST_API.route('/accesses/<space_id>/url', methods=['DELETE'])
@token_required
def reset_access_by_url(space_id):
    """
    Path:
        - space_id: id of space to change access
    Result:
        status of the change
    """

    try:
        result = dataStoreController.edit_access(
            space_id=space_id,
            edit_type=AccessEditTypeEnum.Remove,
            access_class=AccessClassEnum.Url,
        )
        return jsonify({"status": result}), 200

    except NotAllowedError:
        return jsonify({'error': 'Not allowed to do this action'}), 401


@USER_REQUEST_API.route('/accesses/<space_id>/email/<email>', methods=['PUT'])
@token_required
def add_access_by_user(space_id, email):
    """
    Path:
        - space_id: id of space to change access
    Result:
        status of the change
    """

    view_only = request.args.get('view_only', default="true")
    if view_only == "true":
        view_only_bool: bool = True
    else:
        view_only_bool: bool = False

    try:
        result = dataStoreController.edit_access(
            space_id=space_id,
            edit_type=AccessEditTypeEnum.Add,
            access_class=AccessClassEnum.UserEmail,
            view_only=view_only_bool,
            value=email,
        )
        return jsonify({"status": result}), 200

    except NotAllowedError:
        return jsonify({'error': 'Not allowed to do this action'}), 401
    except UserNotFoundError:
        return jsonify({'error': 'User not found'}), 404


@USER_REQUEST_API.route('/accesses/<space_id>/email/<email>', methods=['DELETE'])
@token_required
def remove_access_by_user(space_id, email):
    """
    Path:
        - space_id: id of space to change access
    Result:
        status of the change
    """

    try:
        result = dataStoreController.edit_access(
            space_id=space_id,
            edit_type=AccessEditTypeEnum.Remove,
            access_class=AccessClassEnum.UserEmail,
            value=email,
        )
        return jsonify({"status": result}), 200

    except NotAllowedError:
        return jsonify({'error': 'Not allowed to do this action'}), 401


@USER_REQUEST_API.route('/accesses/<space_id>/department/<department>', methods=['PUT'])
@token_required
def add_access_by_department(space_id, department):
    """
    Path:
        - space_id: id of space to change access
    Result:
        status of the change
    """

    view_only = request.args.get('view_only', default="true")
    if view_only == "true":
        view_only_bool: bool = True
    else:
        view_only_bool: bool = False

    try:
        result = dataStoreController.edit_access(
            space_id=space_id,
            edit_type=AccessEditTypeEnum.Add,
            access_class=AccessClassEnum.Department,
            view_only=view_only_bool,
            value=department,
        )
        return jsonify({"status": result}), 200

    except NotAllowedError:
        return jsonify({'error': 'Not allowed to do this action'}), 401
    except DepartmentNotFoundError:
        return jsonify({'error': 'Department not found'}), 404


@USER_REQUEST_API.route('/accesses/<space_id>/department/<department>', methods=['DELETE'])
@token_required
def remove_access_by_department(space_id, department):
    """
    Path:
        - space_id: id of space to change access
    Result:
        status of the change
    """

    try:
        result = dataStoreController.edit_access(
            space_id=space_id,
            edit_type=AccessEditTypeEnum.Remove,
            access_class=AccessClassEnum.Department,
            value=department,
        )
        return jsonify({"status": result}), 200

    except NotAllowedError:
        return jsonify({'error': 'Not allowed to do this action'}), 401


# FILE CONTROL

@USER_REQUEST_API.route('/rename/<item_id>', methods=['PUT'])
@token_required
def rename_item(item_id):
    """
    Path:
        - space_id: id of space with item
        - item_id: id of item to rename
    """

    new_name = request.args.get('new_name', type=str)

    try:
        if new_name is not None:
            user = get_user_by_token()
            result = dataStoreController.rename_item(user.email, item_id, new_name)
            if result is not None:
                return jsonify({'new_name': result}), 200
            else:
                return jsonify({'error': 'Can\'t find item'}), 404
        else:
            return jsonify({'error': 'No new name presented. Use query parameter \'new_name\''}), 400
    except AccessError:
        return jsonify({'error': 'Not allowed to do this action'}), 401
    except FileNotFoundError:
        return jsonify({'error': 'Can\'t find item'}), 404


@USER_REQUEST_API.route('/upload_file/<document_id>', methods=['POST'])
def upload_file(document_id):
    request_data = request.get_json()
    try:
        document_name = request_data['document_name']
        document_data = request_data['document_data'].split("base64,")[1]
    except KeyError:
        return jsonify({'error': 'Invalid request body'}), 400

    try:
        user = get_user_by_token()

        new_file_id = dataStoreController.update_document(user.email, uuid.UUID(document_id), document_name, document_data)
    except ItemNotFoundError:
        return jsonify({'error': 'Incorrect directory'}), 404
    except NotAllowedError:
        return jsonify("No access to this space"), 401
    return jsonify({'id': new_file_id}), 200


@USER_REQUEST_API.route('/download/<item_id>', methods=['GET'])
@token_required
def download_by_item_id(item_id):
    """
    Path:
        - space_id: id of space with item
        - item_id: id of item to download
    Result:
        file
    """
    user = get_user_by_token()
    try:
        result = dataStoreController.download_item(user.email, item_id)
        return send_file(result[0], download_name=result[1].get_name(), as_attachment=True), 200
    except FileNotFoundError:
        return jsonify({'error': 'Item not found'}), 404


@USER_REQUEST_API.route('/whoiam', methods=['GET'])
@token_required
def get_user_list():
    """
    Result:
        {
            id: string
            email: string
            departments: string
            space_id: string
            root_dir_id: string
        }
    """

    user = get_user_by_token()
    user_info: list[str] = userController.get_user_info(user)

    return jsonify(
        {
            "id": user.get_id(),
            "email": user.email,
            "username": user.username,
            "role": user.role.value,
            "departments": ' '.join(user_info),
        }
    ), 200
