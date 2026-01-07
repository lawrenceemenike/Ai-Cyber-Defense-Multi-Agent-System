import logging
from typing import Dict, Any, Tuple
from src.models.log_schema import NormalizedLog
import random # For MVP simulation

logger = logging.getLogger("agent.anomaly_scoring")

def calculate_anomaly_score(log: NormalizedLog, patterns: list) -> float:
    """
    Step 3: Calculates a Z-score or probability of anomaly.
    For MVP, uses heuristics based on patterns and mock statistical deviations.
    """
    logger.info(f"Calculating anomaly score for {log.event_id}...")
    
    base_score = 0.0
    
    try:
        # Heuristic 1: Pattern Severity
        for p in patterns:
            if p["severity"] == "critical":
                base_score += 3.0 # Immediate high score
            elif p["severity"] == "high":
                base_score += 2.0
            elif p["severity"] == "medium":
                base_score += 1.0

        # Heuristic 2: Behavioral Mock (Simulation of "Unusual IP")
        # In real system, this queries Redis/Chroma for user baseline.
        if log.source_ip and log.source_ip.startswith("192.168.100"): 
            # Assume 192.168.100.x is a sensitive subnet
            logger.info("Access to sensitive subnet detected")
            base_score += 1.5
            
        # Add some statistical noise (to simulate Z-score variance)
        deviation = random.uniform(0, 0.5)
        
        total_score = base_score + deviation
        logger.info(f"Anomaly Score: {total_score:.2f} (Base: {base_score}, Dev: {deviation:.2f})")
        
        return total_score

    except Exception as e:
        logger.error(f"Anomaly scoring failed: {str(e)}")
        return 0.0
