# NAKIVO Backup & Replication - Automated Test Platform

## Enterprise SDET Test Automation Platform for Authentication & Session Management

Target Application: **NAKIVO Backup & Replication v11.2** (`https://localhost:4443/c/main`)  
Repository: https://github.com/tungle9x9/nakivo-automation-login

---

## 1. Prerequisites and Required Tools

Before running the test suite, ensure the following tools and software are ready on the host system:

### Required Software
- **Target Application**: NAKIVO Backup & Replication v11.2 running and accessible on `https://localhost:4443/c/main`.
- **Python**: Version `3.10+` (Validated on Python 3.14.4 Windows 11 x64).
- **Google Chrome**: Latest stable version installed. ChromeDriver binary resolution is handled automatically by Selenium Manager (Selenium 4+).
- **Git**: For cloning and repository management.

### Optional Tools
- **Java Runtime Environment (JRE/JDK 11+)**: Required only when serving interactive Allure dashboards via `allure serve`. Standard self-contained HTML reports (`reports/report.html`) and JUnit XML reports (`reports/junit.xml`) do not require Java.
- **Docker & Docker Compose**: For containerized execution or running on a distributed Selenium Grid cluster.

### Python Dependencies (`requirements.txt` & `pyproject.toml`)
The platform relies strictly on production-grade libraries without superfluous wrappers:
- `selenium>=4.20.0`: W3C-compliant browser automation (leveraging native Selenium Manager).
- `pytest>=8.0.0`: Core test runner, fixture lifecycle, and test filtering.
- `pytest-html>=4.1.1`: Standalone single-file HTML reporting with embedded base64 screenshots.
- `pytest-xdist>=3.5.0`: Multi-process parallel test execution.
- `allure-pytest>=2.13.5`: Structured test telemetry and step analytics.
- `pydantic>=2.7.0`: Strongly typed credential schema validation.
- `pyyaml>=6.0.1`: Hierarchical YAML configuration loader.
- `python-dotenv>=1.0.1`: Runtime credential and environment management via `.env`.
- `requests>=2.31.0`: Direct REST / JSON-RPC backend health checks.
- `ruff>=0.4.0`: Ultra-fast static analysis, formatting, and code quality gate.

---

## 2. Setup Guide

### Step 1: Clone the Repository
```bash
git clone https://github.com/tungle9x9/nakivo-automation-login.git
cd nakivo-automation-login
```

### Step 2: Create and Activate Virtual Environment
- **On Windows (PowerShell)**:
  ```powershell
  python -m venv .venv
  .venv\Scripts\activate
  ```
- **On Linux / macOS**:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### Step 3: Install Dependencies & Editable Platform Package
```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

### Step 4: Configure Credentials
Copy the template `.env.example` to `.env` to configure your live NAKIVO instance credentials:
```bash
cp .env.example .env
```
Edit `.env` (this file is excluded from Git by `.gitignore` for security):
```ini
ENV=local
BROWSER=chrome
HEADLESS=true
NAKIVO_BASE_URL=https://localhost:4443/c/main
NAKIVO_USER=admin
NAKIVO_PASSWORD=your_nakivo_password_here
USE_MOCK=false
```

---

## 3. How to Run the Tests (Live Target: https://localhost:4443/c/main)

All test suites execute directly against the live NAKIVO Backup & Replication instance.

### Quick All-In-One Command (Set User + Run All Tests + Open Report)

Execute all test cases with runtime credentials and automatically launch the HTML report:

**Option 1: Unified Enterprise Launcher (Recommended)**
```powershell
python run_platform_tests.py --user admin --password <YOUR_PASSWORD> --open-report
```

**Option 2: Native PowerShell One-Liner**
```powershell
$env:NAKIVO_USER="admin"; $env:NAKIVO_PASSWORD="<YOUR_PASSWORD>"; pytest tests -v; Invoke-Item "reports\report.html"
```

---

### Execution Modes

#### A. Run All Tests with Visible Chrome UI (On-Screen Demonstration)
Observe the browser open and perform all authentication workflows in real-time:
```powershell
pytest tests --headless=false -v
```
*Or via launcher:*
```powershell
python run_platform_tests.py --headless false
```

#### B. Run All Tests in Headless Mode (Standard CI/CD Execution)
Fast, silent execution without rendering the browser window:
```powershell
pytest tests --headless=true -v
```
*Or via launcher:*
```powershell
python run_platform_tests.py --headless true
```

#### C. Run Specific Test Suites by Marker

```powershell
# 1. Smoke Suite: TC1 (Page Availability) & TC2 (Successful Authentication)
pytest -m smoke -v

