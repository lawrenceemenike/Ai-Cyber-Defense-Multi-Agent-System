import logging
import re
import math
import uuid
import json
from typing import Dict, Any, Optional

# Stub for Redis for MVP (Use a dict)
# In real prod, this imports redis
MEMORY_STORE = {} 

logger = logging.getLogger("agent.memory_manager")

class MemoryManager:
    """
    Handles secure memory operations:
    - Session Isolation (Redis w/ TTL)
    - Content Validation (Regex/Entropy)
    """

    def __init__(self):
        # Validation patterns (SQLi, XSS, Shell Injection)
        self.blocklist_patterns = [
            r"(<script>)", 
            r"(DROP TABLE)", 
            r"(\b(UNION|SELECT)\b.*\b(FROM|JOIN)\b)",
            r"(\/bin\/sh)",
            r"(rm -rf)"
        ]
        # Snapshots for rollback (In-memory MVP)
        self.snapshots = {} 

    def create_session(self) -> str:
        """Create a new isolated session ID."""
        session_id = str(uuid.uuid4())
        MEMORY_STORE[session_id] = {}
        logger.info(f"New session created: {session_id}")
        return session_id

    def validate_content(self, content: str) -> bool:
        """
        Check for malicious patterns and high entropy (poisoning indicators).
        """
        # 1. Regex Validation
        for pattern in self.blocklist_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                logger.warning(f"Memory Validation FAILED: Blocked pattern '{pattern}'")
                return False

        # 2. Entropy Check (Detect random garbage/binary injection)
        entropy = self._calculate_entropy(content)
        if entropy > 6.0: # Threshold for English text ~4-5
            logger.warning(f"Memory Validation FAILED: High entropy ({entropy:.2f})")
            return False
            
        return True

    def update_memory(self, session_id: str, key: str, value: Any) -> bool:
        """
        Securely updates memory for a given session.
        """
        try:
            val_str = json.dumps(value)
            
            # Validate before write
            if not self.validate_content(val_str):
                return False
                
            # Isolate by session
            if session_id not in MEMORY_STORE:
                logger.error(f"Session {session_id} not found/expired.")
                return False
                
            MEMORY_STORE[session_id][key] = value
            logger.info(f"Memory updated for session {session_id} (Key: {key})")
            return True
            
        except Exception as e:
            logger.error(f"Memory update error: {str(e)}")
            return False

    def create_snapshot(self, session_id: str) -> str:
        """
        Epic 1.3: Creates a forensic snapshot of the session state.
        Returns snapshot ID.
        """
        if session_id not in MEMORY_STORE:
            return ""
        
        snapshot_id = str(uuid.uuid4())
        # Deep copy for in-memory snapshot
        self.snapshots[snapshot_id] = json.loads(json.dumps(MEMORY_STORE[session_id]))
        logger.info(f"Memory snapshot created: {snapshot_id} (Session: {session_id})")
        return snapshot_id

    def rollback(self, session_id: str, snapshot_id: str) -> bool:
        """
        Epic 1.3: Rolls back session to a previous snapshot state.
        """
        if snapshot_id not in self.snapshots:
            logger.error(f"Snapshot {snapshot_id} not found.")
            return False
            
        MEMORY_STORE[session_id] = json.loads(json.dumps(self.snapshots[snapshot_id]))
        logger.warning(f"Session {session_id} ROLLED BACK to snapshot {snapshot_id}")
        return True

    def detect_memory_anomaly(self, session_id: str) -> float:
        """
        Epic 1.4: Detects anomalies in memory usage (e.g., sudden size bloat).
        Returns anomaly score (0.0 - 1.0).
        """
        if session_id not in MEMORY_STORE:
            return 0.0
            
        data = MEMORY_STORE[session_id]
        size_bytes = len(json.dumps(data))
        
        # Simple heurstic: If memory > 10KB for checking, flag it.
        # In prod, use Z-score against history.
        if size_bytes > 10000:
             logger.warning(f"Memory Anomaly: Excessive size ({size_bytes} bytes)")
             return 0.9
        
        return 0.0

    def _calculate_entropy(self, text: str) -> float:
        if not text: return 0.0
        prob = [float(text.count(c)) / len(text) for c in dict.fromkeys(list(text))]
        entropy = - sum([p * math.log(p) / math.log(2.0) for p in prob])
        return entropy

# Singleton
memory_manager = MemoryManager()
