from playwright.sync_api import sync_playwright
import os
import json

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Using the saved state from config/tc009_state.json
        state_file = os.path.join(os.path.dirname(__file__), "..", "config", "tc009_state.json")
        context = browser.new_context(storage_state=state_file, ignore_https_errors=True)
        page = context.new_page()
        
        url = "https://stage.momentecbrands.com/FreeStyleSublimationView?catalogId=10601&storeId=10251&langId=-1"
        page.goto(url)
        page.wait_for_load_state("networkidle", timeout=30000)
        
        print("Title:", page.title())
        
        # Check if text FreeStyle Sublimation is on the page
        count = page.locator("text=/FreeStyle Sublimation/i").count()
        print("Count of FreeStyle Sublimation text:", count)
        
        # Check if 'h1' has it
        h1s = page.locator("h1").all_inner_texts()
        print("H1s:", h1s)
        
        # Check if 'h2' has it
        h2s = page.locator("h2").all_inner_texts()
        print("H2s:", h2s)
        
        browser.close()

if __name__ == "__main__":
    run()
