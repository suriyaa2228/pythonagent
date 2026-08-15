# Architecture: Python Playwright Rule-Based Automation Agent

## 1. Document Purpose

This document defines the architecture for a **Python Playwright
Rule-Based Automation Agent**.

The primary objective is to allow an agent to execute existing **Python
Playwright automation scripts** through a deterministic, rule-based
orchestration layer.

### Mandatory architectural principles

1.  **Python Playwright is the automation execution technology.**
2.  **The agent must work without an LLM.**
3.  **MongoDB must be optional.**
4.  **The rule engine and state machine are the primary decision
    mechanisms.**
5.  Existing Playwright scripts must be incorporated into the agent
    through a controlled executor interface.
6.  An LLM may be added later for optional reasoning capabilities such
    as natural-language intent interpretation and failure analysis.
7.  The LLM must never have unrestricted direct access to execute
    arbitrary Python code or browser actions.
8.  The architecture must support a future MongoDB Vector Search
    capability without making MongoDB a runtime dependency.

------------------------------------------------------------------------

# 2. Executive Recommendation

The recommended architecture is:

``` text
                    +----------------------+
                    | Vanilla JS/HTML UI   |
                    |   (Web Dashboard)    |
                    +----------+-----------+
                               |
                         REST API Calls
                               |
                               v
                    +----------------------+
                    |      FastAPI         |
                    |     Agent API        |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Agent Orchestrator   |
                    +----------+-----------+
                               |
              +----------------+----------------+
              |                |                |
              v                v                v
       +-------------+  +-------------+  +-------------+
       | State       |  | Rule Engine |  | Test        |
       | Machine     |  |             |  | Registry    |
       +-------------+  +-------------+  +-------------+
              |                |                |
              +----------------+----------------+
                               |
                               v
                    +----------------------+
                    | Playwright Executor  |
                    |      Python          |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Existing Python      |
                    | Playwright Scripts   |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Browser              |
                    | Chromium / Firefox   |
                    +----------------------+

Optional capabilities:

                    +----------------------+
                    | MongoDB              |
                    | Metadata / Vector DB |
                    +----------------------+

                    +----------------------+
                    | LLM                  |
                    | Optional Reasoning   |
                    +----------------------+
```

The core system does **not** depend on either MongoDB or an LLM.

------------------------------------------------------------------------

# 3. Core Architecture Principle

An agent does not have to be an LLM-based system.

For this project:

``` text
Agent
=
Orchestrator
+
State Machine
+
Rule Engine
+
Tools
+
Execution State
+
Optional Memory
```

The primary control loop is:

``` text
Receive Task
      |
      v
Validate Task
      |
      v
Find Test
      |
      v
Prepare Environment
      |
      v
Execute Playwright
      |
      v
Observe Result
      |
      v
Evaluate Rules
      |
      v
Choose Next Action
      |
      +---------> Retry
      |
      +---------> Capture Artifacts
      |
      +---------> Continue
      |
      +---------> Stop
      |
      v
Generate Result
```

This provides deterministic and auditable behavior.

------------------------------------------------------------------------

# 4. Technology Stack

## 4.1 Frontend

  Component                     Current Technology
  ----------------------------- ------------------------
  Framework                     Vanilla JS / HTML
  Language                      JavaScript
  Build Tool                    None (Served via FastAPI static files)
  UI Library                    Custom CSS
  State Management              Vanilla DOM Events
  API Communication             REST
  Charts                        None

### Frontend responsibilities

The frontend should provide:

``` text
Dashboard
|
+-- Agents
+-- Test Suites
+-- Test Cases
+-- Executions
+-- Execution Logs
+-- Test Reports
+-- Failures
+-- Agent Configuration
+-- Rule Configuration
+-- Environment Configuration
```

The frontend must not execute Playwright scripts directly.

All execution requests must go through the backend API.

------------------------------------------------------------------------

# 5. Backend Technology

## 5.1 Recommended Backend

