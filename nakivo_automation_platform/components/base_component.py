"""
Base Component for Component Object Model (COM).
"""
from nakivo_automation_platform.core.wait.wait_manager import WaitManager
from nakivo_automation_platform.core.element.element_actions import ElementActions


class BaseComponent:
    """Base class for reusable UI fragments (Modals, Toasts, Tables, Headers)."""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WaitManager(driver)
        self.actions = ElementActions(driver, self.wait)
