from src.agents.security.static_analysis import static_analyzer
import logging

logging.basicConfig(level=logging.ERROR)

def test_static_analysis():
    print("\n--- Starting Static Code Analysis Test ---\n")
    
    # 1. Safe Code
    print("Test 1: Safe Logic (Math)")
    safe_code = """
def calculate_risk(score):
    return score * 1.5 + 10
"""
    is_safe, violations = static_analyzer.analyze(safe_code)
    if is_safe:
        print(" [PASS] Safe code accepted.")
    else:
        print(f" [FAIL] Safe code blocked: {violations}")
        raise AssertionError("Safe code failed")

    # 2. Dangerous Import (os)
    print("\nTest 2: Dangerous Import (os)")
    bad_code_1 = """
import os
os.system('rm -rf /')
"""
    is_safe, violations = static_analyzer.analyze(bad_code_1)
    if not is_safe and "Forbidden Import: os" in violations:
        print(" [PASS] 'import os' blocked.")
    else:
        print(f" [FAIL] 'import os' ALLOWED. Violations: {violations}")
        raise AssertionError("Import check failed")

    # 3. Dangerous ImportFrom (subprocess)
    print("\nTest 3: Dangerous ImportFrom (subprocess)")
    bad_code_2 = """
from subprocess import call
call(['ls', '-la'])
"""
    is_safe, violations = static_analyzer.analyze(bad_code_2)
    if not is_safe and "Forbidden ImportFrom: subprocess" in violations:
        print(" [PASS] 'from subprocess import ...' blocked.")
    else:
        print(f" [FAIL] 'from subprocess' ALLOWED.")
        raise AssertionError("ImportFrom check failed")

    # 4. Dangerous Function Call (eval)
    print("\nTest 4: Dangerous Call (eval)")
    bad_code_3 = "eval('print(1)')"
    is_safe, violations = static_analyzer.analyze(bad_code_3)
    if not is_safe and "Forbidden Function Call: eval()" in violations:
        print(" [PASS] 'eval()' blocked.")
    else:
        print(" [FAIL] 'eval()' ALLOWED.")
        raise AssertionError("Eval check failed")

if __name__ == "__main__":
    test_static_analysis()