``` text
Python
+
FastAPI
+
Playwright
+
Pydantic
+
Redis
+
Background Worker
```

Python is recommended because the existing automation scripts are
already Python + Playwright.

This avoids unnecessary cross-language communication between:

``` text
Node.js
    |
    v
Python Playwright
```

Instead:

``` text
FastAPI
    |
    v
Python Agent
    |
    v
Python Playwright
```

------------------------------------------------------------------------

# 6. Backend Components

``` text
backend/
|
+-- api/
|   +-- routes/
|       +-- agent_routes.py
|       +-- execution_routes.py
|       +-- test_routes.py
|
+-- agent/
|   +-- orchestrator/
|   |   +-- agent_orchestrator.py
|   |
|   +-- planner/
|   |   +-- task_planner.py
|   |
|   +-- state/
|   |   +-- agent_state.py
|   |   +-- state_machine.py
|   |
|   +-- rules/
|   |   +-- rule_engine.py
|   |   +-- execution_rules.py
|   |   +-- recovery_rules.py
|   |
|   +-- executor/
|   |   +-- playwright_executor.py
|   |
|   +-- registry/
|   |   +-- test_registry.py
|   |
|   +-- reporting/
|       +-- report_manager.py
|
+-- config/
|   +-- settings.py
|
+-- models/
|   +-- task.py
|   +-- execution.py
|   +-- test_case.py
|
+-- storage/
|   +-- file_store.py
|   +-- optional_mongodb.py
|
+-- workers/
|   +-- execution_worker.py
|
+-- tests/
|
+-- main.py
```

------------------------------------------------------------------------

# 7. Agent Components

## 7.1 Agent Orchestrator

The orchestrator is the central controller.

Responsibilities:

-   Receive task
-   Validate task
-   Resolve test case
-   Prepare execution context
-   Invoke rule engine
-   Invoke Playwright executor
-   Observe execution result
-   Transition agent state
-   Trigger recovery rules
-   Produce final result

Example:

``` python
class AgentOrchestrator:

    def execute(self, task):
        state = self.state_machine.initialize(task)

        while not state.is_terminal():

            action = self.rule_engine.decide(state)

            state = self.execute_action(action, state)

            self.state_machine.validate_transition(state)

        return state.result
```

The orchestrator should not contain business rules directly.

------------------------------------------------------------------------

# 8. State Machine

The state machine controls the lifecycle of an agent execution.

## Recommended states

``` text
RECEIVED
   |
   v
VALIDATING
   |
   v
VALIDATED
   |
   v
TEST_RESOLVED
   |
   v
ENVIRONMENT_VALIDATED
   |
   v
EXECUTING
   |
   v
OBSERVING
   |
   +----------+
   |          |
   v          v
PASSED      FAILED
              |
              v
       FAILURE_ANALYSIS
              |
        +-----+-----+
        |           |
        v           v
      RETRY        STOP
        |
        v
   EXECUTING

PASSED / STOP
      |
      v
REPORTING
      |
      v
COMPLETED
```

## Example state object

``` python
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AgentState:
    task_id: str
    test_id: Optional[str] = None
    environment: Optional[str] = None
    execution_id: Optional[str] = None
    status: str = "RECEIVED"
    retry_count: int = 0
    max_retries: int = 2
    failure_type: Optional[str] = None
    failure_message: Optional[str] = None
    artifacts: list[str] = field(default_factory=list)
```

------------------------------------------------------------------------

# 9. Rule-Based Engine

The rule engine is the primary decision-making component.

## Example rules

### Rule 001 - Validate test

``` text
IF test_id does not exist
THEN FAIL_TASK
```

### Rule 002 - Validate environment

``` text
IF environment is unavailable
THEN FAIL_TASK
```

### Rule 003 - Start execution

``` text
IF test exists
AND environment is available
AND agent status is VALIDATED
THEN EXECUTE_TEST
```

