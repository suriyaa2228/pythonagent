from playwright.sync_api import sync_playwright

def test_iframe():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        url = "https://stage.momentecbrands.com/Configurator?catalogId=10601&partNumber=CUT_227232&configuratorType=uniforms&storeId=10251&langId=-1"
        print(f"Navigating to {url}")
        page.goto(url)
        page.wait_for_timeout(30000)
        
        locators = page.locator("text=/Color/i")
        count = locators.count()
        print(f"Found {count} elements containing 'Color'.")
        
        for i in range(count):
            try:
                el = locators.nth(i)
                is_visible = el.is_visible()
                tag_name = el.evaluate("node => node.tagName")
                class_name = el.evaluate("node => node.className")
                text = el.inner_text().strip()
                html = el.evaluate("node => node.outerHTML")
                
                print(f"\n--- Element {i+1} ---")
                print(f"Visible: {is_visible}")
                print(f"Tag: {tag_name}")
                print(f"Class: {class_name}")
                print(f"Text: {text}")
                print(f"HTML: {html[:200]}...") # truncate HTML
            except Exception as e:
                print(f"Error reading element {i}: {e}")
                
        browser.close()

if __name__ == "__main__":
    test_iframe()
