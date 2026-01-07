from src.agents.security.identity_registry import registry_guard
import logging

logging.basicConfig(level=logging.ERROR)

def test_registry_protection():
    print("\n--- Starting Identity Registry Protection Test ---\n")
    
    # 1. Valid Registration
    print("Test 1: Valid Agent Registration")
    valid_agent = "mitigation_planning_agent"
    if registry_guard.validate_registration_request(valid_agent):
        print(f" [PASS] '{valid_agent}' allowed to register.")
    else:
        print(f" [FAIL] '{valid_agent}' blocked incorrectly.")
        raise AssertionError("Valid agent blocked")

    # 2. Synthetic/Malicious Registration
    print("\nTest 2: Synthetic Identity Injection")
    fake_agent = "rogue_admin_bot"
    if not registry_guard.validate_registration_request(fake_agent):
        print(f" [PASS] '{fake_agent}' correctly BLOCKED.")
    else:
        print(f" [FAIL] '{fake_agent}' ALLOWED (Vulnerability).")
        raise AssertionError("Synthetic identity allowed")

    # 3. Spoofed Name Variation
    print("\nTest 3: Spoofed Name Variation (Typosquatting)")
    sqaut_agent = "mitigation_planning_agent " # Trailing space
    # The set lookup should handle exact matches, so this should fail if not stripped
    # But usually precise string matching is desired for IDs.
    
    if not registry_guard.validate_registration_request(sqaut_agent):
        print(f" [PASS] '{sqaut_agent}' (Typosquat) BLOCKED.")
    else:
         print(f" [FAIL] '{sqaut_agent}' ALLOWED.")
         raise AssertionError("Typosquatting allowed")

if __name__ == "__main__":
    test_registry_protection()
