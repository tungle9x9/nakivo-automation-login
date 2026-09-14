"""
Domain Service orchestrating post-login Dashboard operations.
"""
from nakivo_automation_platform.pages.dashboard.dashboard_page import DashboardPage
from nakivo_automation_platform.core.logging.masked_logger import MaskedLogger

logger = MaskedLogger.get_logger("DashboardService")


class DashboardService:
    """Business operations for authenticated dashboard interactions."""

    def __init__(self, driver):
        self.driver = driver
        self.dashboard_page = DashboardPage(driver)

    def is_operational(self, timeout=10) -> bool:
        """Verify that the system has transitioned into operational status."""
        logger.info("Verifying operational dashboard readiness...")
        return self.dashboard_page.is_operational(timeout=timeout)

    def get_active_username(self) -> str:
        """Retrieve the identity displayed in the user profile."""
        username = self.dashboard_page.get_displayed_username()
        logger.info(f"Active authenticated user profile: '{username}'")
        return username

    def logout(self):
        """Perform application logout."""
        logger.info("Logging out from active session...")
        self.dashboard_page.click_logout()
