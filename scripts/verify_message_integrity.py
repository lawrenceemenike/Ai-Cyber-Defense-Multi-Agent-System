from src.agents.security.message_integrity import message_integrity
from src.agents.security.agent_identity import identity_manager
import logging

logging.basicConfig(level=logging.ERROR)

def test_message_integrity():
    print("\n--- Starting Message Integrity Test ---\n")
    
    # Setup agents
    sender = "mitigation_planning_agent"
    receiver = "action_execution_agent"
    
    # 1. Sign and Verify Valid Message
    print("Test 1: Sign and Verify Valid Message")
    message_data = {"action": "Block Source IP", "target": "192.168.1.50"}
    
    signed_msg = message_integrity.sign_message(sender, message_data)
    
    if message_integrity.verify_message(signed_msg, expected_sender=sender):
        payload = message_integrity.extract_payload(signed_msg)
        print(f" [PASS] Message verified. Payload: {payload}")
    else:
        print(" [FAIL] Valid message rejected.")
        raise AssertionError("Valid message failed")

    # 2. Tampered Message
    print("\nTest 2: Tampered Message (Modified Payload)")
    tampered_msg = signed_msg.copy()
    tampered_msg["envelope"]["payload"]["target"] = "10.0.0.1"  # Attacker changes target
    
    if not message_integrity.verify_message(tampered_msg, expected_sender=sender):
        print(" [PASS] Tampered message detected.")
    else:
        print(" [FAIL] Tampered message ACCEPTED.")
        raise AssertionError("Tamper detection failed")

    # 3. Spoofed Sender
    print("\nTest 3: Spoofed Sender")
    # Attacker tries to send message claiming to be from another agent
    fake_msg = message_integrity.sign_message("action_execution_agent", message_data)
    
    # Verify with wrong expected sender
    if not message_integrity.verify_message(fake_msg, expected_sender=sender):
        print(" [PASS] Sender spoofing detected.")
    else:
        print(" [FAIL] Spoofed sender ACCEPTED.")
        raise AssertionError("Sender verification failed")

if __name__ == "__main__":
    test_message_integrity()