### Rule 004 - Capture artifacts

``` text
IF execution.status == FAILED
THEN CAPTURE_SCREENSHOT
AND CAPTURE_LOG
AND CAPTURE_VIDEO
```

### Rule 005 - Retry timeout

``` text
IF failure.type == TIMEOUT
AND retry_count < max_retries
THEN RETRY
```

### Rule 006 - Stop retry

``` text
IF retry_count >= max_retries
THEN MARK_FAILED
```

------------------------------------------------------------------------

# 10. Rule Engine Design

Rules should be separated from execution code.

Recommended structure:

``` python
class Rule:
    name: str

    def matches(self, state) -> bool:
        raise NotImplementedError

    def execute(self, state):
        raise NotImplementedError
```

Example:

``` python
class RetryTimeoutRule(Rule):

    name = "retry_timeout"

    def matches(self, state):
        return (
            state.failure_type == "TIMEOUT"
            and state.retry_count < state.max_retries
        )

    def execute(self, state):
        state.retry_count += 1
        state.status = "EXECUTING"
        return state
```

This design allows additional rules to be added without modifying the
orchestrator.

------------------------------------------------------------------------

# 11. Incorporating Existing Python Playwright Scripts

This is a mandatory architectural requirement.

The existing Playwright scripts should **not** be copied into the agent
orchestrator.

Instead, create a controlled **Playwright Executor Adapter**.

## Existing automation

For example:

``` text
tests/
|
+-- login/
|   +-- test_login.py
|
+-- checkout/
|   +-- test_checkout.py
|
+-- payment/
|   +-- test_payment.py
```

The agent should treat these scripts as executable test assets.

------------------------------------------------------------------------

# 12. Recommended Playwright Script Contract

The strongest approach is to gradually standardize existing scripts
behind a common contract.

Instead of allowing the agent to know the internal implementation of
every test, expose a standard entry point.

Example:

``` python
class PlaywrightTest:

    def run(self, context):
        raise NotImplementedError
```

Example test:

``` python
from playwright.sync_api import sync_playwright


class LoginTest(PlaywrightTest):

    def run(self, context):

        with sync_playwright() as p:

            browser = p.chromium.launch(
                headless=context.headless
            )

            page = browser.new_page()

            page.goto(context.base_url)

            page.fill("#username", context.username)
            page.fill("#password", context.password)

            page.click("#login")

            page.wait_for_url("**/dashboard")

            browser.close()

        return {
            "status": "PASSED"
        }
```

However, if existing scripts cannot immediately be refactored, the agent
should support a second adapter mode.

------------------------------------------------------------------------

# 13. Two Ways to Integrate Existing Scripts

## Option A - Recommended

Convert scripts to a standard callable interface.

``` text
Agent
  |
  v
PlaywrightExecutor
  |
  v
Test Registry
  |
  v
Python Test Class
  |
  v
Playwright
```

Example registry:

``` python
TEST_REGISTRY = {
    "TC_LOGIN_001": "tests.login.test_login.LoginTest",
    "TC_CHECKOUT_001": "tests.checkout.test_checkout.CheckoutTest",
}
```

The executor dynamically resolves the registered test.

------------------------------------------------------------------------

## Option B - Transitional Approach

If the existing scripts are standalone Python files:

``` text
test_login.py
test_checkout.py
test_payment.py
```

the executor can launch them as subprocesses.

Example:

``` python
import subprocess


class PlaywrightExecutor:

    def execute(self, script_path, environment):

        result = subprocess.run(
            ["python", script_path],
            capture_output=True,
            text=True
        )

        return {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "status": (
                "PASSED"
                if result.returncode == 0
                else "FAILED"
            )
        }
```

### Important

This is useful for migration, but it should not be the final
architecture.

The target architecture should move toward a standard test contract.

------------------------------------------------------------------------

# 14. Recommended Test Execution Contract

Every Playwright test should eventually expose:

