import datetime
import uuid

import pytest

from core.document import Document


@pytest.fixture()
def file():
    return Document(
        name="Test Document",
        task_id=uuid.uuid4(),
        file=uuid.uuid4(),
        time=datetime.datetime.now(),
    )


class TestDocument:

    def test_document_property(self, file):
        file.name = "New name"
        assert file.name == "New name"

        with pytest.raises(TypeError):
            file.name = 42

    def test_task_id_property(self, file):
        _id = uuid.uuid4()

        file.task_id = _id
        assert file.task_id == _id

        with pytest.raises(TypeError):
            file.task_id = "test"

    def test_time_property(self, file):
        time = datetime.datetime.now()

        file.time = time
        assert file.time == time

        with pytest.raises(TypeError):
            file.task_id = "test"

    def test_file_property(self, file):
        _id = uuid.uuid4()

        file.file = _id
        assert file.file == _id

        with pytest.raises(TypeError):
            file.file = "sdgsdg"