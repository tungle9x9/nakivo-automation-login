"""
Allure & HTML reporting adapter providing step logging and automatic screenshot capture per step.
"""
import base64
from contextlib import contextmanager
import allure
from allure_commons.types import AttachmentType


class AllureReporter:
    """Helper for attaching diagnostics and screenshots to Allure reports."""

    @staticmethod
    def attach_screenshot(driver, name="screenshot"):
        """Capture and attach a screenshot to the current Allure test result."""
        try:
            png_bytes = driver.get_screenshot_as_png()
            allure.attach(
                png_bytes,
                name=name,
                attachment_type=AttachmentType.PNG
            )
            return png_bytes
        except Exception:
            return None

    @staticmethod
    def attach_text(content, name="details"):
        """Attach textual logs or metadata to Allure."""
        try:
            allure.attach(
                str(content),
                name=name,
                attachment_type=AttachmentType.TEXT
            )
        except Exception:
            pass


class StepTracker:
    """Manages step execution, creating Allure steps and capturing screenshots for both Allure and HTML reports."""

    def __init__(self, driver, item):
        self.driver = driver
        self.item = item
        if not hasattr(item, "_step_screenshots"):
            item._step_screenshots = []

    def __call__(self, title: str):
        return self._step_ctx(title)

    @contextmanager
    def _step_ctx(self, title: str):
        with allure.step(title):
            yield
            self.capture(title)

    def capture(self, title: str):
        """Capture and store screenshot for the current step."""
        try:
            png_bytes = self.driver.get_screenshot_as_png()
            allure.attach(
                png_bytes,
                name=f"{title} - Screenshot",
                attachment_type=AttachmentType.PNG
            )
            b64 = base64.b64encode(png_bytes).decode("utf-8")
            self.item._step_screenshots.append((title, b64))
        except Exception:
            pass
