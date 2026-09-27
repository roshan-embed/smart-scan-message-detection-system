import re
import unicodedata
from app.models.message_model import MessageModel
from app.services.security_checkup_service import SecurityCheckupService
from app.services.scam_indicator_service import ScamIndicatorService
from app.services.distilbert_service import DistilBertService
from app.services.risk_scoring_service import RiskScoringService

class ScannerService:
    """
    Business Logic Tier: Smart Message Scanner Service
    Handles message validation, sanitization, metadata/entity extraction,
    and preparation for upcoming detection engines (Rule-Engine + DistilBERT).
    """

    # Common urgent scam triggers
    URGENCY_KEYWORDS = [
        "urgent", "immediately", "immediate action", "suspended", "suspension",
        "blocked", "deactivated", "expire", "expires", "24 hours", "12 hours",
        "verify now", "security alert", "unauthorized", "kyc update", "winner",
        "lottery", "claim now", "refund", "tax refund", "prize", "restricted",
        "compromised", "otp", "wire transfer", "crypto", "usdt"
    ]

    @staticmethod
    def sanitize_text(text: str) -> str:
        """
        Cleans and normalizes incoming message text:
        - Removes zero-width characters and invisible control codepoints.
        - Normalizes Unicode representations (NFKC).
        - Strips extraneous leading/trailing whitespace.
        """
        if not text:
            return ""

        # Normalize unicode to NFKC to resolve deceptive homoglyphs
        normalized = unicodedata.normalize("NFKC", text)

        # Remove zero-width characters (ZWSP, ZWNJ, ZWJ, BOM)
        zero_width_pattern = r"[\u200B\u200C\u200D\uFEFF\u00AD]"
        sanitized = re.sub(zero_width_pattern, "", normalized)

        return sanitized.strip()

    @staticmethod
    def extract_urls(text: str) -> list[str]:
        """
        Extracts web links, domains, and IP addresses embedded in text.
        """
        if not text:
            return []
        
        # Comprehensive URL regex (matches http, https, www, shorteners, and raw domain patterns)
        url_pattern = r"(?:https?:\/\/|www\.)[^\s<>{}\[\]]+|(?:[a-zA-Z0-9-]+\.)+(?:com|org|net|xyz|info|top|online|ru|cn|biz|me|live|cc|tk|ml|ga|cf|gq)(?:\/[^\s<>{}\[\]]*)?"
        matches = re.findall(url_pattern, text, re.IGNORECASE)
        
        # Deduplicate while preserving order
        unique_urls = []
        for u in matches:
            cleaned = u.rstrip(".,;!?:)'\"")
            if cleaned and cleaned not in unique_urls:
                unique_urls.append(cleaned)
        return unique_urls

    @staticmethod
    def extract_phone_numbers(text: str) -> list[str]:
        """
        Extracts telephone numbers and international dialing formats.
        """
        if not text:
            return []
        
        phone_pattern = r"(?:\+?\d{1,4}[ -]?)?(?:\(?\d{2,5}\)?[ -]?)?\d{3,5}[ -]?\d{3,5}"
        candidates = re.findall(phone_pattern, text)
        phones = []
        for c in candidates:
            c_clean = c.strip()
            digits_only = re.sub(r"\D", "", c_clean)
            if 7 <= len(digits_only) <= 15:
                if c_clean not in phones:
                    phones.append(c_clean)
        return phones

    @staticmethod
    def extract_emails(text: str) -> list[str]:
        """Extracts email addresses from text."""
        if not text:
            return []
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        matches = re.findall(email_pattern, text)
        return list(dict.fromkeys(matches))

    @classmethod
    def detect_urgency(cls, text: str) -> tuple[bool, list[str]]:
        """Detects whether text contains high-urgency psychological scam pressure."""
        text_lower = text.lower()
        found_triggers = []
        for kw in cls.URGENCY_KEYWORDS:
            if re.search(r"\b" + re.escape(kw) + r"\b", text_lower):
                found_triggers.append(kw)
        return len(found_triggers) > 0, found_triggers

    @staticmethod
    def calculate_metrics(text: str) -> dict:
        """
        Calculates character, word, and SMS segment counts.
        """
        char_count = len(text)
        words = text.split()
        word_count = len(words)
        # 160 characters per standard GSM-7 SMS segment
        sms_segments = 1 if char_count <= 160 else (char_count + 152) // 153

        return {
            "char_count": char_count,
            "word_count": word_count,
            "sms_segments": sms_segments
        }

    @classmethod
    def validate_message(cls, raw_content: str, message_type: str) -> tuple[bool, str]:
        """Validates message submission parameters."""
        if not raw_content or not raw_content.strip():
            return False, "Message content cannot be empty. Please paste an SMS, WhatsApp message, or Email."

        if len(raw_content) > 10000:
            return False, "Message length exceeds the maximum limit of 10,000 characters."

        valid_types = ["sms", "whatsapp", "email", "general"]
        if message_type.lower() not in valid_types:
            return False, f"Invalid message channel type: '{message_type}'."

        return True, ""

    @classmethod
    def ingest_message(cls, user_id: int, form_data: dict) -> tuple[bool, str, dict | None]:
        """
        Validates, sanitizes, extracts entities, and persists an ingested message.
        """
        raw_content = form_data.get("content", "")
        message_type = form_data.get("message_type", "sms").lower()
        sender_info = form_data.get("sender_info", "")
        subject = form_data.get("subject", "")

        # 1. Validation
        is_valid, err_msg = cls.validate_message(raw_content, message_type)
        if not is_valid:
            return False, err_msg, None

        # 2. Text Sanitization
        sanitized = cls.sanitize_text(raw_content)

        # 3. Entity & Metadata Extraction
        metrics = cls.calculate_metrics(sanitized)
        extracted_urls = cls.extract_urls(sanitized)
        extracted_phones = cls.extract_phone_numbers(sanitized)
        extracted_emails = cls.extract_emails(sanitized)
        has_urgency, urgency_triggers = cls.detect_urgency(sanitized)

        # 4. Run Modules: M3 (Security Checkup), M4 (Scam Indicators), M5 (DistilBERT AI), M6 (Risk Scoring)
        checkup = SecurityCheckupService.evaluate(sanitized)
        indicator_report = ScamIndicatorService.generate_report(sanitized, checkup)
        ai_analysis = DistilBertService.classify(sanitized)
        risk_assessment = RiskScoringService.assess_risk(
            sanitized,
            checkup=checkup,
            indicator_report=indicator_report,
            ai_analysis=ai_analysis
        )
        threat_verdict = f"{risk_assessment['risk_level']} ({risk_assessment['final_risk_score']}/100)"

        # 5. Save to Persistent Store
        try:
            msg_id = MessageModel.create(
                user_id=user_id,
                message_type=message_type,
                sender_info=sender_info,
                subject=subject if message_type == "email" else None,
                raw_content=raw_content,
                sanitized_content=sanitized,
                char_count=metrics["char_count"],
                word_count=metrics["word_count"],
                extracted_urls=extracted_urls,
                extracted_phones=extracted_phones,
                extracted_emails=extracted_emails,
                has_urgency=has_urgency,
                threat_verdict=threat_verdict
            )

            result = {
                "id": msg_id,
                "message_type": message_type,
                "sender_info": sender_info,
                "subject": subject,
                "raw_content": raw_content,
                "sanitized_content": sanitized,
                "metrics": metrics,
                "extracted_urls": extracted_urls,
                "extracted_phones": extracted_phones,
                "extracted_emails": extracted_emails,
                "has_urgency": has_urgency,
                "urgency_triggers": urgency_triggers,
                "threat_verdict": threat_verdict,
                "checkup": checkup,
                "indicator_report": indicator_report,
                "ai_analysis": ai_analysis,
                "risk_assessment": risk_assessment
            }

            return True, "Message scanned and ingested successfully!", result
        except Exception as e:
            return False, f"Failed to ingest message: {str(e)}", None

    @staticmethod
    def get_sample_templates() -> dict:
        """
        Provides realistic sample scam messages for SMS, WhatsApp, and Email.
        """
        return {
            "sms": {
                "sender": "+1 (800) 555-0199 [ALERT-SEC]",
                "content": "URGENT: Your bank account ending in #4092 has been temporarily suspended due to unusual activity. Please verify your identity immediately within 24 hours to prevent permanent closure: https://secure-bank-login-verify.xyz/auth?id=9842"
            },
            "whatsapp": {
                "sender": "+44 7911 123456 (Global Career Recruitment)",
                "content": "*Forwarded many times*\n🎉 Congratulations! You have been selected for an online remote job earning $300-$800 daily by simply rating travel bookings. No technical skills required! Instant daily withdrawal via USDT or Bank transfer.\n\nTo claim your $50 signup bonus, contact our hiring manager on WhatsApp: +44 7911 987654 or click http://t.me/GlobalHR_Career_Recruit now!"
            },
            "email": {
                "sender": "security-alert@service-security-update.net",
                "subject": "ACTION REQUIRED: Unauthorized sign-in attempt detected",
                "content": "Dear Customer,\n\nWe detected an unauthorized sign-in attempt to your account from IP address 194.26.29.112 (Moscow, Russia) on September 27, 2026.\n\nFor your security, we have temporarily restricted access to all transaction features. If this was not you, confirm your credentials immediately to avoid permanent deactivation:\n\n👉 Confirm Credentials: http://account-protection-portal.com/update-auth\n\nFailure to verify within 12 hours will result in permanent account restriction.\n\nSincerely,\nSecurity Fraud Prevention Center"
            }
        }