# 2. Regression Suite: TC3 (Invalid / Empty fields) & TC4 (Boundary Edge Cases)
pytest -m regression -v

# 3. Dynamic Data-Driven Testing (11 credential scenarios loaded from data/test_data.csv)
pytest -m data_driven -v

# 4. UI & Security Validations (Forgot Password modal, disabled buttons, password masking)
pytest -m "ui or security" -v
```

#### D. Run Static Analysis & Code Quality Checks (Ruff)
```powershell
ruff check .
```
*Or via Makefile:*
```powershell
make lint
make check
```

#### E. Run in Parallel (Multi-Process via pytest-xdist)
```powershell
pytest tests -n 4 --headless=true -v
```

#### F. Run Live Visual Demonstration (Human-Paced)
```powershell
python run_live_demo.py
```

---

## 4. Test Reporting: 3-Tier Enterprise Strategy

The platform deliberately implements three complementary reporting tiers, answering distinct stakeholder needs:

| Reporting Tier | Format & Destination | Primary Purpose | Audience / Use-Case |
| :--- | :--- | :--- | :--- |
| **Primary Telemetry** | **Allure Report** (`reports/allure-results/`) | Rich interactive dashboards, execution trends, step hierarchies, failure timelines | SDET Engineers & QA Leads |
| **CI/CD Integration** | **JUnit XML** (`reports/junit.xml`) | Machine-readable test execution metrics for native CI pass/fail graphs | Jenkins, GitLab CI, GitHub Actions |
| **Portable Artifact** | **Standalone HTML** (`reports/report.html`) | Single self-contained file with embedded base64 screenshots for zero-dependency offline review | Stakeholder email delivery & CI build artifact archiving |

### Viewing Reports

1. **Standalone Single-File HTML Report**:
   ```powershell
   Invoke-Item "reports\report.html"
   ```
   - Clicking any test case expands an accordion view displaying every sequential step with its title and inline base64 screenshot.

2. **Allure Dashboard**:
   ```powershell
   allure serve reports/allure-results
   ```

---

## 5. Security, Test Isolation & Quality Engineering

### A. Zero Hardcoded Secrets
- Default fallback credentials in version-controlled files are sanitized placeholders (`TestPassword123!`).
- Real credentials are loaded at runtime via environment variables (`NAKIVO_USER`, `NAKIVO_PASSWORD`) or gitignored `.env`.

### B. MaskedLogger (Log PII Redaction)
- `core/logging/masked_logger.py` dynamically intercepts passwords, tokens, and secret patterns across all logging streams, replacing them with `******`.

### C. Rigorous Test Isolation & Session Hygiene
- Every test function runs in a dedicated, isolated WebDriver instance (`scope="function"`).
- Teardown contract enforces complete state cleanup:
  ```python
  driver_instance.delete_all_cookies()
  driver_instance.execute_script("try { window.localStorage.clear(); window.sessionStorage.clear(); } catch(e) {}")
  ```

### D. Deterministic Failure Triage (Rate Limiting vs Defect)
To prevent false-positive passes when NAKIVO server enforces IP rate limiting (5 failed attempts = 15-minute lock):
- **Functional Credential Rejection**: Expected system feedback (`"Incorrect credentials"`) -> `PASS`.
- **Server Rate Limit Lockout**: Infrastructure lockout feedback (`"unsuccessful login attempts"`) -> `pytest.skip("Environment Lockout: Server brute-force IP rate limit active")`.
- **Unexpected Error / DOM Crash**: -> `FAIL`.

### E. Resilient Interaction Contract (No Blanket JS Fallback)
In `core/element/element_actions.py`, clicking follows an explicit multi-stage escalation path to avoid masking real product bugs:
1. **Stage 1 (Standard)**: Native W3C WebDriver click.
2. **Stage 2 (Overlay Handling)**: If `ElementClickInterceptedException`, scroll element to center, wait for overlay/mask to clear, and retry native click.
3. **Stage 3 (Last Resort Fallback)**: JavaScript click executed strictly as a fallback, logging an explicit `[WARNING]` telemetry event so it is tracked.

---

## 6. Requirements Traceability Matrix

Validated against **NAKIVO Backup & Replication v11.2** running on `https://localhost:4443/c/main`:

