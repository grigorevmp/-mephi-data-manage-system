"""Pytest conftest module"""
import os
import shutil
import sys


from tests.test_ui.ui.fixtures import *


def pytest_addoption(parser):
    """Add options that could be used"""

    parser.addoption('--url', default='http://localhost:3000/')
    parser.addoption("--headless", action='store_true')
    parser.addoption('--debug_log', action='store_true')


def pytest_configure(config):
    """Configures base directory when starting tests"""

    if sys.platform.startswith('win'):
        base_dir = f'{os.getcwd()}\\tmp'
    else:
        base_dir = f'{os.getcwd()}/tmp'
    if not hasattr(config, 'workerinput'):
        if os.path.exists(base_dir):
            shutil.rmtree(base_dir)
        os.makedirs(base_dir)
    config.base_temp_dir = base_dir


@pytest.fixture(scope='session')
def config(request):
    """Makes config from entered options"""

    return {
        'url': request.config.getoption("--url"),
        'headless': request.config.getoption("--headless"),
        'debug': request.config.getoption("--debug_log")
    }


@pytest.fixture()
def driver(config):
    """Return driver with specified options"""

    driver = get_driver(config)
    driver.set_page_load_timeout(15)
    driver.get(config['url'])
    driver.maximize_window()
    yield driver
    driver.quit()


@pytest.fixture(scope='session')
def credentials():
    """Read credentials from file"""

    from tests.test_ui.constants import casual_user_1
    return casual_user_1


@pytest.fixture(scope='session')
def repo_root():
    """Return path from the root"""

    return os.path.abspath(os.path.join(__file__, os.path.pardir))


@pytest.fixture()
def file1_path(repo_root):
    return os.path.join(repo_root, 'test_data', 'test.txt')


@pytest.fixture()
def file2_path(repo_root):
    return os.path.join(repo_root, 'test_data', 'test_2.txt')


@pytest.fixture(scope='function')
def temp_dir(request):
    """Making path to temporary directory

    :param request:
    :return:
    """

    test_dir = os.path.join(request.config.base_temp_dir,
                            request._pyfuncitem.nodeid.replace(':', '-'))
    os.makedirs(test_dir)
    return test_dir
