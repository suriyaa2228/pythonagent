from playwright.sync_api import sync_playwright

def get_header_html():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('https://stage.momentecbrands.com/')
        header = page.locator('header').first
        if header:
            print(header.inner_html())
        browser.close()

if __name__ == '__main__':
    get_header_html()
