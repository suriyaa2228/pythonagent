from playwright.sync_api import sync_playwright
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        state_file = os.path.join(os.path.dirname(__file__), "..", "config", "tc009_state.json")
        context = browser.new_context(storage_state=state_file, ignore_https_errors=True)
        page = context.new_page()
        
        url = "https://stage.momentecbrands.com/FreeStyleSublimationView?catalogId=10601&storeId=10251&langId=-1"
        page.goto(url)
        page.wait_for_load_state("networkidle", timeout=30000)
        
        print("Select elements:")
        selects = page.locator("select").all()
        for i, s in enumerate(selects):
            try:
                print(f"Select {i} text: {s.inner_text()}")
            except: pass
            
        print("Divs containing 'date' or 'Please select':")
        divs = page.locator("div:has-text('Please select')").all_inner_texts()
        for text in divs:
            if len(text.strip()) > 0 and len(text) < 100:
                print(f" - {text.strip()}")

        print("Any text containing 'Please':")
        pls = page.locator("*:has-text('Please')").all_inner_texts()
        for text in pls:
            if len(text.strip()) > 0 and len(text) < 100:
                print(f" - {text.strip()}")

        browser.close()

if __name__ == "__main__":
    run()
