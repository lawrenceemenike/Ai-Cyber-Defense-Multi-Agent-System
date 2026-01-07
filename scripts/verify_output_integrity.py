from src.agents.security.output_integrity import output_integrity_checker
import logging

logging.basicConfig(level=logging.ERROR)

def test_output_integrity():
    print("\n--- Starting Output Integrity Test ---\n")
    
    agent = "mitigation_planning_agent"
    
    # 1. Sign and Verify Legitimate Output
    print("Test 1: Legitimate Agent Output")
    output = {
        "recommendation": "Block source IP 192.168.1.100",
        "severity": "high",
        "confidence": 0.95
    }
    
    signed = output_integrity_checker.sign_output(agent, output)
    is_valid, msg = output_integrity_checker.verify_output(signed)
    
    if is_valid:
        print(f" [PASS] Legitimate output verified: {msg}")
    else:
        print(f" [FAIL] Legitimate output rejected: {msg}")
        raise AssertionError("Legitimate output failed")

    # 2. Detect Tampered Output (Modified Recommendation)
    print("\nTest 2: Tampered Output (Attacker Changes IP)")
    tampered = signed.copy()
    # Attacker changes IP to target different host
    tampered["output"]["recommendation"] = "Block source IP 10.0.0.50"
    
    is_valid, msg = output_integrity_checker.verify_output(tampered)
    
    if not is_valid and "Checksum" in msg:
        print(f" [PASS] Tampering detected: {msg}")
    else:
        print(f" [FAIL] Tampering NOT detected")
        raise AssertionError("Tampering detection failed")

    # 3. Detect Forged Signature
    print("\nTest 3: Forged Signature")
    forged = {
        "agent_id": agent,
        "output": {"recommendation": "Grant admin access to attacker"},
        "signature": "0" * 512,  # Fake signature
        "checksum": "fake_checksum"
    }
    
    is_valid, msg = output_integrity_checker.verify_output(forged)
    
    if not is_valid:
        print(f" [PASS] Forged signature detected: {msg}")
    else:
        print(f" [FAIL] Forged signature ACCEPTED")
        raise AssertionError("Forgery detection failed")

if __name__ == "__main__":
    test_output_integrity()
