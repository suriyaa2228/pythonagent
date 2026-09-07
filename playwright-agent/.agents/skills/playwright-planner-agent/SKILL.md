---
name: playwright-planner-agent
description: Decomposes high-level user stories, use cases, and acceptance criteria into structured Playwright test plans.
---

# Playwright Planner Agent Skill

## Overview
Decomposes high-level user stories, use cases, and acceptance criteria into structured JSON test plans aligned with Momentec Page Object Models (`HomePage`, `LoginPage`, `CustomSublimationPage`, `ConfiguratorPage`, `CartPage`, `ShippingBillingPage`, `ReviewSubmitPage`, `ThankYouPage`).

## Instructions
1. Accept raw user story and acceptance criteria inputs.
2. Formulate a structured test plan with `testPlanId`, `useCaseSummary`, and `testCases`.
3. Decompose each test case into sequential step actions matching framework POM methods:
   - `CLEAR_CART`: `CartPage(auth_page_tcXXX).clear_cart()`
   - `NAVIGATE`: `auth_page_tcXXX.goto(sublimation_url)`
   - `VERIFY_TITLE`: `custom_sublimation_page.verify_custom_sublimation_page_title()`
   - `CLICK_CUSTOMIZE`: `custom_sublimation_page.click_customize_on_product(style_number)`
   - `ACCEPT_COOKIES`: `configurator_page.accept_cookies()`
   - `SELECT_DESIGN`: `configurator_page.select_design()`
   - `NEXT_COLOR`: `configurator_page.click_next_color()`
   - `SELECT_COLOR`: `configurator_page.verify_color_dropdowns_and_select()`
   - `NEXT_TEXT_LOGO`: `configurator_page.click_next_text_and_logo()`
   - `ADD_TEXT`: `configurator_page.add_custom_text_with_location(...)`
   - `ADD_ART`: `configurator_page.add_custom_art_upload(...)`
   - `NEXT_ROSTER`: `configurator_page.click_next_roster()`
   - `ADD_ROSTER`: `configurator_page.verify_roster_fields_and_add_size()`
   - `NEXT_SUMMARY`: `configurator_page.click_next_summary()`
   - `ADD_TO_CART`: `configurator_page.add_to_cart()`
   - `FILL_CART_POPUP`: `configurator_page.fill_cart_popup(name, email, phone)`
   - `CHECKOUT`: `cart_page.click_checkout()`
   - `SELECT_FEDEX_GROUND`: `shipping_billing_page.select_fedex_ground_shipping_method()`
   - `REVIEW_SUBMIT`: `shipping_billing_page.click_review_and_submit()`
   - `PLACE_ORDER`: `review_submit_page.click_place_order()`
4. Output structured JSON for downstream consumption by `playwright-generator-agent` or API endpoint `/api/v1/ai/planner/draft`.

