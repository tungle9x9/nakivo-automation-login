"""
Component Object for ExtJS Toast, Notification banners, and Alert messages.
"""
import time
from selenium.webdriver.common.by import By
from nakivo_automation_platform.components.base_component import BaseComponent


class ExtJsToastComponent(BaseComponent):
    """Encapsulates system notifications, error banners, and floating toast alerts."""

    TOAST_SELECTORS = [
        (By.CSS_SELECTOR, ".notification-message-content"),
        (By.CSS_SELECTOR, ".alert-danger"),
        (By.CSS_SELECTOR, ".error-message"),
        (By.CSS_SELECTOR, ".login-error"),
        (By.XPATH, "//div[contains(@class, 'notification') and not(self::script)]"),
        (By.XPATH, "//*[contains(text(), 'Incorrect') or contains(text(), 'credentials') or contains(text(), 'Invalid')]"),
    ]

    def get_visible_message(self, timeout=4):
        """Poll and return visible notification text."""
        start = time.time()
        while time.time() - start < timeout:
            for by, val in self.TOAST_SELECTORS:
                try:
                    elems = self.driver.find_elements(by, val)
                    for el in elems:
                        if el.is_displayed():
                            txt = el.text.strip()
                            if txt:
                                return txt
                except Exception:
                    pass
            time.sleep(0.3)
        return ""

    def is_visible(self, timeout=4):
        """Check if any notification or error is currently displayed."""
        return len(self.get_visible_message(timeout=timeout)) > 0
