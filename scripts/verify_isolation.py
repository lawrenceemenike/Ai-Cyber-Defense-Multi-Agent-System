from src.agents.security.agent_isolator import agent_isolator, IsolationLevel
import logging

logging.basicConfig(level=logging.ERROR)

def test_agent_isolation():
    print("\n--- Starting Agent Isolation Test ---\n")
    
    agent = "suspicious_agent"
    
    # 1. First Violation (Medium) - Monitored
    print("Test 1: First Medium Violation -> MONITORED")
    level = agent_isolator.isolate(agent, 'medium', 'Decision anomaly detected')
    
    if level == IsolationLevel.MONITORED:
        print(f" [PASS] Agent escalated to {level.name}")
    else:
        print(f" [FAIL] Expected MONITORED, got {level.name}")
        raise AssertionError("Isolation level incorrect")

    # Agent should still be able to execute actions
    if agent_isolator.is_allowed(agent, 'execute_command'):
        print(" [PASS] Agent can still execute commands (monitored only)")
    else:
        print(" [FAIL] Agent incorrectly blocked")
        raise AssertionError("Monitored agent blocked")

    # 2. High Violation - Restricted
    print("\nTest 2: High Violation -> RESTRICTED")
    level = agent_isolator.isolate(agent, 'high', 'Timing anomaly detected')
    
    if level == IsolationLevel.RESTRICTED:
        print(f" [PASS] Agent escalated to {level.name}")
    else:
        print(f" [FAIL] Expected RESTRICTED, got {level.name}")
        raise AssertionError("Isolation escalation failed")

    # Restricted agent should be blocked from write operations
    if not agent_isolator.is_allowed(agent, 'execute_command'):
        print(" [PASS] Agent blocked from executing commands (restricted)")
    else:
        print(" [FAIL] Restricted agent NOT blocked")
        raise AssertionError("Restricted agent allowed")

    # But can still read
    if agent_isolator.is_allowed(agent, 'query_state'):
        print(" [PASS] Agent can still query state (read-only)")
    else:
        print(" [FAIL] Read-only action blocked")
        raise AssertionError("Read-only blocked")

    # 3. Critical Violation - Quarantined
    print("\nTest 3: Critical Violation -> QUARANTINED")
    agent2 = "malicious_agent"
    level = agent_isolator.isolate(agent2, 'critical', 'Action spike detected')
    
    if level == IsolationLevel.QUARANTINED:
        print(f" [PASS] Agent escalated to {level.name}")
    else:
        print(f" [FAIL] Expected QUARANTINED, got {level.name}")
        raise AssertionError("Quarantine failed")

    # Quarantined agent should be completely blocked
    if not agent_isolator.is_allowed(agent2, 'query_state'):
        print(" [PASS] Agent blocked from all actions (quarantined)")
    else:
        print(" [FAIL] Quarantined agent NOT fully blocked")
        raise AssertionError("Quarantine incomplete")

    # 4. Manual Release
    print("\nTest 4: Manual Release by Admin")
    agent_isolator.release(agent2, "admin@example.com")
    
    if agent_isolator.is_allowed(agent2, 'execute_command'):
        print(" [PASS] Agent released and can execute again")
    else:
        print(" [FAIL] Released agent still blocked")
        raise AssertionError("Release failed")

if __name__ == "__main__":
    test_agent_isolation()
