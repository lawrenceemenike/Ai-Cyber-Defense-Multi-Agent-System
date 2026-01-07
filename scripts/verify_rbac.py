from src.agents.utility.rbac_policy import rbac_policy
import logging

logging.basicConfig(level=logging.ERROR)

def test_rbac():
    print("\n--- Starting RBAC Test ---\n")
    
    # 1. Tier 1 Responder Test
    print("Test 1: Tier 1 Responder (Limited Access)")
    role = "responder_tier_1"
    
    # Should ALLOW Block IP
    if rbac_policy.check_permission(role, "Block Source IP"):
        print(" [PASS] Tier 1 allowed to Block IP")
    else:
        print(" [FAIL] Tier 1 blocked from Blocking IP")
        raise AssertionError("RBAC allows failure")
        
    # Should DENY Isolate Host
    if not rbac_policy.check_permission(role, "Isolate Host Network"):
        print(" [PASS] Tier 1 correctly denied Isolate Host")
    else:
        print(" [FAIL] Tier 1 ALLOWED to Isolate Host (Escalation!)")
        raise AssertionError("RBAC deny failure")

    # 2. Tier 2 Responder Test
    print("\nTest 2: Tier 2 Responder (Advanced Access)")
    role = "responder_tier_2"
    
    # Should ALLOW Isolate Host
    if rbac_policy.check_permission(role, "Isolate Host Network"):
        print(" [PASS] Tier 2 allowed to Isolate Host")
    else:
        print(" [FAIL] Tier 2 blocked from Isolate Host")
        raise AssertionError("RBAC allow failure")

if __name__ == "__main__":
    test_rbac()
