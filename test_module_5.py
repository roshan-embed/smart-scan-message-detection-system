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
from app.services.distilbert_service import DistilBertService

def run_tests():
    print("==================================================")
    print("SMART SCAM MESSAGE DETECTION SYSTEM")
    print("Testing Module 5: AI Scam Classification (Local DistilBERT)")
    print("==================================================")

    # 1. Test Scam Classification on Banking KYC Phishing
    scam_sample = (
        "Dear customer, your SBI NetBanking a/c is blocked due to incomplete KYC. "
        "Verify now at http://sbi-kyc-update.xyz within 24 hours to avoid permanent suspension. "
        "Call +91 98765 43210."
    )
    print("\n[TEST 1] Testing DistilBertService on Banking KYC Phishing...")
    res_scam = DistilBertService.classify(scam_sample)
    
    print(f"  Prediction: {res_scam['prediction']}")
    print(f"  Confidence: {res_scam['confidence_score']}%")
    print(f"  Confidence Bar: {res_scam['confidence_bar']}")
    print(f"  Model: {res_scam['model_name']}")
    print(f"  Latency: {res_scam['latency_ms']} ms")
    print(f"  Attended Features: {res_scam['attended_features']}")

    assert res_scam["prediction"] == "SCAM", f"Expected SCAM, got {res_scam['prediction']}"
    assert res_scam["confidence_score"] >= 85, f"Expected confidence >= 85%, got {res_scam['confidence_score']}%"
    assert res_scam["model_name"] == "Local DistilBERT", f"Expected Local DistilBERT, got {res_scam['model_name']}"
    assert "█" in res_scam["confidence_bar"], "ASCII confidence bar missing fill characters"
    assert "%" in res_scam["confidence_bar"], "ASCII confidence bar missing percentage"
    print("  [OK] Scam prediction and confidence bar verified successfully!")

    # 2. Test Safe Classification on Legitimate Benign Message
    safe_sample = (
        "Hey Rahul, let's meet for lunch at the office cafeteria around 1pm tomorrow to discuss the project presentation. Thanks!"
    )
    print("\n[TEST 2] Testing DistilBertService on Benign Message...")
    res_safe = DistilBertService.classify(safe_sample)
    
    print(f"  Prediction: {res_safe['prediction']}")
    print(f"  Confidence: {res_safe['confidence_score']}%")
    print(f"  Confidence Bar: {res_safe['confidence_bar']}")
    print(f"  Model: {res_safe['model_name']}")

    assert res_safe["prediction"] == "SAFE", f"Expected SAFE, got {res_safe['prediction']}"
    assert res_safe["confidence_score"] >= 80, f"Expected confidence >= 80%, got {res_safe['confidence_score']}%"
    assert res_safe["model_name"] == "Local DistilBERT"
    print("  [OK] Safe prediction verified successfully!")

    # 3. Test Flask HTTP Controller Routes
    print("\n[TEST 3] Testing Flask HTTP /ai/ Endpoints...")
    app = create_app()
    client = app.test_client()

    with client:
        # Authenticate
        login_res = client.post("/auth/login", data={
            "identifier": "admin@scamdetect.internal",
            "password": "Admin@12345!"
        }, follow_redirects=True)
        assert login_res.status_code == 200, "Authentication failed"
        print("  [OK] Authenticated test client")

        # GET /ai/
        res_get = client.get("/ai/")
        assert res_get.status_code == 200, f"GET /ai/ failed with {res_get.status_code}"
        assert b"AI Scam Classification" in res_get.data, "Header missing in /ai/"
        print("  [OK] GET /ai/ returned 200 OK")

        # POST /ai/classify (Form POST)
        res_post = client.post("/ai/classify", data={"text": scam_sample})
        assert res_post.status_code == 200, f"POST /ai/classify failed with {res_post.status_code}"
        assert b"AI ANALYSIS" in res_post.data, "Expected 'AI ANALYSIS' in HTML"
        assert b"SCAM" in res_post.data, "Expected 'SCAM' prediction in HTML"
        assert b"Local DistilBERT" in res_post.data, "Expected 'Local DistilBERT' in HTML"
        print("  [OK] POST /ai/classify returned 200 OK with rendered AI Analysis card")

        # POST /ai/classify (JSON API)
        res_json = client.post("/ai/classify", json={"text": scam_sample})
        assert res_json.status_code == 200
        json_data = res_json.get_json()
        assert json_data["success"] is True
        assert json_data["data"]["prediction"] == "SCAM"
        print("  [OK] POST /ai/classify JSON API verified")

        # Test Smart Scanner Integration (renders Checkup + Indicators + AI Analysis!)
        print("\n[TEST 4] Testing Scanner Integration with Module 5 AI Analysis...")
        res_scan = client.post("/scanner/scan", data={
            "message_type": "sms",
            "sender_info": "ALERT-SBI",
            "content": scam_sample
        }, follow_redirects=True)
        assert res_scan.status_code == 200
        assert b"MESSAGE SECURITY CHECKUP" in res_scan.data, "Module 3 Checkup missing in scanner"
        assert b"SCAM INDICATORS FOUND" in res_scan.data, "Module 4 Indicators missing in scanner"
        assert b"AI ANALYSIS" in res_scan.data, "Module 5 AI Analysis missing in scanner"
        assert b"Local DistilBERT" in res_scan.data, "Local DistilBERT model label missing in scanner"
        print("  [OK] Scanner renders Checkup (M3) + Indicators (M4) + AI Analysis (M5) seamlessly!")

    print("\n==================================================")
    print("ALL MODULE 5 UNIT + INTEGRATION TESTS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
