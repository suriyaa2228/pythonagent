# AI-Driven Playwright Test Generation & Execution Platform

## Architecture Specification

**Version:** 1.0\
**Date:** 2026-08-17\
**Status:** Proposed\
**Primary Goal:** Replace the existing rule-based test-generation engine
with a LangChain + Groq LLM architecture while preserving the existing
Python Playwright execution framework, Page Object Model, pytest
fixtures, and Extent Report implementation.

------------------------------------------------------------------------

# 1. Executive Summary

The proposed platform converts user stories into production-ready Python
Playwright test scripts by combining:

1.  React.js + TypeScript UI for user-story entry, generated-script
    viewing/editing, LLM chat, execution, and reporting.
2.  Node.js backend as the application/API layer.
3.  LangChain as the mandatory LLM orchestration framework.
4.  Groq as the LLM inference provider.
5.  Mistral AI as the embedding provider.
6.  RAG for retrieving existing framework patterns, Page Objects,
    utilities, test cases, coding conventions, and relevant domain
    context.
7.  An LLM-driven test-generation pipeline replacing the existing
    rule-based engine.
8.  The existing Python Playwright framework as the execution target.
9.  The existing Extent Report implementation as the reporting source.
10. An LLM chat loop that can modify generated scripts without breaking
    framework conventions.

The architecture deliberately separates **AI generation** from **test
execution**.

The LLM does not directly execute browser actions. It generates or
modifies Python Playwright code. The existing Python pytest/Playwright
framework executes that code. This separation reduces hallucination
risk, preserves the existing framework investment, and makes generated
tests auditable.

------------------------------------------------------------------------

# 2. Existing Framework Baseline

The supplied baseline test demonstrates the current framework
conventions.

``` python
import pytest
from playwright.sync_api import sync_playwright, expect
from python_playwright.pages.home_page import HomePage

@pytest.fixture(scope="class")
def auth_context_tc001(request, env_config, browser_instance):
    headless = request.config.getoption("--headless")
    if headless:
        context = browser_instance.new_context(
            viewport={"width": 1440, "height": 900},
            ignore_https_errors=True
        )
    else:
        context = browser_instance.new_context(
            no_viewport=True,
            ignore_https_errors=True
        )
    context.set_default_timeout(30000)
    yield context
    context.close()

@pytest.fixture(scope="class")
def auth_page_tc001(auth_context_tc001):
    page = auth_context_tc001.new_page()
    yield page
    page.close()

@pytest.mark.usefixtures("auth_page_tc001")
class TestTC001VerifyLogin:
    def test_run_login(self, auth_page_tc001, env_config):
        from python_playwright.utils.reporter import Reporter

        Reporter.start_test_case(
            "TC001_VerifyLogin",
            "Verify Login functionality with positive data",
            "Smoke",
            "SURIYAA"
        )

        url = env_config["url"]
        username = env_config["username"]
        password = env_config["password"]

        auth_page_tc001.goto(url)

        home = HomePage(auth_page_tc001, url)
        home.handle_onetrust_cookie()

        login_page = home.verify_home_page().click_login()

        my_account_page = (
            login_page
            .enter_username(username)
            .enter_password(password)
            .click_login_button()
        )

        expect(
            auth_page_tc001.locator(
                "id=Header_GlobalLogin_signOutQuickLinkUser"
            )
        ).to_be_visible(timeout=15000)

        my_account_page.click_username().log_out()
```

## 2.1 Framework characteristics that must be preserved

The AI-generated code must preserve the following characteristics unless
the user explicitly asks to change them:

-   Python
-   pytest
-   Playwright synchronous API
-   Existing `python_playwright` package structure
-   Page Object Model
-   Existing Page Object classes
-   Existing fixtures
-   `env_config`
-   `browser_instance`
-   class-scoped authentication/context fixtures where appropriate
-   `request.config.getoption("--headless")`
-   existing viewport behavior
-   `ignore_https_errors=True`
-   `context.set_default_timeout(30000)`
-   existing Reporter utility
-   existing Extent Report implementation
-   existing locator conventions
-   fluent/chained Page Object methods
-   existing test naming conventions
-   existing environment configuration
-   existing execution command and pytest ecosystem

The LLM must not generate an unrelated Playwright framework.

------------------------------------------------------------------------

# 3. Target Architecture

``` text
                         +-----------------------------+
                         | React + TypeScript UI       |
                         |-----------------------------|
                         | User Story                  |
                         | Generated Script            |
                         | LLM Chat                    |
                         | Execute Test                |
                         | Reports Dashboard           |
                         +-------------+---------------+
                                       |
                                       | REST API / WebSocket
                                       v
                         +-----------------------------+
                         | Node.js Backend              |
                         |-----------------------------|
                         | Auth / Validation           |
                         | Project Management          |
                         | Generation API              |
                         | Chat API                   |
                         | Execution API              |
                         | Report API                  |
                         +-------------+---------------+
                                       |
                                       v
                         +-----------------------------+
                         | LangChain Orchestration      |
                         |-----------------------------|
                         | Prompt Templates            |
                         | RAG Retrieval               |
                         | Context Ranking             |
                         | LLM Generation              |
                         | Structured Output           |
                         | Validation / Guardrails     |
                         +------+----------------------+
                                |
                +---------------+----------------+
                |                                |
                v                                v
      +-------------------+             +-------------------+
      | Mistral AI         |             | Groq LLM          |
      | Embeddings         |             | Generation        |
      +---------+---------+             +---------+---------+
                |                                 |
                v                                 |
      +-------------------+                       |
      | MongoDB Atlas Vector Search |<----------------------+
      | RAG Knowledge Base |
      +-------------------+
                |
                v
      +------------------------------------------------+
      | Existing Python Playwright Framework            |
      |------------------------------------------------|
      | Generated Python Test                          |
      | pytest                                          |
      | Playwright sync API                             |
      | Page Objects                                    |
      | Fixtures                                        |
      | Utilities                                       |
      | Existing Reporter                               |
      +----------------------+-------------------------+
                             |
                             v
                  +-------------------------+
                  | Existing Extent Report  |
                  +------------+------------+
                               |
                               v
                  +-------------------------+
                  | Reports Dashboard        |
                  | React + TypeScript       |
                  +-------------------------+
```

------------------------------------------------------------------------

# 4. Core Architectural Principle

## AI generates. Existing framework executes.

The system must not move browser execution into Node.js or LangChain.

The target flow is:

``` text
User Story
    |
    v
RAG Context Retrieval
    |
    v
LangChain Prompt Construction
    |
    v
Groq LLM
    |
    v
Python Playwright Script
    |
    v
Static / Structural Validation
    |
    v
Existing Python Framework
    |
    v
pytest + Playwright
    |
    v
Existing Reporter
    |
    v
Extent Report
    |
    v
Dashboard
```

This is the most important architectural constraint.

------------------------------------------------------------------------

