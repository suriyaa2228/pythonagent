# Momentec Python Playwright Automation Framework

This repository contains the End-to-End (E2E) automated test suite for the Momentec Brands eCommerce websites (e.g., Augusta, Badger, Alleson, C2 Sport). It is built using **Python 3.12**, **Playwright**, and **Pytest**, designed with a robust Page Object Model (POM) architecture.

## 🚀 Key Technologies
- **Python**: Primary programming language (v3.12+).
- **Playwright (Sync API)**: Modern cross-browser web automation tool providing robust execution and dynamic auto-waiting capabilities.
- **Pytest**: Test execution framework used for parallelization, fixtures, and assertions.
- **Custom Extent Reporter**: Generates interactive HTML reports after test runs with embedded failure screenshots.

## 📁 Project Structure
```text
python_playwright/
│
├── config/                 # Environment configurations (config.json) & saved application states (.json)
├── pages/                  # Page Object classes (POM) encapsulating UI locators and actions
│   ├── base_page.py        # Core utility methods shared across all pages
│   ├── plp_page.py         # Product Listing Page interactions (Filters, Sorting)
│   ├── review_submit_page.py # Checkout review and submission actions
│   └── ...                 # Other page classes
│
├── reports/                # Output directory for HTML Execution Reports and failure screenshots
├── tests/                  # Pytest test scripts (Test cases)
│   ├── conftest.py         # Pytest fixtures and hooks (Browser initialization, Reporting hooks)
│   └── test_*.py           # Individual test scenarios
│
├── utils/                  # Helper utilities and framework-level tools
│   └── reporter.py         # Custom HTML Execution report generator
│
├── pytest.ini              # Pytest configuration file (CLI flags, reruns, logging)
└── requirements.txt        # Python dependency list
```

## 🛠️ Setup & Installation
1. **Clone the Repository**
2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Install Playwright Browsers:**
   ```bash
   playwright install chromium
   ```

## 🏃 Running Tests

The test suite uses `pytest`. The default configurations in `pytest.ini` automatically apply 2 retries for failed tests and enforce verbose logging.

**Run the entire test suite:**
```bash
pytest
```

**Run a specific test script:**
```bash
pytest tests/test_tc014_blank_plp_validation.py
```

**Run in Headless mode:**
```bash
pytest --headless
```

**Run against a specific environment:**
By default, tests run against the `stage` environment. You can specify a different environment (e.g., `prod`, `dev`) configured in `config.json`:
```bash
pytest --env prod
```

## 📊 Reporting
The framework generates a custom, interactive HTML report upon the completion of a test session.
- Reports are saved in the `reports/` directory with a timestamped filename (e.g., `extent_report_YYYYMMDD_HHMMSS.html`).
- The report logs all steps dynamically using the `Reporter.report_step()` method.
- **Failure Screenshots** are automatically captured and embedded into the HTML report for quick debugging.

## 🏗️ Design Principles
1. **Page Object Model (POM):** UI Locators and page-specific logic are abstracted into the `pages/` directory. Tests in `tests/` should only call page methods and refrain from directly interacting with the DOM.
2. **Network Idle Waits:** Instead of using hardcoded sleeps (e.g., `time.sleep()`), the framework relies on Playwright's `networkidle` state to wait for complex AJAX calls (like filtering or sorting) to resolve.
3. **Resiliency:** The framework utilizes `pytest-rerunfailures` to automatically retry flaky tests up to 2 times before marking them as failed.
