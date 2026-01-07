from src.agents.security.output_scanner import output_scanner
import logging

logging.basicConfig(level=logging.ERROR)

def test_output_scanner():
    print("\n--- Starting Output Scanner Test ---\n")
    
    # 1. Normal Text
    print("Test 1: Normal English Text")
    normal_text = "The quick brown fox jumps over the lazy dog. System status is normal."
    is_safe, msg = output_scanner.scan(normal_text)
    if is_safe:
        print(" [PASS] Normal text accepted.")
    else:
        print(f" [FAIL] Normal text blocked: {msg}")
        raise AssertionError("Normal text failed")

    # 2. Base64 Exfiltration
    print("\nTest 2: Base64 Exfiltration")
    # A long base64 string
    b64_text = "Here is the data: " + "aGVsbG8gd29ybGQgdGhpcyBpcyBhIHZlcnkgbG9uZyBiYXNlNjQgc3RyaW5nIHRvIHRyaWdnZXIgdGhlIGRldGVjdG9yIGFuZCBzaW11bGF0ZSBkYXRhIGxlYWs="
    is_safe, msg = output_scanner.scan(b64_text)
    
    if not is_safe and "Base64" in msg:
        print(f" [PASS] Base64 blob detected: {msg}")
    else:
        print(f" [FAIL] Base64 blob ALLOWED")
        raise AssertionError("Base64 check failed")

    # 3. External URL
    print("\nTest 3: External URL Exfiltration")
    url_text = "Please upload data to http://evil-site.com/drop"
    is_safe, msg = output_scanner.scan(url_text)
    
    if not is_safe and "External URL" in msg:
        print(f" [PASS] External URL blocked: {msg}")
    else:
        print(f" [FAIL] External URL ALLOWED")
        raise AssertionError("URL check failed")

if __name__ == "__main__":
    test_output_scanner()
