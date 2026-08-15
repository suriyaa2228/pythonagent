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



def run_task_background(task_id: str, execution_id: str, test_ids: list[str], environment: str):
    executions[execution_id] = {"status": "QUEUED"}
    
    display_test_id = test_ids[0] if len(test_ids) == 1 else f"BATCH_OF_{len(test_ids)}_TESTS"
    state = orchestrator.state_machine.initialize(task_id, display_test_id, environment)
    state.execution_id = execution_id
    
    state = orchestrator.state_machine.transition(state, "VALIDATING")
    executions[execution_id] = {"status": "VALIDATING"}
    
    while not state.is_terminal():
        rule = orchestrator.rule_engine.decide(state)
        if not rule:
            state.status = "FAILED"
            state.failure_message = "No rule matched current state"
            break
            
        state = rule.execute(state)
        
        if state.status == "EXECUTING":
            executions[execution_id] = {"status": "EXECUTING"}
            
            test_infos = [registry.get_test(tid) for tid in test_ids]
            if len(test_infos) == 1:
                result = executor.execute(test_infos[0], state.environment)
            else:
                result = executor.execute_batch(test_infos, state.environment)
            state.exit_code = result["exit_code"]
            state.stdout = result["stdout"]
            state.stderr = result["stderr"]
            state.duration = result["duration"]
            state = orchestrator.state_machine.transition(state, "OBSERVING")
            
        executions[execution_id] = {
            "status": state.status,
            "duration": state.duration,
            "stdout": state.stdout,
            "stderr": state.stderr,
            "failure_message": state.failure_message
        }
    


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
    
    executions[execution_id] = {"status": "QUEUED"}
    
    background_tasks.add_task(run_task_background, task_id, execution_id, tests_to_run, request.environment)
    
    return AgentTaskResponse(
        taskId=task_id,
        executionId=execution_id,
        status="QUEUED"
    )