| Requirement | Test Suite / File | Test Method | Pytest Marker | Status |
| :--- | :--- | :--- | :--- | :---: |
| **Test Case 1: Page Load** | `tests/auth/test_login_smoke.py` | `test_tc1_login_interface_availability` | `@pytest.mark.smoke` | Implemented & Verified |
| **Test Case 2: Valid Login** | `tests/auth/test_login_smoke.py` | `test_tc2_authenticated_session_establishment` | `@pytest.mark.smoke` | Implemented & Verified |
| **Test Case 3.1: Invalid User** | `tests/auth/test_login_negative.py` | `test_tc3_1_authentication_rejection_for_invalid_user` | `@pytest.mark.regression` | Implemented & Verified |
| **Test Case 3.2: Empty Email** | `tests/auth/test_login_negative.py` | `test_tc3_2_empty_username_validation` | `@pytest.mark.regression` | Implemented & Verified |
| **Test Case 3.3: Empty Password** | `tests/auth/test_login_negative.py` | `test_tc3_3_empty_password_validation` | `@pytest.mark.regression` | Implemented & Verified |
| **Test Case 3.4: Both Fields Empty** | `tests/auth/test_login_negative.py` | `test_tc3_4_both_fields_empty` | `@pytest.mark.regression` | Implemented & Verified |
| **Test Case 4.1: Malformed Email** | `tests/auth/test_edge_cases.py` | `test_tc4_1_malformed_email_format` | `@pytest.mark.regression` | Implemented & Verified |
| **Test Case 4.2: Email > 255 Chars** | `tests/auth/test_edge_cases.py` | `test_tc4_2_excessive_length_email_rejection` | `@pytest.mark.regression` | Implemented & Verified |
| **Test Case 4.3: Password > 100 Chars** | `tests/auth/test_edge_cases.py` | `test_tc4_3_excessive_length_password_rejection` | `@pytest.mark.regression` | Implemented & Verified |
| **Data-Driven Testing (CSV)** | `tests/auth/test_login_data_driven.py` | `test_dynamic_credential_matrix` (11 CSV scenarios) | `@pytest.mark.data_driven` | Implemented & Verified |
| **UI: Forgot Password Flow** | `tests/auth/test_ui_validation.py` | `test_forgot_password_component_flow` | `@pytest.mark.ui` | Implemented & Verified |
| **UI: Disabled Button State** | `tests/auth/test_ui_validation.py` | `test_sign_in_button_disabled_when_empty_or_incomplete` | `@pytest.mark.ui` | Implemented & Verified |
| **Security: Password Masking** | `tests/auth/test_security_validation.py` | `test_password_field_is_masked` | `@pytest.mark.security` | Implemented & Verified |
| **Security: Email Restrictions** | `tests/auth/test_security_validation.py` | `test_email_field_format_restrictions` | `@pytest.mark.security` | Implemented & Verified |

---

## 7. Architecture & Design Specification

### 5-Layer Platform Architecture

```
+---------------------------------------------------------------------------------+
|                              LAYER 5: TEST SUITES                               |
|             tests/auth/ (Domain-driven: smoke, regression, DDT, UI)             |
+---------------------------------------+-+---------------------------------------+
                                        | consumes business flows
+---------------------------------------v-----------------------------------------+
|                         LAYER 4: DOMAIN SERVICE LAYER                           |
|       domain/auth/AuthService.py     |  domain/dashboard/DashboardService.py    |
+-----------------------+---------------------------------+-----------------------+
                        | orchestrates                    | manages
+-----------------------v----------------+   +------------v-----------------------+
|      LAYER 3A: PAGE OBJECTS (POM)      |   | LAYER 3B: COMPONENT OBJECTS (COM)  |
|      pages/login/LoginPage.py          |   | components/extjs_toast.py          |
|      pages/dashboard/DashboardPage.py  |   | components/extjs_modal.py          |
+-----------------------+----------------+   +------------+-----------------------+
                        | uses ElementActions & Waits     |
+-----------------------v---------------------------------v-----------------------+
|                        LAYER 2: CORE PLATFORM FOUNDATION                        |
|      core/driver/DriverFactory         | core/element/ElementActions            |
|      core/wait/WaitManager             | core/logging/MaskedLogger              |
|      core/api/NakivoApiClient          | core/reporting/AllureReporter          |
+---------------------------------------+-+---------------------------------------+
                                        | configured by
+---------------------------------------v-----------------------------------------+
|                     LAYER 1: CONFIGURATION & ENVIRONMENT                        |
|      config/environments/*.yaml (local, sit)   | config/browsers/*.yaml (chrome)|
+---------------------------------------------------------------------------------+
```

### Project Directory Layout

