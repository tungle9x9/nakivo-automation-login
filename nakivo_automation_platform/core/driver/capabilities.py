"""
Browser capabilities and options factory.
Configures SSL bypass, headless modes, performance flags, and window sizing.
"""
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions


class CapabilitiesBuilder:
    """Constructs tailored WebDriver options for each browser engine."""

    @staticmethod
    def build_chrome_options(config):
        options = ChromeOptions()
        options.accept_insecure_certs = config.accept_insecure_certs

        # Add arguments from configuration
        for arg in config.browser_arguments:
            options.add_argument(arg)

        options.add_argument(f"--window-size={config.window_size}")

        if config.headless:
            options.add_argument("--headless=new")

        # Performance optimizations
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        return options

    @staticmethod
    def build_edge_options(config):
        options = EdgeOptions()
        options.accept_insecure_certs = config.accept_insecure_certs
        options.add_argument("--ignore-certificate-errors")
        options.add_argument(f"--window-size={config.window_size}")
        if config.headless:
            options.add_argument("--headless=new")
        return options

    @staticmethod
    def build_firefox_options(config):
        options = FirefoxOptions()
        options.accept_insecure_certs = config.accept_insecure_certs
        if config.headless:
            options.add_argument("--headless")
        return options
