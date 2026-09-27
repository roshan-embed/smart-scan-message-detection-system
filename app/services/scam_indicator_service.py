import re
from app.services.security_checkup_service import SecurityCheckupService

class ScamIndicatorService:
    """
    Business Logic Tier: Module 4 - Scam Indicator Report Engine
    Generates granular threat indicator flags with severity ratings:
    - 🔴 Critical Threat Indicators (Suspicious Link, Urgency, KYC Scam, OTP Request, Account-Blocking Threat)
    - 🟠 Moderate Warning Indicators (Banking Reference, Personal Info Request, Payment/UPI, Prize/Lottery)
    - Aggregates warning count: "X warning signs detected"
    """

    @classmethod
    def generate_report(cls, raw_text: str, checkup: dict = None) -> dict:
        """
        Processes text through SecurityCheckup and extracts specific scam indicators.
        """
        if not checkup:
            checkup = SecurityCheckupService.evaluate(raw_text)

        text_lower = checkup.get("preprocessed_text", raw_text).lower()
        indicators = []

        # 1. Suspicious Link Indicator
        link_check = checkup.get("link_check", {})
        if link_check.get("detected") and link_check.get("is_suspicious"):
            indicators.append({
                "code": "SUSPICIOUS_LINK",
                "label": "Suspicious Link",
                "severity": "critical",
                "icon": "🔴",
                "color_class": "badge-danger",
                "detail": f"Deceptive or suspicious link detected ({', '.join(link_check.get('reasons', [])) or 'unverified external domain'}).",
                "evidence": link_check.get("items", [])[:2]
            })
        elif link_check.get("detected"):
            indicators.append({
                "code": "EXTERNAL_LINK",
                "label": "External Link Present",
                "severity": "warning",
                "icon": "🟠",
                "color_class": "badge-warning",
                "detail": "Contains external web address requiring manual domain verification.",
                "evidence": link_check.get("items", [])[:2]
            })

        # 2. Urgency Indicator
        urgency_check = checkup.get("urgency_check", {})
        if urgency_check.get("detected"):
            indicators.append({
                "code": "URGENCY",
                "label": "Urgency",
                "severity": "critical",
                "icon": "🔴",
                "color_class": "badge-danger",
                "detail": "Artificial time-pressure language intended to bypass rational hesitation.",
                "evidence": urgency_check.get("details", [])[:3]
            })

        # 3. KYC Scam Indicator
        kyc_check = checkup.get("kyc_check", {})
        if kyc_check.get("detected"):
            indicators.append({
                "code": "KYC_REQUEST",
                "label": "KYC Request",
                "severity": "critical",
                "icon": "🔴",
                "color_class": "badge-danger",
                "detail": "Unsolicited mandate to submit or update Know-Your-Customer / identity documents.",
                "evidence": kyc_check.get("details", [])[:3]
            })

        # 4. OTP / PIN Request Indicator
        sensitive_check = checkup.get("sensitive_info_check", {})
        if sensitive_check.get("detected"):
            otp_match = any("otp" in str(x).lower() or "pin" in str(x).lower() or "password" in str(x).lower() for x in sensitive_check.get("details", []))
            if otp_match:
                indicators.append({
                    "code": "OTP_REQUEST",
                    "label": "OTP Request",
                    "severity": "critical",
                    "icon": "🔴",
                    "color_class": "badge-danger",
                    "detail": "Requests confidential authentication tokens (OTP, PIN, Password) which institutions never solicit via message.",
                    "evidence": sensitive_check.get("details", [])[:2]
                })

        # 5. Account-Blocking Threat
        blocking_match = re.search(r"\b(?:blocked|suspended|deactivated|frozen|terminated|closed|disabled)\b", text_lower)
        if blocking_match:
            indicators.append({
                "code": "ACCOUNT_THREAT",
                "label": "Account Threat",
                "severity": "critical" if urgency_check.get("detected") else "warning",
                "icon": "🔴" if urgency_check.get("detected") else "🟠",
                "color_class": "badge-danger" if urgency_check.get("detected") else "badge-warning",
                "detail": f"Threatens imminent account lockout or deactivation: '{blocking_match.group(0)}'.",
                "evidence": [blocking_match.group(0)]
            })

        # 6. Banking Reference
        banking_check = checkup.get("banking_check", {})
        if banking_check.get("detected"):
            indicators.append({
                "code": "BANKING_REFERENCE",
                "label": "Banking Reference",
                "severity": "warning",
                "icon": "🟠",
                "color_class": "badge-warning",
                "detail": f"Explicitly references financial institutions or cards: {', '.join(banking_check.get('details', [])[:2])}.",
                "evidence": banking_check.get("details", [])[:3]
            })

        # 7. Payment / UPI Indicator
        payment_check = checkup.get("payment_upi_check", {})
        if payment_check.get("detected"):
            indicators.append({
                "code": "PAYMENT_UPI",
                "label": "Payment/UPI Indicator",
                "severity": "warning",
                "icon": "🟠",
                "color_class": "badge-warning",
                "detail": "Prompts money transfer, digital wallet action, or UPI transactions.",
                "evidence": payment_check.get("details", [])[:3]
            })

        # 8. Prize / Lottery Indicator
        lottery_match = re.findall(r"\b(?:congratulations|winner|won|lottery|prize|lucky draw|jackpot|bonus)\b", text_lower)
        if lottery_match:
            indicators.append({
                "code": "PRIZE_LOTTERY",
                "label": "Prize/Lottery",
                "severity": "critical",
                "icon": "🔴",
                "color_class": "badge-danger",
                "detail": "Unsolicited reward, winning lottery, or jackpot lure.",
                "evidence": list(dict.fromkeys(lottery_match))[:3]
            })

        # 9. Personal-Information Request
        personal_info_match = re.findall(r"\b(?:aadhaar|pan card|ssn|dob|date of birth|mother's maiden name)\b", text_lower)
        if personal_info_match:
            indicators.append({
                "code": "PERSONAL_INFO",
                "label": "Personal-Information Request",
                "severity": "warning",
                "icon": "🟠",
                "color_class": "badge-warning",
                "detail": "Requests government identification or personally identifiable information (PII).",
                "evidence": list(dict.fromkeys(personal_info_match))[:2]
            })

        # Calculate Warning Signs Count & Overall Assessment
        warning_count = len(indicators)
        critical_count = sum(1 for i in indicators if i["severity"] == "critical")

        if critical_count >= 2 or warning_count >= 4:
            overall_verdict = "HIGH RISK SCAM"
            verdict_badge = "badge-danger"
            verdict_icon = "shield-alert"
        elif warning_count >= 1:
            overall_verdict = "SUSPICIOUS MESSAGE"
            verdict_badge = "badge-warning"
            verdict_icon = "alert-triangle"
        else:
            overall_verdict = "NO WARNING SIGNS DETECTED"
            verdict_badge = "badge-safe"
            verdict_icon = "shield-check"

        return {
            "title": "SCAM INDICATORS FOUND",
            "indicators": indicators,
            "warning_count": warning_count,
            "warning_count_text": f"{warning_count} warning sign{'s' if warning_count != 1 else ''} detected",
            "critical_count": critical_count,
            "overall_verdict": overall_verdict,
            "verdict_badge": verdict_badge,
            "verdict_icon": verdict_icon,
            "checkup": checkup
        }
