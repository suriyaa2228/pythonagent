from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        url = "https://stage.momentecbrands.com/"
        print("Navigating to home...")
        page.goto(url)
        
        print("Clicking login...")
        page.locator("id=Header_GlobalLogin_signInQuickLink").click(timeout=15000)
        
        print("Filling credentials...")
        page.locator("id=Header_GlobalLogin_WC_AccountDisplay_FormInput_logonId_In_Logon_1").fill("SURIYAA")
        page.locator("id=Header_GlobalLogin_WC_AccountDisplay_FormInput_logonPassword_In_Logon_1").fill("Augusta@2022!!!")
        
        print("Submitting login...")
        page.locator("id=Header_GlobalLogin_WC_AccountDisplay_links_2").click()
        
        print("Waiting for network idle...")
        page.wait_for_load_state("networkidle")
        
        sublimation_url = f"{url.rstrip('/')}/FreeStyleSublimationView?catalogId=10601&storeId=10251&langId=-1"
        print(f"Navigating to {sublimation_url}...")
        page.goto(sublimation_url)
        
        print("Waiting for load...")
        page.wait_for_load_state("networkidle")
        
        title = page.title()
        print(f"Page Title: {title}")
        
        print("Checking locators...")
        # Date field
        date_fields = page.locator("text=/Please select a date/i").count()
        date_placeholders = page.get_by_placeholder("Please select a date").count()
        print(f"Date fields text: {date_fields}, placeholder: {date_placeholders}")
        
        # Search field
        search_inputs = page.locator("input[type='search'], input[placeholder*='Search'], input[name*='search']").count()
        search_btns = page.locator("button[type='submit'], button:has-text('Search'), input[value='Search']").count()
        print(f"Search inputs: {search_inputs}, buttons: {search_btns}")
        
        # Clear results
        clear_links = page.locator("text=/Clear [rR]esults/i").count()
        print(f"Clear results links: {clear_links}")
        
        # Start new design
        start_links = page.locator("text=/Start [nN]ew [dD]esign/i").count()
        print(f"Start new design links: {start_links}")
        
        print("Done.")
        browser.close()

if __name__ == "__main__":
    run()
