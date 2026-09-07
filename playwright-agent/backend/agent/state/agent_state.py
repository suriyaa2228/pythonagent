from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


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
    artifacts: List[str] = field(default_factory=list)
    
    # Store execution result properties
    exit_code: int = -1
    duration: float = 0.0
    stdout: str = ""
    stderr: str = ""

    def is_terminal(self) -> bool:
        return self.status in ["COMPLETED", "STOPPED"]