# 5. Technology Stack

  -----------------------------------------------------------------------
  Layer                   Technology              Responsibility
  ----------------------- ----------------------- -----------------------
  Frontend                React.js                UI

  Frontend Language       TypeScript              Type-safe frontend

  Backend                 Node.js                 API and orchestration
                                                  gateway

  LLM Framework           LangChain               Prompting, RAG, chains,
                                                  structured generation

  LLM                     Groq                    Test-script generation
                                                  and modification

  Embeddings              Mistral AI              Knowledge-base
                                                  embeddings

  MongoDB Atlas Vector Search            Existing/selected RAG   Context retrieval
                          MongoDB Atlas Vector Search            

  Test Framework          pytest                  Test execution

  Browser Automation      Python Playwright       Browser automation

  Reporting               Existing Extent Report  Test reporting

  API                     REST                    Frontend/backend
                                                  communication

  Optional Streaming      WebSocket/SSE           Streaming LLM chat and
                                                  execution logs

  Configuration           `.env`                  Runtime configuration
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 6. Functional Modules

## 6.1 User Story Management

The UI must allow users to:

-   Enter a user story.
-   Enter acceptance criteria.
-   Enter optional test data.
-   Select project/application.
-   Select environment.
-   Generate test scripts.
-   Save user stories.
-   Reopen previous user stories.
-   Regenerate scripts.

Example:

``` text
As a user, I should be able to log in using valid credentials
so that I can access my account.

Acceptance Criteria:
1. User navigates to the login page.
2. User enters valid username.
3. User enters valid password.
4. User clicks Login.
5. User account is displayed.
6. User can log out.
```

------------------------------------------------------------------------

# 7. Test Script Generation Pipeline

## 7.1 Generation flow

``` text
User Story
    |
    v
Input Validation
    |
    v
Retrieve Relevant RAG Context
    |
    v
Retrieve Existing Page Objects
    |
    v
Retrieve Existing Fixtures
    |
    v
Retrieve Existing Reporter Usage
    |
    v
Retrieve Similar Test Scripts
    |
    v
LangChain Context Assembly
    |
    v
Groq LLM
    |
    v
Structured Test Script
    |
    v
Code Validation
    |
    v
Framework Compatibility Validation
    |
    v
Generated Python Script
```

------------------------------------------------------------------------

# 8. RAG Architecture

RAG is mandatory because the LLM must generate code based on the actual
framework rather than generic Playwright knowledge.

## 8.1 Knowledge sources

The RAG knowledge base should be stored in MongoDB Atlas using MongoDB Vector Search. It should contain:

``` text
python_playwright/
├── pages/
├── tests/
├── utils/
├── fixtures/
├── config/
├── conftest.py
├── pytest.ini
└── existing test scripts
```

Additional documents:

-   User stories
-   Acceptance criteria
-   Existing test cases
-   Existing test scripts
-   Page Object classes
-   Fixture implementations
-   Reporter implementation
-   Configuration examples
-   Locator conventions
-   Naming conventions
-   Framework documentation
-   Application-specific workflows

------------------------------------------------------------------------

# 9. RAG Document Metadata

Every indexed document must contain metadata.

Example:

``` json
{
  "project": "playwright",
  "documentType": "page_object",
  "filePath": "python_playwright/pages/home_page.py",
  "language": "python",
  "framework": "playwright",
  "version": "1.0",
  "module": "home"
}
```

Recommended document types:

``` text
test_script
page_object
fixture
utility
reporter
config
user_story
acceptance_criteria
test_data
framework_documentation
```

Metadata filtering should be used before semantic retrieval wherever
possible.

------------------------------------------------------------------------


## 9.1 MongoDB Atlas RAG Storage

MongoDB Atlas is the mandatory persistence and vector-search layer for RAG.

Recommended logical collections:

```text
MongoDB Database
|
+-- framework_documents
|     +-- chunks
|     +-- embeddings
|     +-- metadata
|
+-- framework_versions
|
+-- moderation_audit
|
+-- generation_context
```

The primary RAG collection should store:

```json
{
  "documentId": "DOC-001",
  "chunkId": "DOC-001-CHUNK-01",
  "content": "Moderated and masked framework content",
  "embedding": [0.012, 0.023, "..."],
  "metadata": {
    "project": "playwright",
    "documentType": "page_object",
    "filePath": "python_playwright/pages/home_page.py",
    "framework": "playwright",
    "frameworkVersion": "1.0"
  }
}
```

MongoDB Atlas Vector Search should be used for semantic retrieval.

The application must never store the original unmasked sensitive source content in the RAG collection.

# 10. RAG Retrieval Strategy

The retrieval process should use:

1.  Semantic similarity.
2.  Metadata filtering.
3.  Top-K retrieval.
4.  Relevance threshold.
5.  Optional reranking.
6.  Context compression.

Example:

``` text
Query:
"Generate login test using valid credentials"

Retrieve:
- HomePage
- LoginPage
- MyAccountPage
- authentication fixture
- Reporter implementation
- similar login tests
- environment configuration
```

The LLM should receive only relevant context rather than the entire
repository.

------------------------------------------------------------------------

# 11. LangChain Architecture

LangChain is the mandatory orchestration framework.

Recommended logical components:

``` text
User Story
    |
    v
Input Parser
    |
    v
Retriever
    |
    v
Context Formatter
    |
    v
Prompt Template
    |
    v
Groq Chat Model
    |
    v
Structured Output Parser
    |
    v
Code Validator
```

Recommended LangChain abstractions:

-   Chat model integration
-   Prompt templates
-   Retriever
-   Runnable sequences
-   Structured output
-   Conversation/message history
-   Output parsing
-   Retrieval chains

The implementation should use current LangChain packages and avoid
deprecated APIs.

------------------------------------------------------------------------

# 12. Groq LLM Architecture

Groq is the mandatory inference provider.

The LLM is responsible for:

-   Understanding user stories.
-   Mapping requirements to existing framework components.
-   Selecting Page Objects.
-   Selecting fixtures.
-   Generating Python Playwright tests.
-   Updating scripts through chat.
-   Explaining generated changes.
-   Fixing generated code based on validation errors.

The LLM must not be responsible for:

-   Executing browser actions directly.
-   Creating arbitrary framework infrastructure without evidence.
-   Inventing Page Object methods.
-   Inventing locators when an existing locator is available.
-   Replacing the existing reporting system.
-   Replacing pytest.
-   Replacing Playwright.
-   Creating a second test framework.

------------------------------------------------------------------------

# 13. LLM Prompt Architecture

The system should use separate prompts rather than one giant prompt.

## 13.1 System prompt

The system prompt establishes immutable rules:

``` text
You are a senior Python Playwright automation architect.

Generate tests only for the supplied framework.

The existing framework is authoritative.

Never invent Page Object methods when relevant implementation is available.

Never replace pytest.

Never replace Playwright.

Never replace the existing Reporter.

Reuse existing fixtures.

Reuse existing Page Objects.

Reuse existing utilities.

Generate Python code compatible with the existing framework.

If required information is unavailable, explicitly identify the missing information.
```

## 13.2 Context prompt

Contains retrieved framework artifacts.

