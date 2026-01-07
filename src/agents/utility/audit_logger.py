import logging
import hashlib
import hmac
import json
import time
from typing import Dict, Any, List

# In-memory store for MVP (simulating append-only DB)
AUDIT_STORE = []

logger = logging.getLogger("agent.audit_logger")

class AuditLogger:
    """
    Handles immutable logging with cryptographic signatures (Epic 8).
    Ensures non-repudiation and integrity.
    """
    
    def __init__(self, secret_key: str = "change_me_in_prod_mvp_secret"):
        self.secret_key = secret_key.encode('utf-8')

    def log_event(self, agent_id: str, action: str, details: Dict[str, Any]) -> str:
        """
        Creates a signed audit entry and appends to the store.
        Returns the signature of the entry.
        """
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        
        entry = {
            "timestamp": timestamp,
            "agent_id": agent_id,
            "action": action,
            "details": details,
            "prev_hash": self._get_last_hash() # Chaining for tamper-evidence
        }
        
        # Canonicalize for signing
        payload = json.dumps(entry, sort_keys=True)
        signature = self._compute_signature(payload)
        
        # Store signed entry
        final_record = {
            "data": entry,
            "signature": signature
        }
        
        AUDIT_STORE.append(final_record)
        logger.info(f"Audit log written: {action} by {agent_id} (Sig: {signature[:8]}...)")
        
        return signature

    def verify_integrity(self) -> List[Dict[str, Any]]:
        """
        Scans values to verify signatures and hash chain.
        Returns list of invalid entries.
        """
        invalid_entries = []
        
        for i, record in enumerate(AUDIT_STORE):
            data = record["data"]
            signature = record["signature"]
            
            # 1. Verify Signature
            payload = json.dumps(data, sort_keys=True)
            expected_sig = self._compute_signature(payload)
            
            if not hmac.compare_digest(signature, expected_sig):
                logger.error(f"Audit Integrity Fail at index {i}: Signature Mismatch")
                invalid_entries.append({"index": i, "reason": "Bad Signature", "record": record})
                continue
            
            # 2. Verify Chain (prev_hash)
            if i > 0:
                prev_record = AUDIT_STORE[i-1]
                prev_sig = prev_record["signature"]
                if data["prev_hash"] != prev_sig:
                    logger.error(f"Audit Integrity Fail at index {i}: Broken Chain")
                    invalid_entries.append({"index": i, "reason": "Broken Chain", "record": record})

        return invalid_entries

    def _compute_signature(self, payload: str) -> str:
        return hmac.new(self.secret_key, payload.encode('utf-8'), hashlib.sha256).hexdigest()

    def _get_last_hash(self) -> str:
        if not AUDIT_STORE:
            return "0" * 64 # Genesis hash
        return AUDIT_STORE[-1]["signature"]

# Singleton
audit_logger = AuditLogger()
