"""Module with base actions for tests"""

import pytest
from _pytest.fixtures import FixtureRequest
from selenium.webdriver.chrome.webdriver import WebDriver

from tests.test_ui.api_client import APIClient
from tests.test_ui.ui.pages.base_page import BasePage
from tests.test_ui.ui.pages.auth_page import AuthPage
from tests.test_ui.ui.pages.branch_page import BranchPage
from tests.test_ui.ui.pages.workspaces_page import WorkspacesPage


class BaseCase:
    """Class with basic actions for tests"""

    driver: WebDriver = None
    config = None
    logger = None
    base_page = None
    auth_page = None
    workspaces_page = None
    branch_page = None

    api_client = None

    @pytest.fixture(scope='function', autouse=True)
    def setup(self, driver, config, logger, request: FixtureRequest):
        """Setup all needed attributes of Base case"""

        self.driver = driver
        self.config = config
        self.logger = logger

        self.api_client: APIClient = (request.getfixturevalue('api_client'))

        self.base_page: BasePage = (request.getfixturevalue('base_page'))
        self.auth_page: AuthPage = (request.getfixturevalue('auth_page'))
        self.workspaces_page: WorkspacesPage = (request.getfixturevalue('workspaces_page'))
        self.branch_page: BranchPage = (request.getfixturevalue('branch_page'))
