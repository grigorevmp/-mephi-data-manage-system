import time

from tests.test_ui.ui.locators import BranchPageLocators
from tests.test_ui.ui.pages.base_page import BasePage


class BranchPage(BasePage):
    """Workspaces page object class"""

    locators = BranchPageLocators()

    def open_branch_page(self, workspace_id, branch_id):
        location = f'http://localhost:3000/branch/{workspace_id}/{branch_id}'
        self.driver.get(location)
        time.sleep(1)

    def view_file(self):
        self.logger.info(f'Opening file on page: {self.driver.current_url}')
        self.click_btn(self.locators.VIEW_FILE_BUTTON)
        time.sleep(1)

    def edit_file(self, file):
        self.logger.info(f'Uploading new file: {file} on page: {self.driver.current_url}')
        self.click_btn(self.locators.EDIT_FILE_BUTTON)
        file_input = self.find_file_input(self.locators.FILE_INPUT)
        self.logger.debug(f'Uploading file {file}')
        file_input.send_keys(file)
        self.click_btn(self.locators.SUBMIT_BUTTON)
        time.sleep(3)

    def add_branch(self, branch_name):
        self.logger.info(f'Adding new branch on page: {self.driver.current_url}')
        self.click_btn(self.locators.ADD_BRANCH_BUTTON)
        branch_title_input = self.find_file_input(self.locators.TITLE_INPUT)
        self.logger.debug(f'Adding new branch: {branch_name}')
        branch_title_input.clear()
        self.logger.debug(f'Input branch title: {branch_name}')
        branch_title_input.send_keys(branch_name)
        self.click_btn(self.locators.SUBMIT_BUTTON)
        time.sleep(3)

    def add_request(self, request_title, request_description):
        self.logger.info(f'Adding new request on page: {self.driver.current_url}')
        self.click_btn(self.locators.ADD_REQUEST_BUTTON)
        request_title_input = self.find_file_input(self.locators.TITLE_INPUT)
        request_title_input.clear()
        self.logger.debug(f'Input branch title: {request_title}')
        request_title_input.send_keys(request_title)
        request_description_input = self.find_file_input(self.locators.DESCRIPTION_INPUT)
        request_description_input.clear()
        self.logger.debug(f'Input branch description: {request_description}')
        request_description_input.send_keys(request_description)
        self.click_btn(self.locators.SUBMIT_BUTTON)
        time.sleep(3)
