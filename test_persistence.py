from playwright.sync_api import sync_playwright
import time
import subprocess
import sys

def test_persistence():
    server = subprocess.Popen(["python3", "-m", "http.server", "8008", "-d", "public"])
    time.sleep(1)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto('http://localhost:8008')

            # Fill in some test values
            page.fill('#pmp-x0', '[99.9, 11.1]')
            page.fill('#pmp-tf', '42.0')

            # Blur to ensure any formatters run and save happens
            page.evaluate("document.getElementById('pmp-x0').blur()")
            page.evaluate("document.getElementById('pmp-tf').blur()")

            time.sleep(0.5)

            # Reload page
            page.reload()

            time.sleep(0.5)

            # Verify values persisted
            x0_val = page.locator('#pmp-x0').input_value()
            tf_val = page.locator('#pmp-tf').input_value()

            print(f"Restored x0: {x0_val}")
            print(f"Restored tf: {tf_val}")

            if x0_val != '[99.9,11.1]' and x0_val != '[99.9, 11.1]':
                print(f"Test failed: Expected [99.9, 11.1] or [99.9,11.1], got {x0_val}")
                sys.exit(1)

            if tf_val != '42.0' and tf_val != '42':
                print(f"Test failed: Expected 42.0 or 42, got {tf_val}")
                sys.exit(1)

            print("Persistence test passed.")
            browser.close()
    finally:
        server.terminate()

if __name__ == "__main__":
    test_persistence()
