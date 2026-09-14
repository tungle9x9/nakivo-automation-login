"""
Standardized WaitManager implementing explicit waits and polling logic.
"""
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class WaitManager:
    """Explicit wait wrapper providing clean condition evaluations."""

    def __init__(self, driver, default_timeout=10, poll_frequency=0.3):
        self.driver = driver
        self.default_timeout = default_timeout
        self.poll_frequency = poll_frequency

    def get_wait(self, timeout=None):
        t = self.default_timeout if timeout is None else timeout
        return WebDriverWait(self.driver, t, poll_frequency=self.poll_frequency)

    def until_visible(self, locator, timeout=None):
        return self.get_wait(timeout).until(EC.visibility_of_element_located(locator))

    def until_presence(self, locator, timeout=None):
        return self.get_wait(timeout).until(EC.presence_of_element_located(locator))

    def until_clickable(self, locator, timeout=None):
        return self.get_wait(timeout).until(EC.element_to_be_clickable(locator))

    def until_invisible(self, locator, timeout=None):
        return self.get_wait(timeout).until(EC.invisibility_of_element_located(locator))

    def until_url_contains(self, fraction, timeout=None):
        return self.get_wait(timeout).until(EC.url_contains(fraction))
