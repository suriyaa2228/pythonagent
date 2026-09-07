from playwright.sync_api import sync_playwright
def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://stage.momentecbrands.com/")
        print("Page loaded.")
        # Find all a tags in the main navigation
        nav_links = page.locator(".navigation a, .nav a, header a").all()
        for link in nav_links:
            text = link.inner_text().strip()
            if text:
                print(f"LINK: {text} | HREF: {link.get_attribute('href')}")
        browser.close()
if __name__ == "__main__":
    run()

