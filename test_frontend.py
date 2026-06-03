from playwright.sync_api import sync_playwright
import time
import sys
import subprocess

def test_form_inputs_disabled():
    server = subprocess.Popen(["python3", "-m", "http.server", "8001", "-d", "public"])
    time.sleep(1)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto('http://localhost:8001')

            # Check initial state
            inputs_initially_disabled = page.evaluate('''() => {
                const form = document.getElementById('pmp-form');
                const inputs = form.querySelectorAll('input');
                return Array.from(inputs).every(input => input.disabled === false);
            }''')

            if not inputs_initially_disabled:
                print("Error: Inputs were disabled initially!")
                sys.exit(1)

            print("Inputs are initially enabled.")

            # We want to pause the route response to check the disabled state mid-flight
            def handle_route(route):
                # Check the disabled state of inputs while the request is intercepted and pending
                inputs_disabled_during_fetch = page.evaluate('''() => {
                    const form = document.getElementById('pmp-form');
                    const inputs = form.querySelectorAll('input');
                    return Array.from(inputs).every(input => input.disabled === true);
                }''')
                if not inputs_disabled_during_fetch:
                    print("Error: Inputs are not disabled during fetch!")
                    route.abort()
                    sys.exit(1)
                else:
                    print("Inputs are successfully disabled during fetch.")
                route.fulfill(status=200, json={"t": [0], "x": [[0], [0]], "u": [[0]]})

            page.route('**/api/pmp', handle_route)

            page.click('#btn-pmp')

            # Wait for the network idle or fetch to complete
            page.wait_for_load_state('networkidle')

            # Check if inputs are enabled again
            inputs_enabled_after_fetch = page.evaluate('''() => {
                const form = document.getElementById('pmp-form');
                const inputs = form.querySelectorAll('input');
                return Array.from(inputs).every(input => input.disabled === false);
            }''')

            if not inputs_enabled_after_fetch:
                print("Error: Inputs were not enabled after fetch!")
                sys.exit(1)

            print("Inputs are enabled after fetch.")
            browser.close()
            print("Test passed successfully.")
    finally:
        server.terminate()
