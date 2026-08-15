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
        
        print("Inputs with placeholders:")
        inputs = page.locator("input").all()
        for i in inputs:
            try:
                ph = i.get_attribute("placeholder")
                if ph: print(f" - {ph}")
            except: pass
            
        print("Labels containing 'date':")
        labels = page.locator("label").all_inner_texts()
        for lbl in labels:
            if 'date' in lbl.lower():
                print(f" - {lbl.strip()}")
                
        print("Any text containing 'date':")
        date_texts = page.locator("*:has-text('date')").all_inner_texts()
        for text in date_texts:
            if len(text.strip()) > 0 and len(text) < 100:
                print(f" - {text.strip()}")

        browser.close()

if __name__ == "__main__":
    run()