## 13.3 User-story prompt

Contains the current user story and acceptance criteria.

## 13.4 Generation prompt

Requests the final Python test.

## 13.5 Modification prompt

Used by the chat feature to modify an existing script.

------------------------------------------------------------------------

# 14. Structured LLM Output

The LLM should not return uncontrolled prose when generating a test.

Recommended logical output:

``` json
{
  "testCaseId": "TC001",
  "testName": "VerifyLogin",
  "description": "Verify Login functionality with positive data",
  "frameworkComponents": {
    "pages": [
      "HomePage",
      "LoginPage",
      "MyAccountPage"
    ],
    "fixtures": [
      "auth_context_tc001",
      "auth_page_tc001"
    ],
    "reporter": "Reporter"
  },
  "pythonScript": "..."
}
```

The backend must extract and validate `pythonScript`.

------------------------------------------------------------------------

# 15. Python Playwright Compatibility Rules

Generated scripts must follow the existing framework.

## Mandatory patterns

### Imports

``` python
import pytest
from playwright.sync_api import expect
from python_playwright.pages.home_page import HomePage
```

### Fixtures

Use existing fixtures whenever available.

### Page Objects

Use:

``` python
home = HomePage(auth_page_tc001, url)
```

rather than embedding all UI interactions directly into the test.

### Fluent Page Object chain

Where the framework already supports chaining:

``` python
login_page = home.verify_home_page().click_login()
```

The LLM must preserve that pattern.

### Reporter

The generated test must use:

``` python
from python_playwright.utils.reporter import Reporter
```

and the existing:

``` python
Reporter.start_test_case(...)
```

implementation.

------------------------------------------------------------------------

# 16. Rule-Based Engine Replacement

## Existing model

``` text
User Story
    |
    v
Rules
    |
    v
Hardcoded Conditions
    |
    v
Template
    |
    v
Python Script
```

## New model

``` text
User Story
    |
    v
RAG
    |
    v
LangChain
    |
    v
Groq LLM
    |
    v
Framework-aware Python Script
```

The rule-based engine must not remain as the primary generation
mechanism.

Rule-based validation may still exist for deterministic safety checks.

This distinction is critical:

``` text
Generation = LLM
Validation = deterministic rules
Execution = existing Python framework
Reporting = existing Extent Report
```

Do not replace deterministic validation with an LLM.

------------------------------------------------------------------------

# 17. Script Validation Layer

Generated code must pass validation before being shown as executable.

## 17.1 Syntax validation

Use Python AST compilation/parsing.

Conceptually:

``` text
ast.parse(generatedScript)
```

## 17.2 Framework validation

Check:

-   pytest usage
-   Playwright sync API
-   valid imports
-   known Page Objects
-   known fixture names
-   Reporter usage
-   valid project paths
-   prohibited framework replacements

## 17.3 Static safety validation

Reject scripts containing:

-   arbitrary shell execution
-   credential leakage
-   hardcoded secrets
-   destructive system commands
-   unknown package installation
-   unauthorized file access
-   generated framework replacement code

------------------------------------------------------------------------

# 18. Hallucination Prevention

The biggest risk in this architecture is hallucinated framework code.

The system must therefore enforce:

``` text
RAG evidence
+
known repository symbols
+
structured generation
+
static validation
+
execution validation
```

If the LLM generates:

``` python
home.click_login_button()
```

but the RAG/repository does not contain that method, the system must
flag it.

The system should return:

``` text
Framework Compatibility Error:
HomePage.click_login_button() was not found in the indexed framework.

Available matching methods:
- click_login()
```

The LLM may then automatically correct the script.

------------------------------------------------------------------------

# 19. Self-Correction Loop

Recommended generation pipeline:

``` text
Generate
   |
   v
Validate
   |
   +---- PASS ----> Return Script
   |
   FAIL
   |
   v
Send validation errors to Groq
   |
   v
Regenerate
   |
   v
Validate Again
```

Maximum retries must be configurable.

Recommended default:

``` env
LLM_MAX_RETRIES=2
```

Do not create an infinite LLM correction loop.

------------------------------------------------------------------------

# 20. LLM Chat-Based Script Modification

The frontend must provide a chat panel.

Example:

``` text
User:
Add a negative login test for invalid password.

LLM:
I will update the existing test using the existing LoginPage
methods and Reporter implementation.

[Updated Script]
```

The LLM receives:

``` text
Current script
+
User modification request
+
Relevant RAG context
+
Framework constraints
```

It should return:

``` text
Updated script
+
Change summary
+
Validation result
```

------------------------------------------------------------------------

# 21. Script Versioning

Every modification should create a version.

Example:

``` text
TC001
 ├── v1 Initial generated script
 ├── v2 Added invalid password
 ├── v3 Added cookie handling
 └── v4 Updated assertion
```

Store:

-   version
-   timestamp
-   user
-   prompt
-   generated script
-   validation result
-   execution result

The user must be able to restore an earlier version.

------------------------------------------------------------------------

# 22. Frontend Architecture

Recommended structure:

``` text
src/
├── components/
│   ├── UserStoryEditor/
│   ├── ScriptViewer/
│   ├── ScriptEditor/
│   ├── ChatPanel/
│   ├── ExecutionPanel/
│   ├── ReportsDashboard/
│   └── Common/
│
├── pages/
│   ├── Dashboard/
│   ├── UserStory/
│   ├── TestGeneration/
│   ├── TestScript/
│   └── Reports/
│
├── services/
│   ├── api.ts
│   ├── generationApi.ts
│   ├── executionApi.ts
│   ├── reportApi.ts
│   └── chatApi.ts
│
├── hooks/
├── types/
├── utils/
└── App.tsx
```

------------------------------------------------------------------------

# 23. User Story UI

The UI should contain:

``` text
+------------------------------------------------+
| User Story                                      |
+------------------------------------------------+
| [Enter user story...]                           |
|                                                |
| Acceptance Criteria                             |
| [Enter acceptance criteria...]                   |
|                                                |
| Test Data                                       |
| [Optional]                                      |
|                                                |
| Project: [Playwright Project v]                |
| Environment: [Stage v]                         |
|                                                |
|              [Generate Test Script]             |
+------------------------------------------------+
```

------------------------------------------------------------------------

# 24. Generated Script UI

The script screen should show:

``` text
+------------------------------------------------+
| TC001 - Verify Login                            |
+------------------------------------------------+
| Status: VALID                                   |
| Framework: Python Playwright                    |
|                                                |
| +--------------------------------------------+ |
| | Python source code                         | |
| |                                            | |
| | class TestTC001VerifyLogin:                | |
| |     ...                                    | |
| +--------------------------------------------+ |
|                                                |
| [Validate] [Run Test] [Save] [Version History] |
+------------------------------------------------+
```

A syntax-highlighted editor should be used.

------------------------------------------------------------------------

# 25. LLM Chat UI

Layout:

