import os
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://stage.momentecbrands.com/")
        page.locator("id=Header_GlobalLogin_signInQuickLink").click()
        
        username = os.environ.get("MOMENTEC_USERNAME", "testaccount1@momentecbrands.com")
        password = os.environ.get("MOMENTEC_PASSWORD", "Test@123")
        
        page.locator("//input[@id='Header_GlobalLogin_WC_AccountDisplay_FormInput_logonId_In_Logon_1']").fill(username)
        page.locator("//input[@name='logonPassword']").fill(password)
        page.locator("text=LOGIN").click()
        
        # wait for user icon
        page.wait_for_selector("id=Header_GlobalLogin_signOutQuickLinkUser")
        page.locator("id=Header_GlobalLogin_signOutQuickLinkUser").click()
        
        page.wait_for_timeout(2000)
        
        # Click My Account
        page.locator("//a[translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='my account'] | //a[contains(text(), 'My Account')] | //a[contains(text(), 'My account')]").click()
        
        page.wait_for_load_state("networkidle", timeout=10000)
        
        html = page.content()
        with open("dashboard_dump.html", "w", encoding='utf-8') as f:
            f.write(html)
            
        browser.close()

if __name__ == "__main__":
    run()