``` text
Input
|
+-- environment
+-- browser
+-- headless
+-- credentials reference
+-- test data
+-- execution id
|
v
Playwright Test
|
v
Output
|
+-- status
+-- duration
+-- steps
+-- error
+-- screenshots
+-- video
+-- trace
+-- logs
```

Example:

``` json
{
  "executionId": "EXEC-1001",
  "testId": "TC_LOGIN_001",
  "status": "PASSED",
  "duration": 14.32,
  "artifacts": [
    "screenshots/login.png",
    "videos/EXEC-1001.webm"
  ]
}
```

------------------------------------------------------------------------

# 15. Test Registry

The agent needs a controlled mapping between test IDs and Playwright
implementations.

Example:

``` json
{
  "TC_LOGIN_001": {
    "name": "Valid Login",
    "type": "playwright",
    "module": "tests.login.test_login",
    "class": "LoginTest",
    "enabled": true
  },
  "TC_CHECKOUT_001": {
    "name": "Checkout",
    "type": "playwright",
    "module": "tests.checkout.test_checkout",
    "class": "CheckoutTest",
    "enabled": true
  }
}
```

The registry can initially be a version-controlled JSON/YAML
configuration.

MongoDB is not required.

------------------------------------------------------------------------

# 16. Agent API

## Execute Test

``` http
POST /api/v1/agent/tasks
```

Request:

``` json
{
  "action": "run_test",
  "testId": "TC_LOGIN_001",
  "environment": "staging"
}
```

Response:

``` json
{
  "taskId": "TASK-1001",
  "executionId": "EXEC-1001",
  "status": "QUEUED"
}
```

------------------------------------------------------------------------

## Get Execution

``` http
GET /api/v1/executions/{executionId}
```

Response:

``` json
{
  "executionId": "EXEC-1001",
  "testId": "TC_LOGIN_001",
  "status": "PASSED",
  "duration": 12.45
}
```

------------------------------------------------------------------------

## Cancel Execution

``` http
POST /api/v1/executions/{executionId}/cancel
```

------------------------------------------------------------------------

## Get Logs

``` http
GET /api/v1/executions/{executionId}/logs
```

------------------------------------------------------------------------

# 17. Background Execution

Playwright execution should not block the FastAPI request thread.

Recommended:

``` text
POST /agent/tasks
        |
        v
FastAPI
        |
        v
Queue
        |
        v
Worker
        |
        v
Agent Orchestrator
        |
        v
Playwright
```

Recommended components:

``` text
Redis
+
Celery
```

or a simpler worker implementation initially.

For a first production version:

``` text
FastAPI
+
Redis
+
Celery
```

is a reasonable choice.

------------------------------------------------------------------------

# 18. Execution Artifacts

Every execution should generate structured artifacts.

``` text
artifacts/
|
+-- EXEC-1001/
|   |
|   +-- screenshots/
|   +-- videos/
|   +-- traces/
|   +-- logs/
|   +-- result.json
|   +-- stdout.log
|   +-- stderr.log
```

The agent should store artifact metadata separately from large binary
files.

------------------------------------------------------------------------

# 19. Environment Management

Do not hard-code environment URLs or credentials inside Playwright
scripts.

Use configuration:

``` text
ENVIRONMENT=staging
BASE_URL=https://staging.example.com
```

Recommended environment configuration:

``` json
{
  "staging": {
    "baseUrl": "https://staging.example.com"
  },
  "production": {
    "baseUrl": "https://www.example.com"
  }
}
```

Credentials should be retrieved from a secure secret store.

Do not store passwords in:

-   Source code
-   Git
-   Test registry
-   MongoDB documents
-   Logs

------------------------------------------------------------------------

# 20. MongoDB - STRICTLY OPTIONAL

MongoDB must not be required for the core agent.

## Without MongoDB

The system can operate using:

``` text
Git / YAML / JSON
       +
Local artifact storage
       +
Rule configuration
       +
Test registry
```

