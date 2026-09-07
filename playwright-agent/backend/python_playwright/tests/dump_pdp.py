import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()
        print("Navigating...")
        await page.goto("https://stage.momentecbrands.com/alleson-athletic-on-the-rise-two-button-baseball-jersey-795000")
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(3000)
        print("Dumping...")
        content = await page.content()
        with open("c:\\Users\\SuriyaaP\\momentecautomation\\Momentec_Automation\\python_playwright\\tests\\pdp_dump.html", "w", encoding="utf-8") as f:
            f.write(content)
        await browser.close()
        print("Done.")

if __name__ == "__main__":
    asyncio.run(main())
