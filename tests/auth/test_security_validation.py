"""
Security Validation Test Suite:
- Password field input masking (DOM input type='password' and no plain text leakage).
- Input field restrictions (rejection of malformed email formats).
All steps captured with screenshots.
"""
import pytest
import allure
from nakivo_automation_platform.models.user_credential import UserCredential
from nakivo_automation_platform.pages.login.login_locators import LoginLocators


@allure.feature("Authentication Security")
@allure.story("Client-Side Security Safeguards")
class TestSecurityValidation:
    """Security verification suite inspecting credential masking and input sanitization."""

    @pytest.mark.security
    @allure.title("SEC-01: Validate password input characters are masked and unexposed")
    def test_password_field_is_masked(self, auth_service, step):
        """Validate that passwords entered into the password field are masked (hidden)."""
        with step("Step 1: Open login page"):
            auth_service.open_login_page()

        with step("Step 2: Enter confidential password"):
            auth_service.login_page.enter_password("ConfidentialPass123!")

        with step("Step 3: Verify DOM attribute type is strictly 'password'"):
            assert auth_service.is_password_masked(), (
                "Security vulnerability: Password input field does not enforce type='password'."
            )

        with step("Step 4: Confirm plaintext password is not leaked in element innerText"):
            password_elem = auth_service.login_page.wait.until_presence(LoginLocators.PASSWORD_INPUT)
            assert password_elem.text == "", (
                "Security vulnerability: Plaintext password was found exposed in DOM text content."
            )

    @pytest.mark.security
    @allure.title("SEC-02: Check input field restrictions: email field rejects malformed formats")
    def test_email_field_format_restrictions(self, auth_service, step):
        """Verify that malformed email inputs are rejected with validation feedback."""
        malformed_inputs = [
            "invaliduser.com",          # Missing @
            "invaliduser@",             # Missing domain
            "@domain.com",              # Missing local part
        ]

        for malformed in malformed_inputs:
            user = UserCredential(
                username=malformed,
                password="TestPassword123!",
                scenario=f"malformed_email_{malformed}"
            )
            with step(f"Step: Test format rejection for '{malformed}'"):
                auth_service.open_login_page()
                auth_service.login_page.enter_username(user.username)
                auth_service.login_page.enter_password(user.password)

                if auth_service.is_sign_in_button_enabled():
                    auth_service.login_page.click_sign_in()

                toast = auth_service.toast.get_visible_message()
                val_msg = auth_service.login_page.get_email_validation_message()
                feedback = toast or val_msg

                assert len(feedback) > 0 or not auth_service.is_sign_in_button_enabled(), (
                    f"Malformed email '{malformed}' was accepted without validation or restriction."
                )