``` text
+----------------------+-------------------------+
| Generated Script     | AI Assistant            |
|                      |                         |
| Python code          | User: Add logout check  |
|                      |                         |
|                      | AI: Updated script...   |
|                      |                         |
|                      | [Type instruction...]   |
+----------------------+-------------------------+
```

The chat must operate against the selected script only.

------------------------------------------------------------------------

# 26. Reports Dashboard

The dashboard must consume the existing Extent Report output.

It should show:

-   Total test cases
-   Passed
-   Failed
-   Skipped
-   Pass percentage
-   Execution duration
-   Test case status
-   Suite status
-   Environment
-   Browser
-   Execution timestamp
-   Failure reason
-   Screenshot availability
-   Test execution history

Example:

``` text
+------------------------------------------------+
| Execution Summary                               |
+------------------------------------------------+
| Total | Passed | Failed | Skipped | Pass %     |
|  115  |  110   |   3    |    2    | 95.65%    |
+------------------------------------------------+

Test Results
--------------------------------------------------
TC001   Verify Login        PASS
TC002   Invalid Login      PASS
TC003   Checkout           FAIL
TC004   Logout              PASS
```

------------------------------------------------------------------------

# 27. Extent Report Integration

The existing Extent Report remains the source of truth for execution
reporting.

Do not create a second reporting engine unless required only as a
read-only adapter.

Architecture:

``` text
pytest
   |
   v
Existing Reporter
   |
   v
Extent Report
   |
   v
Report Parser / Adapter
   |
   v
Node.js Reports API
   |
   v
React Dashboard
```

The dashboard should parse the existing report output rather than asking
the LLM to interpret test results.

------------------------------------------------------------------------

# 28. Test Execution Architecture

The Node.js backend should trigger the existing Python execution
process.

``` text
React
  |
  | POST /api/tests/:id/execute
  v
Node.js
  |
  | spawn controlled process
  v
pytest
  |
  v
Python Playwright
  |
  v
Browser
  |
  v
Extent Report
```

Node.js must not rewrite the generated test before execution.

------------------------------------------------------------------------

# 29. Execution Isolation

Each execution should have an execution ID.

Example:

``` text
executionId = EXEC-20260817-0001
```

Execution workspace:

``` text
executions/
└── EXEC-20260817-0001/
    ├── generated_test.py
    ├── stdout.log
    ├── stderr.log
    ├── screenshots/
    └── report/
```

This prevents concurrent executions from corrupting one another.

------------------------------------------------------------------------

# 30. Execution API

Recommended APIs:

``` text
POST   /api/user-stories
GET    /api/user-stories/:id

POST   /api/tests/generate
GET    /api/tests/:id

POST   /api/tests/:id/validate
POST   /api/tests/:id/execute

GET    /api/executions/:id
GET    /api/executions/:id/logs

POST   /api/tests/:id/chat
GET    /api/tests/:id/versions
POST   /api/tests/:id/versions/:version/restore

GET    /api/reports
GET    /api/reports/:executionId
GET    /api/reports/:executionId/details
```

------------------------------------------------------------------------

# 31. Chat API

Example:

``` http
POST /api/tests/TC001/chat
```

Request:

``` json
{
  "message": "Add an assertion that the username is displayed after login.",
  "version": 4
}
```

Response:

``` json
{
  "version": 5,
  "script": "...",
  "summary": "Added username visibility assertion.",
  "validation": {
    "status": "PASS",
    "errors": []
  }
}
```

------------------------------------------------------------------------

# 32. Generation API

Example:

``` http
POST /api/tests/generate
```

Request:

``` json
{
  "userStory": "As a user, I should be able to login...",
  "acceptanceCriteria": [
    "Valid username should be accepted",
    "Valid password should be accepted",
    "User should reach account page"
  ],
  "project": "playwright",
  "environment": "stage"
}
```

------------------------------------------------------------------------

# 33. Backend Project Structure

Recommended:

``` text
backend/
├── src/
│   ├── api/
│   │   ├── routes/
│   │   └── controllers/
│   │
│   ├── services/
│   │   ├── generation/
│   │   ├── rag/
│   │   ├── validation/
│   │   ├── execution/
│   │   ├── reports/
│   │   └── chat/
│   │
│   ├── langchain/
│   │   ├── prompts/
│   │   ├── chains/
│   │   ├── retrievers/
│   │   ├── parsers/
│   │   └── models/
│   │
│   ├── repositories/
│   ├── config/
│   ├── middleware/
│   ├── utils/
│   └── app.ts
│
├── .env
├── .env.example
├── package.json
└── tsconfig.json
```

------------------------------------------------------------------------

# 34. Python Framework Boundary

The existing Python framework remains independently executable.

``` text
AI Platform
     |
     | Generated .py
     v
Existing Python Playwright Framework
     |
     +-- pages/
     +-- tests/
     +-- utils/
     +-- fixtures/
     +-- reporter/
     +-- config/
```

The AI platform should not force a migration of the Python framework to
Node.js.

------------------------------------------------------------------------

# 35. `.env` Configuration

The application must use environment variables.

Example `.env`:

``` env
# =========================
# Application
# =========================
NODE_ENV=development
PORT=3000
FRONTEND_URL=http://localhost:5173

# =========================
# Groq
# =========================
GROQ_API_KEY=
GROQ_MODEL=
GROQ_TEMPERATURE=0

# =========================
# Mistral AI
# =========================
MISTRAL_API_KEY=
MISTRAL_EMBEDDING_MODEL=

# =========================
# MongoDB / RAG
# =========================
MONGODB_URI=
MONGODB_DATABASE=
MONGODB_COLLECTION=
MONGODB_VECTOR_INDEX=
RAG_TOP_K=8
RAG_SCORE_THRESHOLD=0.70

# =========================
# Rule-Based Moderation
# =========================
MODERATION_ENABLED=true
MODERATION_RULES_PATH=
MODERATION_TOXIC_TERMS_PATH=
MODERATION_BLOCK_THRESHOLD=
MODERATION_MASK_URL=true
MODERATION_MASK_EMAIL=true
MODERATION_MASK_USERNAME=true
MODERATION_MASK_PASSWORD=true

# =========================
# LangChain
# =========================
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=
LANGCHAIN_PROJECT=

# =========================
# Python Playwright
# =========================
PYTHON_EXECUTABLE=python
PLAYWRIGHT_PROJECT_PATH=
PYTEST_COMMAND=pytest

# =========================
# Reports
# =========================
EXTENT_REPORT_PATH=
REPORT_OUTPUT_PATH=

# =========================
# LLM Controls
# =========================
LLM_MAX_RETRIES=2
LLM_MAX_OUTPUT_TOKENS=
```

Secrets must never be committed to source control.

The repository must contain:

``` text
.env.example
```

but not real API keys.

------------------------------------------------------------------------

# 36. Configuration Rules

Configuration must not be hardcoded.

At minimum, the following must be configurable:

-   Groq API key
-   Groq model
-   Mistral API key
-   Mistral embedding model
-   RAG top-K
-   RAG threshold
-   Python executable
-   Playwright project path
-   pytest command
-   Extent report location
-   LLM retry count
-   LLM temperature
-   backend port
-   frontend URL

