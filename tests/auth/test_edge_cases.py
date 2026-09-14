"""
Regression Test Suite: Boundary and Edge Cases.
Covers Test Case 4: Malformed email format, >255 char email, >100 char password.
All steps captured with screenshots.
"""
import pytest
import allure
from nakivo_automation_platform.data.factories.user_factory import UserFactory


@allure.feature("Authentication")
@allure.story("Edge Case Validation")
class TestEdgeCases:
    """Test suite verifying application stability under edge-case inputs."""

    @pytest.mark.regression
    @pytest.mark.edge_case
    @allure.title("TC4.1: Verify error message for invalid email format (e.g. testuser.com)")
    def test_tc4_1_malformed_email_format(self, auth_service, step):
        """TC4.1: Entering malformed email string must be rejected with validation error."""
        user = UserFactory.malformed_email()

        with step("Step 1: Open login page"):
            auth_service.open_login_page()

        with step(f"Step 2: Enter malformed email ('{user.username}') and password"):
            auth_service.login_page.enter_username(user.username)
            auth_service.login_page.enter_password(user.password)

        with step("Step 3: Click 'Log In' button"):
            if auth_service.is_sign_in_button_enabled():
                auth_service.login_page.click_sign_in()

        with step("Step 4: Verify validation rejection for malformed email"):
            toast = auth_service.toast.get_visible_message()
            validation_msg = auth_service.login_page.get_email_validation_message() or toast
            assert len(validation_msg) > 0, "No error displayed for malformed email."
            assert any(
                token in validation_msg.lower()
                for token in ["valid", "email", "@", "format", "enter", "incorrect", "credentials", "attempts"]
            )

    @pytest.mark.regression
    @pytest.mark.edge_case
    @allure.title("TC4.2: Verify error message for excessively long email (>255 characters)")
    def test_tc4_2_excessive_length_email_rejection(self, auth_service, step):
        """TC4.2: Email address exceeding RFC 255 characters must be rejected gracefully."""
        user = UserFactory.excessive_length_email()

        with step("Step 1: Open login page"):
            auth_service.open_login_page()

        with step("Step 2: Enter excessively long email (>255 chars)"):
            auth_service.login_page.enter_username(user.username)
            auth_service.login_page.enter_password(user.password)

        with step("Step 3: Click 'Log In' button"):
            if auth_service.is_sign_in_button_enabled():
                auth_service.login_page.click_sign_in()

        with step("Step 4: Verify error response for excessively long email"):
            toast = auth_service.toast.get_visible_message()
            assert len(toast) > 0, "Expected error toast for excessively long email."
            assert any(
                token in toast.lower()
                for token in ["255", "exceed", "length", "long", "valid", "invalid", "incorrect", "credentials", "attempts"]
            )

    @pytest.mark.regression
    @pytest.mark.edge_case
    @allure.title("TC4.3: Verify error message for excessively long password (>100 characters)")
    def test_tc4_3_excessive_length_password_rejection(self, auth_service, step):
        """TC4.3: Password exceeding 100 characters must not crash the service and must be rejected."""
        user = UserFactory.excessive_length_password()

        with step("Step 1: Open login page"):
            auth_service.open_login_page()

        with step("Step 2: Enter valid user with excessively long password (>100 chars)"):
            auth_service.login_page.enter_username(user.username)
            auth_service.login_page.enter_password(user.password)

        with step("Step 3: Click 'Log In' button"):
            if auth_service.is_sign_in_button_enabled():
                auth_service.login_page.click_sign_in()

        with step("Step 4: Verify error response for excessively long password"):
            toast = auth_service.toast.get_visible_message()
            assert len(toast) > 0, "Expected error toast for excessively long password."
            assert any(
                token in toast.lower()
                for token in ["100", "exceed", "length", "long", "invalid", "password", "incorrect", "credentials", "attempts"]
            )
