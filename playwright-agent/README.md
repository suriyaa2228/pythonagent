# Python Playwright Rule-Based Automation Agent

This is a deterministic, rule-based execution engine and orchestrator for Python Playwright scripts. It provides a FastAPI backend that runs your existing standalone Playwright scripts using a background task queue, a State Machine, and a Rule Engine.

## Features

- **No LLM Dependency**: Core execution logic is deterministic and driven by rules.
- **State Machine**: Tracks the lifecycle of tests (`RECEIVED` -> `VALIDATING` -> `EXECUTING` -> `OBSERVING` -> `PASSED`/`FAILED`).
- **Rule Engine**: Clean separation of decision-making logic (retries, timeouts, validation).
- **FastAPI Backend**: Provides REST endpoints to trigger executions and query results.
- **Web Dashboard**: An intuitive Web UI served by FastAPI to easily run tests, track progress, and view reports.
- **Subprocess Executor**: Easily integrates with your existing `.py` Playwright tests without requiring immediate code refactoring.

## Getting Started

### Prerequisites
- Python 3.9+
- `pip`

### Installation

1. Create and activate a virtual environment (optional but recommended):
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

3. (If you haven't already installed playwright browsers):
   ```powershell
   playwright install
   ```

### Running the Server

Start the FastAPI application locally:

```powershell
uvicorn main:app --reload
```

The Web Dashboard will be available at `http://127.0.0.1:8000/`.
The API is available at `http://127.0.0.1:8000/api/v1/agent`.
You can view the interactive API documentation (Swagger UI) at `http://127.0.0.1:8000/docs`.

---

## How to Test It

The repository comes with two mock tests out of the box (`TC_MOCK_SUCCESS` and `TC_MOCK_FAILURE`) to help you verify the execution loop.

### 1. Using the Web Dashboard (Recommended)

Open `http://127.0.0.1:8000/` in your browser. From the Dashboard, you can select an environment, pick tests from the list, run them, and view real-time logs and results. You can also navigate to the "Reports Dashboard" to view execution history.

### 2. Using the API (cURL)

#### Trigger a Test Execution

Using `curl` or Postman, send a `POST` request to start a task:

```powershell
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/agent/tasks' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "action": "run_test",
  "testId": "TC_MOCK_SUCCESS",
  "environment": "staging"
}'
```

You will get a response with an `executionId` and a `taskId`:
```json
{
  "taskId": "TASK-a1b2c3d4",
  "executionId": "EXEC-e5f6g7h8",
  "status": "QUEUED"
}
```

### 2. Check Execution Status

Use the `executionId` from the previous step to poll the status of your test:

```powershell
curl -X 'GET' 'http://127.0.0.1:8000/api/v1/executions/EXEC-e5f6g7h8' -H 'accept: application/json'
```

If the test is finished, you'll see a response like:
```json
{
  "status": "COMPLETED",
  "duration": 2.01,
  "stdout": "Starting mock success test...\nEnvironment: staging\n...",
  "stderr": "",
  "failure_message": null
}
```

### 3. Retrieve Execution Logs

You can specifically request the standard output and error logs:

```powershell
curl -X 'GET' 'http://127.0.0.1:8000/api/v1/executions/EXEC-e5f6g7h8/logs' -H 'accept: application/json'
```

---

## How to Integrate Existing Playwright Scripts

One of the main architectural benefits of this agent is the **Playwright Subprocess Executor**. You do not need to rewrite your existing Playwright `.py` scripts to use them.

### Step 1: Place your script in the repository
Copy your existing python script into the agent directory (e.g., inside a `tests/` folder).

*Example:* `tests/checkout/my_checkout_test.py`

### Step 2: Register your script
Open `config/test_registry.yaml` and add a new entry for your test. Assign it a unique `testId` (e.g., `TC_CHECKOUT_001`).

```yaml
TC_CHECKOUT_001:
  name: "My Existing Checkout Test"
  type: "python_script"
  path: "tests/checkout/my_checkout_test.py"
  enabled: true
```

### Step 3: Run your script via the API
You can now trigger your existing script via the orchestrator! 

```json
POST /api/v1/agent/tasks

{
  "action": "run_test",
  "testId": "TC_CHECKOUT_001",
  "environment": "production"
}
```

### Accessing the Environment Variable (Optional)
If your script needs to know which environment it is running against (e.g., staging vs. production), the agent automatically injects a `TEST_ENVIRONMENT` environment variable into the subprocess.

You can access it inside your existing scripts like this:

```python
import os

environment = os.environ.get("TEST_ENVIRONMENT", "default")
print(f"Running script against: {environment}")
```
