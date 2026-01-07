import logging
from typing import Dict, Any, List

logger = logging.getLogger("agent.mitigation_planning")

# Approved Action Library
ACTION_LIBRARY = {
    "block_ip": {"id": "ACT-001", "name": "Block Source IP", "risk": "low"},
    "disable_user": {"id": "ACT-002", "name": "Disable User Account", "risk": "medium"},
    "isolate_host": {"id": "ACT-003", "name": "Isolate Host Network", "risk": "high"},
    "kill_process": {"id": "ACT-004", "name": "Kill Suspicious Process", "risk": "medium"}
}

def plan_mitigation(classification: Dict[str, Any], hypothesis: str) -> Dict[str, Any]:
    """
    Step 6: Selects mitigation actions based on threat severity and type.
    """
    logger.info("Planning mitigation strategy...")
    
    severity = classification.get("max_severity", "low")
    techniques = [t["name"] for t in classification.get("techniques", [])]
    
    plan = {
        "actions": [],
        "reasoning": hypothesis,
        "requires_approval": False
    }
    
    # Mitigation Logic (Rule-based for MVP)
    if "Brute Force" in techniques:
        plan["actions"].append(ACTION_LIBRARY["block_ip"])
        plan["actions"].append(ACTION_LIBRARY["disable_user"])
        
    if "Data Exfiltration" in techniques:
        plan["actions"].append(ACTION_LIBRARY["isolate_host"])
        plan["actions"].append(ACTION_LIBRARY["block_ip"])
        plan["requires_approval"] = True # High impact
        
    if severity == "critical":
        plan["requires_approval"] = True
        
    # Default fallback
    if not plan["actions"]:
        plan["actions"].append({"id": "ACT-000", "name": "Log and Monitor Only", "risk": "low"})
        
    logger.info(f"Plan generated with {len(plan['actions'])} actions. Approval req: {plan['requires_approval']}")
    return plan
