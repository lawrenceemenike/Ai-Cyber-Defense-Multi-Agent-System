from src.agents.security.agent_identity import identity_manager
import logging

logging.basicConfig(level=logging.ERROR)

def test_agent_identity():
    print("\n--- Starting Agent Identity Test ---\n")
    
    agent_id = "mitigation_planning_agent"
    message = "Plan: isolate_host(id=5)"
    
    # 1. Signing
    print("Test 1: Signing Message")
    signature = identity_manager.sign_message(agent_id, message)
    print(f" [PASS] Signed message (Sig len: {len(signature)})")
    
    # 2. Valid Verification
    print("\nTest 2: Verifying Valid Signature")
    if identity_manager.verify_signature(agent_id, message, signature):
        print(" [PASS] Signature verified successfully.")
    else:
        print(" [FAIL] Valid signature rejected.")
        raise AssertionError("Verification failed")

    # 3. Invalid/Tampered Verification
    print("\nTest 3: Verifying Tampered Message")
    tampered_message = "Plan: isolate_host(id=999)" # Attackers changed the ID
    
    if not identity_manager.verify_signature(agent_id, tampered_message, signature):
        print(" [PASS] Tampered message correctly rejected.")
    else:
        print(" [FAIL] Tampered message accepted (Signature collision?)")
        raise AssertionError("Tamper check failed")
        
    # 4. Impersonation Attempt
    print("\nTest 4: Impersonation Attempt")
    # Attacker tries to sign as 'mitigation_planning_agent' but uses their own key (or random bytes)
    fake_signature = b'A'*256 
    
    if not identity_manager.verify_signature(agent_id, message, fake_signature):
        print(" [PASS] Fake signature rejected.")
    else:
        print(" [FAIL] Fake signature accepted.")
        raise AssertionError("Impersonation check failed")

if __name__ == "__main__":
    test_agent_identity()
