from playwright.sync_api import sync_playwright
import time
import subprocess
import sys

def test_inline_a11y():
    server = subprocess.Popen(["python3", "-m", "http.server", "8010", "-d", "public"])
    time.sleep(1)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto('http://localhost:8010')

            # We will patch the announceA11y to see if it is called correctly
            page.evaluate('''() => {
                window.lastAnnounce = null;
                const orig = announceA11y;
                announceA11y = function(msg) {
                    window.lastAnnounce = msg;
                    orig(msg);
                };
            }''')

            # Focus the input, make it invalid, then blur (focusout)
            page.click('#pmp-x0')
            page.fill('#pmp-x0', '')
            page.type('#pmp-x0', 'invalid_json')

            # Click somewhere else to trigger focusout
            page.click('body')

            time.sleep(0.5)

            last_announce = page.evaluate("window.lastAnnounce")
            print(f"Last announcement: {last_announce}")

            if not last_announce:
                print("BUG: Announcement was not triggered on focusout!")
                sys.exit(1)
            elif "Error in" not in last_announce:
                print(f"BUG: Announcement didn't contain 'Error in', got: {last_announce}")
                sys.exit(1)
            elif "Initial State (x0)" not in last_announce:
                print(f"BUG: Announcement didn't contain label 'Initial State (x0)', got: {last_announce}")
                sys.exit(1)
            else:
                print("Test passed: focusout triggers correct a11y announcement.")

            browser.close()
    finally:
        server.terminate()

if __name__ == "__main__":
    test_inline_a11y()
