"""
DriverFactory managing WebDriver instantiations across local and remote grid environments.
Ensures thread-safety for parallel execution via pytest-xdist.
"""
from selenium import webdriver
from nakivo_automation_platform.core.driver.capabilities import CapabilitiesBuilder
from nakivo_automation_platform.core.logging.masked_logger import MaskedLogger

logger = MaskedLogger.get_logger("DriverFactory")


class DriverFactory:
    """Factory responsible for WebDriver lifecycle and grid dispatch."""

    @staticmethod
    def create_driver(config):
        browser = config.browser_name.lower()
        remote_url = config.remote_url

        logger.info(f"Initializing WebDriver for browser='{browser}' (headless={config.headless})")

        if remote_url:
            logger.info(f"Connecting to remote Selenium Grid at: {remote_url}")
            if browser == "firefox":
                options = CapabilitiesBuilder.build_firefox_options(config)
            elif browser == "edge":
                options = CapabilitiesBuilder.build_edge_options(config)
            else:
                options = CapabilitiesBuilder.build_chrome_options(config)
            return webdriver.Remote(command_executor=remote_url, options=options)

        # Local Execution
        if browser == "edge":
            options = CapabilitiesBuilder.build_edge_options(config)
            driver = webdriver.Edge(options=options)
        elif browser == "firefox":
            options = CapabilitiesBuilder.build_firefox_options(config)
            driver = webdriver.Firefox(options=options)
        else:  # Default to Chrome
            options = CapabilitiesBuilder.build_chrome_options(config)
            driver = webdriver.Chrome(options=options)

        if not config.headless:
            try:
                driver.maximize_window()
            except Exception:
                pass


        # Strict SDET contract: Zero implicit wait. All dynamic synchronization is governed by WaitManager (WebDriverWait).
        driver.set_page_load_timeout(config.timeout_page_load)

        return driver
