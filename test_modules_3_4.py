import sys
import os

# Set UTF-8 encoding for stdout on Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.services.security_checkup_service import SecurityCheckupService
from app.services.scam_indicator_service import ScamIndicatorService

def run_tests():
    print("==================================================")
    print("SMART SCAM MESSAGE DETECTION SYSTEM")
    print("Testing Module 3: Message Security Checkup")
    print("Testing Module 4: Scam Indicator Report")
    print("==================================================")

    # 1. Test Module 3 Service with Banking KYC Scam
    kyc_sample = (
        "Dear customer, your SBI NetBanking a/c is blocked due to incomplete KYC. "
        "Verify now at http://sbi-kyc-update.xyz within 24 hours to avoid permanent suspension. "
        "Call +91 98765 43210."
    )
    print("\n[TEST 1] Testing SecurityCheckupService on Banking KYC message...")
    checkup1 = SecurityCheckupService.evaluate(kyc_sample)
    
    assert checkup1["link_check"]["detected"] is True, "Link should be detected"
    assert checkup1["link_check"]["is_suspicious"] is True, "Link should be flagged suspicious"
    assert checkup1["banking_check"]["detected"] is True, "Banking content should be detected"
    assert "SBI" in checkup1["banking_check"]["details"], "SBI should be detected"
    assert checkup1["kyc_check"]["detected"] is True, "KYC request should be detected"
    assert checkup1["urgency_check"]["detected"] is True, "Urgency should be detected"
    assert checkup1["phone_check"]["detected"] is True, "Phone should be detected"
    print("  [OK] Link Check: Found & Suspicious ->", checkup1["link_check"]["status"])
    print("  [OK] Banking Content: Detected ->", checkup1["banking_check"]["details"])
    print("  [OK] KYC Request: Detected ->", checkup1["kyc_check"]["details"])
    print("  [OK] Urgency: Detected ->", checkup1["urgency_check"]["details"])
    print("  [OK] Category: ->", checkup1["message_category"])

    # 2. Test Module 4 on the exact 5 Warning Signs User Sample
    print("\n[TEST 2] Testing ScamIndicatorService for the 5 Warning Signs...")
    test_5_signs = (
        "URGENT: Your HDFC Bank account is scheduled to be blocked today! "
        "Complete mandatory KYC verification immediately within 24 hours at "
        "http://hdfc-netbanking-verify.xyz to prevent permanent suspension."
    )
    report = ScamIndicatorService.generate_report(test_5_signs)
    
    labels = [i["label"] for i in report["indicators"]]
    print("  Detected Indicators:")
    for ind in report["indicators"]:
        print(f"    [{ind['severity'].upper()}] {ind['label']}")

    assert "Suspicious Link" in labels, "Suspicious Link indicator missing"
    assert "Urgency" in labels, "Urgency indicator missing"
    assert "KYC Request" in labels, "KYC Request indicator missing"
    assert "Banking Reference" in labels, "Banking Reference indicator missing"
    assert "Account Threat" in labels, "Account Threat indicator missing"
    assert report["warning_count"] == 5, f"Expected 5 warning signs, got {report['warning_count']}"
    print(f"\n  [OK] Warning Count Text: '{report['warning_count_text']}'")
    assert report["warning_count_text"] == "5 warning signs detected", f"Mismatch in count text: {report['warning_count_text']}"

    # 3. Test OTP & Sensitive Information Phishing
    print("\n[TEST 3] Testing OTP Request Indicator...")
    otp_sample = "Security Alert: Unusual sign-in attempt detected. Reply with your ATM PIN and the OTP sent to your phone."
    otp_report = ScamIndicatorService.generate_report(otp_sample)
    otp_labels = [i["label"] for i in otp_report["indicators"]]
    assert "OTP Request" in otp_labels, "OTP Request indicator should be triggered"
    print("  [OK] OTP Request Flagged:", otp_labels)

    # 4. Test Flask HTTP Endpoints via Test Client with Authenticated Session
    print("\n[TEST 4] Testing Flask HTTP Controllers & Templates...")
    app = create_app()
    client = app.test_client()

    with client:
        # Authenticate via /auth/login
        login_res = client.post("/auth/login", data={
            "identifier": "admin@scamdetect.internal",
            "password": "Admin@12345!"
        }, follow_redirects=True)
        assert login_res.status_code == 200, "Login failed in test client"
        print("  [OK] Test client authenticated successfully as admin@scamdetect.internal")

        # Test GET /checkup/
        res = client.get("/checkup/")
        assert res.status_code == 200, f"GET /checkup/ failed with {res.status_code}"
        assert b"Message Security Checkup" in res.data, "Checkup heading missing"
        print("  [OK] GET /checkup/ returned 200 OK")

        # Test POST /checkup/analyze
        res_post_chk = client.post("/checkup/analyze", data={"text": kyc_sample})
        assert res_post_chk.status_code == 200, f"POST /checkup/analyze failed with {res_post_chk.status_code}"
        assert b"MESSAGE SECURITY CHECKUP" in res_post_chk.data, "Checkup card title missing"
        assert b"Suspicious" in res_post_chk.data, "Suspicious badge missing in checkup HTML"
        assert b"Banking Content" in res_post_chk.data, "Banking Content row missing"
        print("  [OK] POST /checkup/analyze returned 200 OK with rendered checklist")

        # Test GET /indicators/
        res_ind = client.get("/indicators/")
        assert res_ind.status_code == 200, f"GET /indicators/ failed with {res_ind.status_code}"
        assert b"Scam Indicator Report" in res_ind.data, "Scam indicator report heading missing"
        print("  [OK] GET /indicators/ returned 200 OK")

        # Test POST /indicators/analyze
        res_post_ind = client.post("/indicators/analyze", data={"text": test_5_signs})
        assert res_post_ind.status_code == 200, f"POST /indicators/analyze failed with {res_post_ind.status_code}"
        assert b"SCAM INDICATORS FOUND" in res_post_ind.data, "Expected 'SCAM INDICATORS FOUND' heading"
        assert b"5 warning signs detected" in res_post_ind.data, "Expected '5 warning signs detected' in HTML"
        assert b"Suspicious Link" in res_post_ind.data, "Expected Suspicious Link badge"
        print("  [OK] POST /indicators/analyze returned 200 OK with '5 warning signs detected'")

        # Test Scanner integration
        print("\n[TEST 5] Testing Smart Scanner Integration (Module 2 + 3 + 4)...")
        res_scan = client.post("/scanner/scan", data={
            "message_type": "sms",
            "sender_info": "AX-HDFCBK",
            "content": test_5_signs
        }, follow_redirects=True)
        assert res_scan.status_code == 200, f"Scanner scan failed with {res_scan.status_code}"
        assert b"MESSAGE SECURITY CHECKUP" in res_scan.data, "Checkup card not found in scanner results"
        assert b"SCAM INDICATORS FOUND" in res_scan.data, "Indicators card not found in scanner results"
        assert b"5 warning signs detected" in res_scan.data, "'5 warning signs detected' not found in scanner results"
        # Test /preprocessor/ graceful redirect
        res_prep = client.get("/preprocessor/")
        assert res_prep.status_code == 302, f"Expected 302 redirect from /preprocessor/, got {res_prep.status_code}"
        assert "/scanner" in res_prep.headers.get("Location", ""), "Expected redirect to /scanner/"
        print("  [OK] /preprocessor/ successfully redirects to /scanner/ (developer workbench hidden from end-users)")

    print("\n==================================================")
    print("ALL MODULE 3 & 4 UNIT + INTEGRATION TESTS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
