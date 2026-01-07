import logging
from typing import Dict, Any, List, Tuple
from src.models.log_schema import NormalizedLog

logger = logging.getLogger("agent.verifier")

def verify_plan(plan: Dict[str, Any], classification: Dict[str, Any], log: NormalizedLog) -> Dict[str, Any]:
    """
    Step 7: Verifier Agent (Quality Gate).
    Checks for:
    1. Groundedness: Are actions supported by the threat class?
    2. Proportionality: Is the response too severe for the threat level?
    3. Hallucination: Are we acting on entities (IPs/Users) actually present in the log?
    """
    logger.info("Running verification checks...")
    
    score = 1.0
    issues = []
    
    # 1. Proportionality Check
    # Avoid blocking IP for Low severity
    severity = classification.get("max_severity", "low")
    actions = plan.get("actions", [])
    
    for action in actions:
        if action["risk"] == "high" and severity == "low":
            issues.append(f"Disproportionate response: High risk action '{action['name']}' for Low severity threat.")
            score -= 0.4

    # 2. Hallucination Check (Entity Validation)
    # Ensure the IP in the plan matches the log source
    # (Simplified for MVP: Check if 'Block Source IP' is in plan, does log have IP?)
    for action in actions:
        if "Block Source IP" in action["name"]:
            if not log.source_ip or log.source_ip == "0.0.0.0":
                 issues.append("Hallucination Risk: Blocking Source IP but no valid IP found in log.")
                 score -= 0.5

    # 3. Groundedness Check (Reasoning Alignment)
    # Does the plan reasoning mention the techniques found?
    techniques = [t["name"] for t in classification.get("techniques", [])]
    reasoning = plan.get("reasoning", "")
    
    match_count = sum(1 for t in techniques if t in reasoning)
    if techniques and match_count == 0:
        issues.append("Reasoning gap: Plan justification does not mention any classified techniques.")
        score -= 0.2

    approved = score >= 0.7
    
    logger.info(f"Verification Complete. Score: {score:.2f}. Approved: {approved}")
    return {
        "score": score,
        "approved": approved,
        "issues": issues
    }
