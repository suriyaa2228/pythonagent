from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://stage.momentecbrands.com/")

    
    selector_str = "//a[contains(text(),'Info & Resources') or contains(text(),'RESOURCES') or contains(text(),'Resources')]"
    
    # Let's find all elements matching the exact XPath used in the test
    links = page.locator(f"xpath={selector_str}")
    count = links.count()
    print(f"Found {count} matching links for xpath={selector_str}")
    for i in range(count):
        print(f"Link {i}: Is visible: {links.nth(i).is_visible()}")
        try:
            print(f"  HTML: {links.nth(i).evaluate('node => node.outerHTML')}")
        except Exception as e:
            print(f"  Could not get HTML: {e}")
        
    browser.close()
