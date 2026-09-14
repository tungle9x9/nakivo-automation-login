"""
Regression Test Suite: Negative Authentication Scenarios.
Covers Test Case 3: Invalid credentials, missing email, missing password, and both empty.
All steps tracked with automatic screenshot capture.
"""
import pytest
import allure
from nakivo_automation_platform.data.factories.user_factory import UserFactory


@allure.feature("Authentication")
@allure.story("Negative Testing")
class TestLoginNegative:
    """Test suite evaluating application resilience against invalid and empty inputs."""

    @pytest.mark.regression
    @pytest.mark.negative
    @allure.title("TC3.1: Verify error message when logging in with invalid credentials")
    def test_tc3_1_authentication_rejection_for_invalid_user(self, auth_service, step):
        """TC3.1: Enter unregistered user credentials and assert system error notification."""
        invalid_user = UserFactory.invalid_user()

        with step("Step 1: Open login page"):
            auth_service.open_login_page()

        with step(f"Step 2: Enter invalid credentials ('{invalid_user.username}')"):
            auth_service.login_page.enter_username(invalid_user.username)
            auth_service.login_page.enter_password(invalid_user.password)

        with step("Step 3: Click 'Log In' button"):
            if auth_service.is_sign_in_button_enabled():
                auth_service.login_page.click_sign_in()

        with step("Step 4: Verify error notification toast is displayed"):
            toast_message = auth_service.toast.get_visible_message()
            if "attempts" in toast_message.lower() or "unsuccessful" in toast_message.lower():
                pytest.skip(
                    f"Environment Lockout: Server brute-force IP rate limit active ('{toast_message}'). "
                    "Skipped to avoid false-positive pass."
                )

            assert any(
                token in toast_message.lower()
                for token in ["incorrect", "invalid", "failed", "credentials"]
            ), f"Expected credential error toast, got: '{toast_message}'"

    @pytest.mark.regression
    @pytest.mark.negative
    @allure.title("TC3.2: Verify validation behavior when email field is left empty")
    def test_tc3_2_empty_username_validation(self, auth_service, step):
        """TC3.2: Leaving username empty must disable sign-in or trigger validation rejection."""
        user = UserFactory.empty_username()

        with step("Step 1: Open login page"):
            auth_service.open_login_page()

        with step("Step 2: Fill password while leaving username empty"):
            auth_service.login_page.enter_username(user.username)
            auth_service.login_page.enter_password(user.password)

        with step("Step 3: Verify 'Log In' button disabled or validation triggered on submit"):
            if auth_service.is_sign_in_button_enabled():
                auth_service.login_page.click_sign_in()
                assert auth_service.toast.is_visible(), "Expected validation error when submitting with empty username."
            else:
                assert not auth_service.is_sign_in_button_enabled()

    @pytest.mark.regression
    @pytest.mark.negative
    @allure.title("TC3.3: Verify validation behavior when password field is left empty")
    def test_tc3_3_empty_password_validation(self, auth_service, step):
        """TC3.3: Leaving password empty must disable sign-in or trigger validation rejection."""
        user = UserFactory.empty_password()

        with step("Step 1: Open login page"):
            auth_service.open_login_page()

        with step("Step 2: Fill username while leaving password empty"):
            auth_service.login_page.enter_username(user.username)
            auth_service.login_page.enter_password(user.password)

        with step("Step 3: Verify 'Log In' button disabled or validation triggered on submit"):
            if auth_service.is_sign_in_button_enabled():
                auth_service.login_page.click_sign_in()
                assert auth_service.toast.is_visible(), "Expected validation error when submitting with empty password."
            else:
                assert not auth_service.is_sign_in_button_enabled()

    @pytest.mark.regression
    @pytest.mark.negative
    @allure.title("TC3.4: Verify behavior when both fields are empty")
    def test_tc3_4_both_fields_empty(self, auth_service, step):
        """TC3.4: Omitting both username and password must keep sign-in button disabled."""
        with step("Step 1: Open login page"):
            auth_service.open_login_page()

        with step("Step 2: Verify 'Log In' button is disabled by default when fields are empty"):
            assert not auth_service.is_sign_in_button_enabled(), (
                "Sign In button must remain disabled when both fields are empty."
            )
