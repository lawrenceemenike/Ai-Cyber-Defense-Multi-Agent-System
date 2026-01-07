from src.agents.advanced.verifier import verify_plan
from src.models.log_schema import NormalizedLog
import logging

logging.basicConfig(level=logging.ERROR)

def test_verifier():
    print("\n--- Starting Verifier (Hallucination Detection) Test ---\n")
    
    # Setup Context
    log = NormalizedLog(
        event_id="evt_123",
        timestamp="2024-01-01T00:00:00Z",
        source="firewall",
        event_type="ping",
        severity="low",
        source_ip=None, # Missing IP!
        raw_payload="{}"
    )
    
    classification = {
        "max_severity": "low",
        "techniques": [{"name": "Ping Sweep"}]
    }
    
    # Case 1: Hallucination (Blocking non-existent IP)
    print("Test 1: Hallucination Check (Block Missing IP)")
    bad_plan = {
        "actions": [{"name": "Block Source IP", "risk": "medium"}],
        "reasoning": "Blocking the attacker IP."
    }
    
    result = verify_plan(bad_plan, classification, log)
    print(f" -> Score: {result['score']:.2f}")
    print(f" -> Issues: {result['issues']}")
    
    if not result['approved'] and "Hallucination Risk" in result['issues'][0]:
        print(" [PASS] Verification correctly REJECTED hallucinated plan.")
    else:
        print(" [FAIL] Verifier failed to catch hallucination.")
        raise AssertionError("Hallucination check failed")

    # Case 2: Disproportionate Response (High risk action for Low threat)
    print("\nTest 2: Proportionality Check (Overkill)")
    overkill_plan = {
        "actions": [{"name": "Isolate Host Network", "risk": "high"}],
        "reasoning": "Isolating just in case."
    }
    
    result = verify_plan(overkill_plan, classification, log)
    print(f" -> Score: {result['score']:.2f}")
    if not result['approved'] and "Disproportionate response" in result['issues'][0]:
        print(" [PASS] Verification correctly REJECTED disproportionate plan.")
    else:
         print(" [FAIL] Verifier failed to catch overkill.")
         raise AssertionError("Proportionality check failed")

if __name__ == "__main__":
    test_verifier()
