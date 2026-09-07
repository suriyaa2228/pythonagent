from fastapi import APIRouter, HTTPException
from api.routes.agent_routes import executions # Import the in-memory store for MVP

router = APIRouter()

@router.get("/{execution_id}")
async def get_execution(execution_id: str):
    if execution_id not in executions:
        raise HTTPException(status_code=404, detail="Execution not found")
        
    return executions[execution_id]

@router.get("/{execution_id}/logs")
async def get_execution_logs(execution_id: str):
    if execution_id not in executions:
        raise HTTPException(status_code=404, detail="Execution not found")
        
    exec_data = executions[execution_id]
    return {
        "stdout": exec_data.get("stdout", ""),
        "stderr": exec_data.get("stderr", "")
    }
