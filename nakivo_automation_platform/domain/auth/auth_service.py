"""
Domain Service orchestrating authentication workflows and business interactions.
Strictly follows Dependency Injection: receives driver and runtime config.
Zero arbitrary thread sleeps; all dynamic synchronization is wait-governed.
"""
from nakivo_automation_platform.models.user_credential import UserCredential
from nakivo_automation_platform.pages.login.login_page import LoginPage
from nakivo_automation_platform.components.extjs_toast import ExtJsToastComponent
from nakivo_automation_platform.components.extjs_modal import ExtJsModalComponent
from nakivo_automation_platform.core.logging.masked_logger import MaskedLogger

logger = MaskedLogger.get_logger("AuthService")


class AuthService:
    """Business operations for authentication and security validation."""

    def __init__(self, driver, config):
        self.driver = driver
        self.config = config
        self.login_page = LoginPage(driver)
        self.toast = ExtJsToastComponent(driver)
        self.recovery_modal = ExtJsModalComponent(driver)

    def open_login_page(self):
        """Navigate to configured login URL."""
        logger.info(f"Opening login page at {self.config.base_url}")
        self.login_page.load(self.config.base_url)

    def is_login_page_loaded(self) -> bool:
        """Check if login page elements are available."""
        return self.login_page.is_loaded()

    def login_as(self, user: UserCredential):
        """Execute full authentication workflow for a given user."""
        logger.info(f"Authenticating user '{user.username}' (scenario: {user.scenario})")
        self.open_login_page()
        self.login_page.enter_username(user.username)
        self.login_page.enter_password(user.password)
        self.login_page.click_sign_in()

    def attempt_invalid_login(self, user: UserCredential) -> str:
        """Submit credentials expecting a rejection toast or validation message."""
        logger.info(f"Attempting negative login for scenario: {user.scenario}")
        self.open_login_page()
        self.login_page.enter_username(user.username)
        self.login_page.enter_password(user.password)
        if self.login_page.is_sign_in_enabled():
            self.login_page.click_sign_in()
        return self.toast.get_visible_message()

    def is_sign_in_button_enabled(self) -> bool:
        """Query if sign-in button is enabled."""
        return self.login_page.is_sign_in_enabled()

    def is_password_masked(self) -> bool:
        """Verify that entered password characters are visually masked."""
        return self.login_page.is_password_masked()

    def request_password_recovery(self, email: str) -> str:
        """Initiate password recovery through modal workflow."""
        logger.info(f"Requesting password recovery for '{email}'")
        if not self.recovery_modal.is_open(timeout=2):
            self.login_page.click_forgot_password()
        self.recovery_modal.enter_recovery_email(email)
        self.recovery_modal.submit()
        return self.recovery_modal.get_status_message()

    def is_recovery_modal_accessible(self) -> bool:
        """Check if recovery modal opens when clicking forgot password link."""
        self.open_login_page()
        self.login_page.click_forgot_password()
        return self.recovery_modal.is_open(timeout=5)
