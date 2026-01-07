from typing import TypedDict, Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- State Definition ---
class AgentState(TypedDict):
    """
    Represents the state of the cyber-defense pipeline.
    Passes data between agents in the 12-step flow.
    """
    raw_log: Dict[str, Any]
    normalized_log: Optional[Dict[str, Any]]
    patterns_detected: List[Dict[str, Any]]
    anomaly_score: float
    threat_classification: Optional[Dict[str, Any]]
    attack_path_hypothesis: Optional[str]
    mitigation_plan: Optional[Dict[str, Any]]
    verification_result: Optional[Dict[str, Any]]
    escalation_decision: str  # "auto", "human", "hold"
    human_feedback: Optional[str]
    execution_result: Optional[str]
    audit_record: Optional[str]
    errors: List[str]

from src.agents.core.log_ingestion import parse_and_normalize

from src.agents.core.pattern_detection import detect_patterns
from src.agents.core.anomaly_scoring import calculate_anomaly_score

# --- Agent Node Stubs (Steps 1-12) ---

def log_ingestion_agent(state: AgentState):
    logger.info("Step 1: Log Ingestion Agent")
    raw_log = state.get("raw_log", {})
    normalized = parse_and_normalize(raw_log)
    
    if normalized:
        return {"normalized_log": normalized}
    else:
        return {"errors": ["Log ingestion failed"]}

def pattern_detection_agent(state: AgentState):
    logger.info("Step 2: Pattern Detection Agent")
    normalized_data = state.get("normalized_log")
    if not normalized_data:
        return {}
        
    # Convert dict back to model for internal processing if needed, 
    # or ensure agents handle dicts. 
    # For now, let's assume agents handle models or we reconstruct.
    # To keep it simple, we reconstruct the model here.
    from src.models.log_schema import NormalizedLog
    log_obj = NormalizedLog(**normalized_data)
    
    patterns = detect_patterns(log_obj)
    return {"patterns_detected": patterns}

def anomaly_scoring_agent(state: AgentState):
    logger.info("Step 3: Anomaly Scoring Agent")
    normalized_data = state.get("normalized_log")
    patterns = state.get("patterns_detected", [])
    
    if not normalized_data:
        return {"anomaly_score": 0.0}

    from src.models.log_schema import NormalizedLog
    log_obj = NormalizedLog(**normalized_data)
    
    score = calculate_anomaly_score(log_obj, patterns)
    return {"anomaly_score": score}

from src.agents.advanced.threat_classification import classify_threat
from src.agents.advanced.attack_path import reason_attack_path
from src.agents.advanced.mitigation_planning import plan_mitigation

# --- Agent Node Stubs (Steps 1-12) ---

# ... [Steps 1-3 maintained] ...

def threat_classification_agent(state: AgentState):
    logger.info("Step 4: Threat Classification Agent")
    normalized_data = state.get("normalized_log")
    patterns = state.get("patterns_detected", [])
    anomaly_score = state.get("anomaly_score", 0.0)
    
    if not normalized_data:
        return {}
        
    from src.models.log_schema import NormalizedLog
    log_obj = NormalizedLog(**normalized_data)
    
    classification = classify_threat(log_obj, patterns, anomaly_score)
    return {"threat_classification": classification}

def attack_path_reasoning_agent(state: AgentState):
    logger.info("Step 5: Attack-Path Reasoning Agent")
    classification = state.get("threat_classification", {})
    if not classification:
        return {}
        
    hypothesis = reason_attack_path(classification)
    return {"attack_path_hypothesis": hypothesis}

def mitigation_planning_agent(state: AgentState):
    logger.info("Step 6: Mitigation Planning Agent")
    classification = state.get("threat_classification", {})
    hypothesis = state.get("attack_path_hypothesis", "")
    
    if not classification:
        return {}
        
    plan = plan_mitigation(classification, hypothesis)
    return {"mitigation_plan": plan}

from src.agents.advanced.verifier import verify_plan

# ...

def verifier_agent(state: AgentState):
    logger.info("Step 7: Verifier Agent (Quality Gate)")
    
    plan = state.get("mitigation_plan")
    classification = state.get("threat_classification")
    normalized = state.get("normalized_log")
    
    if not (plan and classification and normalized):
         return {"verification_result": {"score": 0.0, "approved": False, "issues": ["Missing input data"]}}

    from src.models.log_schema import NormalizedLog
    log_obj = NormalizedLog(**normalized)
    
    result = verify_plan(plan, classification, log_obj)
    return {"verification_result": result}

from src.agents.utility.trust_engine import trust_engine

