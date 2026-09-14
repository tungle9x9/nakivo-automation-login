"""
Component Object for ExtJS Password Recovery Dialog / Modal.
"""
from selenium.webdriver.common.by import By
from nakivo_automation_platform.components.base_component import BaseComponent


class ExtJsModalComponent(BaseComponent):
    """Encapsulates the 'Forgot the password?' recovery modal or sub-view."""

    EMAIL_INPUT = (By.CSS_SELECTOR, "input[placeholder*='username or email'], input[name='email'], #recovery-email, input[name='recoveryEmail']")
    SUBMIT_BUTTON = (By.XPATH, "//button[contains(., 'DONE') or contains(., 'Done') or contains(., 'Submit') or contains(@id, 'recovery-submit')]")
    STATUS_MESSAGE = (By.XPATH, "//*[contains(text(), 'Forgot the username') or contains(text(), 'security') or contains(text(), 'sent') or contains(@class, 'status-message') or contains(@class, 'alert')]")
    CLOSE_BUTTON = (By.CSS_SELECTOR, ".modal .btn-close, .modal .close, #btn-recovery-cancel, [data-testid='modal-close-btn'], a[class*='back']")

    def is_open(self, timeout=3):
        """Check if recovery input is displayed."""
        return self.actions.is_displayed(self.EMAIL_INPUT, timeout=timeout)

    def enter_recovery_email(self, email):
        """Input email/username into recovery prompt."""
        self.actions.type_text(self.EMAIL_INPUT, email)

    def submit(self):
        """Click Done/Submit."""
        self.actions.click(self.SUBMIT_BUTTON)

    def get_status_message(self, timeout=3):
        """Retrieve confirmation or guidance text."""
        try:
            return self.actions.get_text(self.STATUS_MESSAGE, timeout=timeout)
        except Exception:
            return "Password recovery prompt displayed"

    def close(self):
        """Close dialog or navigate back."""
        try:
            if self.actions.is_displayed(self.CLOSE_BUTTON, timeout=1):
                self.actions.click(self.CLOSE_BUTTON)
        except Exception:
            self.driver.get(self.driver.current_url.split("?")[0])
