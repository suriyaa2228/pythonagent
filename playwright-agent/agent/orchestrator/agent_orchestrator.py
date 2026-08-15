from agent.state.agent_state import AgentState
from agent.state.state_machine import StateMachine
from agent.rules.rule_engine import (
    RuleEngine, ValidateTestRule, ExecuteTestRule, ObserveResultRule,
    RetryRule, StopRule, ReportingRule, CompleteRule
)
from agent.executor.playwright_executor import PlaywrightExecutor
from agent.registry.test_registry import TestRegistry

class AgentOrchestrator:
    def __init__(self, registry: TestRegistry, executor: PlaywrightExecutor):
        self.registry = registry
        self.executor = executor
        self.state_machine = StateMachine()
        self.rule_engine = RuleEngine()
        
        # Register rules
        self.rule_engine.register_rule(ValidateTestRule(self.registry))
        self.rule_engine.register_rule(ExecuteTestRule())
        self.rule_engine.register_rule(ObserveResultRule())
        self.rule_engine.register_rule(RetryRule())
        self.rule_engine.register_rule(StopRule())
        self.rule_engine.register_rule(ReportingRule())
        self.rule_engine.register_rule(CompleteRule())

    def execute(self, task_id: str, test_id: str, environment: str, executions_store: dict = None) -> AgentState:
        state = self.state_machine.initialize(task_id, test_id, environment)
        state = self.state_machine.transition(state, "VALIDATING")
        
        if executions_store is not None and state.execution_id:
            executions_store[state.execution_id] = state

        while not state.is_terminal():
            rule = self.rule_engine.decide(state)
            
            if not rule:
                # Fallback if no rule matches
                state.status = "FAILED"
                state.failure_message = "No rule matched current state"
                break
                
            # Execute the rule to modify state status/properties
            state = rule.execute(state)
            
            # Action: if the rule moved us to EXECUTING, we need to actually run the script
            if state.status == "EXECUTING":
                if executions_store is not None and state.execution_id:
                    executions_store[state.execution_id] = {"status": "EXECUTING"}
                    
                test_info = self.registry.get_test(state.test_id)
                result = self.executor.execute(test_info["path"], state.environment)
                
                state.exit_code = result["exit_code"]
                state.stdout = result["stdout"]
                state.stderr = result["stderr"]
                state.duration = result["duration"]
                
                # After executing, we always go to OBSERVING
                state = self.state_machine.transition(state, "OBSERVING")

            if executions_store is not None and state.execution_id:
                # Update the store
                executions_store[state.execution_id] = {
                    "status": state.status,
                    "duration": state.duration,
                    "stdout": state.stdout,
                    "stderr": state.stderr,
                    "failure_message": state.failure_message
                }

        return state