```text
nakivo-automation-login/
├── nakivo_automation_platform/       # Core Python Package (pip install -e .)
│   ├── components/                   # Component Object Model (ExtJS toasts, modals)
│   ├── config/                       # Hierarchical YAML configs & ConfigManager
│   │   ├── environments/             # local.yaml, sit.yaml
│   │   └── browsers/                 # chrome.yaml, edge.yaml
│   ├── core/                         # Enterprise Core Engine
│   │   ├── api/                      # Direct backend API client (Router/Director)
│   │   ├── driver/                   # DriverFactory & CapabilitiesBuilder
│   │   ├── element/                  # Resilient ElementActions (Native -> Escalate -> JS fallback)
│   │   ├── exceptions/               # Typed custom framework exceptions
│   │   ├── logging/                  # MaskedLogger (PII / credential redaction)
│   │   ├── reporting/                # Allure telemetry & step hooks
│   │   └── wait/                     # Explicit WaitManager (zero implicit waits)
│   ├── data/                         # Test Data & Factories
│   │   ├── factories/                # Dynamic UserFactory
│   │   ├── data_loader.py            # CSV / YAML data loader (UTF-8-SIG resilient)
│   │   └── test_data.csv             # Parameterized test matrix
│   ├── domain/                       # Domain Business Services
│   │   ├── auth/                     # AuthService (pure Dependency Injection)
│   │   └── dashboard/                # DashboardService
│   ├── models/                       # Pydantic data models & DTOs
│   └── pages/                        # Page Object Model (POM - no assertions)
│       ├── login/                    # LoginPage & LoginLocators
│       └── dashboard/                # DashboardPage & DashboardLocators
├── tests/                            # Test Suites (Domain-grouped)
│   └── auth/                         # Smoke, regression, DDT, security, UI tests
├── reports/                          # Generated Allure, HTML, and JUnit reports
├── conftest.py                       # Pytest fixtures (pure Dependency Injection)
├── docker-compose.yml                # Selenium Grid cluster orchestrator
├── Dockerfile                        # Test runner container definition
├── Jenkinsfile                       # Multi-stage CI/CD pipeline (P0/P1 quality gates)
├── Makefile                          # Developer convenience CLI targets
├── pyproject.toml                    # PEP 621 package metadata & Ruff lint config
├── pytest.ini                        # Pytest markers and execution defaults
├── requirements.txt                  # Direct pinned dependencies
├── run_live_demo.py                  # Live visual demonstration script
└── run_platform_tests.py             # Enterprise unified CLI launcher
```

### Extensible Test Organization
Tests are grouped under domain packages (`tests/auth/`), establishing an architecture that scales cleanly as the product grows (e.g. `tests/dashboard/`, `tests/backup/`, `tests/recovery/`).

---

## 8. Handling Sencha ExtJS Single Page Application Challenges

| Challenge | Root Cause in ExtJS | Platform Engineering Solution |
| :--- | :--- | :--- |
| **Dynamic Element IDs** | ExtJS generates dynamic runtime IDs (e.g. `ext-gen-1049`). | Bypassed IDs completely; used stable attribute combinations (`input[placeholder*='Username']`, `button[contains(., 'Log In')]`). |
| **Click Interception by Overlays** | ExtJS loading masks (`.x-mask`) intercept native clicks. | Multi-stage escalation: scroll element, wait for mask fade-out, retry native click. JS fallback as tracked last resort. |
| **Ghost Toast Notifications** | Expired notification elements linger in the DOM with `display: none`. | `ExtJsToastComponent` scans all `.notification-message-content` nodes, filters out hidden elements via `is_displayed()`, and reads only visible messages. |
| **Self-Signed SSL Certificates** | NAKIVO defaults to HTTPS on port 4443 with self-signed certificate. | `CapabilitiesBuilder` injects `--ignore-certificate-errors`, `--allow-insecure-localhost`, and `accept_insecure_certs=True`. |
| **Brute-Force Rate Limiting** | Server blocks client IP after repeated invalid attempts. | Deterministic triage: functional rejection asserted, rate limits flagged as environment security state (`pytest.skip`). |

---

## 9. CI/CD & Distributed Container Execution

### Mature Multi-Stage Jenkins Pipeline (`Jenkinsfile`)
```
[Pre-Flight Validation] -> [Install Dependencies] -> [Code Quality Gate (Ruff)]
         |
         v
[Smoke Quality Gate (Fast-Fail)] -> [Regression & Security Suite (Parallel)]
         |
         v
[Publish Telemetry (JUnit + HTML + Allure)] -> [Enforce Quality Gate]
```
- **Environment Safety**: Target environments restricted to `['local', 'sit', 'uat']`. Production execution is strictly prohibited.
- **Fast-Fail Gate**: Smoke failures fail the pipeline immediately before launching expensive regression jobs.

### Distributed Selenium Grid (`docker-compose.yml`)
```
[nakivo-test-runner] ---> [selenium-hub:4444] ---> [chrome-node]
         |
         +---> Host NAKIVO Director via https://host.docker.internal:4443/c/main
```
```bash
docker-compose up --build --abort-on-container-exit
```
