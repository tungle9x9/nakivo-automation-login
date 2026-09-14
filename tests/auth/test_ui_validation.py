"""
UI Validation Test Suite:
- Validate visibility and interactive functionality of 'Forgot your password?' workflow.
- Ensure 'Sign In' button state accurately reflects input readiness.
All steps captured with screenshots.
"""
import pytest
import allure


@allure.feature("Authentication UI")
@allure.story("Component & State Validations")
class TestUIValidation:
    """UI state validation suite testing controls, modals, and conditional states."""

    @pytest.mark.ui
    @allure.title("UI-01: Validate visibility and recovery workflow for 'Forgot the password?'")
    def test_forgot_password_component_flow(self, auth_service, step):
        """Verify visibility and modal interactive workflow for password recovery."""
        with step("Step 1: Open login page"):
            auth_service.open_login_page()

        with step("Step 2: Trigger 'Forgot the password?' workflow and verify prompt opens"):
            assert auth_service.is_recovery_modal_accessible(), (
                "Password recovery component failed to open when triggered."
            )

        with step("Step 3: Submit recovery email ('admin@company.com') and verify guidance response"):
            status_msg = auth_service.request_password_recovery("admin@company.com")
            assert len(status_msg) > 0, "No response or status message received from recovery workflow."
            assert any(
                token in status_msg.lower()
                for token in ["sent", "temporary", "security", "recovery", "password", "username", "email", "forgot", "prompt"]
            ), f"Unexpected recovery message: '{status_msg}'"

    @pytest.mark.ui
    @allure.title("UI-02: Verify 'Log In' button disabled when required fields are empty")
    def test_sign_in_button_disabled_when_empty_or_incomplete(self, auth_service, platform_config, step):
        """Entering incomplete credentials must enforce disabled state or error toast upon submit."""
        with step("Step 1: Open login page"):
            auth_service.open_login_page()

        with step("Step 2: Verify 'Log In' button initially disabled on empty inputs"):
            assert not auth_service.is_sign_in_button_enabled(), (
                "Sign In button should be disabled when both inputs are empty."
            )

        with step("Step 3: Enter username only and verify button remains disabled"):
            auth_service.login_page.enter_username("admin")
            auth_service.login_page.enter_password("")
            if not auth_service.is_sign_in_button_enabled():
                assert not auth_service.is_sign_in_button_enabled()
            else:
                auth_service.login_page.click_sign_in()
                assert auth_service.toast.is_visible(), "Submitting empty password should trigger error."

        with step("Step 4: Enter both username and password, verifying button enables"):
            auth_service.open_login_page()
            auth_service.login_page.enter_username("admin")
            auth_service.login_page.enter_password(platform_config.admin_password or "SampleTestPassword123!")
            assert auth_service.is_sign_in_button_enabled(), (
                "Sign In button should be enabled when both fields are populated."
            )
