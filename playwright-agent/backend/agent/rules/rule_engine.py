from abc import ABC, abstractmethod
from typing import List, Optional
from agent.state.agent_state import AgentState

class Rule(ABC):
    name: str

    @abstractmethod
    def matches(self, state: AgentState) -> bool:
        pass

    @abstractmethod
    def execute(self, state: AgentState) -> AgentState:
        pass

class RuleEngine:
    def __init__(self):
        self.rules: List[Rule] = []

    def register_rule(self, rule: Rule):
        self.rules.append(rule)

    def decide(self, state: AgentState) -> Optional[Rule]:
        # Return the first matching rule, or None if no rules match
        for rule in self.rules:
            if rule.matches(state):
                return rule
        return None

# --- Concrete Rules ---

class ValidateTestRule(Rule):
    name = "validate_test"
    
    def __init__(self, registry):
        self.registry = registry
        
    def matches(self, state: AgentState) -> bool:
        return state.status == "VALIDATING"

    def execute(self, state: AgentState) -> AgentState:
        if state.test_id.startswith("BATCH_OF_") or self.registry.test_exists(state.test_id):
            state.status = "VALIDATED"
        else:
            state.failure_message = f"Test {state.test_id} not found or disabled."
            state.status = "FAILED"
        return state

class ExecuteTestRule(Rule):
    name = "execute_test"
    
    def matches(self, state: AgentState) -> bool:
        # Simplification: Skip resolving/env validation for MVP and go straight to EXECUTING
        return state.status in ["VALIDATED", "RETRY"]

    def execute(self, state: AgentState) -> AgentState:
        state.status = "EXECUTING"
        return state

class ObserveResultRule(Rule):
    name = "observe_result"
    
    def matches(self, state: AgentState) -> bool:
        return state.status == "OBSERVING"

    def execute(self, state: AgentState) -> AgentState:
        if state.exit_code == 0:
            state.status = "PASSED"
        else:
            state.status = "FAILED"
            state.failure_type = "EXECUTION_ERROR"
            state.failure_message = state.stderr
        return state

class RetryRule(Rule):
    name = "retry_test"
    
    def matches(self, state: AgentState) -> bool:
        return state.status == "FAILED" and state.retry_count < state.max_retries

    def execute(self, state: AgentState) -> AgentState:
        state.retry_count += 1
        state.status = "RETRY"
        return state

class StopRule(Rule):
    name = "stop_test"
    
    def matches(self, state: AgentState) -> bool:
        return state.status == "FAILED" and state.retry_count >= state.max_retries

    def execute(self, state: AgentState) -> AgentState:
        state.status = "STOP"
        return state

class ReportingRule(Rule):
    name = "report_result"
    
    def matches(self, state: AgentState) -> bool:
        return state.status in ["PASSED", "STOP"]

    def execute(self, state: AgentState) -> AgentState:
        state.status = "REPORTING"
        return state

class CompleteRule(Rule):
    name = "complete_execution"
    
    def matches(self, state: AgentState) -> bool:
        return state.status == "REPORTING"

    def execute(self, state: AgentState) -> AgentState:
        state.status = "COMPLETED"
        return state
