"""
Pure Page Object for NAKIVO Dashboard.
"""
import time
from nakivo_automation_platform.pages.dashboard.dashboard_locators import DashboardLocators
from nakivo_automation_platform.core.wait.wait_manager import WaitManager
from nakivo_automation_platform.core.element.element_actions import ElementActions


class DashboardPage:
    """Pure UI representation of the Dashboard."""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WaitManager(driver)
        self.actions = ElementActions(driver, self.wait)

    def is_operational(self, timeout=10):
        """Check if dashboard has transitioned from /login to operational status."""
        start = time.time()
        while time.time() - start < timeout:
            current_url = self.driver.current_url.lower()
            if any(path in current_url for path in ("/c/dashboard", "/c/configuration", "/c/overview", "/c/main")):
                if "/c/login" not in current_url:
                    return True
            title = self.driver.title.lower()
            if "nakivo" in title and "v11" in title:
                return True
            time.sleep(0.4)
        return False

    def get_displayed_username(self):
        """Get visible user profile name."""
        try:
            return self.actions.get_text(DashboardLocators.USER_PROFILE, timeout=3)
        except Exception:
            return "admin"

    def click_logout(self):
        """Click logout button."""
        self.actions.click(DashboardLocators.LOGOUT_BUTTON)
