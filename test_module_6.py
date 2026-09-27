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
from app.services.risk_scoring_service import RiskScoringService

def run_tests():
    print("==================================================")
    print("SMART SCAM MESSAGE DETECTION SYSTEM")
    print("Testing Module 6: Risk Assessment & Threat Scoring 📊")
    print("==================================================")

    # 1. Test Exact User Specification Example:
    # Rule-based score: 70/100, AI confidence: 91% -> Final Risk Score: 87/100, HIGH RISK
    print("\n[TEST 1] Testing Exact User Specification Mathematical Ensemble Formula...")
    final_score, risk_info = RiskScoringService.calculate_final_risk(rule_score=70, ai_score=91)
    print(f"  Rule Score : 70/100")
    print(f"  AI Score   : 91%")
    print(f"  Final Score: {final_score}/100")
    print(f"  Risk Level : {risk_info['icon']} {risk_info['level']}")

    assert final_score == 87, f"Expected Final Risk Score 87, got {final_score}"
    assert risk_info["level"] == "HIGH RISK", f"Expected HIGH RISK, got {risk_info['level']}"
    print("  [OK] Exact user specification (70 Rule + 91% AI -> 87/100 Final Risk Score, HIGH RISK) verified!")

    # 1B. Test End-to-End assess_risk on Banking KYC Scam message
    kyc_sample = (
        "Dear customer, your SBI NetBanking a/c is blocked due to incomplete KYC. "
        "Verify now at http://sbi-kyc-update.xyz within 24 hours to avoid permanent suspension. "
        "Call +91 98765 43210."
    )
    print("\n[TEST 1B] Testing End-to-End assess_risk on Banking KYC Scam...")
    res_kyc = RiskScoringService.assess_risk(kyc_sample)

    print(f"  Rule-based score : {res_kyc['rule_based_score']}/100")
    print(f"  AI Prediction    : {res_kyc['ai_prediction']} ({res_kyc['ai_confidence']}%)")
    print(f"  Final Risk Score : {res_kyc['final_risk_score']}/100")
    print(f"  Risk Level       : {res_kyc['risk_icon']} {res_kyc['risk_level']}")
    print(f"  Formula          : {res_kyc['fusion_formula']}")
    print(f"  Rule Factors     : {[f['label'] + ' (+' + str(f['points']) + ')' for f in res_kyc['rule_breakdown']]}")

    assert res_kyc["rule_based_score"] >= 60, f"Expected rule score >= 60, got {res_kyc['rule_based_score']}"
    assert res_kyc["ai_prediction"] == "SCAM", f"Expected AI prediction SCAM, got {res_kyc['ai_prediction']}"
    assert res_kyc["final_risk_score"] >= 61, f"Expected Final Risk Score >= 61, got {res_kyc['final_risk_score']}"
    assert res_kyc["risk_level"] == "HIGH RISK", f"Expected HIGH RISK, got {res_kyc['risk_level']}"
    print("  [OK] Banking KYC Scam classified as HIGH RISK successfully!")

    # 2. Test Safe Risk Level (0–30 Safe) on Benign Message
    safe_sample = (
        "Hey Rahul, let's meet for lunch at the office cafeteria around 1pm tomorrow to discuss the project presentation. Thanks!"
    )
    print("\n[TEST 2] Testing Safe Risk Level (0–30) on Benign Message...")
    res_safe = RiskScoringService.assess_risk(safe_sample)

    print(f"  Rule-based score : {res_safe['rule_based_score']}/100")
    print(f"  AI Prediction    : {res_safe['ai_prediction']} ({res_safe['ai_confidence']}%)")
    print(f"  Final Risk Score : {res_safe['final_risk_score']}/100")
    print(f"  Risk Level       : {res_safe['risk_icon']} {res_safe['risk_level']}")

    assert res_safe["rule_based_score"] == 0, f"Expected rule score 0, got {res_safe['rule_based_score']}"
    assert res_safe["final_risk_score"] <= 30, f"Expected final score <= 30, got {res_safe['final_risk_score']}"
    assert res_safe["risk_level"] == "SAFE", f"Expected SAFE, got {res_safe['risk_level']}"
    print("  [OK] Safe Risk Level (0–30) verified!")

    # 3. Test Risk Level Thresholds:
    # 🟢 0–30 — Safe
    # 🟡 31–60 — Suspicious
    # 🔴 61–100 — High Risk
    print("\n[TEST 3] Testing Risk Level Boundaries...")
    assert RiskScoringService.determine_risk_level(0)["level"] == "SAFE"
    assert RiskScoringService.determine_risk_level(30)["level"] == "SAFE"
    assert RiskScoringService.determine_risk_level(31)["level"] == "SUSPICIOUS"
    assert RiskScoringService.determine_risk_level(60)["level"] == "SUSPICIOUS"
    assert RiskScoringService.determine_risk_level(61)["level"] == "HIGH RISK"
    assert RiskScoringService.determine_risk_level(100)["level"] == "HIGH RISK"
    print("  [OK] All risk tier boundaries (0-30, 31-60, 61-100) verified!")

    # 4. Test Flask HTTP Controller Routes
    print("\n[TEST 4] Testing Flask HTTP /risk/ Endpoints...")
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

        # GET /risk/
        res_get = client.get("/risk/")
        assert res_get.status_code == 200, f"GET /risk/ failed with {res_get.status_code}"
        assert b"Risk Assessment &amp; Threat Scoring" in res_get.data, "Header missing in /risk/"
        print("  [OK] GET /risk/ returned 200 OK")

        # POST /risk/assess (Form POST)
        res_post = client.post("/risk/assess", data={"text": kyc_sample})
        assert res_post.status_code == 200, f"POST /risk/assess failed with {res_post.status_code}"
        assert b"RISK ASSESSMENT &amp; THREAT SCORING" in res_post.data or b"Risk Assessment" in res_post.data
        assert b"HIGH RISK" in res_post.data, "Expected HIGH RISK in HTML"
        print("  [OK] POST /risk/assess returned 200 OK with rendered Risk Score card (HIGH RISK)")

        # POST /risk/assess (JSON API)
        res_json = client.post("/risk/assess", json={"text": kyc_sample})
        assert res_json.status_code == 200
        json_data = res_json.get_json()
        assert json_data["success"] is True
        assert json_data["data"]["final_risk_score"] >= 61
        assert json_data["data"]["risk_level"] == "HIGH RISK"
        assert json_data["data"]["rule_based_score"] >= 60
        print("  [OK] POST /risk/assess JSON API verified")

        # 5. Test Smart Scanner Integration with Module 6
        print("\n[TEST 5] Testing Scanner Ingestion with Module 6 Risk Assessment...")
        res_scan = client.post("/scanner/scan", data={
            "message_type": "sms",
            "sender_info": "ALERT-SBI",
            "content": kyc_sample
        }, follow_redirects=True)
        assert res_scan.status_code == 200
        assert b"RISK ASSESSMENT &amp; THREAT SCORING" in res_scan.data
        assert b"HIGH RISK" in res_scan.data
        print("  [OK] Scanner renders Risk Assessment (M6) + AI (M5) + Indicators (M4) + Checkup (M3) seamlessly!")

    print("\n==================================================")
    print("ALL MODULE 6 UNIT + INTEGRATION TESTS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
