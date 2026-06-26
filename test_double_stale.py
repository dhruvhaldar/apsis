from playwright.sync_api import sync_playwright
import time
import subprocess
import sys

def test_double_stale():
    server = subprocess.Popen(["python3", "-m", "http.server", "8008", "-d", "public"])
    time.sleep(1)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto('http://localhost:8008')

            # Show the output for lqr
            page.evaluate('''() => {
                const el = document.getElementById('lqr-output');
                el.style.display = 'block';
                el.style.opacity = '1';
                el.removeAttribute('aria-hidden');
            }''')

            # We will patch the announceA11y to see if it is called multiple times
            page.evaluate('''() => {
                window.announceCallCount = 0;
                const orig = announceA11y;
                announceA11y = function(msg) {
                    if (msg.includes('stale')) {
                        window.announceCallCount++;
                    }
                    orig(msg);
                };
            }''')

            # Wait a moment
            time.sleep(0.5)

            # Type in lqr-A to mark it as stale
            page.fill('#lqr-A', '')
            page.type('#lqr-A', '[[1]]')

            time.sleep(0.5)

            count = page.evaluate("window.announceCallCount")
            print(f"Stale announcement call count: {count}")

            if count > 1:
                print("BUG: Announcement called multiple times!")
                sys.exit(1)
            elif count == 1:
                print("Test passed: called exactly once.")
            else:
                print("BUG: Not called at all.")
                sys.exit(1)

            browser.close()
    finally:
        server.terminate()

if __name__ == "__main__":
    test_double_stale()
