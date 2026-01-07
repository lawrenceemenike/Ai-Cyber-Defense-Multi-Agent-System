import logging
from typing import Dict, Any

logger = logging.getLogger("agent.attack_path")

def reason_attack_path(classification: Dict[str, Any]) -> str:
    """
    Step 5: Generates a hypothesis about the attack chain (Step A -> Step B).
    For MVP, uses simple template-based generation.
    """
    logger.info("Generating attack path hypothesis...")
    
    tactics = classification.get("tactics", [])
    techniques = [t["name"] for t in classification.get("techniques", [])]
    
    if not techniques:
        return "No specific attack path identified (Anomaly only)."
        
    hypothesis = f"Attacker is using {', '.join(techniques)} to achieve {', '.join(tactics)}."
    
    if "Privilege Escalation" in tactics and "Credential Access" in tactics:
         hypothesis += " Likely attempting to gain root access after compromising credentials."
         
    if "Exfiltration" in tactics:
        hypothesis += " CRITICAL: Active data theft detected."
        
    logger.info(f"Hypothesis: {hypothesis}")
    return hypothesis