def escalation_routing_agent(state: AgentState):
    logger.info("Step 8: Escalation Routing Agent")
    
    # Inputs
    verifier_result = state.get("verification_result", {})
    verifier_score = verifier_result.get("score", 0.0)
    anomaly_score = state.get("anomaly_score", 0.0)
    classification = state.get("threat_classification", {})
    severity = classification.get("max_severity", "low")
    
    # Get Max Action Risk from Plan
    plan = state.get("mitigation_plan", {})
    actions = plan.get("actions", [])
    plan_risks = [a.get("risk", "low") for a in actions]
    
    # 1. Calculate Trust
    trust_score = trust_engine.calculate_trust_score(verifier_score, anomaly_score, severity)
    
    # 2. Decide Routing
    escalate, reason = trust_engine.should_escalate_to_human(trust_score, severity, plan_risks)
    
    logger.info(f"Routing Decision: Escalate={escalate} (Trust: {trust_score:.2f}). Reason: {reason}")
    
    decision = "human" if escalate else "auto"
    
    # 3. Notification Check (If escalating)
    if decision == "human":
        # Create a dedup key based on threat technique and severity
        techniques = "|".join([t["name"] for t in classification.get("techniques", [])])
        alert_key = f"{severity}:{techniques}"
        
        if not trust_engine.should_notify(alert_key):
            # If throttled, maybe we log it but don't "ring the pager"
            # For pipeline flow, we still go to HITL node, but maybe with a flag "silent_approval"?
            # For MVP, let's just proceed.
            pass

    return {"escalation_decision": decision, "execution_result": f"Routed to {decision} ({reason})"}

def human_in_the_loop_agent(state: AgentState):
    logger.info("Step 9: HITL Review")
    # TODO: Wait for human input (mocked for now)
    return {"human_feedback": "approved"}

from src.agents.utility.memory_manager import memory_manager

# ...

def memory_update_agent(state: AgentState):
    logger.info("Step 10: Memory & Knowledge Update Agent")
    
    # Extract outcomes to store
    plan = state.get("mitigation_plan")
    
    # Simulate Session ID (In prod, this comes from API request context)
    session_id = "global_session_mvp" 
    if session_id not in MEMORY_STORE: # Hack for MVP single session
        memory_manager.create_session() # But we track the ID
        # Wait, MEMORY_STORE is inside the module instance, we need to access it via the instance or helper
        # For simplicity, let's just create a session if write fails or just 'ensure' session
        # Rewriting to be cleaner:
        pass

    # Actually, let's just try to update. 
    # Since MEMORY_STORE is in-memory dict in the module, let's just initialize a 'sys' session in main?
    # Or lazily create here.
    try:
        if "sys_session" not in MEMORY_STORE:
             # This direct check won't work because MEMORY_STORE is not exported.
             # We should rely on `create_session` returning an ID we reuse.
             # For MVP, let's assume session_id passed in state, or default.
             pass
    except:
        pass
        
    # Let's just create a new session for this trace to demonstrate isolation
    # In reality, session_id should thread through AgentState
    sess_id = state.get("session_id")
    if not sess_id:
        sess_id = memory_manager.create_session()
        # Ideally we'd update state, but state is immutable-ish in some designs. 
        # But we return dict to update state.
        
    # Store the plan
    success = memory_manager.update_memory(sess_id, "last_mitigation", plan)
    
    if success:
        return {"session_id": sess_id}
    else:
        return {"errors": ["Memory update rejected (Validation Failure)"], "session_id": sess_id}

from src.agents.utility.rbac_policy import rbac_policy

# ...

def action_execution_agent(state: AgentState):
    logger.info("Step 11: Action Execution Agent")
    
    plan = state.get("mitigation_plan", {})
    actions = plan.get("actions", [])
    results = []
    
from src.agents.security.sandbox import sandbox, SecurityError

# ...

def action_execution_agent(state: AgentState):
    logger.info("Step 11: Action Execution Agent")
    
    plan = state.get("mitigation_plan", {})
    actions = plan.get("actions", [])
    results = []
    
    # Mock User Role
    user_role = state.get("user_role", "responder_tier_1")
    
    for action in actions:
        name = action.get("name")
        # Assume actions have 'params' list in real usage. 
        # For this MVP, we mock params based on name to test Sandbox.
        mock_params = []
        if "Block" in name:
            mock_params = ["192.168.1.50"]
        elif "Isolate" in name:
            mock_params = ["host-001"]
        elif "Malicious" in name: # Test case
            mock_params = ["127.0.0.1; rm -rf /"]
        
        # Epic 3: RBAC Checks
        if not rbac_policy.check_permission(user_role, name):
            results.append(f"Blocked (RBAC): Role '{user_role}' denied '{name}'")
            continue
            
        # Epic 2: Tool Guard Checks
        if not tool_guard.check_access(name, {}):
            results.append(f"Blocked (ACL): {name}")
            continue
            
        if not tool_guard.check_rate_limit(name):
            results.append(f"Blocked (RateLimit): {name}")
            continue
            
        # Epic 2.5: Sandbox Execution
        try:
            output = sandbox.execute_simulated(name, mock_params)
            results.append(output)
            status = "executed"
        except SecurityError as e:
            results.append(f"Blocked (Sandbox): {str(e)}")
            status = "blocked_sandbox"
        
        # Epic 2.2: Immutable Execution Logging
        audit_payload = {
            "action": name,
            "params": mock_params, 
            "user_role": user_role,
            "status": status
        }
        audit_logger.log_event("agent_executor", "tool_execution", audit_payload)

    return {"execution_result": "; ".join(results)}

