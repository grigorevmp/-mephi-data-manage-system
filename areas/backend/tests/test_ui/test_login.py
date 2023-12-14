import time

import pytest

from tests.test_ui.base_actions import BaseCase


class TestLogin(BaseCase):

    def test_success(self, credentials):
        self.auth_page.login(*credentials)
        assert 'workspaces' in self.driver.current_url
