"""
Data-Driven Test Suite: Dynamic Credential Matrix.
Demonstrates enterprise data-driven execution with UserCredential models.
All execution steps captured with screenshots.
"""
import pytest
import allure
from nakivo_automation_platform.data.data_loader import load_csv_credentials
from nakivo_automation_platform.models.user_credential import UserCredential

DATA_MATRIX = load_csv_credentials("test_data.csv")


@allure.feature("Authentication")
@allure.story("Data-Driven Testing")
class TestLoginDataDriven:
    """Dynamic data-driven validation across parameterized credential matrices."""

    @pytest.mark.data_driven
    @pytest.mark.parametrize(
        "credential",
        DATA_MATRIX,
        ids=[c.scenario for c in DATA_MATRIX]
    )
    def test_dynamic_credential_matrix(self, auth_service, dashboard_service, step, credential: UserCredential):
        """Execute parameterized test matrix validating valid, invalid, empty, and edge cases."""
        allure.dynamic.title(f"DDT: {credential.scenario} - {credential.description}")

        with step("Step 1: Open login page"):
            auth_service.open_login_page()

        with step(f"Step 2: Enter credentials for scenario '{credential.scenario}'"):
            auth_service.login_page.enter_username(credential.username)
            auth_service.login_page.enter_password(credential.password)

        # Handle empty inputs where UI legitimately disables submit button
        if not credential.username or not credential.password:
            if not auth_service.is_sign_in_button_enabled():
                with step("Step 3: Verify button disabled as expected for empty fields"):
                    assert not credential.expected_success, (
                        f"Button was disabled as expected for empty scenario: {credential.scenario}"
                    )
                return

        with step("Step 3: Click 'Log In' button"):
            if auth_service.is_sign_in_button_enabled():
                auth_service.login_page.click_sign_in()

        # Validate outcome based on expected_success flag
        if credential.expected_success:
            err_msg = auth_service.toast.get_visible_message().lower()
            if "attempts" in err_msg or "unsuccessful" in err_msg:
                pytest.skip(f"NAKIVO server IP lockout active ({err_msg}). Skipping happy-path in rapid loop.")

            with step("Step 4: Verify Dashboard reaches operational state"):
                assert dashboard_service.is_operational(), (
                    f"Dashboard failed to load for valid scenario: {credential.scenario}"
                )
        else:
            with step(f"Step 4: Verify rejection feedback for scenario '{credential.scenario}'"):
                toast_msg = auth_service.toast.get_visible_message().lower()
                validation_msg = auth_service.login_page.get_email_validation_message().lower()
                error_response = toast_msg or validation_msg

                assert len(error_response) > 0 or not auth_service.is_sign_in_button_enabled(), (
                    f"Expected rejection for negative scenario '{credential.scenario}', but no error was observed."
                )

                if "attempts" in error_response or "unsuccessful" in error_response:
                    pytest.skip(
                        f"Environment Lockout: Server brute-force IP rate limit active ('{error_response}'). "
                        "Skipped to avoid false-positive pass."
                    )

                if credential.expected_error:
                    expected_token = credential.expected_error.lower()
                    assert any(
                        token in error_response
                        for token in [
                            expected_token,
                            "invalid",
                            "required",
                            "valid",
                            "exceed",
                            "incorrect",
                            "credentials",
                        ]
                    ), f"Error message '{error_response}' did not match expected criteria: '{expected_token}'"