Architecture:

``` text
FastAPI
   |
Agent
   |
Rule Engine
   |
Test Registry
   |
Playwright
```

This is the minimum viable architecture.

------------------------------------------------------------------------

# 21. MongoDB - Optional Extension

MongoDB can be introduced later for:

``` text
Test Case Metadata
Execution History
Agent State
Rules
Failure History
Knowledge Base
```

Optional architecture:

``` text
              Agent
                |
          +-----+------+
          |            |
          v            v
       Files       MongoDB
                    |
                    v
              Vector Search
```

MongoDB should therefore be an **optional persistence and knowledge
layer**, not a hard dependency of the agent runtime.

------------------------------------------------------------------------

# 22. MongoDB Vector Search - Optional Future Capability

When semantic retrieval becomes necessary, store embeddings for:

``` text
Test Cases
Failure Messages
Execution Logs
Known Issues
Troubleshooting Knowledge
```

Example:

``` json
{
  "testId": "TC_CHECKOUT_001",
  "description": "Verify checkout flow",
  "failure": "Checkout button timeout",
  "embedding": [0.012, -0.234, 0.554]
}
```

Future flow:

``` text
Current Failure
      |
      v
Generate Embedding
      |
      v
MongoDB Vector Search
      |
      v
Similar Historical Failures
      |
      v
Rule Engine / Optional LLM
```

The vector database should not be added until there is a real semantic
retrieval requirement.

------------------------------------------------------------------------

# 23. LLM - STRICTLY OPTIONAL

The core system must work without an LLM.

## Core system

``` text
Rule Engine
+
State Machine
+
Playwright
```

is sufficient.

The LLM can later be introduced for:

### Natural-language task interpretation

``` text
"Run all checkout tests on staging"
```

becomes:

``` json
{
  "action": "run_suite",
  "suite": "checkout",
  "environment": "staging"
}
```

### Failure analysis

Input:

``` text
Playwright error
+
Screenshot
+
DOM snapshot
+
Network logs
+
Historical failures
```

Output:

``` text
Likely cause:
Checkout selector changed.

Recommended action:
Validate selector and update test.
```

### Test discovery

``` text
"Run tests related to payment failure"
```

can retrieve semantically related tests.

------------------------------------------------------------------------

# 24. LLM Safety Boundary

The LLM must not directly execute arbitrary Python.

Bad architecture:

``` text
User
 |
 v
LLM
 |
 v
Execute Python
 |
 v
Browser
```

Recommended:

``` text
User
 |
 v
LLM
 |
 v
Structured Action
 |
 v
Schema Validation
 |
 v
Authorization
 |
 v
Rule Engine
 |
 v
Approved Tool
 |
 v
Playwright
```

Example allowed action:

``` json
{
  "action": "run_test",
  "testId": "TC_123",
  "environment": "staging"
}
```

The agent validates the action before execution.

------------------------------------------------------------------------

# 25. Complete Agent Execution Example

User request:

``` text
Run the checkout test on staging.
```

## Step 1 - Receive task

``` json
{
  "action": "run_test",
  "testId": "TC_CHECKOUT_001",
  "environment": "staging"
}
```

## Step 2 - Validate

``` text
Test exists?
YES

Environment exists?
YES

Test enabled?
YES

User authorized?
YES
```

## Step 3 - Initialize state

``` text
RECEIVED
    |
VALIDATING
    |
VALIDATED
```

## Step 4 - Resolve test

``` text
TC_CHECKOUT_001
       |
       v
tests.checkout.test_checkout.CheckoutTest
```

## Step 5 - Execute

``` text
PLAYWRIGHT_EXECUTOR
       |
       v
CheckoutTest.run()
       |
       v
Chromium
```

## Step 6 - Observe

``` text
PASSED
```

## Step 7 - Report

``` json
{
  "executionId": "EXEC-1001",
  "status": "PASSED",
  "duration": 42.1
}
```