------------------------------------------------------------------------

# 37.1 Pre-Embedding Moderation

The moderation layer is a mandatory security boundary.

```text
Input
 |
 v
Rule-Based Moderation
 |
 +--> blocked --> stop
 |
 v
PII/Credential Masking
 |
 v
Embedding
 |
 v
MongoDB Atlas Vector Search
```

No raw URL, email address, username, or password may be sent to Mistral for embedding.

No blocked toxic/inappropriate content may be embedded or stored.

# 37. Security Architecture

## Secrets

Never expose:

``` text
GROQ_API_KEY
MISTRAL_API_KEY
LANGCHAIN_API_KEY
```

to React.

The frontend communicates only with Node.js.

## Credentials

Generated tests must use:

``` python
env_config["username"]
env_config["password"]
```

and must not generate:

``` python
username = "real-user"
password = "real-password"
```

## Prompt injection

User stories and retrieved documents must be treated as untrusted
content.

The system prompt must explicitly instruct the model to treat retrieved
code/document content as reference material rather than instructions
capable of overriding system constraints.

------------------------------------------------------------------------

# 38. Prompt Injection Defense

RAG documents may contain malicious or accidental instructions.

The pipeline should conceptually separate:

``` text
SYSTEM RULES
    >
FRAMEWORK CONSTRAINTS
    >
VALIDATION RULES
    >
RAG REFERENCE
    >
USER REQUEST
```

The model must never allow a retrieved document to override framework or
security rules.

------------------------------------------------------------------------

# 39. Data Flow

## Generation

``` text
React
 |
 | User Story
 v
Node API
 |
 v
LangChain
 |
 +--> Mistral Embedding
 |        |
 |        v
 |    MongoDB Atlas Vector Search
 |        |
 |        v
 |    Relevant Context
 |
 v
Prompt
 |
 v
Groq
 |
 v
Python Script
 |
 v
Validator
 |
 v
React
```

## Execution

``` text
React
 |
 v
Node.js
 |
 v
Python pytest
 |
 v
Playwright
 |
 v
Extent Reporter
 |
 v
Extent Report
 |
 v
Report Adapter
 |
 v
React Dashboard
```

------------------------------------------------------------------------

# 40. State Management

The frontend should maintain:

``` text
User Story State
Script State
Script Version
Chat State
Execution State
Report State
```

Backend should maintain persistent entities such as:

``` text
UserStory
TestScript
TestScriptVersion
Execution
Report
ChatMessage
```

------------------------------------------------------------------------

# 41. Suggested Data Model

## UserStory

``` json
{
  "id": "US-001",
  "title": "Verify Login",
  "description": "...",
  "acceptanceCriteria": [],
  "project": "playwright",
  "environment": "stage"
}
```

## TestScript

``` json
{
  "id": "TC001",
  "userStoryId": "US-001",
  "name": "VerifyLogin",
  "language": "python",
  "framework": "playwright",
  "currentVersion": 4,
  "validationStatus": "PASS"
}
```

## Execution

``` json
{
  "id": "EXEC-20260817-0001",
  "testScriptId": "TC001",
  "status": "PASSED",
  "environment": "stage",
  "startedAt": "...",
  "completedAt": "...",
  "reportPath": "..."
}
```

------------------------------------------------------------------------

# 42. RAG Ingestion Pipeline

A mandatory **rule-based moderation and masking layer** must execute **before embedding**.

The moderation layer is deliberately deterministic. It must not use the LLM because sensitive-data masking and toxic/inappropriate-content blocking must be predictable and auditable.

The ingestion pipeline is:

```text
Repository / User Content
        |
        v
Rule-Based Moderation Layer
        |
        +---- BLOCK ----> Reject content + audit reason
        |
        +---- ALLOW ----> Mask sensitive values
                              |
                              v
                       Document Chunking
                              |
                              v
                       Mistral Embeddings
                              |
                              v
                 MongoDB Atlas Vector Search
```

## 42.1 Mandatory Moderation Responsibilities

The rule-based moderation engine must:

1. Detect and mask URLs.
2. Detect and mask email addresses.
3. Detect and mask usernames.
4. Detect and mask passwords.
5. Detect inappropriate/toxic content.
6. Block content classified as inappropriate/toxic.
7. Prevent secrets and credentials from reaching the embedding model.
8. Prevent masked sensitive data from entering the RAG vector database.
9. Produce an auditable moderation result.

## 42.2 Sensitive Data Masking

Sensitive values must be replaced before embedding.

Example:

```text
Original:
Username: suriyaa@example.com
Password: MySecretPassword123
URL: https://stage.example.com/login

Masked:
Username: [MASKED_USERNAME]
Password: [MASKED_PASSWORD]
URL: [MASKED_URL]
```

Email addresses must also be masked even when they appear outside explicit `email=` fields.

Example:

```text
user@example.com
```

becomes:

```text
[MASKED_EMAIL]
```

The masking layer must operate before:

```text
chunking
embedding
vector storage
LLM context construction
```

## 42.3 Rule-Based Detection

The moderation layer should use deterministic rules such as:

- regular expressions for URL detection
- regular expressions for email detection
- known configuration/key names for username/password detection
- credential-pattern detection
- configurable toxic/inappropriate-content dictionary
- configurable prohibited phrase/category rules

The rules must be externalized/configurable rather than hardcoded throughout the application.

Example:

```text
URL_PATTERN
EMAIL_PATTERN
USERNAME_FIELD_NAMES
PASSWORD_FIELD_NAMES
TOXIC_TERMS
BLOCKED_PATTERNS
```

## 42.4 Toxic/Inappropriate Content Handling

If content matches a configured blocked category:

```text
Moderation
    |
    v
TOXIC / INAPPROPRIATE
    |
    v
BLOCK
    |
    +--> Do not embed
    +--> Do not store in MongoDB
    +--> Do not send to Groq
    +--> Return moderation error
```

Example response:

```json
{
  "status": "BLOCKED",
  "reason": "INAPPROPRIATE_CONTENT",
  "message": "The submitted content cannot be processed."
}
```

Do not send the original blocked content to the LLM for classification.

## 42.5 Moderation Result

Each ingestion request should produce an internal moderation result:

```json
{
  "status": "ALLOWED",
  "maskedFields": [
    "url",
    "email",
    "username",
    "password"
  ],
  "blocked": false
}
```

For blocked content:

```json
{
  "status": "BLOCKED",
  "blocked": true,
  "reason": "TOXIC_CONTENT"
}
```

The original sensitive content must not be persisted in moderation logs.

## 42.6 Critical Security Boundary

The mandatory sequence is:

```text
RAW CONTENT
    |
    v
RULE-BASED MODERATION
    |
    +---- BLOCK
    |
    +---- MASK
           |
           v
       CHUNKING
           |
           v
    MISTRAL EMBEDDING
           |
           v
 MONGODB ATLAS VECTOR SEARCH
```

It is prohibited to execute:

