from src.agents.security.consensus_manager import consensus_manager
import logging

logging.basicConfig(level=logging.ERROR)

def test_consensus():
    print("\n--- Starting Consensus & Anti-Replay Test ---\n")
    
    # 1. Consensus Test
    print("Test 1: Multi-Agent Consensus (3 voters)")
    decision = {"id": "decision_001", "action": "Shutdown Critical System"}
    voters = ["mitigation_planning_agent", "threat_classification_agent", "verifier_agent"]
    
    if consensus_manager.collect_votes(decision, voters):
        print(" [PASS] Consensus reached (3/3 = 100% > 66% threshold).")
    else:
        print(" [FAIL] Consensus failed unexpectedly.")
        raise AssertionError("Consensus test failed")

    # 2. Anti-Replay Test
    print("\nTest 2: Anti-Replay (Nonce Check)")
    nonce1 = consensus_manager.generate_nonce()
    
    if consensus_manager.check_nonce(nonce1):
        print(f" [PASS] Fresh nonce '{nonce1[:16]}...' accepted.")
    else:
        print(" [FAIL] Fresh nonce rejected.")
        raise AssertionError("Fresh nonce failed")
    
    # Try to reuse the same nonce (replay attack)
    if not consensus_manager.check_nonce(nonce1):
        print(f" [PASS] Replay nonce '{nonce1[:16]}...' correctly REJECTED.")
    else:
        print(" [FAIL] Replay nonce ACCEPTED.")
        raise AssertionError("Replay detection failed")

if __name__ == "__main__":
    test_consensus()
