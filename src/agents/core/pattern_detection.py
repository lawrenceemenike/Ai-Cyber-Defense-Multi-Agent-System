import logging
from typing import List, Dict, Any
from src.models.log_schema import NormalizedLog

logger = logging.getLogger("agent.pattern_detection")

# Mock Pattern Database (MVP)
SIGNATURES = [
    {
        "id": "SIG-001",
        "name": "Brute Force Attempt", 
        "pattern": lambda log: log.event_type == "login_failure",
        "severity": "medium"
    },
    {
        "id": "SIG-002",
        "name": "Root Privilege Escalation",
        "pattern": lambda log: log.action == "sudo" or "root" in (log.user or ""),
        "severity": "high"
    },
    {
        "id": "SIG-003",
        "name": "Data Exfiltration",
        "pattern": lambda log: log.event_type == "data_transfer" and "external" in (log.source_ip or ""),
        "severity": "critical"
    }
]

def detect_patterns(log: NormalizedLog) -> List[Dict[str, Any]]:
    """
    Step 2: Scans the normalized log against a database of attack signatures.
    """
    detected = []
    logger.info(f"Scanning log {log.event_id} for patterns...")

    try:
        for sig in SIGNATURES:
            if sig["pattern"](log):
                logger.warning(f"Pattern MATCH: {sig['name']} ({sig['id']})")
                detected.append({
                    "signature_id": sig["id"],
                    "name": sig["name"],
                    "severity": sig["severity"],
                    "timestamp": log.timestamp
                })
        
        return detected

    except Exception as e:
        logger.error(f"Pattern detection failed: {str(e)}")
        return []
