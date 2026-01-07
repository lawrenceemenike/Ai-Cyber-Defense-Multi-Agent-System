import logging
from typing import Dict, Any, List
from src.models.log_schema import NormalizedLog

logger = logging.getLogger("agent.threat_classification")

# Mock MITRE Knowledgebase
MITRE_DB = {
    "SIG-001": {"technique": "T1110", "name": "Brute Force", "tactic": "Credential Access", "level": "medium"},
    "SIG-002": {"technique": "T1068", "name": "Exploitation for Privilege Escalation", "tactic": "Privilege Escalation", "level": "high"},
    "SIG-003": {"technique": "T1048", "name": "Exfiltration Over Alternative Protocol", "tactic": "Exfiltration", "level": "critical"}
}

def classify_threat(log: NormalizedLog, patterns: List[Dict[str, Any]], anomaly_score: float) -> Dict[str, Any]:
    """
    Step 4: Maps detected patterns to MITRE ATT&CK and determines threat severity.
    """
    logger.info(f"Classifying threat for {log.event_id} (Score: {anomaly_score:.2f})")
    
    classification = {
        "techniques": [],
        "tactics": set(),
        "max_severity": "low",
        "score": anomaly_score
    }
    
    # Map patterns to MITRE
    for p in patterns:
        sig_id = p.get("signature_id")
        if sig_id in MITRE_DB:
            mitre_info = MITRE_DB[sig_id]
            classification["techniques"].append(mitre_info)
            classification["tactics"].add(mitre_info["tactic"])
            
            # Update max severity
            current_level = classification["max_severity"]
            new_level = mitre_info["level"]
            if _level_to_int(new_level) > _level_to_int(current_level):
                classification["max_severity"] = new_level

    # If no patterns but high anomaly score, treat as "Unknown Anomaly"
    if not classification["techniques"] and anomaly_score > 2.0:
        classification["max_severity"] = "medium"
        classification["techniques"].append({"name": "Unusual Behavioral Anomaly", "technique": "T1XXX"})

    classification["tactics"] = list(classification["tactics"]) # Serialize set
    
    logger.info(f"Classification Result: {classification['max_severity']} - {classification['techniques']}")
    return classification

def _level_to_int(level: str) -> int:
    levels = {"low": 1, "medium": 2, "high": 3, "critical": 4}
    return levels.get(level.lower(), 0)
