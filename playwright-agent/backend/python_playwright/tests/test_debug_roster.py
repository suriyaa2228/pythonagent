import pytest
import os

def test_debug_roster(browser_instance):
    context = browser_instance.new_context(ignore_https_errors=True)
    page = context.new_page()
    
    print("\\nNavigating to configurator...")
    page.goto("https://stage.momentecbrands.com/Configurator?catalogId=10601&partNumber=CUT_227232&configuratorType=uniforms&storeId=10251&langId=-1", timeout=60000)
    
    try:
        page.locator("id=onetrust-accept-btn-handler").click(timeout=5000)
    except:
        pass
        
    print("Clicking Roster tab directly...")
    try:
        page.locator("text='4. ROSTER'").click(timeout=10000)
        page.wait_for_timeout(3000)
        
        print("\\n--- DEBUG ROSTER HTML ---")
        # Dump all inputs, buttons, and select tags
        elements = page.locator("button, a, input, select").all()
        for el in elements:
            if el.is_visible():
                tag = el.evaluate("e => e.tagName")
                text = el.inner_text().strip() if tag != "INPUT" else el.input_value()
                print(f"<{tag}> class='{el.get_attribute('class')}' id='{el.get_attribute('id')}' type='{el.get_attribute('type')}'> {text}")
        print("-------------------------\\n")
    except Exception as e:
        print("Failed:", e)
        
    page.close()
    context.close()
