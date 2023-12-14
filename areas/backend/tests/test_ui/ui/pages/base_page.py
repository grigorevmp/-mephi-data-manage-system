"""Module of base page and its methods"""

from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BasePage:
    """Basic page object class"""

    CLICK_RETRY = 5

    def __init__(self, driver, logger):
        """Init needed attributes"""

        self.driver = driver
        self.logger = logger

    def wait(self, timeout=None):
        """Waits until the timeout expires

        :param timeout:
        """

        if timeout is None:
            timeout = 10
        self.logger.debug(f'Waiting with timeout={timeout}')
        return WebDriverWait(self.driver, timeout=timeout)

    def find(self, locator, timeout=None):
        """Finds specified element on page

        :param locator:
        :param timeout:
        """

        self.logger.debug(f'Finding element with locator={locator}, timeout={timeout}')
        return self.wait(timeout).until(EC.visibility_of_element_located(locator))

    def find_file_input(self, locator, timeout=None):
        """Finds specified file input

        :param locator:
        :param timeout:
        """

        self.logger.debug(f'Finding file input element with locator={locator}, timeout={timeout}')
        return self.wait(timeout).until(EC.presence_of_element_located(locator))

    def click_btn(self, locator, timeout=None):
        """Clicking button with specified locator

        :param locator:
        :param timeout:
        """

        self.logger.debug(f'Click on page with locator={locator}, timeout={timeout}')
        for i in range(self.CLICK_RETRY):
            try:
                btn = self.find(locator, timeout)
                self.wait(timeout).until(EC.element_to_be_clickable(btn)).click()
                return
            except StaleElementReferenceException:
                self.logger.warning(
                    f'StaleElementReferenceException caught when clicking, number of try={i+1}'
                )
                if i == self.CLICK_RETRY - 1:
                    raise
            except ElementClickInterceptedException:
                self.logger.warning(
                    f'ElementClickInterceptedException caught when clicking, number of try={i+1}'
                )
                if i == self.CLICK_RETRY - 1:
                    raise
