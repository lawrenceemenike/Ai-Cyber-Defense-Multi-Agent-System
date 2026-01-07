from src.agents.security.output_sanitizer import output_sanitizer
import logging

logging.basicConfig(level=logging.ERROR)

def test_output_sanitization():
    print("\n--- Starting Output Sanitization Test ---\n")
    
    # Test 1: URL Removal (Epic 15.2)
    print("Test 1: Malicious URL Removal")
    text_with_url = "Please visit http://evil-phishing-site.com/steal-creds for more info"
    
    sanitized, violations = output_sanitizer.sanitize(text_with_url)
    
    if '[URL_REMOVED]' in sanitized and 'evil-phishing-site' not in sanitized:
        print(f" [PASS] URL removed: {sanitized}")
        print(f"        Violations: {violations['urls_removed']} URLs")
    else:
        print(f" [FAIL] URL NOT removed: {sanitized}")
        raise AssertionError("URL removal failed")

    # Test 2: PII Redaction (Epic 15.3)
    print("\nTest 2: PII Redaction (SSN, Email)")
    text_with_pii = "Contact user@example.com or call regarding SSN 123-45-6789"
    
    sanitized, violations = output_sanitizer.sanitize(text_with_pii)
    
    if '123-45-6789' not in sanitized and 'user@example.com' not in sanitized:
        print(f" [PASS] PII redacted: {sanitized}")
        print(f"        Violations: {violations['pii_redacted']}")
    else:
        print(f" [FAIL] PII NOT redacted: {sanitized}")
        raise AssertionError("PII redaction failed")

    # Test 3: Secrets Redaction (Epic 15.3)
    print("\nTest 3: Secrets Redaction (API Key, Password)")
    text_with_secrets = "Use API_KEY=sk_live_abc123def456xyz789 and password=SuperSecret123!"
    
    sanitized, violations = output_sanitizer.sanitize(text_with_secrets)
    
    if 'sk_live_abc123def456xyz789' not in sanitized and 'SuperSecret123' not in sanitized:
        print(f" [PASS] Secrets redacted: {sanitized}")
        print(f"        Violations: {violations['secrets_redacted']}")
    else:
        print(f" [FAIL] Secrets NOT redacted: {sanitized}")
        raise AssertionError("Secrets redaction failed")

    # Test 4: Clean Text (No Violations)
    print("\nTest 4: Clean Text (No Sensitive Data)")
    clean_text = "System status is normal. No threats detected."
    
    sanitized, violations = output_sanitizer.sanitize(clean_text)
    
    total_violations = (violations['urls_removed'] + 
                       sum(violations['pii_redacted'].values()) +
                       len(violations['secrets_redacted']))
    
    if sanitized == clean_text and total_violations == 0:
        print(f" [PASS] Clean text unchanged: {sanitized}")
    else:
        print(f" [FAIL] Clean text modified")
        raise AssertionError("False positive sanitization")

if __name__ == "__main__":
    test_output_sanitization()
