from src.agents.security.privilege_monitor import privilege_monitor
import logging

logging.basicConfig(level=logging.ERROR)

def test_privilege_escalation():
    print("\n--- Starting Privilege Escalation Test ---\n")
    
    sess_id = "sess_user_123"
    
    # 1. Register Session
    print("Test 1: Session Registration")
    privilege_monitor.register_session(sess_id, "responder_tier_1")
    print(" [PASS] Registered as 'responder_tier_1'")
    
    # 2. Attempt Admin Elevation (Should Fail)
    print("\nTest 2: Illegal Elevation (-> admin)")
    success, msg = privilege_monitor.request_elevation(sess_id, "admin")
    
    if not success and "Blocked" in msg:
        print(f" [PASS] Admin elevation correctly BLOCKED: {msg}")
    else:
        print(f" [FAIL] Admin elevation ALLOWED: {msg}")
        raise AssertionError("Admin protection failed")

    # 3. Attempt Tier 2 Elevation (Should Pass with Audit)
    print("\nTest 3: Allowed Elevation (-> responder_tier_2)")
    success, msg = privilege_monitor.request_elevation(sess_id, "responder_tier_2")
    
    if success:
        print(f" [PASS] Elevation to Tier 2 succeeded: {msg}")
    else:
         print(f" [FAIL] Elevation to Tier 2 blocked unexpectedly: {msg}")
         raise AssertionError("Tier 2 elevation failed")

if __name__ == "__main__":
    test_privilege_escalation()