------------------------------------------------------------------------

# 26. Failure Scenario

Suppose Playwright reports:

``` text
Timeout waiting for:
button[data-testid="checkout"]
```

Agent state:

``` text
EXECUTING
   |
   v
FAILED
   |
   v
OBSERVING
```

Rule engine evaluates:

``` text
Is failure retryable?
YES

Retry count < 2?
YES
```

Action:

``` text
RETRY
```

After retry:

``` text
PASSED
```

If retry fails twice:

``` text
FAILED
   |
   v
CAPTURE_ARTIFACTS
   |
   v
REPORT
   |
   v
COMPLETED
```

No LLM is required.

------------------------------------------------------------------------

# 27. Agent Decision Flow

``` text
                    +----------------+
                    | Receive Task   |
                    +-------+--------+
                            |
                            v
                    +----------------+
                    | Validate Task  |
                    +-------+--------+
                            |
                            v
                    +----------------+
                    | Resolve Test   |
                    +-------+--------+
                            |
                            v
                    +----------------+
                    | Validate Env   |
                    +-------+--------+
                            |
                            v
                    +----------------+
                    | Execute Test   |
                    +-------+--------+
                            |
                            v
                    +----------------+
                    | Observe Result |
                    +-------+--------+
                            |
                 +----------+----------+
                 |                     |
                 v                     v
              PASSED                FAILED
                 |                     |
                 |                     v
                 |              +-------------+
                 |              | Apply Rules |
                 |              +------+------+
                 |                     |
                 |              +------+------+
                 |              |             |
                 |              v             v
                 |            RETRY          STOP
                 |              |             |
                 |              +----->-------+
                 |                            |
                 +------------+---------------+
                              |
                              v
                       Generate Report
                              |
                              v
                         COMPLETED
```

------------------------------------------------------------------------

# 28. Project Structure

Recommended final project:

``` text
playwright-agent/
|
+-- frontend/
|   +-- src/
|   +-- package.json
|
+-- backend/
|   |
|   +-- api/
|   |   +-- routes/
|   |
|   +-- agent/
|   |   +-- orchestrator/
|   |   +-- planner/
|   |   +-- rules/
|   |   +-- state/
|   |   +-- executor/
|   |   +-- registry/
|   |   +-- reporting/
|   |
|   +-- models/
|   +-- config/
|   +-- workers/
|   +-- storage/
|   |
|   +-- main.py
|   +-- requirements.txt
|
+-- tests/
|   +-- login/
|   +-- checkout/
|   +-- payment/
|
+-- config/
|   +-- test_registry.yaml
|   +-- rules.yaml
|   +-- environments.yaml
|
+-- artifacts/
|
+-- docs/
|   +-- architecture.md
|
+-- Dockerfile
+-- docker-compose.yml
+-- README.md
```

------------------------------------------------------------------------

# 29. Implementation Roadmap

## Phase 1 - Playwright Execution Engine

Build:

``` text
FastAPI
    |
Playwright Executor
    |
Existing Python Playwright scripts
```

Deliverables:

-   Execution API
-   Test registry
-   Playwright executor
-   Execution status
-   Logs
-   Screenshots
-   Result handling

------------------------------------------------------------------------

## Phase 2 - Agent Orchestrator

Add:

``` text
Agent Orchestrator
+
State Machine
```

Deliverables:

-   Task lifecycle
-   State transitions
-   Execution tracking
-   Error handling

------------------------------------------------------------------------

## Phase 3 - Rule Engine

Add:

``` text
Rule Engine
```

Implement:

-   Validation rules
-   Retry rules
-   Timeout rules
-   Artifact rules
-   Failure rules
-   Stop conditions

------------------------------------------------------------------------

## Phase 4 - Worker Infrastructure

Add:

``` text
Redis
+
Celery
```

This enables asynchronous test execution and multiple concurrent
executions.

------------------------------------------------------------------------

## Phase 5 - React Dashboard

Build:

``` text
Dashboard
Test Cases
Executions
Logs
Reports
Agent Status
```

------------------------------------------------------------------------

## Phase 6 - Optional MongoDB

Only after the core agent works reliably.

Add:

``` text
MongoDB
|
+-- Execution History
+-- Test Metadata
+-- Failure History
+-- Knowledge
```

------------------------------------------------------------------------

## Phase 7 - Optional Vector Search

Add semantic retrieval for:

``` text
Similar Tests
Similar Failures
Historical Issues
Knowledge Retrieval
```

------------------------------------------------------------------------

## Phase 8 - Optional LLM

Introduce LLM for:

``` text
Natural Language → Structured Task
Failure Analysis
Test Discovery
Root Cause Suggestions
```

The LLM remains outside the deterministic execution boundary.

------------------------------------------------------------------------

## Phase 9 - Intelligent Recovery

Potential future flow:

``` text
Playwright Failure
       |
       v
Rule Engine
       |
       v
Retrieve Similar Failures
       |
       v
Optional LLM
       |
       v
Recovery Recommendation
       |
       v
Policy Validation
       |
       v
Approved Recovery Action
       |
       v
Playwright
```

Automatic test-code modification should **not** be enabled by default.

------------------------------------------------------------------------

# 30. Security and Governance

The agent should enforce:

## Authentication

All API endpoints should require authentication.

## Authorization

Users should have permissions for:

``` text
Run Test
Cancel Test
View Logs
Manage Rules
Manage Environments
Manage Test Registry
Run Production Tests
```

## Environment Protection

Production execution should require additional authorization.

Example:

``` text
IF environment == production
AND user.role != authorized
THEN DENY
```

## Audit Trail

Record:

``` text
Who
What
When
Which test
Which environment
Which rule
Which action
Result
```

## Secret Protection

Credentials must never be exposed in:

-   Logs
-   API responses
-   Screenshots
-   Source code
-   Test registry

------------------------------------------------------------------------

# 31. Observability

Every agent execution should generate structured logs.

Example:

``` json
{
  "timestamp": "2026-08-10T10:30:00Z",
  "taskId": "TASK-1001",
  "executionId": "EXEC-1001",
  "state": "EXECUTING",
  "action": "RUN_PLAYWRIGHT",
  "testId": "TC_LOGIN_001"
}
```

Metrics should include:

``` text
Total executions
Passed
Failed
Retries
Average duration
Failure rate
Timeout rate
Browser launch failures
Environment failures
```

------------------------------------------------------------------------

# 32. Non-Functional Requirements

## Reliability

The agent must not lose execution state when a test fails.

## Determinism

The same task and same environment should produce predictable decisions
under the same conditions.

## Scalability

Multiple Playwright executions should be supported through worker
processes.

## Maintainability

Rules, test registrations, and execution logic should remain
independently maintainable.

## Security

Execution must be controlled through authorization and approved actions.

## Auditability

Every agent decision should be traceable to a rule or approved system
action.

------------------------------------------------------------------------

# 33. Anti-Patterns to Avoid

## Anti-pattern 1 - LLM-first architecture

``` text
User
 ↓
LLM
 ↓
Playwright
```

Do not start here.

------------------------------------------------------------------------

## Anti-pattern 2 - Hard-coded agent rules

Avoid a giant:

``` python
if/elif/else
```

chain.

Use independent rule classes.

------------------------------------------------------------------------

## Anti-pattern 3 - Direct browser access from API

The API layer should not contain Playwright test logic.

Use:

``` text
API
 ↓
Agent
 ↓
Executor
 ↓
Playwright
```

------------------------------------------------------------------------

## Anti-pattern 4 - MongoDB as a mandatory dependency

The MVP should work without MongoDB.

------------------------------------------------------------------------

## Anti-pattern 5 - LLM controlling arbitrary code

Never allow:

``` text
LLM → arbitrary Python execution
```

Use structured, validated actions.

