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
        
        screenshot_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", ".gemini", "antigravity-ide", "brain", "83423497-0bc9-4d92-9266-edf635e69fdb", "freestyle_screenshot.png")
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"Screenshot saved to {screenshot_path}")

        browser.close()

if __name__ == "__main__":
    run()
