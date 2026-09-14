"""
Pure Page Object for NAKIVO Login screen.
Contains only UI interactions; no test assertions or business logic.
"""
from nakivo_automation_platform.pages.login.login_locators import LoginLocators
from nakivo_automation_platform.components.extjs_toast import ExtJsToastComponent
from nakivo_automation_platform.components.extjs_modal import ExtJsModalComponent
from nakivo_automation_platform.core.wait.wait_manager import WaitManager
from nakivo_automation_platform.core.element.element_actions import ElementActions


class LoginPage:
    """Pure UI representation of the login page."""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WaitManager(driver)
        self.actions = ElementActions(driver, self.wait)
        self.toast = ExtJsToastComponent(driver)
        self.recovery_modal = ExtJsModalComponent(driver)

    def load(self, url):
        """Navigate to URL and wait for username input visibility."""
        self.driver.get(url)
        self.wait.until_visible(LoginLocators.USERNAME_INPUT, timeout=25)

    def enter_username(self, username):
        """Type into username field."""
        self.actions.type_text(LoginLocators.USERNAME_INPUT, username)

    def enter_password(self, password):
        """Type into password field."""
        self.actions.type_text(LoginLocators.PASSWORD_INPUT, password)

    def click_sign_in(self):
        """Click sign in button."""
        self.actions.click(LoginLocators.SIGN_IN_BUTTON)

    def click_forgot_password(self):
        """Click 'Forgot the password?' link."""
        self.actions.click(LoginLocators.FORGOT_PASSWORD_LINK)

    def is_sign_in_enabled(self):
        """Check if sign in button is enabled in DOM."""
        return self.actions.is_enabled(LoginLocators.SIGN_IN_BUTTON)

    def is_password_masked(self):
        """Check type='password' on password input."""
        return self.actions.get_attribute(LoginLocators.PASSWORD_INPUT, "type") == "password"

    def is_loaded(self):
        """Verify presence of key inputs."""
        return (
            self.actions.is_displayed(LoginLocators.USERNAME_INPUT)
            and self.actions.is_displayed(LoginLocators.PASSWORD_INPUT)
            and self.actions.is_displayed(LoginLocators.SIGN_IN_BUTTON)
            and self.actions.is_displayed(LoginLocators.FORGOT_PASSWORD_LINK)
        )

    def get_email_validation_message(self):
        """Retrieve browser HTML5 validation message if present."""
        try:
            elem = self.wait.until_presence(LoginLocators.USERNAME_INPUT, timeout=2)
            return self.driver.execute_script("return arguments[0].validationMessage;", elem) or ""
        except Exception:
            return ""
