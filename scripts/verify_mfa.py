from src.agents.security.mfa_enforcer import mfa_enforcer
import logging
import time

logging.basicConfig(level=logging.ERROR)

def test_mfa():
    print("\n--- Starting MFA Enforcement Test ---\n")
    
    # 1. Low Risk Action (Always Allowed)
    print("Test 1: Low Risk Action (ping)")
    if mfa_enforcer.check_mfa("ping", {}):
        print(" [PASS] Low risk action allowed without token.")
    else:
         print(" [FAIL] Low risk action blocked.")
         raise AssertionError("Low risk block")

    # 2. High Risk Action WITHOUT Token (Blocked)
    print("\nTest 2: High Risk Action (isolate_host) - NO TOKEN")
    if not mfa_enforcer.check_mfa("isolate_host", {}):
        print(" [PASS] High risk action blocked (Missing Token).")
    else:
        print(" [FAIL] High risk action ALLOWED without token.")
        raise AssertionError("Missing token check failed")

    # 3. High Risk Action WITH Valid Token (Allowed)
    print("\nTest 3: High Risk Action - WITH VALID TOKEN")
    token = mfa_enforcer.generate_token()
    context = {"mfa_token": token}
    
    if mfa_enforcer.check_mfa("isolate_host", context):
        print(" [PASS] High risk action authorized.")
    else:
        print(" [FAIL] High risk action rejected with valid token.")
        raise AssertionError("Valid token check failed")
        
    # 4. Replay Attack (Token reuse)
    print("\nTest 4: Replay Attack (Token Reuse)")
    # Try to use the same token again
    if not mfa_enforcer.check_mfa("isolate_host", context):
        print(" [PASS] Reused token rejected (OTP enforced).")
    else:
        print(" [FAIL] Reused token accepted.")
        raise AssertionError("Replay check failed")

if __name__ == "__main__":
    test_mfa()
