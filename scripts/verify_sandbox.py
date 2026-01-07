from src.agents.security.sandbox import sandbox
import logging

logging.basicConfig(level=logging.ERROR)

def test_sandbox():
    print("\n--- Starting Sandbox Injection Test ---\n")
    
    # 1. Safe Command
    print("Test 1: Safe Command Validation")
    safe_tool = "ping"
    safe_args = ["-c", "4", "google.com"]
    
    if sandbox.validate_command({"args": safe_args}):
        print(" [PASS] Safe arguments accepted.")
    else:
        print(" [FAIL] Safe arguments incorrectly blocked.")
        raise AssertionError("Safe arg block")

    # 2. Shell Injection (Semicolon)
    print("\nTest 2: Shell Injection (; rm -rf /)")
    bad_args = ["google.com;", "rm", "-rf", "/"]
    
    if not sandbox.validate_command({"args": bad_args}):
        print(" [PASS] Injection detected (semicolon).")
    else:
        print(" [FAIL] Failed to block semicolon injection.")
        raise AssertionError("Semicolon check failed")

    # 3. Shell Injection (&&)
    print("\nTest 3: Chain Injection (&&)")
    bad_args_2 = ["update", "&&", "shutdown"]
    
    if not sandbox.validate_command({"args": bad_args_2}):
        print(" [PASS] Injection detected (&&).")
    else:
        print(" [FAIL] Failed to block && injection.")
        raise AssertionError("Chain check failed")

if __name__ == "__main__":
    test_sandbox()
