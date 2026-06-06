from playwright.sync_api import sync_playwright
import time
import subprocess
import sys

def test_copy_btn_focus():
    server = subprocess.Popen(["python3", "-m", "http.server", "8002", "-d", "public"])
    time.sleep(1)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Context needs clipboard permissions
            context = browser.new_context(permissions=['clipboard-read', 'clipboard-write'])
            page = context.new_page()
            page.goto('http://localhost:8002')

            # We need to simulate the LQR synthesis to show the output block containing copy buttons
            page.route('**/api/lqr', lambda route: route.fulfill(status=200, json={"K": [[0,0]], "eigvals": [0,0]}))
            page.click('#btn-lqr')
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(500) # Give it a moment to show the output

            # Focus the first copy button
            copy_btn = page.locator('.copy-btn').first
            copy_btn.focus()

            # Verify initial focus
            is_focused = page.evaluate('document.activeElement === document.querySelector(".copy-btn")')
            assert is_focused, "Copy button should be focused initially"

            # Click it by pressing Enter (keyboard interaction)
            page.keyboard.press('Enter')

            # Verify it's still focused immediately after
            is_focused_after_click = page.evaluate('document.activeElement === document.querySelector(".copy-btn")')
            assert is_focused_after_click, "Copy button should still be focused during the 2-second timeout"

            # Wait for timeout to complete
            page.wait_for_timeout(2500)

            print("Test passed: copy-btn maintained focus successfully")
            browser.close()
    finally:
        server.terminate()

if __name__ == "__main__":
    test_copy_btn_focus()
