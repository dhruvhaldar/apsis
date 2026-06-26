from playwright.sync_api import sync_playwright
import time
import subprocess
import sys

def test_lqr_stale():
    server = subprocess.Popen(["python3", "-m", "http.server", "8008", "-d", "public"])
    time.sleep(1)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto('http://localhost:8008')

            # Synthesize will fail since we don't have the API running here, so we will use the page.evaluate
            # to artificially show the output and make sure the logic is tested correctly
            page.evaluate('''() => {
                const el = document.getElementById('lqr-output');
                el.style.display = 'block';
                el.style.opacity = '1';
                el.removeAttribute('aria-hidden');
            }''')

            # Wait a moment
            time.sleep(0.5)

            # Type in lqr-A to mark it as stale
            page.fill('#lqr-A', '')
            page.type('#lqr-A', '[[1]]')

            time.sleep(0.5)

            announcer_text = page.evaluate('''() => {
                return document.getElementById('a11y-announcer').textContent;
            }''')

            print(f"Announcer text after first typing: {announcer_text}")

            if "stale" not in announcer_text:
                print("BUG: Screen reader failed to announce stale output!")
                sys.exit(1)
            else:
                print("Announcement was correct. Checking if output block is visually stale.")

            is_stale = page.evaluate('''() => {
                const el = document.getElementById('lqr-output');
                return el.style.opacity === '0.5' && el.getAttribute('aria-hidden') === 'true';
            }''')

            if not is_stale:
                print("BUG: Output block is not visually stale!")
                sys.exit(1)
            else:
                print("Test passed.")

            browser.close()
    finally:
        server.terminate()

if __name__ == "__main__":
    test_lqr_stale()
