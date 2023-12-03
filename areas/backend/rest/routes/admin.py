"""The Endpoints to manage the ADMIN_REQUESTS"""
import uuid

from flask import jsonify, Blueprint, request

from areas.backend.controller.data_store_controller import *
from areas.backend.controller.user_controller import UserController
from areas.backend.core.department import Department
from areas.backend.decorators.token_required import admin_access
from areas.backend.exceptions.exceptions import AlreadyExistsError, ItemNotFoundError, UserNotFoundError, \
    SpaceNotFoundError
from areas.backend.core.department_manager import DepartmentNotFoundError

ADMIN_REQUEST_API = Blueprint('request_admin_api', __name__)

dataStoreController = DataStoreController()
userController = UserController()


def get_blueprint():
    """Return the blueprint for the main app module"""
    return ADMIN_REQUEST_API


"""
    ===================
    Block with Workspace
    ===================
"""


@ADMIN_REQUEST_API.route('/all_workspaces', methods=['GET'])
@admin_access
def get_workspaces_list():
    """
    Query:
        - query: page
        - query: limit
        - query: deleted
    Result:
        {
            workspaces: [{
              owner: string,
              title: string,
              description: string,
              status: string,
              id: string
            }]
        }
    """
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=10, type=int)
    deleted = request.args.get('deleted', default=False, type=bool)
    workspaces = dataStoreController.get_all_workspaces(page, limit, deleted)
    items = [{"owner": workspace[0],
              "title": workspace[1].title,
              "description": workspace[1].description,
              "status": workspace[1].status,
              "id": workspace[1].get_id()
              } for workspace in workspaces]
    return jsonify(
        {
            "workspaces": items
        }
    ), 200


@ADMIN_REQUEST_API.route('/workspace/<space_id>', methods=['PUT'])
@admin_access
def update_workspace(space_id):
    """
    Query:
        - path: space_id
        - body: new_status
        - body: new_owner
    Result:
        {
            'status': "ok",
            workspace: {
              owner: string,
              title: string,
              description: string,
              status: string,
              id: string
            }
        }
    """
    request_data = request.get_json()
    new_status = request_data['new_status'] if 'new_status' in request_data.keys() else None
    try:
        new_owner = uuid.UUID(request_data['new_owner']) if 'new_owner' in request_data.keys() else None
    except Exception:
        return jsonify({'error': 'Invalid format of new workspace owner ID'}), 400
    if new_status is None and new_owner is None:
        return jsonify({'error': 'Invalid request body!'}), 400
    try:
        new_workspace = dataStoreController.update_workspace(uuid.UUID(space_id), new_status, new_owner)
    except ItemNotFoundError:
        return jsonify({'error': 'Incorrect workspace'}), 404
    except SpaceNotFoundError:
        return jsonify({'error': 'Incorrect workspace'}), 404
    except UserNotFoundError:
        return jsonify({'error': 'Incorrect new owner'}), 404
    except NotImplementedError:
        return jsonify({'error': 'Incorrect new workspace status'}), 404
    except ValueError:
        return jsonify({'error': 'Invalid workspace ID'}), 400
    return jsonify({"status": "ok",
                    "workspace": {"owner": new_workspace[0],
                                  "title": new_workspace[1].title,
                                  "description": new_workspace[1].description,
                                  "status": new_workspace[1].status,
                                  "id": new_workspace[1].get_id()
                                  }}), 200


@ADMIN_REQUEST_API.route('/workspace/<space_id>', methods=['DELETE'])
@admin_access
def delete_workspace(space_id):
    """
    Query:
        - path: space_id
    Result:
        {
            'status': "ok",
            workspace: {
              owner: string,
              title: string,
              description: string,
              status: string,
              id: string
            }
        }
    """
    try:
        new_workspace = dataStoreController.update_workspace(uuid.UUID(space_id), WorkSpaceStatus.Deleted.value)
    except ItemNotFoundError:
        return jsonify({'error': 'Incorrect workspace'}), 404
    except ValueError:
        return jsonify({'error': 'Invalid workspace ID'}), 400
    return jsonify({"status": "ok",
                    "workspace": {"owner": new_workspace[0],
                                  "title": new_workspace[1].title,
                                  "description": new_workspace[1].description,
                                  "status": new_workspace[1].status,
                                  "id": new_workspace[1].get_id()
                                  }}), 200


"""
    ===================
    Block with Department
    ===================
"""


