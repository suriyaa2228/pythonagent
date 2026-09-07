import sys
from playwright.sync_api import sync_playwright

def test_iframe():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        url = "https://stage.momentecbrands.com/Configurator?catalogId=10601&partNumber=CUT_227232&configuratorType=uniforms&storeId=10251&langId=-1"
        print(f"Navigating to {url}", flush=True)
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print(f"Goto failed: {e}", flush=True)
            
        print("Waiting 30 seconds for app to load...", flush=True)
        page.wait_for_timeout(30000)
        
        print("Finding all elements containing 'Color'...", flush=True)
        locators = page.locator("text=/Color/i")
        count = locators.count()
        print(f"Found {count} elements containing 'Color'.", flush=True)
        
        for i in range(count):
            try:
                el = locators.nth(i)
                is_visible = el.is_visible()
                tag_name = el.evaluate("node => node.tagName")
                class_name = el.evaluate("node => node.className")
                text = el.inner_text().strip()
                html = el.evaluate("node => node.outerHTML")
                
                print(f"\n--- Element {i+1} ---", flush=True)
                print(f"Visible: {is_visible}", flush=True)
                print(f"Tag: {tag_name}", flush=True)
                print(f"Class: {class_name}", flush=True)
                print(f"Text: {text}", flush=True)
                print(f"HTML: {html[:200]}...", flush=True) 
            except Exception as e:
                print(f"Error reading element {i}: {e}", flush=True)
                
        browser.close()

if __name__ == "__main__":
    test_iframe()
