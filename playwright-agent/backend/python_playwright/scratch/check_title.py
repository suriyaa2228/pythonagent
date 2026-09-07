from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://stage.momentecbrands.com/")
    print(f"Title: {page.title()}")
    browser.close()
