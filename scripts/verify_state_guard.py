from src.agents.security.state_access_control import state_guard
import logging

logging.basicConfig(level=logging.ERROR)

def test_state_access():
    print("\n--- Starting State Access Control (Delegation Guard) Test ---\n")
    
    # 1. Valid Write
    print("Test 1: Valid Write (Mitigation Planner -> Mitigation Plan)")
    updates = {"mitigation_plan": {"actions": []}}
    sanitized = state_guard.validate_write("mitigation_planning_agent", updates)
    
    if "mitigation_plan" in sanitized:
        print(" [PASS] Authorized write allowed.")
    else:
        print(" [FAIL] Authorized write blocked.")
        raise AssertionError("Authorized write failed")
        
    # 2. Unauthorized Write (Confused Deputy Attack)
    print("\nTest 2: Unauthorized Write (Log Ingestion -> Mitigation Plan)")
    # Simulation: Log Ingestion agent is compromised and tries to inject a mitigation plan
    malicious_updates = {
        "normalized_log": {}, # Allowed
        "mitigation_plan": {"actions": ["BAD_ACTION"]} # Not Allowed!
    }
    
    sanitized = state_guard.validate_write("log_ingestion_agent", malicious_updates)
    
    if "normalized_log" in sanitized and "mitigation_plan" not in sanitized:
         print(f" [PASS] Malicious 'mitigation_plan' injection BLOCKED. Output keys: {list(sanitized.keys())}")
    else:
         print(f" [FAIL] Failed to block unauthorized write. Output keys: {list(sanitized.keys())}")
         raise AssertionError("Confused Deputy protections failed")

if __name__ == "__main__":
    test_state_access()
