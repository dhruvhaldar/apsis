from playwright.sync_api import sync_playwright
import time
import subprocess

def test_user_valid_false_positive():
    server = subprocess.Popen(["python3", "-m", "http.server", "8002", "-d", "public"])
    time.sleep(1)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto('http://localhost:8002')

            # Clear and type
            page.fill('#pmp-x0', '')
            page.type('#pmp-x0', 'abc')

            # Check if it has the valid background
            valid_bg = page.evaluate('''() => {
                const el = document.getElementById('pmp-x0');
                return window.getComputedStyle(el).backgroundImage;
            }''')

            print(f"Background image while typing 'abc': {valid_bg}")

            if '50e3c2' in valid_bg:
                print("BUG: False positive green checkmark shown while typing invalid JSON!")
            else:
                print("No false positive.")

            browser.close()
    finally:
        server.terminate()

if __name__ == "__main__":
    test_user_valid_false_positive()