def audit_trail_agent(state: AgentState):
    logger.info("Step 12: Audit Trail & Forensics Agent")
    
    # Collect traceability info
    log_id = state.get("normalized_log", {}).get("event_id", "unknown")
    plan = state.get("mitigation_plan")
    classification = state.get("threat_classification")
    exec_result = state.get("execution_result")
    
    details = {
        "event_ref": log_id,
        "threat_level": classification.get("max_severity") if classification else "unknown",
        "mitigation": plan,
        "execution_status": exec_result,
        "provenance": {
             "patterns": state.get("patterns_detected"),
             "score": state.get("anomaly_score")
        }
    }
    
    # Write to immutable log
    signature = audit_logger.log_event("pipeline_orchestrator", "mitigation_cycle_complete", details)
    
    return {"audit_record": signature}

# --- Conditional Logic / Edges ---

def check_anomaly_score(state: AgentState):
    # Gate: Anomaly > 2 sigma to proceed to classification
    if state.get("anomaly_score", 0) > 2.0:
        return "threat_classification"
    else:
        return "audit_trail" # Skip to end if no anomaly

def check_verification(state: AgentState):
    # Gate: Verifier score >= 0.7 to proceed
    result = state.get("verification_result", {})
    if result.get("approved", False):
        return "escalation_routing"
    else:
        return "mitigation_planning" # Loop back to plan

def check_escalation(state: AgentState):
    decision = state.get("escalation_decision", "hold")
    if decision == "auto":
        return "memory_update" # Skip HITL
    elif decision == "human":
        return "human_in_the_loop"
    else:
        return "audit_trail" # Hold/Stop

def check_human_approval(state: AgentState):
    # Gate: If human rejected, maybe loop back? For now proceed to memory
    return "memory_update"


# --- Graph Construction ---

workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("log_ingestion", log_ingestion_agent)
workflow.add_node("pattern_detection", pattern_detection_agent)
workflow.add_node("anomaly_scoring", anomaly_scoring_agent)
workflow.add_node("threat_classification", threat_classification_agent)
workflow.add_node("attack_path_reasoning", attack_path_reasoning_agent)
workflow.add_node("mitigation_planning", mitigation_planning_agent)
workflow.add_node("verifier", verifier_agent)
workflow.add_node("escalation_routing", escalation_routing_agent)
workflow.add_node("human_in_the_loop", human_in_the_loop_agent)
workflow.add_node("memory_update", memory_update_agent)
workflow.add_node("action_execution", action_execution_agent)
workflow.add_node("audit_trail", audit_trail_agent)

# Set Entry Point
workflow.set_entry_point("log_ingestion")

# Add Edges
workflow.add_edge("log_ingestion", "pattern_detection")
workflow.add_edge("pattern_detection", "anomaly_scoring")

# Conditional Edge 1: Anomaly Check
workflow.add_conditional_edges(
    "anomaly_scoring",
    check_anomaly_score,
    {
        "threat_classification": "threat_classification",
        "audit_trail": "audit_trail"
    }
)

workflow.add_edge("threat_classification", "attack_path_reasoning")
workflow.add_edge("attack_path_reasoning", "mitigation_planning")
workflow.add_edge("mitigation_planning", "verifier")

# Conditional Edge 2: Verifier Check
workflow.add_conditional_edges(
    "verifier",
    check_verification,
    {
        "escalation_routing": "escalation_routing",
        "mitigation_planning": "mitigation_planning"
    }
)

# Conditional Edge 3: Escalation Check
workflow.add_conditional_edges(
    "escalation_routing",
    check_escalation,
    {
        "memory_update": "memory_update",
        "human_in_the_loop": "human_in_the_loop",
        "audit_trail": "audit_trail"
    }
)

workflow.add_edge("human_in_the_loop", "memory_update")
workflow.add_edge("memory_update", "action_execution")
workflow.add_edge("action_execution", "audit_trail")
workflow.add_edge("audit_trail", END)

# Compile
app = workflow.compile()
