---
name: playwright-generator-agent
description: Generates production-grade, AST-validated Python Playwright scripts aligned with Page Object Models, pytest fixtures, and Extent Reporter calls.
---

# Playwright Generator Agent Skill

## Overview
Generates production-ready, AST-validated Python Playwright test scripts strictly adhering to the Momentec test suite architecture (`auth_context_tcXXX`, `auth_page_tcXXX` storage state fixtures, Page Object Models, and `Reporter` logging).

## Framework Rules & Template

### 1. Mandatory Storage State Caching Fixtures
```python
@pytest.fixture(scope="class")
def auth_context_tcXXX(request, env_config, browser_instance):
    url = env_config["url"]
    username = env_config["username"]
    password = env_config["password"]
    
    config_dir = os.path.join(os.path.dirname(__file__), "..", "config")
    os.makedirs(config_dir, exist_ok=True)
    state_file = os.path.join(config_dir, "tcXXX_state.json")

    if not os.path.exists(state_file):
        temp_context = browser_instance.new_context(ignore_https_errors=True, no_viewport=True)
        temp_page = temp_context.new_page()
        temp_page.goto(url)
        
        home = HomePage(temp_page, url)
        home.handle_onetrust_cookie()
        login_page = home.verify_home_page().click_login()
        login_page.enter_username(username).enter_password(password).click_login_button()
        expect(temp_page.locator("id=Header_GlobalLogin_signOutQuickLinkUser")).to_be_visible(timeout=15000)
            
        temp_context.storage_state(path=state_file)
        temp_page.close()
        temp_context.close()

    context = browser_instance.new_context(storage_state=state_file, ignore_https_errors=True, no_viewport=True)
    context.set_default_timeout(30000)
    yield context
    context.close()

@pytest.fixture(scope="class")
def auth_page_tcXXX(auth_context_tcXXX):
    page = auth_context_tcXXX.new_page()
    yield page
    page.close()
```

### 2. Test Class & Extent Reporter Structure
```python
@pytest.mark.usefixtures("auth_page_tcXXX")
class TestTCXXXName:
    def test_tcXXX_description(self, auth_page_tcXXX, env_config):
        Reporter.start_test_case("TCXXX_TestName", "Description of test case", "E2E", "QA")
        # Step execution using Page Objects
```