------------------------------------------------------------------------

## Anti-pattern 6 - Agent modifying test scripts automatically

Do not allow autonomous test-code changes in the first version.

A failure-analysis system can recommend a change, but a human or
controlled workflow should approve modifications.

------------------------------------------------------------------------

# 34. MVP Definition

The first working version should contain only:

``` text
React
+
FastAPI
+
Agent Orchestrator
+
State Machine
+
Rule Engine
+
Test Registry
+
Playwright Executor
+
Existing Python Playwright Scripts
+
Artifact Storage
```

### Explicitly excluded from MVP

``` text
MongoDB
Vector Search
LLM
Autonomous Code Modification
Complex AI Planning
```

This keeps the first implementation deterministic and testable.

------------------------------------------------------------------------

# 35. Final Recommended Architecture

``` text
                         USER
                           |
                           v
                 +-------------------+
                 | React + TypeScript |
                 +---------+---------+
                           |
                     REST / WebSocket
                           |
                           v
                 +-------------------+
                 |      FastAPI      |
                 +---------+---------+
                           |
                           v
                 +-------------------+
                 | Agent Orchestrator|
                 +---------+---------+
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
       +-----------+ +-----------+ +-----------+
       |   State   | |   Rule    | |   Test    |
       |  Machine  | |  Engine   | |  Registry |
       +-----------+ +-----------+ +-----------+
             |             |             |
             +-------------+-------------+
                           |
                           v
                 +-------------------+
                 | Playwright        |
                 | Executor          |
                 +---------+---------+
                           |
                           v
                 +-------------------+
                 | Existing Python   |
                 | Playwright Tests  |
                 +---------+---------+
                           |
                           v
                 +-------------------+
                 | Browser           |
                 | Chromium/Firefox  |
                 +-------------------+

                    OPTIONAL
                       |
          +------------+------------+
          |                         |
          v                         v
    +-----------+             +-----------+
    | MongoDB   |             | LLM       |
    | Vector    |             | Reasoning |
    | Search    |             |           |
    +-----------+             +-----------+
```

------------------------------------------------------------------------

# 36. Architecture Decision Summary

  Decision                       Recommendation               Mandatory
  ------------------------------ ---------------------------- ------------
  Python                         Yes                          Yes
  Playwright                     Yes                          Yes
  FastAPI                        Yes                          Yes
  React                          Yes                          Yes for UI
  TypeScript                     Yes                          Yes for UI
  Rule Engine                    Yes                          Yes
  State Machine                  Yes                          Yes
  Playwright Executor            Yes                          Yes
  Test Registry                  Yes                          Yes
  Redis                          Recommended                  No
  Celery                         Recommended for scale        No
  MongoDB                        Optional                     **No**
  MongoDB Vector Search          Optional future capability   **No**
  LLM                            Optional                     **No**
  Failure Analysis               Rule-based initially         Yes
  LLM Failure Analysis           Future                       No
  Autonomous Code Modification   Not recommended initially    No

------------------------------------------------------------------------

# 37. Final Architecture Recommendation

The project should be built as a **deterministic Rule-Based Playwright
Agent first**.

The correct progression is:

``` text
Existing Playwright Scripts
            |
            v
Playwright Executor
            |
            v
Agent Orchestrator
            |
            v
State Machine
            |
            v
Rule Engine
            |
            v
Reliable Agent
            |
            +----------------------+
            |                      |
            v                      v
       Optional MongoDB       Optional LLM
            |                      |
       Vector Search          Reasoning
            |                      |
            +----------+-----------+
                       |
                       v
              Intelligent Agent
```

The core principle is:

> **Make the automation agent reliable without AI first. Add AI only
> where it solves a demonstrated reasoning problem.**

This gives the system a stable foundation, avoids unnecessary LLM cost
and unpredictability, and allows MongoDB and LLM capabilities to be
introduced independently without redesigning the core Playwright
execution architecture.
