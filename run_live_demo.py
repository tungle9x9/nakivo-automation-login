"""
Live Interactive Visual UI Demo for User:
Runs Chrome maximized on foreground with human-like pacing so every action is clearly visible.
"""
import sys
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

URL = os.getenv("NAKIVO_BASE_URL", "https://localhost:4443/c/main")
USERNAME = os.getenv("NAKIVO_USER", "admin")
PASSWORD = os.getenv("NAKIVO_PASSWORD", "")

print("=" * 60)
print("[DEMO] LAUNCHING VISIBLE CHROME UI ON SCREEN")
print("=" * 60)

options = Options()
options.add_argument("--ignore-certificate-errors")
options.add_argument("--allow-insecure-localhost")
options.add_argument("--start-maximized")
options.add_argument("--disable-infobars")
options.add_argument("--disable-notifications")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

print("[1/5] Opening Google Chrome in maximized window...")
driver = webdriver.Chrome(options=options)
driver.maximize_window()

try:
    print(f"[2/5] Navigating to NAKIVO Web Director: {URL}")
    driver.get(URL)

    wait = WebDriverWait(driver, 25)
    email_elem = wait.until(EC.visibility_of_element_located((
        By.CSS_SELECTOR,
        "input[placeholder*='Username'], input[placeholder*='Email'], #email, input[name='username']"
    )))
    print("   [OK] Login page loaded successfully. Title: " + driver.title)
    print("   [INFO] Pausing 3 seconds for visual inspection...")
    time.sleep(3)

    print(f"[3/5] Typing username: '{USERNAME}'...")
    email_elem.clear()
    for char in USERNAME:
        email_elem.send_keys(char)
        time.sleep(0.08)
    driver.execute_script("arguments[0].dispatchEvent(new Event('input', {bubbles: true}));", email_elem)
    time.sleep(1)

    print("[4/5] Typing password: '••••••••••••'...")
    pass_elem = wait.until(EC.visibility_of_element_located((
        By.CSS_SELECTOR,
        "input[placeholder*='Password'], #password, input[name='password'], input[type='password']"
    )))
    pass_elem.clear()
    for char in PASSWORD:
        pass_elem.send_keys(char)
        time.sleep(0.08)
    driver.execute_script("arguments[0].dispatchEvent(new Event('input', {bubbles: true}));", pass_elem)
    time.sleep(1.5)

    print("[5/5] Clicking 'Log In' button...")
    login_btn = wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "//button[contains(., 'Log In') or contains(., 'Log in') or contains(@id, 'login')]"
    )))
    login_btn.click()

    print("   [INFO] Authenticating with NAKIVO server...")
    dashboard_wait = WebDriverWait(driver, 15)
    dashboard_wait.until(EC.presence_of_element_located((
        By.XPATH,
        "//*[contains(@class, 'x-tab-inner') or contains(@class, 'dashboard') or contains(text(), 'Jobs') or contains(text(), 'admin')]"
    )))
    print("   [OK] SUCCESS: Dashboard reached and active session verified.")
    print("   [INFO] Keeping browser window open for 8 seconds for inspection...")
    time.sleep(8)

finally:
    print("[INFO] Closing Chrome window. Demo finished.")
    driver.quit()

print("=" * 60)

