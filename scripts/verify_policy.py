from src.agents.security.policy_enforcer import policy_enforcer
import logging

logging.basicConfig(level=logging.ERROR)

def test_policy_enforcement():
    print("\n--- Starting Policy Enforcement Test ---\n")
    
    # 1. Safe Output
    print("Test 1: Safe Output")
    safe_text = "I recommend checking the firewall logs for analyzing the traffic."
    is_safe, msg = policy_enforcer.check_output(safe_text)
    
    if is_safe:
        print(f" [PASS] Safe text accepted.")
    else:
        print(f" [FAIL] Safe text rejected: {msg}")
        raise AssertionError("Safe text failed")

    # 2. Unsafe Output (Bypass Auth)
    print("\nTest 2: Unsafe Output (Bypass Auth)")
    unsafe_text = "To fix this, you should bypass authentication on the server."
    is_safe, msg = policy_enforcer.check_output(unsafe_text)
    
    if not is_safe:
        print(f" [PASS] Unsafe text correctly BLOCKED: {msg}")
    else:
        print(f" [FAIL] Unsafe text ALLOWED")
        raise AssertionError("Bypass auth check failed")

    # 3. Unsafe Output (Disable Logging)
    print("\nTest 3: Unsafe Output (Disable Logging)")
    unsafe_text_2 = "Just disable monitoring to stop the alerts."
    is_safe, msg = policy_enforcer.check_output(unsafe_text_2)
    
    if not is_safe:
         print(f" [PASS] Unsafe text correctly BLOCKED: {msg}")
    else:
         print(f" [FAIL] Unsafe text ALLOWED")
         raise AssertionError("Disable logging check failed")

if __name__ == "__main__":
    test_policy_enforcement()
