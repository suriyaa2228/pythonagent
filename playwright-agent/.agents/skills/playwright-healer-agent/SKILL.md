---
name: playwright-healer-agent
description: Analyzes execution failures, stack traces, and DOM dumps to auto-repair broken locators and Playwright test scripts.
---

# Playwright Healer Agent Skill

## Overview
Analyzes Playwright test execution stack traces, error logs, and DOM dumps to diagnose root causes (stale element IDs, dynamic locators, timing issues, or invalid syntax) and automatically repair failing Python Playwright test scripts.

## Framework Healing Rules
1. **Preserve Fixtures & Storage State**: Maintain `@pytest.fixture(scope="class") def auth_context_tcXXX` storage state caching and `@pytest.mark.usefixtures("auth_page_tcXXX")`.
2. **Preserve Extent Reporter Logging**: Maintain `Reporter.start_test_case(...)` and `Reporter.report_step(page, description, status)` calls.
3. **Avoid Unqualified `.first` Locators**: Replace un-parameterized `.first` queries with explicit style/product parameters (e.g. `custom_sublimation_page.click_customize_on_product("227232")`).
4. **Fix Invalid CSS/Playwright Selectors**: Ensure locator strings use valid CSS/Playwright syntax (e.g., replace invalid `text='Browse'` with `:has-text("Browse")` or `text="Browse"`).
5. **Output**: Return the repaired script and structured JSON summary (`isHealed`, `healingSummary`, `repairedLocators`, `pythonScript`).

