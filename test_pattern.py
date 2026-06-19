from playwright.sync_api import sync_playwright
import time
import subprocess

def test_user_valid_false_positive():
    server = subprocess.Popen(["python3", "-m", "http.server", "8003", "-d", "public"])
    time.sleep(1)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto('http://localhost:8003')

            # Click the input to focus and interact
            page.click('#pmp-x0')
            page.fill('#pmp-x0', '')
            page.type('#pmp-x0', '1')

            # Wait a bit
            time.sleep(0.5)

            # Check if it has the valid background
            bg_image = page.evaluate('''() => {
                const el = document.getElementById('pmp-x0');
                const style = window.getComputedStyle(el);
                return style.backgroundImage;
            }''')

            validity = page.evaluate('''() => {
                const el = document.getElementById('pmp-x0');
                return el.validity.valid;
            }''')

            print(f"Background image while typing '1': {bg_image}")
            print(f"Is valid natively? {validity}")

            browser.close()
    finally:
        server.terminate()

if __name__ == "__main__":
    test_user_valid_false_positive()
