"""Module of element's locators"""

from selenium.webdriver.common.by import By


class AuthPageLocators:
    """Locators of auth page"""

    LOGIN_INPUT = (By.XPATH, '//*[@id="email"]')
    PASSWORD_INPUT = (By.XPATH, '//*[@id="password"]')
    SIGN_IN_BUTTON = (By.XPATH, '//*[@id="root"]/div/div/form/button[1]')
    SIGN_UP_BUTTON = (By.XPATH, '//*[@id="root"]/div/div/form/button[2]')


class WorkspacesPageLocators:

    ADD_WS_BUTTON = (By.XPATH, '//button[@class="add-workspace"]')
    TITLE_INPUT = (By.XPATH, '//input[@id="title"]')
    DESCRIPTION_INPUT = (By.XPATH, '//input[@id="description"]')
    FILE_INPUT = (By.XPATH, '//input[@id="fileUpload"]')
    SUBMIT_BUTTON = (By.XPATH, '//button[@class="add-workspace-button"]')


class BranchPageLocators:

    VIEW_FILE_BUTTON = (By.XPATH, '//button[@class="document-action-bottom" and text()="Просмотр"]')
    EDIT_FILE_BUTTON = (By.XPATH, '//button[@class="document-action-bottom" and text()="Загрузить"]')
    FILE_INPUT = (By.XPATH, '//input[@id="fileUpload"]')
    SUBMIT_BUTTON = (By.XPATH, '//button[@class="add-workspace-button"]')
    ADD_BRANCH_BUTTON = (By.XPATH, '//button[@class="branch-add"]')
    TITLE_INPUT = (By.XPATH, '//input[@id="title"]')
    DESCRIPTION_INPUT = (By.XPATH, '//input[@id="description"]')
    ADD_REQUEST_BUTTON = (By.XPATH, '//button[@class="add-workspace"]')
