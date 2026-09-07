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
        
        frames = page.frames
        print(f"Total frames: {len(frames)}")
        for i, frame in enumerate(frames):
            print(f"Frame {i}: name='{frame.name}', url='{frame.url}'")
            try:
                # search for "select a date" inside each frame
                count = frame.locator("text=/Please select a date/i").count()
                print(f"  - Occurrences of 'Please select a date': {count}")
                if count > 0:
                    inputs = frame.locator("input[placeholder*='date' i]").count()
                    print(f"  - Date placeholder inputs: {inputs}")
            except Exception as e:
                print(f"  - Error interacting with frame: {e}")

        browser.close()

if __name__ == "__main__":
    run()
