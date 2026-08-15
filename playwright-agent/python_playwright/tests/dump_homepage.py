from playwright.sync_api import sync_playwright
def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://stage.momentecbrands.com/")
        page.wait_for_load_state("networkidle")
        with open("homepage_dump.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        browser.close()
if __name__ == "__main__":
    run()