```text
RAW CONTENT
    |
    v
MISTRAL EMBEDDING
    |
    v
Moderation
```

because sensitive information would already have been transmitted to the embedding provider.


``` text
Repository
   |
   v
File Discovery
   |
   v
File Filtering
   |
   v
Document Loading
   |
   v
Chunking
   |
   v
Mistral Embeddings
   |
   v
MongoDB Atlas Vector Search
```

Do not index:

``` text
.env
.git/
node_modules/
__pycache__/
venv/
secrets/
temporary reports
```

------------------------------------------------------------------------

# 43. Chunking Strategy

Chunk based on code structure rather than arbitrary character boundaries
whenever practical.

For Python:

``` text
Class
  |
  +-- Method
  +-- Fixture
```

For Page Objects:

``` text
Class
  |
  +-- locator definitions
  +-- actions
  +-- assertions
```

This improves retrieval quality.

------------------------------------------------------------------------

# 44. Retrieval Context Example

For the supplied login test, the RAG retriever should ideally return:

``` text
HomePage
LoginPage
MyAccountPage
auth_context fixture
auth_page fixture
Reporter
environment configuration
similar login test
```

The LLM can then generate a script consistent with the existing
framework.

------------------------------------------------------------------------

# 45. Framework Symbol Registry

A useful enhancement is a lightweight repository symbol index.

Example:

``` json
{
  "HomePage": {
    "file": "python_playwright/pages/home_page.py",
    "methods": [
      "handle_onetrust_cookie",
      "verify_home_page",
      "click_login"
    ]
  },
  "LoginPage": {
    "file": "python_playwright/pages/login_page.py",
    "methods": [
      "enter_username",
      "enter_password",
      "click_login_button"
    ]
  }
}
```

This registry can be used for deterministic validation and should
complement RAG rather than replace it.

------------------------------------------------------------------------

# 46. Generated Script Quality Gates

A script should be marked executable only when:

``` text
[PASS] Python syntax
[PASS] Required imports
[PASS] pytest compatibility
[PASS] Playwright compatibility
[PASS] Page Object references
[PASS] Fixture references
[PASS] Reporter integration
[PASS] No secrets detected
[PASS] No prohibited operations
```

------------------------------------------------------------------------

# 47. Execution Feedback Loop

After execution:

``` text
Test Failed
    |
    v
Capture:
- traceback
- failed assertion
- screenshot
- browser logs
- test output
    |
    v
Show in UI
    |
    v
User can ask LLM:
"Fix this failure"
```

The LLM receives the failure information plus relevant framework
context.

It must not automatically modify production code without user approval.

------------------------------------------------------------------------

# 48. Failure Diagnosis

LLM-assisted diagnosis can identify:

-   locator mismatch
-   Page Object method issue
-   assertion issue
-   synchronization issue
-   test-data issue
-   environment issue

The system should distinguish:

``` text
TEST CODE FAILURE
APPLICATION FAILURE
ENVIRONMENT FAILURE
DATA FAILURE
FRAMEWORK FAILURE
```

This classification should be shown separately in the UI.

------------------------------------------------------------------------

# 49. Deterministic vs LLM Responsibilities

  Responsibility                Technology
  ----------------------------- --------------------------
  Understand user story         Groq LLM
  Retrieve context              LangChain + MongoDB Atlas Vector Search
  Generate code                 Groq LLM
  Modify code                   Groq LLM
  Python syntax validation      Python AST
  Framework symbol validation   Deterministic validator
  Secret detection              Deterministic validator
  Browser execution             Playwright
  Test execution                pytest
  Reporting                     Existing Extent Report
  Dashboard aggregation         Node.js
  UI                            React

This boundary should not be blurred.

------------------------------------------------------------------------

# 50. Observability

Log every major pipeline step.

Example:

``` text
GENERATION_STARTED
RAG_RETRIEVAL_COMPLETED
LLM_GENERATION_COMPLETED
VALIDATION_STARTED
VALIDATION_PASSED
SCRIPT_SAVED
EXECUTION_STARTED
EXECUTION_COMPLETED
REPORT_PARSED
```

Do not log API keys, passwords, or sensitive test data.

------------------------------------------------------------------------

# 51. LLM Observability

If LangSmith is enabled, tracing should capture:

-   prompt execution
-   retrieval
-   token usage
-   latency
-   model response
-   validation result

However, sensitive user/test data must be redacted before external
tracing if required by the organization's security policy.

------------------------------------------------------------------------

# 52. Performance Considerations

The generation pipeline should minimize unnecessary context.

Use:

``` text
metadata filter
        |
semantic retrieval
        |
top-K
        |
optional reranking
        |
context compression
        |
LLM
```

Do not send the entire Python repository to Groq.

------------------------------------------------------------------------

# 53. Caching

Cache stable RAG results where appropriate.

Potential cache keys:

``` text
hash(userStory + acceptanceCriteria + project + frameworkVersion)
```

Cache generated results only when deterministic reuse is acceptable.

Do not cache secrets or environment credentials.

------------------------------------------------------------------------

# 54. Concurrency

Multiple users may generate scripts concurrently.

Every generation request should have:

``` text
requestId
userId
testScriptId
generationVersion
timestamp
```

Execution processes must use isolated workspaces.

------------------------------------------------------------------------

# 55. Error Handling

Frontend should receive structured errors.

Example:

``` json
{
  "errorCode": "FRAMEWORK_CONTEXT_MISSING",
  "message": "LoginPage was not found in the RAG knowledge base.",
  "retryable": false
}
```

Possible categories:

``` text
RAG_RETRIEVAL_FAILED
LLM_GENERATION_FAILED
LLM_TIMEOUT
INVALID_LLM_OUTPUT
FRAMEWORK_CONTEXT_MISSING
SCRIPT_VALIDATION_FAILED
PYTEST_EXECUTION_FAILED
REPORT_NOT_FOUND
REPORT_PARSE_FAILED
```

------------------------------------------------------------------------

# 56. API Security

Recommended controls:

-   authentication
-   authorization
-   request validation
-   rate limiting
-   payload size limits
-   audit logging
-   CORS restriction
-   secure headers
-   command execution allowlisting

The test execution endpoint is especially sensitive because it launches
a local process.

------------------------------------------------------------------------

# 57. Controlled Python Execution

Never construct shell commands directly from user input.

Bad:

``` text
exec(userProvidedCommand)
```

Preferred model:

``` text
Allowed executable
+
validated test file
+
controlled arguments
+
isolated working directory
```

The backend should use a process API with argument arrays rather than
shell string concatenation.

------------------------------------------------------------------------

# 58. Repository Synchronization

Because the LLM depends on the current framework, the RAG index must be
refreshed whenever:

-   Page Object changes
-   Fixture changes
-   Reporter changes
-   Test framework changes
-   Utility changes

Recommended flow:

``` text
Code Change
    |
    v
RAG Ingestion
    |
    v
New Framework Version
```

------------------------------------------------------------------------

# 59. Framework Versioning

The RAG knowledge base should track framework versions.

Example:

