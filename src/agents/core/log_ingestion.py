import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json
from src.models.log_schema import NormalizedLog

logger = logging.getLogger("agent.log_ingestion")

def parse_and_normalize(raw_log: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Step 1: Parses raw log data and normalizes it into a standard schema.
    Also performs basic validation and PII redaction (stubbed).
    """
    logger.info("Ingesting raw log...")
    
    try:
        # 1. Basic Validation
        required_fields = ["source", "event_type", "timestamp"]
        for field in required_fields:
            if field not in raw_log:
                raise ValueError(f"Missing required field: {field}")

        # 2. Normalization Logic (Stubbed for MVP)
        # In a real system, this would handle syslog parsing, various JSON formats, etc.
        
        # Parse timestamp to ensure ISO format
        # Assuming input is already ISO string for MVP, or we would parse it here.
        ts = raw_log.get("timestamp")
        
        # 3. PII Redaction (Simple Stub)
        # TODO: Implement regex-based PII redaction
        
        # 4. Construct Normalized Object
        normalized = NormalizedLog(
            event_id=f"evt_{hash(json.dumps(raw_log))}", # Simple hash ID
            timestamp=ts,
            source=raw_log["source"],
            event_type=raw_log["event_type"],
            severity=raw_log.get("severity", "unknown"),
            user=raw_log.get("user", "unknown"),
            source_ip=raw_log.get("source_ip", "0.0.0.0"),
            action=raw_log.get("action", "unknown"),
            raw_payload=json.dumps(raw_log.get("raw_payload", {}))
        )
        
        logger.info(f"Log normalized: {normalized.event_id}")
        return normalized.model_dump()

    except Exception as e:
        logger.error(f"Log ingestion failed: {str(e)}")
        return None # Returning None indicates failure to ingest
