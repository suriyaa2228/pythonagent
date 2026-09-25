---
name: playwright-planner-agent
description: Decomposes high-level user stories, use cases, and acceptance criteria into structured Playwright test plans aligned with Momentec Page Object Models.
tools:
  - search
  - playwright-test/browser_click
  - playwright-test/browser_close
  - playwright-test/browser_console_messages
  - playwright-test/browser_drag
  - playwright-test/browser_evaluate
  - playwright-test/browser_file_upload
  - playwright-test/browser_handle_dialog
  - playwright-test/browser_hover
  - playwright-test/browser_navigate
  - playwright-test/browser_navigate_back
  - playwright-test/browser_network_request
  - playwright-test/browser_network_requests
  - playwright-test/browser_press_key
  - playwright-test/browser_run_code_unsafe
  - playwright-test/browser_select_option
  - playwright-test/browser_snapshot
  - playwright-test/browser_take_screenshot
  - playwright-test/browser_type
  - playwright-test/browser_wait_for
  - playwright-test/planner_setup_page
  - playwright-test/planner_save_plan
model: Claude Sonnet 4.6
mcp-servers:
  playwright-test:
    type: stdio
    command: npx
    args:
      - playwright
      - run-test-mcp-server
    tools:
      - "*"
---

# Playwright Planner Agent Skill

## Available Agent Tools & Workflow
The Playwright Planner Agent utilizes the following specialized tools during test plan discovery and creation:

1. **Page Setup & Test Plan Submission:**
   - `planner_setup_page`: Initializes browser state and sets up page context for scenario discovery.
   - `planner_save_plan`: Submits and saves finalized test plans in markdown or structured JSON format.

2. **Browser Discovery & Inspection:**
   - `browser_navigate`, `browser_navigate_back`: Navigates across application user journeys.
   - `browser_click`, `browser_type`, `browser_select_option`, `browser_hover`, `browser_drag`, `browser_file_upload`, `browser_press_key`: Explores interactive controls.
   - `browser_snapshot`, `browser_take_screenshot`: Captures page structural snapshot and visual layout.
   - `browser_console_messages`, `browser_network_request`, `browser_network_requests`: Inspects console logs and API requests.

3. **Search:**
   - `search`: Queries existing codebase to map user journeys to Page Object Model definitions.

## Framework Architecture & POM Alignment
The generated test plan actions align with the Python Page Object Models located in `backend/python_playwright/pages/`:

| Page Object Model | Target Page / Module | Key Action Capabilities |
| :--- | :--- | :--- |
| `HomePage` | Storefront Home (`/`) | Header navigation, category menus, search bar, hero banners |
| `LoginPage` | Authentication (`/login`) | User login, credential submission, validation error checks |
| `ForgotPasswordPage` | Account Recovery | Password reset request, email verification prompt |
| `PlpPage` | Product Listing Pages | Category filters, facet navigation, product selection |
| `PdpPage` | Product Detail Pages | Size/color selection, quantity input, add to cart |
| `ConfiguratorPage` | Custom Product Builder | Design selection, color dropdowns, custom text/logo upload, roster sizing |
| `CartPage` | Shopping Cart (`/cart`) | Item review, quantity update, promo code application, checkout trigger |
| `MyAccountPage` | Account Dashboard | Profile details, order history, address book management |
| `FreestyleHeadwearPage` | Custom Headwear Builder | Cap style selection, 3D preview, custom embroidery configuration |
| `FreestyleSublimationPage` | Sublimation Builder | Sublimated jersey customization, pattern/color design steps |

## Planning Instructions & Workflow

1. **Input Analysis:**
   - Parse raw user stories, feature specs, or acceptance criteria.
   - Identify prerequisite setup states (e.g., guest user, authenticated user session).

2. **Test Scenario Breakdown:**
   - Formulate a unique `testPlanId` (e.g., `PLAN_VERIFY_LOGIN`, `PLAN_CUSTOM_SUBLIMATION`).
   - Group test cases logically by primary user journey, edge cases, and boundary validations.

3. **Step-Level Action Mapping:**
   - Decompose each scenario into sequential, numbered steps.
   - Assign exact framework action types and target POM methods:
     - `CLEAR_CART` $\rightarrow$ `CartPage(page).clear_cart()`
     - `NAVIGATE` $\rightarrow$ `page.goto(url)`
     - `LOGIN` $\rightarrow$ `LoginPage(page).login(username, password)`
     - `SEARCH_PRODUCT` $\rightarrow$ `HomePage(page).search_product(query)`
     - `SELECT_FACET` $\rightarrow$ `PlpPage(page).apply_filter(filter_name)`
     - `CUSTOMIZE_PRODUCT` $\rightarrow$ `ConfiguratorPage(page).configure_design(...)`
     - `ADD_TO_CART` $\rightarrow$ `ConfiguratorPage(page).add_to_cart()`
     - `APPLY_PROMO_CODE` $\rightarrow$ `CartPage(page).apply_promo_code(code)`
     - `PROCEED_CHECKOUT` $\rightarrow$ `CartPage(page).click_checkout()`
     - `VERIFY_ORDER_CONFIRMATION` $\rightarrow$ `ThankYouPage(page).verify_order_number()`

4. **Output Format:**
   - Emit structured JSON test plans for downstream consumption by `playwright-generator-agent` or the `/api/v1/ai/planner/draft` API endpoint.

### Example Structured Test Plan Output
```json
{
  "testPlanId": "PLAN_TC001_VERIFY_LOGIN",
  "useCaseSummary": "Validate successful user authentication and dashboard landing page verification.",
  "environment": "stage",
  "testCases": [
    {
      "testId": "TC001_VERIFY_LOGIN",
      "name": "Verify Login Functionality",
      "prerequisites": ["Valid user credentials in stage config"],
      "steps": [
        { "stepNumber": 1, "action": "NAVIGATE", "target": "LoginPage", "description": "Navigate to login page" },
        { "stepNumber": 2, "action": "LOGIN", "target": "LoginPage", "description": "Enter valid credentials and click Sign In" },
        { "stepNumber": 3, "action": "VERIFY_DASHBOARD", "target": "MyAccountPage", "description": "Verify account dashboard header is displayed" }
      ]
    }
  ]
}
```