``` text
Framework Version:
playwright-framework-v1.4.0
```

A generated test should record the framework version used during
generation.

This prevents a script generated against old Page Objects from silently
being used with a newer framework.

------------------------------------------------------------------------

# 60. Recommended Frontend Pages

## Dashboard

Shows:

-   executions
-   pass/fail trends
-   generated tests
-   recent activity

## User Story

Create/edit user stories.

## Test Generator

Generate scripts from user stories.

## Script Workspace

View/edit generated scripts.

## AI Chat

Modify scripts conversationally.

## Execution

Run tests and stream execution status.

## Reports

View Extent Report-derived results.

## Version History

Compare and restore script versions.

------------------------------------------------------------------------

# 61. Script Workspace Layout

Recommended:

``` text
------------------------------------------------------------
| Test Case: TC001                                         |
------------------------------------------------------------
|                    |                                     |
| Python Editor      | AI Chat                             |
|                    |                                     |
| class Test...      | User: Add invalid login            |
|                    |                                     |
|                    | AI: Updating...                    |
|                    |                                     |
------------------------------------------------------------
| Validate | Save | Execute | Versions | Report            |
------------------------------------------------------------
```

------------------------------------------------------------------------

# 62. Chat Context Management

Do not send the entire conversation indefinitely.

Use:

``` text
Current Script
+
Recent Relevant Chat
+
Current User Request
+
Relevant RAG Context
```

Summarize older conversation context when necessary.

------------------------------------------------------------------------

# 63. Acceptance Criteria-to-Test Mapping

The LLM should explicitly map each acceptance criterion to one or more
test steps.

Example:

``` text
AC1 -> Navigate to application
AC2 -> Verify home page
AC3 -> Click Login
AC4 -> Enter username
AC5 -> Enter password
AC6 -> Click Login
AC7 -> Verify account
AC8 -> Logout
```

The generated test should not silently omit acceptance criteria.

------------------------------------------------------------------------

# 64. Coverage Validation

Before returning a generated script, the backend should compare:

``` text
Acceptance Criteria
        vs
Generated Test Steps
```

If an acceptance criterion is not covered, the script should be marked:

``` text
INCOMPLETE
```

and sent back to the LLM for correction.

------------------------------------------------------------------------

# 65. Example Generated Output for Supplied Script

For the supplied login scenario, the architecture expects the LLM to
recognize:

``` text
Page Objects:
HomePage
LoginPage
MyAccountPage

Fixtures:
auth_context_tc001
auth_page_tc001

Utilities:
Reporter

Assertions:
expect(...).to_be_visible()

Execution:
pytest + Playwright sync API
```

It should preserve the same framework pattern instead of generating raw:

``` python
page.locator(...)
page.fill(...)
page.click(...)
```

when corresponding Page Object methods already exist.

------------------------------------------------------------------------

# 66. Recommended Prompt Constraints for the Supplied Framework

The generation prompt should include rules equivalent to:

``` text
1. Use the existing Python Playwright framework.
2. Use pytest.
3. Use Playwright sync API.
4. Reuse existing fixtures.
5. Reuse existing Page Objects.
6. Reuse existing Reporter.
7. Do not create a new framework.
8. Do not introduce Selenium.
9. Do not use JavaScript browser automation.
10. Do not replace Extent Reports.
11. Do not hardcode credentials.
12. Prefer existing fluent Page Object methods.
13. Every acceptance criterion must be represented.
14. Do not invent methods not present in retrieved framework context.
15. If a required Page Object/action is unavailable, report it instead of hallucinating it.
```

------------------------------------------------------------------------

# 67. Test Generation Lifecycle

``` text
1. User enters user story
2. Backend validates request
3. LangChain analyzes intent
4. RAG retrieves framework context
5. LangChain builds generation prompt
6. Groq generates structured response
7. Backend validates Python syntax
8. Backend validates framework compatibility
9. Backend checks acceptance-criteria coverage
10. If validation fails, controlled LLM correction occurs
11. Script is saved as a version
12. React displays script
13. User reviews script
14. User executes script
15. Existing pytest/Playwright framework runs it
16. Existing Reporter creates Extent Report
17. Backend parses report
18. Dashboard displays results
19. User can chat with LLM for modifications
```

------------------------------------------------------------------------

# 68. Deployment Architecture

Recommended deployment:

``` text
                  Internet / Internal Network
                             |
                             v
                    React Frontend
                             |
                             v
                    Node.js Backend
                     /             \
                    /               \
                   v                 v
             LangChain          Execution Service
                |                     |
          +-----+-----+               v
          |           |         Python Playwright
       Groq       Mistral             |
          |           |               v
          |       Embeddings        Browser
          |           |               |
          |           v               v
          |      MongoDB Atlas Vector Search     Extent Report
          |                           |
          +-------------+-------------+
                        |
                        v
                   Report API
                        |
                        v
                  React Dashboard
```

------------------------------------------------------------------------

# 69. Recommended Service Boundaries

Initially, a modular monolith is preferable to microservices.

``` text
Node.js Application
├── API
├── LangChain orchestration
├── RAG
├── validation
├── execution orchestration
└── report adapter
```

Do not introduce microservices merely because the application contains
multiple modules.

Split services only when scaling, isolation, or deployment requirements
justify it.

------------------------------------------------------------------------

# 70. Testing Strategy for the AI Platform

The platform itself must be tested.

## Unit tests

-   Prompt construction
-   RAG retrieval
-   Output parsing
-   Validation
-   Report parsing
-   API services

## Integration tests

-   Node + LangChain
-   LangChain + Groq
-   LangChain + Mistral
-   RAG + MongoDB Atlas Vector Search
-   Node + Python execution
-   Extent Report parser

## End-to-end tests

``` text
User Story
    |
    v
Generate
    |
    v
Validate
    |
    v
Execute
    |
    v
Extent Report
    |
    v
Dashboard
```

------------------------------------------------------------------------

# 71. AI Evaluation

LLM quality must not be measured only by whether Python syntax is valid.

Evaluate:

1.  Acceptance criteria coverage.
2.  Page Object reuse.
3.  Fixture reuse.
4.  Locator correctness.
5.  Framework compatibility.
6.  Reporter integration.
7.  Execution success.
8.  Hallucination rate.
9.  Correction rate.
10. Token usage.
11. Generation latency.

Recommended key metric:

``` text
First-Pass Executable Test Rate
=
Tests executing successfully without manual modification
/
Total generated tests
```

------------------------------------------------------------------------

# 72. Golden Test Set

Create a fixed evaluation dataset containing representative user
stories:

``` text
Login
Logout
Search
PLP
PDP
Add to Cart
Checkout
Order History
Account
Negative scenarios
Validation scenarios
Builder workflows
```

Each should have a known expected framework pattern.

Every prompt/model/RAG change should be evaluated against this set.

------------------------------------------------------------------------

# 73. Model Strategy

The Groq model should be configurable.

Do not hardcode a model name into business logic.

``` env
GROQ_MODEL=
```

The application should allow model changes without rewriting the
generation pipeline.

