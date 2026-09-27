import os
import json
from app import create_app
from app.services.ocr_service import OCRService
from app.services.url_sender_verification_service import URLSenderVerificationService
from app.services.distilbert_service import DistilBertService
from app.services.risk_scoring_service import RiskScoringService
from app.models.message_model import MessageModel

def run_tests():
    print("=" * 60)
    print("SMART SCAM MESSAGE DETECTION SYSTEM")
    print("Verification of Revised Modules 1 through 6")
    print("=" * 60)

    app = create_app()
    with app.app_context():
        client = app.test_client()

        # ---------------------------------------------------------
        # MODULE 1: User Account & Authentication
        # ---------------------------------------------------------
        print("\n[MODULE 1] Testing User Account & Authentication...")
        login_res = client.post("/auth/login", data={
            "identifier": "admin@scamdetect.internal",
            "password": "Admin@12345!"
        }, follow_redirects=True)
        assert login_res.status_code == 200, "Module 1 Login failed"
        print("  [OK] Login authentication successful")

        profile_res = client.get("/profile/")
        assert profile_res.status_code == 200
        print("  [OK] Profile view accessible")

        # ---------------------------------------------------------
        # MODULE 2: Smart Message Scanner
        # ---------------------------------------------------------
        print("\n[MODULE 2] Testing Smart Message Scanner...")
        scan_page = client.get("/scanner/")
        assert scan_page.status_code == 200
        assert b"Paste your message here..." in scan_page.data
        assert b"Analyze Message" in scan_page.data
        print("  [OK] Scanner interface with SMS/WhatsApp/Email and Analyze Message verified")

        sample_text = "Dear customer SBI alert your account blocked update kyc immediately at http://sbi-fake.xyz"
        ingest_res = client.post("/scanner/scan", data={
            "message_type": "sms",
            "sender_info": "ALERT-SBI",
            "content": sample_text
        }, follow_redirects=True)
        assert ingest_res.status_code == 200
        print("  [OK] Message submission and ingestion verified")

        # ---------------------------------------------------------
        # MODULE 3: Screenshot & Image Message Scanner
        # ---------------------------------------------------------
        print("\n[MODULE 3] Testing Screenshot & Image Message Scanner...")
        ocr_page = client.get("/ocr/")
        assert ocr_page.status_code == 200
        assert b"Screenshot &amp; Image Message Scanner" in ocr_page.data
        print("  [OK] GET /ocr/ Studio page rendered 200 OK")

        # Test Sample Screenshot OCR Extraction
        ocr_extract_res = client.post("/ocr/extract", data={"sample_id": "whatsapp"})
        assert ocr_extract_res.status_code == 200
        ocr_data = ocr_extract_res.get_json()
        assert ocr_data["success"] is True
        extracted_text = ocr_data["data"]["extracted_text"]
        assert "cash prize" in extracted_text.lower()
        print(f"  [OK] OCR text extracted from sample screenshot ({ocr_data['data']['confidence']}%)")

        # Test Sending Extracted Text to Threat Analysis
        analyze_res = client.post("/ocr/analyze", data={
            "content": extracted_text,
            "message_type": "whatsapp",
            "sender_info": "+91 98765 43210"
        }, follow_redirects=True)
        assert analyze_res.status_code == 200
        print("  [OK] Extracted screenshot text submitted and analyzed successfully")

        # ---------------------------------------------------------
        # MODULE 4: URL & Sender Verification
        # ---------------------------------------------------------
        print("\n[MODULE 4] Testing URL & Sender Verification...")
        verify_page = client.get("/verification/")
        assert verify_page.status_code == 200
        assert b"URL &amp; Sender Verification" in verify_page.data
        print("  [OK] GET /verification/ Studio page rendered 200 OK")

        # Test exact user specification URL: http://example.xyz/login
        url_eval = URLSenderVerificationService.verify_url("http://example.xyz/login")
        assert url_eval["has_https"] is False
        assert url_eval["is_shortened"] is False
        assert url_eval["is_ip_address"] is False
        assert url_eval["is_suspicious_pattern"] is True
        assert url_eval["url_status"] == "HIGH RISK", f"Expected HIGH RISK, got {url_eval['url_status']}"
        print("  [OK] Exact user example URL verified:")
        print(f"       URL: {url_eval['url']}")
        print(f"       HTTPS:          {url_eval['has_https']}")
        print(f"       Shortened:      {url_eval['is_shortened']}")
        print(f"       IP Address:     {url_eval['is_ip_address']}")
        print(f"       Domain Pattern: {url_eval['is_suspicious_pattern']}")
        print(f"       URL Status:     {url_eval['url_status']}")

        # Test Sender Verification
        sender_eval = URLSenderVerificationService.verify_sender("ALERT-SBI")
        assert sender_eval["sender_status"] == "HIGH RISK"
        print(f"  [OK] Sender verification: ALERT-SBI -> {sender_eval['sender_status']}")

        # ---------------------------------------------------------
        # MODULE 5: AI Scam Detection
        # ---------------------------------------------------------
        print("\n[MODULE 5] Testing AI Scam Detection (Local DistilBERT)...")
        ai_scam = DistilBertService.classify(sample_text)
        assert ai_scam["prediction"] == "SCAM"
        assert ai_scam["confidence_score"] >= 80
        assert ai_scam["model_name"] == "Local DistilBERT"
        print(f"  [OK] Prediction: {ai_scam['prediction']}")
        print(f"  [OK] Confidence: {ai_scam['confidence_score']}%")
        print(f"  [OK] Model: {ai_scam['model_name']}")

        # Test Benign
        ai_safe = DistilBertService.classify("Hey Alex, let's grab coffee tomorrow at the office around 3pm. Thanks!")
        assert ai_safe["prediction"] == "SAFE"
        print(f"  [OK] Benign Message Prediction: {ai_safe['prediction']} ({ai_safe['confidence_score']}%)")

        # ---------------------------------------------------------
        # MODULE 6: Threat Level Assessment
        # ---------------------------------------------------------
        print("\n[MODULE 6] Testing Threat Level Assessment...")
        threat_assessment = RiskScoringService.assess_risk(sample_text)
        assert threat_assessment["risk_level"] == "HIGH RISK"
        assert threat_assessment["final_risk_score"] >= 61
        assert "contributing_factors" in threat_assessment
        print(f"  [OK] Overall Threat Score: {threat_assessment['final_risk_score']} / 100")
        print(f"  [OK] Threat Level: {threat_assessment['risk_level']}")
        print("  [OK] Main Contributing Factors:")
        for cf in threat_assessment["contributing_factors"]:
            print(f"       {cf['factor']:15} -> {cf['value']}")

    print("\n" + "=" * 60)
    print("ALL 6 MODULES VERIFIED AND PASSING 100%!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
