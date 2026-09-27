import math
from app.services.security_checkup_service import SecurityCheckupService
from app.services.scam_indicator_service import ScamIndicatorService
from app.services.distilbert_service import DistilBertService

class RiskScoringService:
    """
    Business Logic Tier: Module 6 - Risk Assessment & Threat Scoring Engine
    
    Combines:
    1. Scam Indicators (Rule-Based Detection Engine Score out of 100)
    2. AI Prediction (Local DistilBERT Model confidence and classification)
       ↓
    Risk Assessment
       ↓
    Final Risk Score (0–100)
    
    Risk Levels:
    🟢 0–30  — Safe
    🟡 31–60 — Suspicious
    🔴 61–100 — High Risk
    """

    # Rule-based indicator weight matrix
    INDICATOR_WEIGHTS = {
        "SUSPICIOUS_LINK": 25,
        "EXTERNAL_LINK": 10,
        "KYC_REQUEST": 20,
        "OTP_REQUEST": 25,
        "URGENCY": 15,
        "ACCOUNT_THREAT": 15,
        "PRIZE_LOTTERY": 20,
        "BANKING_REFERENCE": 10,
        "PAYMENT_UPI": 10,
        "PERSONAL_INFO": 10
    }

    # Weight distribution for final fusion:
    # Final = round(0.20 * Rule_Score + 0.80 * AI_Score)
    # e.g., Rule 70/100 + AI 91% -> 0.20*70 + 0.80*91 = 14 + 72.8 = 86.8 -> 87/100 (HIGH RISK)
    RULE_WEIGHT = 0.20
    AI_WEIGHT = 0.80

    @classmethod
    def calculate_rule_based_score(cls, indicator_report: dict) -> tuple[int, list[dict]]:
        """
        Calculates the deterministic rule-based threat score (0-100) based on detected indicators.
        Returns total score and granular breakdown of contributing rules.
        """
        indicators = indicator_report.get("indicators", [])
        total_score = 0
        rule_breakdown = []

        for ind in indicators:
            code = ind.get("code", "")
            severity = ind.get("severity", "warning")
            weight = cls.INDICATOR_WEIGHTS.get(code, 15 if severity == "critical" else 10)
            
            total_score += weight
            rule_breakdown.append({
                "code": code,
                "label": ind.get("label", code),
                "severity": severity,
                "icon": ind.get("icon", "🟠"),
                "points": weight,
                "detail": ind.get("detail", "")
            })

        # Clamp rule score to maximum of 100
        clamped_score = min(100, max(0, total_score))
        return clamped_score, rule_breakdown

    @classmethod
    def calculate_ai_threat_score(cls, ai_analysis: dict) -> tuple[int, int, str]:
        """
        Extracts AI prediction, confidence, and maps to an AI threat contribution (0-100).
        """
        prediction = ai_analysis.get("prediction", "SAFE")
        confidence = ai_analysis.get("confidence_score", 50)

        if prediction == "SCAM":
            ai_threat_score = confidence
        else:
            # If AI predicted SAFE with 95% confidence, threat is 5
            ai_threat_score = max(0, 100 - confidence)

        return ai_threat_score, confidence, prediction

    @classmethod
    def determine_risk_level(cls, score: int) -> dict:
        """
        Maps a 0–100 Final Risk Score to strict Risk Levels:
        🟢 0–30  — Safe
        🟡 31–60 — Suspicious
        🔴 61–100 — High Risk
        """
        if score <= 30:
            return {
                "level": "SAFE",
                "label": "Safe",
                "icon": "🟢",
                "badge_class": "badge-safe",
                "color": "#2E7D32",
                "lucide_icon": "shield-check",
                "range_text": "0–30",
                "summary": "Low threat level. No coercive signatures or malicious payloads detected."
            }
        elif score <= 60:
            return {
                "level": "SUSPICIOUS",
                "label": "Suspicious",
                "icon": "🟡",
                "badge_class": "badge-warning",
                "color": "#F9A825",
                "lucide_icon": "alert-triangle",
                "range_text": "31–60",
                "summary": "Moderate threat level. Contains unverified external references or suspicious patterns requiring caution."
            }
        else:
            return {
                "level": "HIGH RISK",
                "label": "High Risk",
                "icon": "🔴",
                "badge_class": "badge-danger",
                "color": "#C62828",
                "lucide_icon": "shield-alert",
                "range_text": "61–100",
                "summary": "Severe threat level! High probability of credential harvesting, fraud, or phishing."
            }

    @classmethod
    def calculate_final_risk(cls, rule_score: int, ai_score: int) -> tuple[int, dict]:
        """
        Pure ensemble fusion function:
        Combines Rule-based score (0-100) + AI score (0-100)
        Formula: round(0.20 * Rule_Score + 0.80 * AI_Score)
        Example from specification:
        Rule-based score: 70/100
        AI confidence:    91%
        Final Risk Score: round(0.20*70 + 0.80*91) = round(14 + 72.8) = 87/100 (HIGH RISK)
        """
        raw_final = (cls.RULE_WEIGHT * rule_score) + (cls.AI_WEIGHT * ai_score)
        final_score = int(round(raw_final))
        final_score = max(0, min(100, final_score))
        risk_level_info = cls.determine_risk_level(final_score)
        return final_score, risk_level_info

    @classmethod
    def assess_risk(cls, raw_text: str, checkup: dict = None, indicator_report: dict = None, ai_analysis: dict = None) -> dict:
        """
        Executes complete Module 6 Threat Level Assessment:
        Takes outputs from detection modules (AI result, Suspicious URL, Urgency, KYC request)
        and converts them into a simple threat level (0-100, Safe, Suspicious, High Risk).
        """
        from app.services.url_sender_verification_service import URLSenderVerificationService
        url_verification = URLSenderVerificationService.verify_message_sources(raw_text)

        # Step 1: Ensure underlying pipeline components are computed
        if not checkup:
            checkup = SecurityCheckupService.evaluate(raw_text)
        if not indicator_report:
            indicator_report = ScamIndicatorService.generate_report(raw_text, checkup)
        if not ai_analysis:
            ai_analysis = DistilBertService.classify(raw_text)

        # Step 2: Compute Rule-Based Score
        rule_score, rule_breakdown = cls.calculate_rule_based_score(indicator_report)

        # Step 3: Compute AI Threat Contribution
        ai_threat_score, ai_confidence, ai_prediction = cls.calculate_ai_threat_score(ai_analysis)

        # Step 4: Calculate Final Risk Score using Ensemble Fusion
        final_risk_score, risk_level_info = cls.calculate_final_risk(rule_score, ai_threat_score)

        # Safety floor for multiple critical factors
        critical_count = indicator_report.get("critical_count", 0)
        has_otp = any(i.get("code") == "OTP_REQUEST" for i in indicator_report.get("indicators", []))
        if (critical_count >= 2 or has_otp) and final_risk_score < 61:
            final_risk_score = 65
            risk_level_info = cls.determine_risk_level(final_risk_score)

        # Step 5: Build Module 6 Contributing Factors (Matching User Specification)
        has_suspicious_url = url_verification.get("has_suspicious_url", False) or any(i.get("code") == "SUSPICIOUS_LINK" for i in indicator_report.get("indicators", []))
        has_urgency = any(i.get("code") == "URGENCY" for i in indicator_report.get("indicators", []))
        has_kyc = any(i.get("code") == "KYC_REQUEST" for i in indicator_report.get("indicators", []))

        contributing_factors = [
            {
                "factor": "AI result",
                "value": f"{ai_confidence}%" if ai_prediction == "SCAM" else f"{ai_confidence}% ({ai_prediction})",
                "triggered": ai_prediction in ["SCAM", "SUSPICIOUS"],
                "icon": "cpu",
                "severity": "critical" if ai_prediction == "SCAM" else ("warning" if ai_prediction == "SUSPICIOUS" else "safe")
            },
            {
                "factor": "Suspicious URL",
                "value": "Yes" if has_suspicious_url else ("No URLs detected" if not url_verification["urls"] else "No (Verified HTTPS)"),
                "triggered": has_suspicious_url,
                "icon": "globe",
                "severity": "critical" if has_suspicious_url else "safe"
            },
            {
                "factor": "Urgency",
                "value": "Yes" if has_urgency else "No",
                "triggered": has_urgency,
                "icon": "zap",
                "severity": "warning" if has_urgency else "safe"
            },
            {
                "factor": "KYC request",
                "value": "Yes" if has_kyc else "No",
                "triggered": has_kyc,
                "icon": "file-text",
                "severity": "critical" if has_kyc else "safe"
            }
        ]

        # Step 6: Generate Safety Recommendations
        recommendations = []
        if risk_level_info["level"] == "HIGH RISK":
            recommendations.append("Do NOT click any web links or download attachments.")
            recommendations.append("NEVER share OTPs, PINs, passwords, or personal banking credentials.")
            recommendations.append("Block the sender and report to national cybercrime reporting portal (e.g. cybercrime.gov.in / 1930).")
        elif risk_level_info["level"] == "SUSPICIOUS":
            recommendations.append("Verify sender identity directly through official corporate website or verified app.")
            recommendations.append("Inspect web addresses manually before interacting.")
            recommendations.append("Do not make immediate payments or transfer funds under time pressure.")
        else:
            recommendations.append("Message appears benign and consistent with normal communication.")
            recommendations.append("Standard digital hygiene and vigilance always recommended.")

        return {
            "title": "RISK ASSESSMENT & THREAT SCORING",
            "rule_based_score": rule_score,
            "rule_breakdown": rule_breakdown,
            "ai_confidence": ai_confidence,
            "ai_prediction": ai_prediction,
            "ai_threat_score": ai_threat_score,
            "fusion_formula": f"round({cls.RULE_WEIGHT} × {rule_score} + {cls.AI_WEIGHT} × {ai_threat_score})",
            "final_risk_score": final_risk_score,
            "risk_level": risk_level_info["level"],
            "risk_label": risk_level_info["label"],
            "risk_icon": risk_level_info["icon"],
            "risk_badge": risk_level_info["badge_class"],
            "risk_color": risk_level_info["color"],
            "lucide_icon": risk_level_info["lucide_icon"],
            "risk_summary": risk_level_info["summary"],
            "recommendations": recommendations,
            "contributing_factors": contributing_factors,
            "url_verification": url_verification,
            "checkup": checkup,
            "indicator_report": indicator_report,
            "ai_analysis": ai_analysis
        }
