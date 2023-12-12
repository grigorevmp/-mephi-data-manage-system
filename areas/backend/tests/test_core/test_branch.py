import datetime
import uuid

import pytest

from areas.backend.core.branch import Branch
from areas.backend.core.branch_status import BranchStatus
from areas.backend.core.document import Document


@pytest.fixture()
def file():
    return Document(
        name="Test Document",
        task_id=uuid.uuid4(),
        file=uuid.uuid4(),
        time=datetime.datetime.now(),
    )


author_id = uuid.uuid4()
parent_id = uuid.uuid4()
test_id = uuid.uuid4()


@pytest.fixture(scope='function')
def branch(file):
    return Branch(
        _id=test_id,
        name="test_space",
        author=author_id,
        status=BranchStatus.Active.value,
        parent=parent_id,
        document=file,
    )


class TestBranch:

    def test_id_property(self, branch):
        assert branch.get_id() == test_id
        assert branch.get_parent_id() == parent_id

    def test_document_property(self, branch, file):
        branch.document = file
        assert branch.document == file

        with pytest.raises(TypeError):
            branch.document = "3453"

    def test_author_property(self, branch):
        new_id = uuid.uuid4()

        branch.author = new_id
        assert branch.author == new_id

        with pytest.raises(TypeError):
            branch.author = 534

    def test_file_property(self, branch):
        branch.name = "34"
        assert branch.name == "34"

        with pytest.raises(TypeError):
            branch.name = 34
