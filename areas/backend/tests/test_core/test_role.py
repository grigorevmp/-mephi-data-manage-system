import pytest

from core.role import Role


class TestRole:

    def test_get_role(self):
        assert Role.get_enum_from_value(1) == Role.Admin
        assert Role.get_enum_from_value(2) == Role.Client
        with pytest.raises(NotImplementedError):
            a = Role.get_enum_from_value(3)
