import pytest
import os
import re
from playwright.sync_api import sync_playwright, expect
from python_playwright.pages.home_page import HomePage
from python_playwright.pages.pdp_page import PDPPage
from python_playwright.utils.reporter import Reporter

@pytest.fixture(scope="class")
def auth_context_tc015(request, env_config, browser_instance):
    """
    Session Reuse (Mandatory): Logs in once and reuses session using Storage State.
    If storage state does not exist, authenticates and creates it.
    """
    url = env_config["url"]
    username = env_config["username"]
    password = env_config["password"]
    
    config_dir = os.path.join(os.path.dirname(__file__), "..", "config")
    os.makedirs(config_dir, exist_ok=True)
    state_file = os.path.join(config_dir, "tc015_state.json")

    if not os.path.exists(state_file):
        temp_context = browser_instance.new_context(ignore_https_errors=True)
        temp_page = temp_context.new_page()
        temp_page.goto(url)
        
        home = HomePage(temp_page, url)
        home.handle_onetrust_cookie()
        login_page = home.verify_home_page().click_login()
        login_page.enter_username(username) \
            .enter_password(password) \
            .click_login_button()
            
        # Assert login was successful
        expect(temp_page.locator("id=Header_GlobalLogin_signOutQuickLinkUser")).to_be_visible(timeout=15000)
            
        temp_context.storage_state(path=state_file)
        temp_page.close()
        temp_context.close()

    context = browser_instance.new_context(
        storage_state=state_file,
        ignore_https_errors=True
    )
    context.set_default_timeout(30000)
    yield context
    context.close()

@pytest.fixture(scope="class")
def auth_page_tc015(auth_context_tc015):
    page = auth_context_tc015.new_page()
    yield page
    page.close()


@pytest.mark.usefixtures("auth_page_tc015")
class TestTC015BlankPDPValidation:
    
    def test_run_blank_pdp_validation(self, auth_page_tc015, env_config):
        Reporter.start_test_case(
            "TC015_BlankPDPValidation", 
            "Blank PDP Validation covering all 37 steps", 
            "Regression", 
            "SURIYAA"
        )
        
        url = env_config["url"]
        
        # 1. Navigate to URL and accept cookie banner
        Reporter.report_step(auth_page_tc015, "Step 1: Navigate to URL and accept cookie banner", "info", snap=False)
        auth_page_tc015.goto(url)
        home = HomePage(auth_page_tc015, url)
        home.handle_onetrust_cookie()
        auth_page_tc015.wait_for_timeout(2000)
        
        # 2. Verify home page
        Reporter.report_step(auth_page_tc015, "Step 2: Verify home page", "info", snap=False)
        home.verify_home_page()
        
        # 3. Search for product "795000"
        Reporter.report_step(auth_page_tc015, "Step 3: Search for product '795000'", "info", snap=False)
        pdp = home.search_product("795000")
        auth_page_tc015.wait_for_timeout(3000)
        
        # 4. Verify search product in PDP page
        Reporter.report_step(auth_page_tc015, "Step 4: Verify search product in PDP page", "info", snap=False)
        pdp.verify_search_product("795000")
        
        # 5. verify page navigates to https://www.momentecbrands.com/alleson-athletic-on-the-rise-two-button-baseball-jersey-795000
        Reporter.report_step(auth_page_tc015, "Step 5: Verify page navigation URL", "info", snap=False)
        pdp.verify_url_contains("alleson-athletic-on-the-rise-two-button-baseball-jersey-795000")
        
        # 6. Verify brand logo is showing on the PDP
        Reporter.report_step(auth_page_tc015, "Step 6: Verify brand logo is showing on the PDP", "info", snap=False)
        pdp.verify_brand_logo_on_pdp()
        
        # 7. Verify product title is showing on the PDP
        Reporter.report_step(auth_page_tc015, "Step 7: Verify product title is showing on the PDP", "info", snap=False)
        pdp.verify_product_title()
        
        # 8. Verify the product description is showing on the PDP
        Reporter.report_step(auth_page_tc015, "Step 8: Verify the product description is showing on the PDP", "info", snap=False)
        pdp.verify_product_description()
        
        # 9-13. Show more / Show less functionality
        Reporter.report_step(auth_page_tc015, "Steps 9-13: Verify show more/less functionality and description", "info", snap=False)
        pdp.verify_show_more_less_functionality()
        
        # 14-16. View spec link functionality
        Reporter.report_step(auth_page_tc015, "Steps 14-16: Verify View spec link functionality", "info", snap=False)
        pdp.verify_view_spec_link()
        
        # 17-18. View Inventory link functionality
        Reporter.report_step(auth_page_tc015, "Steps 17-18: Verify View Inventory link functionality", "info", snap=False)
        pdp.verify_view_inventory_link()
        
        # 19-21. View sizing info functionality
        Reporter.report_step(auth_page_tc015, "Steps 19-21: Verify View sizing info link functionality", "info", snap=False)
        pdp.verify_view_sizing_info_link()
        
        # 22-23. Hero and Angle images
        Reporter.report_step(auth_page_tc015, "Steps 22-23: Verify Hero and angle images", "info", snap=False)
        pdp.verify_hero_and_angle_images()
        
        # 24. Different color thumbnails
        Reporter.report_step(auth_page_tc015, "Step 24: Verify that the different color thumbnails are showing", "info", snap=False)
        pdp.verify_color_thumbnails()
        
        # 25-26. Placeholder state without color selected
        Reporter.report_step(auth_page_tc015, "Steps 25-26: Verify placeholder state without color selected", "info", snap=False)
        pdp.verify_placeholder_empty()
        
        # 27. Placeholder state with color selected
        Reporter.report_step(auth_page_tc015, "Step 27: Verify selected colors shown on the place holder", "info", snap=False)
        pdp.verify_placeholder_with_color()
        
        # 28-30. ShowPrice/Hide Price toggle
        Reporter.report_step(auth_page_tc015, "Steps 28-30: Verify Show/Hide Price toggle functionality", "info", snap=False)
        pdp.verify_show_hide_price_toggle()
        
        # 31. Similar style section
        Reporter.report_step(auth_page_tc015, "Step 31: Verify similar style section", "info", snap=False)
        pdp.verify_similar_styles_section()
        
        # 32. Enter quantities in textbox
        Reporter.report_step(auth_page_tc015, "Step 32: Verify able to enter quantities", "info", snap=False)
        pdp.enter_quantity("795000")
        
        # 33. Add to cart from PDP page
        Reporter.report_step(auth_page_tc015, "Step 33: Verify able to add to cart from PDP page", "info", snap=False)
        pdp.add_to_cart()
        
        # 34. Minicart should popup
        Reporter.report_step(auth_page_tc015, "Step 34: Verify minicart should popup", "info", snap=False)
        pdp.verify_mini_shop_cart()
        
        # 35-36. Minicart buttons (Go To Cart, Continue Shopping)
        Reporter.report_step(auth_page_tc015, "Steps 35-36: Verify minicart buttons", "info", snap=False)
        pdp.verify_minicart_buttons()
        
        # 37. Collection styles section
        Reporter.report_step(auth_page_tc015, "Step 37: Verify collection styles are showing on the PDP", "info", snap=False)
        pdp.verify_collection_styles_section()

