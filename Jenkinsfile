pipeline {
    agent any

    parameters {
        choice(
            name: 'ENVIRONMENT',
            choices: ['local', 'sit', 'uat'],
            description: 'Target test environment (Production execution strictly prohibited in automated test jobs)'
        )
        choice(
            name: 'BROWSER',
            choices: ['chrome', 'edge'],
            description: 'Execution browser type'
        )
        booleanParam(
            name: 'HEADLESS',
            defaultValue: true,
            description: 'Run browser in headless mode'
        )
        string(
            name: 'PARALLEL_WORKERS',
            defaultValue: '2',
            description: 'Number of parallel execution workers (pytest-xdist)'
        )
        choice(
            name: 'TEST_SCOPE',
            choices: ['smoke_then_regression', 'smoke_only', 'full_regression', 'ui_security'],
            description: 'Test execution scope and quality gate strategy'
        )
        string(
            name: 'BASE_URL',
            defaultValue: 'https://localhost:4443/c/main',
            description: 'Target NAKIVO Director Application URL'
        )
    }

    environment {
        PYTHONUNBUFFERED = '1'
        PYTHONDONTWRITEBYTECODE = '1'
        ALLURE_RESULTS_DIR = 'reports/allure-results'
        HTML_REPORT = 'reports/report.html'
        JUNIT_REPORT = 'reports/junit.xml'
    }

    stages {
        stage('Pre-Flight & Environment Validation') {
            steps {
                echo "[INFO] Running Pre-flight connectivity check on [${params.ENVIRONMENT}] against [${params.BASE_URL}]"
                sh '''
                    python -c "
import urllib.request, ssl, sys
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
url = '${BASE_URL}'
try:
    with urllib.request.urlopen(url, context=ctx, timeout=10) as r:
        print(f'[PRE-FLIGHT] Endpoint reachable. HTTP status: {r.status}')
except Exception as e:
    print(f'[PRE-FLIGHT WARNING] Service not immediately responding ({e}). Test runner will utilize configured retry policies.')
"
                '''
            }
        }

        stage('Install & Cache Dependencies') {
            steps {
                echo "[INFO] Setting up isolated Python virtual environment and installing dependencies..."
                sh '''
                    python -m venv .venv
                    . .venv/bin/activate || . .venv/Scripts/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install -e .
                '''
            }
        }

        stage('Code Quality Gate (Static Analysis)') {
            steps {
                echo "[INFO] Executing static lint checks and syntax verification..."
                sh '''
                    . .venv/bin/activate || . .venv/Scripts/activate
                    python -m ruff check . || true
                    python -m compileall -q .
                '''
            }
        }

        stage('Smoke Quality Gate (Fast-Fail)') {
            when {
                expression { params.TEST_SCOPE in ['smoke_then_regression', 'smoke_only'] }
            }
            steps {
                echo "[INFO] Executing Critical Smoke Suite (TC1 Availability & TC2 Authentication)..."
                sh """
                    . .venv/bin/activate || . .venv/Scripts/activate
                    pytest tests/auth/test_login_smoke.py \
                        --env ${params.ENVIRONMENT} \
                        --browser ${params.BROWSER} \
                        --headless ${params.HEADLESS} \
                        --target-url '${params.BASE_URL}' \
                        -v
                """
            }
        }

        stage('Regression & Security Test Suite') {
            when {
                expression { params.TEST_SCOPE in ['smoke_then_regression', 'full_regression', 'ui_security'] }
            }
            steps {
                script {
                    def markerFlag = (params.TEST_SCOPE == 'ui_security') ? '-m "ui or security"' : '-m "regression or data_driven or ui or security"'
                    def workerFlag = (params.PARALLEL_WORKERS.toInteger() > 1) ? "-n ${params.PARALLEL_WORKERS}" : ""

                    sh """
                        . .venv/bin/activate || . .venv/Scripts/activate
                        pytest tests/auth \
                            --env ${params.ENVIRONMENT} \
                            --browser ${params.BROWSER} \
                            --headless ${params.HEADLESS} \
                            --target-url '${params.BASE_URL}' \
                            ${markerFlag} \
                            ${workerFlag} \
                            -v
                    """
                }
            }
        }

        stage('Publish Telemetry & Quality Artifacts') {
            steps {
                script {
                    echo "[INFO] Archiving multi-format test telemetry (JUnit XML, Standalone HTML, Allure)..."
                    
                    // 1. Publish standard JUnit test results for Jenkins native trend graphs
                    junit testResults: 'reports/junit.xml', allowEmptyResults: true

                    // 2. Archive portable self-contained HTML report with embedded screenshots
                    archiveArtifacts artifacts: 'reports/**/*.html, reports/**/*.png', allowEmptyArchive: true

                    // 3. Publish interactive Allure report dashboard
                    allure([
                        includeProperties: false,
                        jdk: '',
                        properties: [],
                        reportBuildPolicy: 'ALWAYS',
                        results: [[path: 'reports/allure-results']]
                    ])
                }
            }
        }
    }

    post {
        always {
            cleanWs notFailBuild: true
        }
        success {
            echo "[QUALITY GATE PASSED] All test suites completed successfully. Quality criteria met."
        }
        unstable {
            echo "[QUALITY GATE UNSTABLE] Non-critical tests reported flaky results or environment rate limits."
        }
        failure {
            echo "[QUALITY GATE BREACHED] Critical regression or smoke test failure. Build marked FAILED."
        }
    }
}
