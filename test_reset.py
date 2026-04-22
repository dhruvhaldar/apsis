from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("http://localhost:8000")

    page.wait_for_selector('#pmp-x0')
    page.fill('#pmp-x0', '[1.0, 1.0]')
    page.click('#btn-pmp')
    page.wait_for_selector('#pmp-chart.js-plotly-plot')

    # Check if opacity is reset
    opacity = page.locator('#pmp-chart').evaluate("el => el.style.opacity")
    print("Opacity after first solve:", repr(opacity))

    # Trigger input change
    page.fill('#pmp-x0', '[2.0, 2.0]')
    page.wait_for_timeout(500)

    # Check if opacity is 0.5
    opacity = page.locator('#pmp-chart').evaluate("el => el.style.opacity")
    print("Opacity after input change:", repr(opacity))

    # Solve again
    page.click('#btn-pmp')
    page.wait_for_timeout(1000)

    # Check if opacity is reset
    opacity = page.locator('#pmp-chart').evaluate("el => el.style.opacity")
    print("Opacity after second solve:", repr(opacity))

    browser.close()
