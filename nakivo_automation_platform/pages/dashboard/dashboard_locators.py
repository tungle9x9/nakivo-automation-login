"""
Locators for NAKIVO Dashboard.
"""
from selenium.webdriver.common.by import By


class DashboardLocators:
    CONTAINER = (By.CSS_SELECTOR, "#dashboard-container, .main-layout, [data-testid='dashboard-container'], .x-panel")
    USER_PROFILE = (By.XPATH, "//*[contains(text(), 'admin') or contains(@class, 'user-name') or contains(@id, 'user-menu')]")
    LOGOUT_BUTTON = (By.CSS_SELECTOR, "#btn-logout, .btn-logout, a[href*='logout'], [data-testid='logout-button']")
