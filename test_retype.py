from playwright.sync_api import sync_playwright
import time
import subprocess
import sys

def test_user_valid_retype():
    server = subprocess.Popen(["python3", "-m", "http.server", "8005", "-d", "public"])
    time.sleep(1)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto('http://localhost:8005')

            # Type '1' and blur to trigger invalid
            page.fill('#pmp-x0', '')
            page.type('#pmp-x0', '1')
            page.evaluate("document.getElementById('pmp-x0').blur()")

            time.sleep(0.5)

            invalid_bg = page.evaluate('''() => {
                const el = document.getElementById('pmp-x0');
                return window.getComputedStyle(el).backgroundImage;
            }''')
            print(f"After typing '1' and blur (expect red X): {invalid_bg}")

            # Now type `[` so value is `1[`
            page.focus('#pmp-x0')
            page.type('#pmp-x0', '[')

            time.sleep(0.5)

            retype_bg = page.evaluate('''() => {
                const el = document.getElementById('pmp-x0');
                return window.getComputedStyle(el).backgroundImage;
            }''')
            validity = page.evaluate("document.getElementById('pmp-x0').validity.valid")

            print(f"After typing '[' (value is '1['). Is valid natively? {validity}")
            print(f"Background image while typing '1[': {retype_bg}")

            if "50e3c2" in retype_bg:
                print("Test failed: Green checkmark showing while typing.")
                sys.exit(1)

            page.fill('#pmp-x0', '')
            page.type('#pmp-x0', '[1]')
            page.evaluate("document.getElementById('pmp-x0').blur()")
            time.sleep(0.5)

            valid_bg = page.evaluate('''() => {
                const el = document.getElementById('pmp-x0');
                return window.getComputedStyle(el).backgroundImage;
            }''')
            print(f"After typing '[1]' and blur: {valid_bg}")
            if "50e3c2" not in valid_bg:
                print("Test failed: Green checkmark not showing for valid input.")
                sys.exit(1)

            browser.close()
    finally:
        server.terminate()

if __name__ == "__main__":
    test_user_valid_retype()
