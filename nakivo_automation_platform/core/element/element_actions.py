"""
ElementActions layer providing resilient DOM interactions, JS event dispatches, and diagnostics.
"""
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException
from nakivo_automation_platform.core.wait.wait_manager import WaitManager
from nakivo_automation_platform.core.logging.masked_logger import MaskedLogger

logger = MaskedLogger.get_logger("ElementActions")


class ElementActions:
    """Robust actions on web elements with auto-retry on stale references."""

    def __init__(self, driver, wait_manager: WaitManager):
        self.driver = driver
        self.wait = wait_manager

    def click(self, locator, timeout=None, allow_js_fallback=False):
        """
        Click element with multi-stage resilient interaction:
        1. Native W3C WebDriver click.
        2. Scroll into view and retry native click if intercepted by transient overlay.
        3. JavaScript click fallback permitted ONLY if allow_js_fallback=True (e.g. ExtJS mask),
           logging an explicit warning to prevent masking real UI defects.
        """
        element = self.wait.until_clickable(locator, timeout=timeout)
        try:
            element.click()
            return
        except (ElementClickInterceptedException, StaleElementReferenceException) as exc:
            # Stage 2: Scroll into view to clear sticky headers/overlays and re-attempt native click
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", element)
                element.click()
                return
            except Exception:
                pass

            # Stage 3: Governed JS fallback policy
            if allow_js_fallback:
                logger.warning(
                    f"[WARNING] Native click intercepted for {locator} ({type(exc).__name__}). "
                    f"Executing JavaScript click fallback as permitted override."
                )
                self.driver.execute_script("arguments[0].click();", element)
            else:
                logger.error(f"[ERROR] Native click intercepted for {locator}. JS fallback disabled by policy.")
                raise exc

    def type_text(self, locator, text, clear_first=True, timeout=None):
        """Type into an input field, dispatching input/change events for reactive/ExtJS forms."""
        element = self.wait.until_visible(locator, timeout=timeout)
        if clear_first:
            element.clear()
            if element.get_attribute("value"):
                self.driver.execute_script("arguments[0].value = '';", element)
        if text:
            element.send_keys(text)
            self.driver.execute_script(
                "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));"
                "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
                element
            )

    def get_text(self, locator, timeout=None):
        """Retrieve innerText of element."""
        element = self.wait.until_visible(locator, timeout=timeout)
        return element.text.strip()

    def get_attribute(self, locator, attribute_name, timeout=None):
        """Retrieve attribute value."""
        element = self.wait.until_presence(locator, timeout=timeout)
        return element.get_attribute(attribute_name)

    def is_displayed(self, locator, timeout=2):
        """Check visibility within timeout seconds."""
        try:
            return self.wait.until_visible(locator, timeout=timeout).is_displayed()
        except Exception:
            return False

    def is_enabled(self, locator, timeout=2):
        """Check if an element is enabled and not disabled via attribute or class."""
        try:
            element = self.wait.until_presence(locator, timeout=timeout)
            disabled_attr = element.get_attribute("disabled")
            aria_disabled = element.get_attribute("aria-disabled")
            class_name = element.get_attribute("class") or ""

            if disabled_attr in (True, "true", "disabled"):
                return False
            if aria_disabled == "true":
                return False
            if any(c in class_name.lower().split() for c in ("disabled", "x-btn-disabled")):
                return False
            return element.is_enabled()
        except Exception:
            return False
