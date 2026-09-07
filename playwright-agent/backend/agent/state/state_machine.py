from agent.state.agent_state import AgentState

class StateMachine:
    
    VALID_TRANSITIONS = {
        "RECEIVED": ["VALIDATING", "FAILED"],
        "VALIDATING": ["VALIDATED", "FAILED"],
        "VALIDATED": ["TEST_RESOLVED", "FAILED"],
        "TEST_RESOLVED": ["ENVIRONMENT_VALIDATED", "FAILED"],
        "ENVIRONMENT_VALIDATED": ["EXECUTING", "FAILED"],
        "EXECUTING": ["OBSERVING", "FAILED"],
        "OBSERVING": ["PASSED", "FAILED"],
        "PASSED": ["REPORTING"],
        "FAILED": ["RETRY", "STOP"],
        "RETRY": ["EXECUTING", "FAILED"],
        "STOP": ["REPORTING"],
        "REPORTING": ["COMPLETED"],
        "COMPLETED": [],
        "STOPPED": []
    }

    def initialize(self, task_id: str, test_id: str, environment: str) -> AgentState:
        return AgentState(
            task_id=task_id,
            test_id=test_id,
            environment=environment,
            status="RECEIVED"
        )

    def transition(self, state: AgentState, next_status: str) -> AgentState:
        if next_status not in self.VALID_TRANSITIONS.get(state.status, []):
            raise ValueError(f"Invalid state transition from {state.status} to {next_status}")
            
        state.status = next_status
        return state
