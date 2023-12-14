"""Module of workspaces page and its methods"""
import time

from tests.test_ui.ui.locators import WorkspacesPageLocators
from tests.test_ui.ui.pages.base_page import BasePage


class WorkspacesPage(BasePage):
    """Workspaces page object class"""

    locators = WorkspacesPageLocators()

    def __init__(self, driver, logger):
        super().__init__(driver, logger)
        self.driver.get('http://localhost:3000/workspaces')

    def add_workspace(self, file1_path, title: str = "Test", description: str = "Test description"):
        self.logger.info(f'Creating workspace {title}')
        self.click_btn(self.locators.ADD_WS_BUTTON)
        title_input = self.find(self.locators.TITLE_INPUT)
        title_input.clear()
        self.logger.debug(f'Input workspace title: {title}')
        title_input.send_keys(title)
        description_input = self.find(self.locators.DESCRIPTION_INPUT)
        description_input.clear()
        self.logger.debug(f'Input workspace description: {description}')
        description_input.send_keys(description)

        file_input = self.find_file_input(self.locators.FILE_INPUT)
        self.logger.debug(f'Uploading file {file1_path}')
        file_input.send_keys(file1_path)
        self.click_btn(self.locators.SUBMIT_BUTTON)
        time.sleep(3)
        self.logger.info(f'Workspace {title} created successfully')
        return title
