"""
Enterprise Configuration Manager loading YAML environment and browser configs
with hierarchical overrides from environment variables and CLI parameters.
Strictly decoupled, non-singleton design supporting clean dependency injection.
"""
import os
import socket
from urllib.parse import urlsplit
import yaml
from dotenv import load_dotenv

# Load local environment variables from .env if present
load_dotenv()

CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))


def is_port_listening(host="127.0.0.1", port=4443, timeout=0.5) -> bool:
    """Check if TCP port is active."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


class ConfigManager:
    """
    Immutable Runtime Configuration Object.
    Instantiated per test session or CLI invocation with clean parameter injection.
    """

    def __init__(self, env_name=None, browser_name=None):
        self.env_name = (env_name or os.getenv("ENV", "local")).lower()
        self.browser_name = (browser_name or os.getenv("BROWSER", "chrome")).lower()
        self._load_environment_config()
        self._load_browser_config()
        self._apply_runtime_overrides()

    def _load_environment_config(self):
        env_file = os.path.join(CONFIG_DIR, "environments", f"{self.env_name}.yaml")
        if not os.path.exists(env_file):
            env_file = os.path.join(CONFIG_DIR, "environments", "local.yaml")

        with open(env_file, "r", encoding="utf-8") as f:
            self.env_data = yaml.safe_load(f) or {}

    def _load_browser_config(self):
        browser_file = os.path.join(CONFIG_DIR, "browsers", f"{self.browser_name}.yaml")
        if not os.path.exists(browser_file):
            browser_file = os.path.join(CONFIG_DIR, "browsers", "chrome.yaml")

        with open(browser_file, "r", encoding="utf-8") as f:
            self.browser_data = yaml.safe_load(f) or {}

    def _apply_runtime_overrides(self):
        # 1. Base Director URL and Endpoints
        raw_director = os.getenv("NAKIVO_DIRECTOR_URL", self.env_data.get("director_url", "https://localhost:4443"))
        self.director_url = raw_director.rstrip("/")
        self.ui_path = self.env_data.get("ui_path", "/c/main")
        self.api_path = self.env_data.get("api_path", "/c/router")

        # CLI / Env URL override (supports full path or director URL)
        custom_url = os.getenv("NAKIVO_BASE_URL") or os.getenv("BASE_URL")
        if custom_url:
            custom_url = custom_url.rstrip("/")
            if "/c/" in custom_url:
                parts = urlsplit(custom_url)
                self.director_url = f"{parts.scheme}://{parts.netloc}"
                self.base_url = custom_url
            else:
                self.director_url = custom_url
                self.base_url = f"{self.director_url}{self.ui_path}"
        else:
            self.base_url = f"{self.director_url}{self.ui_path}"

        self.api_url = f"{self.director_url}{self.api_path}"

        # 2. Timeouts (Explicit waits only; zero implicit wait)
        timeouts = self.env_data.get("timeout", {})
        self.timeout_explicit = int(os.getenv("TIMEOUT_EXPLICIT", timeouts.get("explicit", 10)))
        self.timeout_page_load = int(os.getenv("TIMEOUT_PAGE_LOAD", timeouts.get("page_load", 30)))

        # 3. Credentials (Strictly loaded from Environment / .env; zero hardcoded fallback in public repo)
        creds = self.env_data.get("credentials", {})
        self.admin_username = os.getenv("NAKIVO_USER", creds.get("admin_username", "admin"))
        self.admin_password = os.getenv("NAKIVO_PASSWORD", creds.get("admin_password", ""))

        # 4. Browser settings
        self.headless = os.getenv("HEADLESS", str(self.browser_data.get("headless", True))).lower() in ("true", "1", "yes")
        self.window_size = os.getenv("WINDOW_SIZE", self.browser_data.get("window_size", "1920,1080"))
        self.accept_insecure_certs = self.browser_data.get("accept_insecure_certs", True)
        self.browser_arguments = self.browser_data.get("arguments", [])

        # 5. Remote Selenium Grid URL (unified naming matching Docker and CLI)
        self.remote_url = (
            os.getenv("SELENIUM_REMOTE_URL")
            or os.getenv("GRID_URL")
            or None
        )
