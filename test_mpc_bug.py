import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        import os
        url = "file://" + os.path.abspath("public/index.html")
        await page.goto(url)

        # Print outerHTML of pmp-chart before
        html_before = await page.locator('#mpc-chart').evaluate("el => el.outerHTML")
        print("BEFORE:", html_before)

        # Type in the form
        await page.fill('#mpc-N', '30')

        # Give event listeners time to run
        await asyncio.sleep(0.5)

        # Print outerHTML of pmp-chart after
        html_after = await page.locator('#mpc-chart').evaluate("el => el.outerHTML")
        print("AFTER:", html_after)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
