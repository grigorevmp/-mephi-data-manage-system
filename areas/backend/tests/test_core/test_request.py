import uuid

import pytest

from core.request import Request
from core.request_status import RequestStatus


@pytest.fixture()
def request_fixture():
    return Request(
        title="title",
        description="description",
        status=RequestStatus.Open,
        source_branch_id=source_branch_id,
        target_branch_id=target_branch_id,
        _id=test_id
    )


source_branch_id = uuid.uuid4()
target_branch_id = uuid.uuid4()
test_id = uuid.uuid4()


class TestRequest:

    def test_id_property(self, request_fixture):
        assert request_fixture.get_id() == test_id

    def test_title_property(self, request_fixture):
        request_fixture.title = "3453"
        assert request_fixture.title == "3453"

        with pytest.raises(TypeError):
            request_fixture.title = 435

    def test_description_property(self, request_fixture):
        request_fixture.description = "3453"
        assert request_fixture.description == "3453"

        with pytest.raises(TypeError):
            request_fixture.description = 435

    def test_status_property(self, request_fixture):
        request_fixture.status = RequestStatus.Merged
        assert request_fixture.status == RequestStatus.Merged

        with pytest.raises(TypeError):
            request_fixture.status = "435"

    def test_source_branch_id_property(self, request_fixture):
        new_id = uuid.uuid4()

        request_fixture.source_branch_id = new_id
        assert request_fixture.source_branch_id == new_id

    def test_target_branch_id_property(self, request_fixture):
        new_id = uuid.uuid4()

        request_fixture.target_branch_id = new_id
        assert request_fixture.target_branch_id == new_id
