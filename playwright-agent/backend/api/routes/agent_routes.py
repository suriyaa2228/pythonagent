import uuid
import os
import datetime
from fastapi import APIRouter, BackgroundTasks, HTTPException
from models.task import AgentTaskRequest, AgentTaskResponse, AgentTestListResponse, AgentTestInfo
from agent.registry.test_registry import TestRegistry
from agent.executor.playwright_executor import PlaywrightExecutor
from agent.orchestrator.agent_orchestrator import AgentOrchestrator

router = APIRouter()
registry = TestRegistry()
executor = PlaywrightExecutor()
orchestrator = AgentOrchestrator(registry, executor)

# In-memory store for execution results (for MVP)
executions = {}



def run_task_background(task_id: str, execution_id: str, test_ids: list[str], environment: str, engine: str = "PYTEST", headless: bool = False):
    total_count = len(test_ids)
    first_test = test_ids[0] if test_ids else ""
    executions[execution_id] = {
        "status": "QUEUED",
        "total_tests": total_count,
        "completed_tests": 0,
        "current_test": first_test,
        "current_test_index": 1,
        "progress_percent": 0,
        "stdout": "",
        "stderr": "",
        "duration": 0.0,
        "failure_message": None
    }
    
    display_test_id = first_test if total_count == 1 else f"BATCH_OF_{total_count}_TESTS"
    state = orchestrator.state_machine.initialize(task_id, display_test_id, environment)
    state.execution_id = execution_id
    
    state = orchestrator.state_machine.transition(state, "VALIDATING")
    executions[execution_id]["status"] = "VALIDATING"
    executions[execution_id]["progress_percent"] = 5
    
    if engine == "MCP_AGENT":
        from agent.mcp.playwright_mcp_adapter import PlaywrightMcpAdapter
        mcp_adapter = PlaywrightMcpAdapter()
        test_infos = []
        for tid in test_ids:
            t_info = registry.get_test(tid)
            if t_info:
                test_infos.append({"testId": tid, "name": t_info.get("name", tid), "path": t_info.get("path", "")})
        
        executions[execution_id]["status"] = "EXECUTING"
        mcp_res = mcp_adapter.run_agentic_regression(
            test_infos=test_infos,
            environment=environment,
            headless=headless,
            execution_id=execution_id,
            executions_store=executions
        )
        return

    while not state.is_terminal():
        rule = orchestrator.rule_engine.decide(state)
        if not rule:
            state.status = "FAILED"
            state.failure_message = "No rule matched current state"
            break
            
        state = rule.execute(state)
        
        if state.status == "EXECUTING":
            executions[execution_id]["status"] = "EXECUTING"
            
            test_infos = [registry.get_test(tid) for tid in test_ids]
            result = executor.execute_batch(test_infos, state.environment, execution_id=execution_id, executions_store=executions)
            state.exit_code = result["exit_code"]
            state.stdout = result["stdout"]
            state.stderr = result["stderr"]
            state.duration = result["duration"]
            state = orchestrator.state_machine.transition(state, "OBSERVING")
            
        executions[execution_id].update({
            "status": state.status,
            "duration": state.duration,
            "stdout": state.stdout,
            "stderr": state.stderr,
            "failure_message": state.failure_message,
            "completed_tests": total_count,
            "progress_percent": 100
        })



@router.get("/tests", response_model=AgentTestListResponse)
async def get_all_tests():
    tests = registry.get_all_tests()
    test_list = []
    for t_id, t_info in tests.items():
        test_list.append(AgentTestInfo(
            testId=t_id,
            name=t_info.get("name", t_id),
            path=t_info.get("path", ""),
            enabled=t_info.get("enabled", True)
        ))
    return AgentTestListResponse(tests=test_list)

@router.post("/tasks", response_model=AgentTaskResponse)
async def create_task(request: AgentTaskRequest, background_tasks: BackgroundTasks):
    if request.action != "run_test":
        raise HTTPException(status_code=400, detail="Unsupported action")
        
    if request.testIds:
        tests_to_run = request.testIds
        for t_id in tests_to_run:
            if not registry.test_exists(t_id):
                raise HTTPException(status_code=404, detail=f"Test ID {t_id} not found or not enabled")
    elif request.testId:
        if not registry.test_exists(request.testId):
            raise HTTPException(status_code=404, detail="Test ID not found or not enabled")
        tests_to_run = [request.testId]
    else:
        raise HTTPException(status_code=400, detail="No test IDs provided")
        
    task_id = f"TASK-{uuid.uuid4().hex[:8]}"
    execution_id = f"EXEC-{uuid.uuid4().hex[:8]}"
    
    executions[execution_id] = {
        "status": "QUEUED",
        "total_tests": len(tests_to_run),
        "completed_tests": 0,
        "current_test": tests_to_run[0],
        "current_test_index": 1,
        "progress_percent": 0,
        "stdout": "",
        "stderr": "",
        "duration": 0.0,
        "failure_message": None
    }
    
    background_tasks.add_task(
        run_task_background,
        task_id,
        execution_id,
        tests_to_run,
        request.environment,
        request.engine or "PYTEST",
        request.headless if request.headless is not None else False
    )
    
    return AgentTaskResponse(
        taskId=task_id,
        executionId=execution_id,
        status="QUEUED"
    )

