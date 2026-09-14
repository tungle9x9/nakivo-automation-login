"""
Locators strictly encapsulated for the NAKIVO Login Page.
Semantically aligned with NAKIVO Web Director DOM.
"""
from selenium.webdriver.common.by import By


class LoginLocators:
    USERNAME_INPUT = (
        By.CSS_SELECTOR,
        "input[placeholder*='Username'], input[name='username'], input[placeholder*='Email'], #username, #email, input[type='email']"
    )
    # Backward compatibility alias
    EMAIL_INPUT = USERNAME_INPUT

    PASSWORD_INPUT = (
        By.CSS_SELECTOR,
        "input[placeholder*='Password'], input[name='password'], #password, input[type='password']"
    )
    SIGN_IN_BUTTON = (
        By.XPATH,
        "//button[contains(., 'Log In') or contains(., 'LOG IN') or contains(., 'Sign in') or contains(., 'Sign In') or @type='submit']"
    )
    FORGOT_PASSWORD_LINK = (
        By.XPATH,
        "//a[contains(text(), 'Forgot the password?') or contains(text(), 'Forgot your password?') or contains(text(), 'Forgot password') or contains(@class, 'forgot-password')]"
    )
    EMAIL_ERROR = (By.CSS_SELECTOR, ".email-error, #email-error, .invalid-feedback, [data-testid='email-error']")
    PASSWORD_ERROR = (By.CSS_SELECTOR, ".password-error, #password-error, [data-testid='password-error']")
