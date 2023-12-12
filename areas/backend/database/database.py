from typing import List

from flask import current_app
from sqlalchemy.orm import Mapped

from app_db import get_current_db
from core.accesses import Access, AccessType
from core.role import Role

db = get_current_db(current_app)


class DepartmentModel(db.Model):
    __tablename__ = 'department'
    __table_args__ = {'extend_existing': True}

    id = db.Column('department_id', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('department_name', db.String, unique=True)


class UserModel(db.Model):
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}

    id = db.Column('user_id', db.String, primary_key=True)

    email = db.Column(db.String(100))
    passwordHash = db.Column(db.String(50))
    username = db.Column(db.String(200))
    role = db.Column(db.Enum(Role))

    department_id = db.Column(db.String, db.ForeignKey("department.department_id"))


class DocumentModel(db.Model):
    __tablename__ = "document"
    __table_args__ = {'extend_existing': True}

    id = db.Column('document_id', db.String, primary_key=True)

    name = db.Column(db.String)
    task_id = db.Column(db.String)
    modification_time = db.Column(db.Integer)
    file_id = db.Column(db.String)


class RequestModel(db.Model):
    __tablename__ = "request"
    __table_args__ = {'extend_existing': True}

    id = db.Column('request_id', db.String, primary_key=True)

    title = db.Column(db.String)
    description = db.Column(db.Integer)
    status = db.Column(db.String)

    source_branch_id = db.Column(db.String, db.ForeignKey("branch.branch_id"))
    target_branch_id = db.Column(db.String, db.ForeignKey("branch.branch_id"))


class BranchModel(db.Model):
    __tablename__ = "branch"
    __table_args__ = {'extend_existing': True}

    id = db.Column('branch_id', db.String, primary_key=True)

    name = db.Column('branch_name', db.String)
    parent_branch_id = db.Column(db.String)
    author = db.Column(db.String)
    status = db.Column(db.String)

    document_id = db.Column(db.String, db.ForeignKey("document.document_id"))
    workspace_id = db.Column(db.String, db.ForeignKey("workspace.workspace_id"))


class BaseAccessModel(db.Model):
    __tablename__ = 'access'
    __table_args__ = {'extend_existing': True}

    id = db.Column('access_id', db.Integer, primary_key=True, autoincrement=True)
    access_level = db.Column(db.Enum(Access))
    access_type = db.Column(db.Enum(AccessType))
    value = db.Column(db.String)

    workspace_id = db.Column(db.String, db.ForeignKey("workspace.workspace_id"))


class WorkspaceModel(db.Model):
    __tablename__ = "workspace"
    __table_args__ = {'extend_existing': True}

    id = db.Column('workspace_id', db.String, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    status = db.Column(db.String)
    main_branch = db.Column(db.String)

    user_id = db.Column(db.String, db.ForeignKey("user.user_id"))

    accesses: Mapped[List[BaseAccessModel]] = db.relationship(
        'BaseAccessModel',
        uselist=True,
        backref="workspace",
        cascade="all,delete"
    )

