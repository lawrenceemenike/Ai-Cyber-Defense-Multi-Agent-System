from src.agents.utility.audit_logger import audit_logger, AUDIT_STORE
import logging
import time

# Disable logging for cleaner output
logging.getLogger("agent.audit_logger").setLevel(logging.CRITICAL)

def test_audit_integrity():
    print("\n--- Starting Audit Integrity Test ---\n")
    
    # 1. Generate Valid Logs
    print("Test 1: Generating Signed Logs")
    sig1 = audit_logger.log_event("agent_1", "login", {"user": "admin"})
    sig2 = audit_logger.log_event("agent_2", "access_file", {"file": "shadow"})
    sig3 = audit_logger.log_event("agent_1", "logout", {})
    
    print(f" [PASS] Generated 3 entries. Chain length: {len(AUDIT_STORE)}")
    
    # 2. Verify Valid Chain
    print("\nTest 2: Verifying Valid Chain")
    invalids = audit_logger.verify_integrity()
    if len(invalids) == 0:
        print(" [PASS] Chain Integrity Verified")
    else:
        print(f" [FAIL] Expected 0 invalid entries, found {len(invalids)}")
        raise AssertionError("Chain should be valid")
        
    # 3. Simulate Tampering
    print("\nTest 3: Simulating Tampering Attack")
    # Attack: Modify the "action" of the second entry
    print(" ... Attacker changing 'access_file' to 'read_news' in entry #1")
    AUDIT_STORE[1]["data"]["action"] = "read_news"
    
    # 4. Verify Detection
    print("\nTest 4: Verifying Tamper Detection")
    invalids = audit_logger.verify_integrity()
    
    # Expect failure at index 1 (Bad Sig) AND index 2 (Broken Chain from prev_hash mismatch)
    # Actually, modifying data breaks sig for that entry.
    # It might NOT break prev_hash of next entry if we don't recompute hash, 
    # but the verify function checks sig matches payload.
    
    found_tamper = False
    for fault in invalids:
        print(f" -> Detected Fault at Index {fault['index']}: {fault['reason']}")
        if fault["index"] == 1:
            found_tamper = True
            
    if found_tamper:
         print(" [PASS] Tampering Successfully Detected")
    else:
         print(" [FAIL] System failed to detect tampering")
         raise AssertionError("Tampering not detected")

if __name__ == "__main__":
    test_audit_integrity()
