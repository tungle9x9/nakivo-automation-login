"""
Enterprise Test Platform CLI Launcher.
Provides unified entry point for CLI execution, CI/CD runners, and developer local debug.
"""
import sys
import os
import argparse
import socket
import pytest

# Ensure root platform package is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def is_port_in_use(port: int, host="127.0.0.1") -> bool:
    """Check if target host:port is listening."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.0)
        return s.connect_ex((host, port)) == 0


def main():
    parser = argparse.ArgumentParser(description="NAKIVO SDET Enterprise Automation Platform Runner")
    parser.add_argument("--env", default="local", help="Target test environment (local, sit, uat)")
    parser.add_argument("--browser", default="chrome", help="Browser engine (chrome, edge)")
    parser.add_argument("--headless", default="true", help="Run browser headlessly (true/false)")
    parser.add_argument("--url", default="", help="Override target application base URL")
    parser.add_argument("--grid", default="", help="Remote Selenium Grid Hub URL (e.g. http://hub:4444/wd/hub)")
    parser.add_argument("-m", "--marker", default="", help="Pytest marker filter (smoke, regression, data_driven, ui, security)")
    parser.add_argument("-k", "--keyword", default="", help="Pytest keyword expression filter")
    parser.add_argument("-n", "--workers", default="", help="Number of parallel worker processes (pytest-xdist)")
    parser.add_argument("--user", default="", help="NAKIVO login username override (e.g. admin)")
    parser.add_argument("--password", default="", help="NAKIVO login password override")
    parser.add_argument("--open-report", action="store_true", help="Automatically open HTML report in default browser upon completion")
    parser.add_argument("--html", default="reports/report.html", help="Path to self-contained HTML test report")
    parser.add_argument("--alluredir", default="reports/allure-results", help="Directory for Allure results")
    parser.add_argument("--junitxml", default="reports/junit.xml", help="Path to JUnit XML test report")

    args, unknown_args = parser.parse_known_args()

    # Pass environment variables to pytest runtime
    os.environ["ENV"] = args.env
    os.environ["BROWSER"] = args.browser
    os.environ["HEADLESS"] = args.headless.lower()
    if args.url:
        os.environ["BASE_URL"] = args.url
    if args.grid:
        os.environ["SELENIUM_REMOTE_URL"] = args.grid
        os.environ["GRID_URL"] = args.grid
    if args.user:
        os.environ["NAKIVO_USER"] = args.user
    if args.password:
        os.environ["NAKIVO_PASSWORD"] = args.password

    print("\n" + "=" * 65)
    print(" [PLATFORM] NAKIVO SDET ENTERPRISE AUTOMATION PLATFORM")
    print("=" * 65)
    print(f" Environment   : {args.env.upper()}")
    print(f" Browser       : {args.browser}")
    print(f" Headless      : {args.headless}")
    print(f" Target URL    : {args.url or '(from config)'}")
    print(f" Grid Remote   : {args.grid or '(Local Browser)'}")
    print(f" Parallelism   : {args.workers if args.workers else 'Sequential'}")
    print(f" Marker Filter : {args.marker if args.marker else 'All'}")
    print("=" * 65 + "\n")

    # Build pytest CLI arguments
    pytest_args = [
        os.path.join(BASE_DIR, "tests"),
        "-v",
        f"--alluredir={os.path.join(BASE_DIR, args.alluredir)}",
        f"--html={os.path.join(BASE_DIR, args.html)}",
        "--self-contained-html",
        f"--junitxml={os.path.join(BASE_DIR, args.junitxml)}",
        f"--env={args.env}",
        f"--browser={args.browser}",
        f"--headless={args.headless}",
    ]

    if args.url:
        pytest_args.append(f"--target-url={args.url}")
    if args.grid:
        pytest_args.append(f"--grid-url={args.grid}")
    if args.marker:
        pytest_args.extend(["-m", args.marker])
    if args.keyword:
        pytest_args.extend(["-k", args.keyword])
    if args.workers and args.workers not in ("0", "1"):
        pytest_args.extend(["-n", args.workers])

    pytest_args.extend(unknown_args)

    exit_code = pytest.main(pytest_args)

    print("\n" + "=" * 65)
    print(f" Test Execution Finished with Status Code: {exit_code}")
    print(f" HTML Report  : {os.path.abspath(os.path.join(BASE_DIR, args.html))}")
    print(f" JUnit XML    : {os.path.abspath(os.path.join(BASE_DIR, args.junitxml))}")
    print(f" Allure Output: {os.path.abspath(os.path.join(BASE_DIR, args.alluredir))}")
    print("=" * 65 + "\n")

    if args.open_report:
        report_file = os.path.abspath(os.path.join(BASE_DIR, args.html))
        if os.path.exists(report_file):
            import webbrowser
            print(f"[INFO] Launching HTML report in browser: {report_file}")
            webbrowser.open(f"file:///{report_file}")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
