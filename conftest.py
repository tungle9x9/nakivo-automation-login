"""
Pytest configuration, worker isolation, and lifecycle fixtures for the SDET Test Automation Platform.
Follows pure Dependency Injection: injects platform_config into services and drivers.
Zero sys.modules hacks, zero global singleton dependencies, and zero arbitrary sleeps.
"""
import os
import pytest
from nakivo_automation_platform.config.config_loader import ConfigManager
from nakivo_automation_platform.core.driver.driver_factory import DriverFactory
from nakivo_automation_platform.core.reporting.allure_reporter import AllureReporter, StepTracker
from nakivo_automation_platform.domain.auth.auth_service import AuthService
from nakivo_automation_platform.domain.dashboard.dashboard_service import DashboardService
from nakivo_automation_platform.core.api.nakivo_api_client import NakivoApiClient


def pytest_addoption(parser):
    """Register CLI flags for environment, browser, and execution modes."""
    parser.addoption("--env", action="store", default=os.getenv("ENV", "local"), help="Environment: local, sit, uat")
    parser.addoption("--browser", action="store", default=os.getenv("BROWSER", "chrome"), help="Browser: chrome, edge")
    parser.addoption("--headless", action="store", default=os.getenv("HEADLESS", "true"), help="Headless mode: true/false")
    parser.addoption("--target-url", action="store", default=None, help="Explicit URL override")
    parser.addoption("--grid-url", action="store", default=None, help="Selenium Grid Remote URL")


@pytest.fixture(scope="session")
def platform_config(request):
    """
    Session-level immutable configuration object initialized from CLI and environment.
    Decoupled from global state and injected into downstream fixtures.
    """
    env_name = request.config.getoption("--env")
    browser_name = request.config.getoption("--browser")
    cfg = ConfigManager(env_name=env_name, browser_name=browser_name)

    # Runtime overrides from CLI options
    cli_url = request.config.getoption("--target-url") or os.getenv("BASE_URL")
    if cli_url:
        cfg.base_url = cli_url

    cli_headless = request.config.getoption("--headless")
    if cli_headless is not None:
        cfg.headless = cli_headless.lower() in ("true", "1", "yes")

    cli_grid = request.config.getoption("--grid-url") or os.getenv("SELENIUM_REMOTE_URL")
    if cli_grid:
        cfg.remote_url = cli_grid

    return cfg


@pytest.fixture(scope="function")
def driver(request, platform_config):
    """
    Provide isolated WebDriver instance per test function.
    Enforces clean session hygiene on teardown: purges cookies, localStorage, and sessionStorage.
    """
    driver_instance = DriverFactory.create_driver(platform_config)

    yield driver_instance

    try:
        driver_instance.delete_all_cookies()
        driver_instance.execute_script(
            "try { window.localStorage.clear(); window.sessionStorage.clear(); } catch(e) {}"
        )
    except Exception:
        pass
    finally:
        driver_instance.quit()


@pytest.fixture(scope="function")
def auth_service(driver, platform_config):
    """Provide initialized AuthService for domain-level operations with injected config."""
    return AuthService(driver, platform_config)


@pytest.fixture(scope="function")
def dashboard_service(driver):
    """Provide initialized DashboardService for domain-level operations."""
    return DashboardService(driver)


@pytest.fixture(scope="session")
def api_client(platform_config):
    """Provide initialized NakivoApiClient for pre-flight health checks and contract verification."""
    return NakivoApiClient(director_url=platform_config.director_url)


@pytest.fixture(scope="function")
def step(driver, request):
    """Provide step-by-step reporting with automatic screenshot capture."""
    return StepTracker(driver, request.node)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attach step screenshots and failure diagnostics to Allure and HTML reports."""
    outcome = yield
    report = outcome.get_result()
    extras = getattr(report, "extras", getattr(report, "extra", []))

    if report.when == "call":
        # 1. Embed step-by-step screenshots into pytest-html report
        import pytest_html
        step_screenshots = getattr(item, "_step_screenshots", [])
        for title, b64 in step_screenshots:
            html_snippet = (
                f'<div style="margin: 10px 0; padding: 8px; border: 1px solid #cce5ff; '
                f'border-radius: 6px; background: #f0f7ff;">'
                f'<div style="font-weight: bold; color: #0056b3; margin-bottom: 6px;">Step: {title}</div>'
                f'<img src="data:image/png;base64,{b64}" style="max-width: 800px; width: 100%; '
                f'border: 1px solid #b8daff; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); '
                f'display: block;"/></div>'
            )
            extras.append(pytest_html.extras.html(html_snippet))

        # 2. Attach failure diagnostics if test failed
        if report.failed:
            driver = item.funcargs.get("driver")
            if driver:
                AllureReporter.attach_screenshot(driver, name=f"failure_{item.name}")
                screenshots_dir = os.path.join(os.path.dirname(__file__), "reports", "screenshots")
                os.makedirs(screenshots_dir, exist_ok=True)
                try:
                    driver.save_screenshot(os.path.join(screenshots_dir, f"{item.name}.png"))
                except Exception:
                    pass

        if hasattr(report, "extras"):
            report.extras = extras
        else:
            report.extra = extras