Use temperature near zero for code generation unless there is a
documented reason to increase it.

------------------------------------------------------------------------

# 74. Embedding Strategy

Mistral AI is the mandatory embedding provider.

Embeddings are used for:

``` text
User Story
    |
    v
Embedding
    |
    v
Similarity Search
    |
    v
Relevant Framework Context
```

Embedding model selection must be configurable through:

``` env
MISTRAL_EMBEDDING_MODEL=
```

------------------------------------------------------------------------

# 75. Important Architecture Decision

The platform should **not** use an LLM to decide everything.

Use LLMs where semantic reasoning is required.

Use deterministic code where correctness is required.

Therefore:

``` text
LLM:
- requirement interpretation
- test design
- code generation
- code modification
- failure explanation

Deterministic:
- syntax validation
- symbol validation
- secret detection
- execution
- reporting
- acceptance coverage checks
- security controls
```

This hybrid architecture is substantially safer than an LLM-only system.

------------------------------------------------------------------------

# 76. Non-Functional Requirements

## Reliability

Generated scripts must be validated before execution.

## Maintainability

Existing Python framework remains the execution foundation.

## Scalability

Generation and execution should be independently queueable/scalable
later.

## Security

Secrets and credentials must never enter prompts or frontend state
unnecessarily.

## Observability

Generation and execution must be traceable using request/execution IDs.

## Auditability

Every generated/modified script must have version history.

## Reproducibility

Record:

-   model
-   framework version
-   RAG version
-   prompt version
-   timestamp
-   generation parameters

------------------------------------------------------------------------

# 77. Architecture Decisions Summary

  Decision                   Choice
  -------------------------- ----------------------------------------
  Frontend                   React + TypeScript
  Backend                    Node.js
  LLM framework              LangChain
  LLM                        Groq
  Embeddings                 Mistral AI
  Generation                 LLM
  RAG                        Mandatory
  Browser automation         Existing Python Playwright
  Test runner                Existing pytest
  Reporting                  Existing Extent Report
  Rule-based generation      Removed
  Deterministic validation   Retained
  Script modification        LLM chat
  UI                         User story + script + chat + dashboard
  Configuration              `.env`
  Execution                  Controlled Python process
  Versioning                 Mandatory
  Repository context         RAG
  Framework compatibility    Mandatory

------------------------------------------------------------------------

# 78. Critical Risks and Mitigations

  -----------------------------------------------------------------------
  Risk                                Mitigation
  ----------------------------------- -----------------------------------
  LLM hallucinates Page Objects       RAG + symbol validation

  LLM invents locators                Prefer existing Page Objects

  Generated code breaks framework     Static compatibility validator

  Credentials exposed                 env_config + secret detection

  LLM produces unsafe code            deterministic security validator

  RAG returns irrelevant context      metadata filtering + threshold

  Large prompts                       top-K + context compression

  LLM changes framework               strict system prompt + validation

  Report inconsistency                existing Extent Report remains
                                      source of truth

  Concurrent test collision           isolated execution workspaces

  Framework changes invalidate        framework versioning
  scripts                             

  Infinite correction loop            configurable retry limit

  User story not fully covered        acceptance-criteria coverage
                                      validator
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 79. Recommended Implementation Phases

## Phase 1 --- Framework Discovery

-   Index existing Python framework.
-   Identify Page Objects.
-   Identify fixtures.
-   Identify Reporter.
-   Identify test naming conventions.
-   Build framework symbol registry.

## Phase 2 --- RAG

-   Implement document ingestion.
-   Add Mistral embeddings.
-   Configure MongoDB Atlas Vector Search.
-   Implement metadata filtering.
-   Implement retrieval.

## Phase 3 --- LangChain + Groq

-   Implement prompts.
-   Implement generation chain.
-   Implement structured output.
-   Implement validation/correction loop.

## Phase 4 --- Node.js API

-   User story API.
-   Generation API.
-   Script API.
-   Chat API.
-   Execution API.
-   Report API.

## Phase 5 --- React UI

-   User story editor.
-   Script viewer/editor.
-   Chat interface.
-   Execution controls.
-   Reports dashboard.
-   Version history.

## Phase 6 --- Execution Integration

-   Controlled pytest execution.
-   Execution workspace.
-   Log collection.
-   Extent Report integration.

## Phase 7 --- Hardening

-   Security.
-   Prompt injection protection.
-   Rate limiting.
-   Audit logging.
-   AI evaluation.
-   Golden test suite.

------------------------------------------------------------------------

# 80. Definition of Done

The architecture implementation is complete only when:

-   [ ] User can enter a user story through React UI.
-   [ ] Acceptance criteria can be entered.
-   [ ] Backend retrieves relevant framework context using RAG.
-   [ ] Mistral AI generates embeddings.
-   [ ] LangChain orchestrates retrieval and generation.
-   [ ] Groq generates Python Playwright scripts.
-   [ ] Existing Python Playwright framework remains the execution
    target.
-   [ ] Existing Page Objects are reused.
-   [ ] Existing pytest fixtures are reused.
-   [ ] Existing Reporter is reused.
-   [ ] Existing Extent Report remains the reporting source.
-   [ ] Rule-based generation is removed.
-   [ ] Deterministic validation remains for safety and compatibility.
-   [ ] Generated scripts are shown in React UI.
-   [ ] Users can chat with the LLM to modify scripts.
-   [ ] Script versions are maintained.
-   [ ] Scripts can be executed from the UI.
-   [ ] Execution logs are visible.
-   [ ] Extent Report results appear in the dashboard.
-   [ ] `.env` configuration is supported.
-   [ ] API keys are not exposed to the frontend.
-   [ ] Acceptance criteria coverage is validated.
-   [ ] Generated code passes syntax and framework validation.
-   [ ] Unsafe generated code is rejected.
-   [ ] RAG context is versioned.
-   [ ] The supplied TC001-style framework structure remains compatible.

------------------------------------------------------------------------

# 81. Final Architecture Principle

The final system should be treated as an **AI-assisted test engineering
platform**, not an AI replacement for the existing automation framework.

The correct architecture is:

``` text
             REQUIREMENT
                  |
                  v
              RAG CONTEXT
                  |
                  v
              LANGCHAIN
                  |
                  v
               GROQ LLM
                  |
                  v
       PYTHON PLAYWRIGHT SCRIPT
                  |
          +-------+-------+
          |               |
          v               v
   DETERMINISTIC      FRAMEWORK
    VALIDATION        VALIDATION
          |               |
          +-------+-------+
                  |
                  v
            EXISTING PYTEST
                  |
                  v
          EXISTING PLAYWRIGHT
                  |
                  v
          EXISTING REPORTER
                  |
                  v
            EXTENT REPORT
                  |
                  v
          REPORTS DASHBOARD
```

The most important constraint is:

> **Do not rebuild the existing Python Playwright framework. Make the AI
> understand and generate code for it.**

This preserves the organization's existing automation investment while
adding LLM-powered test design, generation, maintenance, and
conversational modification.