# TODO REFACTOR OLD
@ADMIN_REQUEST_API.route('/department', methods=['GET'])
@admin_access
def get_department_list():
    """
    Query:
        - query: page
        - query: limit
    Result:
        {
            departments: [{
              department_name: string
            }]
        }
    """
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=10, type=int)
    departments = userController.get_all_departments(page, limit)
    items = [{"department_name": department.department_name} for department in departments]
    return jsonify(
        {
            "departments": items
        }
    ), 200


# TODO REFACTOR OLD
@ADMIN_REQUEST_API.route('/department', methods=['POST'])
@admin_access
def add_new_department():
    """
    Request Body:
        {
          department_name: string
        }
    Result:
        {}
    """
    request_data = request.get_json()
    try:
        new_department = Department(department_name=request_data['department_name'], users=None)
    except KeyError:
        return jsonify({'error': 'Invalid request body'}), 400

    try:
        userController.add_new_department(new_department)
    except AlreadyExistsError:
        return jsonify({'error': 'Already exists department with such name'}), 400

    return jsonify({}), 200


# TODO REFACTOR OLD
@ADMIN_REQUEST_API.route('/department', methods=['DELETE'])
@admin_access
def delete_department():
    """
    Request Body:
        {
          department_name: string
        }
    Result:
        {}
    """
    request_data = request.get_json()
    try:
        new_department = Department(department_name=request_data['department_name'], users=None)
    except KeyError:
        return jsonify({'error': 'Invalid request body'}), 400

    try:
        userController.delete_department_by_name(new_department.department_name)
    except DepartmentNotFoundError:
        return jsonify({'error': 'Department with such name doesnt exist'}), 404

    return jsonify({}), 200


# TODO REFACTOR OLD
@ADMIN_REQUEST_API.route('/department/users', methods=['GET'])
@admin_access
def get_department_with_users():
    """
    Query:
        - query: name
    Result:
        {
            users: [{
              id: string
            }],
            department_name: string
        }
    """
    name = request.args.get('name', default=None, type=str)
    print(name)
    try:
        department = userController.get_department_by_name(name)
    except DepartmentNotFoundError:
        return jsonify({'error': 'Department with such name doesnt exist'}), 404
    users = [{"id": user.get_id(), "email": user.email} for user in department.users]
    return jsonify(
        {
            "department_name": department.department_name,
            "users": users
        }
    ), 200


# TODO REFACTOR OLD
@ADMIN_REQUEST_API.route('/department/users', methods=['POST'])
@admin_access
def add_users_to_department():
    """
    Query:
        - query: name
    Request Body:
    {
      users: [{
            id: string
            }]
    }
    Result:
        {
            users: [{
              id: string
            }],
            department_name: string
        }
    """
    name = request.args.get('name', default=None, type=str)
    request_data = request.get_json()
    try:
        users = request_data['users']
    except KeyError:
        return jsonify({'error': 'invalid request body'}), 400
    try:
        department = userController.add_users_to_department(name, users)
    except DepartmentNotFoundError:
        return jsonify({'error': 'Department with such name doesnt exist'}), 404
    except UserNotFoundError:
        return jsonify({'error': 'Such user not found'}), 404
    users = [{"id": user.get_id(), "email": user.email} for user in department.users]
    return jsonify(
        {
            "department_name": department.department_name,
            "users": users
        }
    ), 200


# TODO REFACTOR OLD
@ADMIN_REQUEST_API.route('/department/users', methods=['DELETE'])
@admin_access
def delete_user_from_department():
    """
    Query:
        - query: name
    Request Body:
    {
      users: [{
            id: string
            }]
    }
    Result:
        {
            users: [{
              id: string
            }],
            department_name: string
        }
    """
    name = request.args.get('name', default=None, type=str)
    request_data = request.get_json()
    try:
        users = request_data['users']
    except KeyError:
        return jsonify({'error': 'invalid request body'}), 400
    try:
        department = userController.delete_users_from_department(name, users)
    except DepartmentNotFoundError:
        return jsonify({'error': 'Department with such name doesnt exist'}), 404
    users = [{"id": user.get_id(), "email": user.email} for user in department.users]
    return jsonify(
        {
            "department_name": department.department_name,
            "users": users
        }
    ), 200


# TODO REFACTOR OLD
@ADMIN_REQUEST_API.route('/user', methods=['GET'])
@admin_access
def get_user_list():
    """
    Query:
        - query: page
        - query: limit
    Result:
        {
            users: [{
              id: string
            }]
        }
    """
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=10, type=int)
    users = userController.get_all_users(page, limit)
    items = [{"id": user.get_id(), "email": user.email} for user in users]
    return jsonify(
        {
            "users": items
        }
    ), 200
