"""UI fixtures"""

import logging
import os

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from tests.test_ui.api_client import APIClient
from tests.test_ui.ui.pages.auth_page import AuthPage
from tests.test_ui.ui.pages.base_page import BasePage
from tests.test_ui.ui.pages.branch_page import BranchPage
from tests.test_ui.ui.pages.workspaces_page import WorkspacesPage


def get_driver(config):
    """Return driver with specified config"""

    options = Options()
    if config['headless']:
        options.add_argument("--headless=new")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager(
        driver_version='120.0.6099.109'
    ).install()), options=options)
    return driver


@pytest.fixture(scope='session')
def api_client(credentials, config, logger):
    api_client = APIClient(base_url=config['url'], login=credentials[0], password=credentials[1], logger=logger)
    api_client.post_login()
    return api_client


@pytest.fixture(scope='session')
def cookies(credentials, config, logger):
    """Return all cookies from authorized session

    :param credentials:
    :param config:
    :param logger:
    :return: session cookies
    """

    api_client = APIClient(base_url=config['url'], login=credentials[0], password=credentials[1], logger=logger)

    api_client.post_registration()
    cookie = api_client.post_login().headers.get('Set-Cookie')
    return [{'name': 'token', 'value': cookie.split('token=')[1].split('; Path=/')[0], 'path': '/'}]


@pytest.fixture(scope='function')
def auto_auth(auth_page, cookies):
    """Return authorized auth page object"""

    for cookie in cookies:
        auth_page.driver.add_cookie(cookie)
    auth_page.driver.refresh()
    return auth_page


@pytest.fixture
def base_page(driver, logger):
    """Return base page object"""

    return BasePage(driver=driver, logger=logger)


@pytest.fixture
def auth_page(driver, logger):
    """Return auth page object"""

    return AuthPage(driver=driver, logger=logger)


@pytest.fixture
def workspaces_page(driver, logger):
    """Return auth page object"""

    return WorkspacesPage(driver=driver, logger=logger)


@pytest.fixture
def branch_page(driver, logger):
    """Return auth page object"""

    return BranchPage(driver=driver, logger=logger)


@pytest.fixture(scope='session')
def logger(request, config):
    """Writing logs to specified files

    :param request:
    :param config:
    :return:
    """

    log_formatter = logging.Formatter(
        '%(asctime)s - %(filename)s - %(levelname)s - %(message)s')
    log_file = os.path.join(request.config.base_temp_dir, 'test.log')
    log_level = logging.DEBUG if config['debug'] else logging.INFO

    file_handler = logging.FileHandler(log_file, 'w')
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(log_level)

    log = logging.getLogger('test')
    log.propagate = False
    log.setLevel(log_level)
    log.handlers.clear()
    log.addHandler(file_handler)

    yield log

    for handler in log.handlers:
        handler.close()
