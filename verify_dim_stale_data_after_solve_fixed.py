import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Load local page layout directly since we don't strictly need backend for UI tests
        import os
        url = "file://" + os.path.abspath("public/index.html")
        await page.goto(url)

        # Inject fake chart state
        await page.evaluate("""
            const chart = document.getElementById('pmp-chart');
            chart.style.display = 'block';
            chart.style.width = '100%';
            chart.style.height = '400px';
            chart.style.backgroundColor = '#1e1e90';
            chart.innerHTML = '<div style="color:white; padding: 10px;">Fake Chart Data</div>';
            chart.removeAttribute('data-empty');
        """)

        # Ensure it's not dimmed initially
        await page.evaluate("""
            const chart = document.getElementById('pmp-chart');
            chart.style.opacity = '1';
        """)

        # Verify initial opacity
        opacity = await page.locator('#pmp-chart').evaluate("el => el.style.opacity")
        print("Opacity before input edit:", opacity)

        # Dispatch input event on form
        await page.fill('#pmp-x0', '[1.0, 1.0]')
        await page.evaluate("document.getElementById('pmp-form').dispatchEvent(new Event('input'))")

        # Wait a moment
        await asyncio.sleep(0.5)

        # Verify stale opacity
        opacity = await page.locator('#pmp-chart').evaluate("el => el.style.opacity")
        print("Opacity after input edit:", opacity)

        # Call clearOutputStale
        await page.evaluate("window.clearOutputStale('pmp-chart')")

        # Wait a moment
        await asyncio.sleep(0.5)

        # Verify restored opacity
        opacity = await page.locator('#pmp-chart').evaluate("el => el.style.opacity")
        print("Opacity after clearOutputStale:", opacity)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
