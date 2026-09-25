import pytest
import json
import os
from playwright.sync_api import sync_playwright

try:
    from dotenv import load_dotenv
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(os.path.join(base_dir, ".env"))
    load_dotenv(os.path.join(base_dir, "..", ".env"))
except ImportError:
    pass

def pytest_addoption(parser):
    parser.addoption("--env", action="store", default="stage", help="Environment to run tests against (dev, stage, prod)")
    parser.addoption("--headless", action="store_true", default=False, help="Run browser in headless mode")

@pytest.fixture(scope="session")
def env(request):
    return request.config.getoption("--env")

@pytest.fixture(scope="session")
def env_config(request):
    env_name = (request.config.getoption("--env") or os.environ.get("ENV") or "stage").lower()
    # Locate configuration file relative to this conftest.py
    config_path = os.path.join(os.path.dirname(__file__), "config", "config.json")
    
    config = {}
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = json.load(f)

    env_data = config.get(env_name, {})

    # Override or fallback from environment variables
    env_upper = env_name.upper()
    url = os.environ.get(f"{env_upper}_URL") or env_data.get("url")
    username = os.environ.get(f"{env_upper}_USERNAME") or env_data.get("username")
    password = os.environ.get(f"{env_upper}_PASSWORD") or env_data.get("password")

    if not url:
        raise ValueError(f"Environment '{env_name}' missing configuration or environment variables.")

    return {
        "url": url,
        "username": username or "",
        "password": password or ""
    }

@pytest.fixture(scope="class")
def browser_instance(request):
    headless = request.config.getoption("--headless")
    playwright_ctx = sync_playwright().start()
    browser = playwright_ctx.chromium.launch(
        headless=headless,
        args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu-sandbox",
            "--ignore-gpu-blocklist",
            "--disable-notifications",
            "--window-size=1440,900"
        ]
    )
    yield browser
    browser.close()
    playwright_ctx.stop()

@pytest.fixture(scope="class")
def page_instance(request, browser_instance):
    # Share a single context and page across all tests in a test class
    # to emulate TestNG @BeforeClass behaviour
    context = browser_instance.new_context(
        viewport={"width": 1440, "height": 900},
        ignore_https_errors=True
    )
    context.set_default_timeout(30000)
    page = context.new_page()
    yield page
    page.close()
    context.close()

def pytest_sessionstart(session):
    from python_playwright.utils.reporter import Reporter
    Reporter.start_report()

def pytest_sessionfinish(session, exitstatus):
    from python_playwright.utils.reporter import Reporter
    Reporter.end_result()

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    if rep.failed:
        from python_playwright.utils.reporter import Reporter
        error_msg = str(call.excinfo.value) if hasattr(call, 'excinfo') and call.excinfo else "Test failed"
        
        # Determine if this is a setup failure where the test case might not have been started
        if rep.when == "setup" and not Reporter._current_test:
            Reporter.start_test_case(item.name, "Failed during setup")
            
        # Log the failure to the Reporter without raising an AssertionError
        # and attach the exception message
        step_desc = f"Test failed during {rep.when}: {error_msg}"
        Reporter.report_step(None, step_desc, "FAIL", snap=False, raise_error=False)
