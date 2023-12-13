from datetime import datetime

import pytest
from bcrypt import hashpw, gensalt

from tests.test_new_api.conftest_constants import *
from core.workspace_status import WorkSpaceStatus
from web_server import create_app


app_testing = create_app(True, db_uri=f'sqlite:///:memory:')


@pytest.fixture(scope='function', autouse=True)
def user1_workspaces():
    from app_db import get_current_db
    with app_testing.app_context():
        db_ = get_current_db(app_testing)
        from database.database import WorkspaceModel
        for workspace in [
            {'id': user1_workspace1_id, 'status': WorkSpaceStatus.Active.value, 'main_branch': user1_workspace1_master_id},
            {'id': user1_workspace2_id, 'status': WorkSpaceStatus.Archived.value, 'main_branch': user1_workspace2_master_id},
            {'id': user1_workspace3_id, 'status': WorkSpaceStatus.Deleted.value, 'main_branch': user1_workspace2_master_id},
        ]:
            test_workspace = WorkspaceModel(
                id=workspace['id'],
                title='Test Workspace',
                description='Test Description',
                status=workspace['status'],
                main_branch=workspace['main_branch'],
                user_id=casual_user_id
            )
            db_.session.add(test_workspace)
        db_.session.commit()
        return test_workspace


@pytest.fixture(scope='function', autouse=True)
def department():
    from app_db import get_current_db
    with app_testing.app_context():
        db_ = get_current_db(app_testing)
        from database.database import DepartmentModel
        test_department = DepartmentModel(
            name='Test Department',
        )
        db_.session.add(test_department)
        db_.session.commit()
        return test_department


@pytest.fixture(scope='function', autouse=True)
def admin_user():
    from app_db import get_current_db
    with app_testing.app_context():
        db_ = get_current_db(app_testing)
        from database.database import UserModel
        from core.role import Role
        test_user = UserModel(
            id=admin_id,
            email='admin@mail.com',
            username='admin',
            passwordHash=hashpw(str('password').encode(), gensalt()).decode(),
            role=Role.Admin
        )
        db_.session.add(test_user)
        db_.session.commit()
        return test_user


@pytest.fixture(scope='function', autouse=True)
def casual_user():
    from app_db import get_current_db
    with app_testing.app_context():
        db_ = get_current_db(app_testing)
        from database.database import UserModel
        from core.role import Role
        test_user = UserModel(
            email='user@mail.com',
            id=casual_user_id,
            username='user',
            passwordHash=hashpw(str('password').encode(), gensalt()).decode(),
            role=Role.Client
        )

        db_.session.add(test_user)
        db_.session.commit()
        return test_user


@pytest.fixture(scope='function')
def casual_user_2():
    from app_db import get_current_db
    with app_testing.app_context():
        db_ = get_current_db(app_testing)
        from database.database import UserModel
        from core.role import Role
        test_user = UserModel(
            email=casual_user_email2,
            id=casual_user_id2,
            username='user',
            passwordHash=hashpw(str('password').encode(), gensalt()).decode(),
            role=Role.Client
        )

        db_.session.add(test_user)
        db_.session.commit()
        return test_user


# @pytest.fixture(scope='function')
# def fill_db(admin_user, casual_user, department):
#     data = {
#         'admin': admin_user,
#         'user': casual_user,
#         'department': department,
#     }
#     return data


@pytest.fixture(scope='function')
def client():
    with app_testing.app_context():
        yield app_testing.test_client()
        app_testing.db.session.remove()
        app_testing.db.drop_all()
        app_testing.db.create_all()


@pytest.fixture
def app_client_admin(client):
    login_data = {'email': 'admin@mail.com', 'password': 'password'}
    client.put('/login', json=login_data)
    yield client


@pytest.fixture
def app_client_user(client):
    login_data = {'email': 'user@mail.com', 'password': 'password'}
    client.put('/login', json=login_data)
    yield client
