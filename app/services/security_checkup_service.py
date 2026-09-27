import re
from app.services.preprocessor_service import PreprocessorService

class SecurityCheckupService:
    """
    Business Logic Tier: Module 3 - Message Security Checkup Engine
    Performs initial multi-vector heuristic screening on incoming messages:
    - Links & URL reputation heuristics
    - Phone number & contact identification
    - Email address detection & validation
    - UPI & digital payment handles
    - Banking & financial institution references
    - Sensitive information requests (OTP, PIN, CVV, passwords)
    - Psychological urgency & coercive threat language
    - Message category classification
    """

    # Comprehensive Indian & International Banking Institutions & Keywords
    BANK_KEYWORDS = [
        "sbi", "hdfc", "icici", "axis", "pnb", "kotak", "canara", "bank of baroda",
        "bob", "indusind", "yes bank", "union bank", "idbi", "central bank",
        "chase", "wells fargo", "bank of america", "citi", "citibank", "barclays",
        "hsbc", "santander", "standard chartered", "rbi", "reserve bank",
        "bank account", "savings account", "current account", "debit card",
        "credit card", "netbanking", "mobile banking", "atm card", "bank branch",
        "account ending in", "a/c no", "a/c", "acct"
    ]

    # UPI Handles & Payment Vectors
    UPI_PATTERNS = [
        r"\b[\w\.\-]+@(okhdfcbank|okaxis|oksbi|okicici|paytm|ybl|apl|upi|ibl|axl|barodampay|pnb|federal)\b",
        r"\b(?:gpay|google pay|phonepe|paytm|bhim upi|bhim|amazon pay|upi id|upi pin|vpa)\b",
        r"\b(?:send money|transfer funds|cashback|refund credit|wire transfer|crypto|usdt|bitcoin|wallet)\b"
    ]

    # Sensitive Information Request Triggers
    SENSITIVE_INFO_PATTERNS = [
        r"\b(?:otp|one time password|verification code|security code)\b",
        r"\b(?:atm pin|upi pin|mpin|secret pin|login pin)\b",
        r"\b(?:cvv|cvv2|card verification value|card security code)\b",
        r"\b(?:password|netbanking password|login credentials|security question)\b",
        r"\b(?:aadhaar|aadhar|ssn|social security|pan card|pan number|credit card number)\b",
        r"\b(?:mother's maiden name|date of birth|dob)\b"
    ]

    # KYC & Account Verification Mandates
    KYC_PATTERNS = [
        r"\b(?:kyc|know your customer|c-kyc|e-kyc)\b",
        r"\b(?:kyc update|update kyc|kyc expired|complete your kyc|kyc verification|submit kyc)\b",
        r"\b(?:aadhaar pan link|pan aadhaar linking|sim kyc|wallet kyc|profile update)\b"
    ]

    # Psychological Urgency & Threat Triggers
    URGENCY_PATTERNS = [
        r"\b(?:urgent|immediately|immediate action|act now|hurry|right now)\b",
        r"\b(?:suspended|suspension|blocked|deactivated|frozen|terminated|closed|disabled)\b",
        r"\b(?:within 24 hours|within 12 hours|within 2 hours|within 24h|today only|expires today)\b",
        r"\b(?:legal action|court notice|police complaint|arrest warrant|penalty|fine)\b",
        r"\b(?:unauthorized access|suspicious activity|security breach|account restricted)\b"
    ]

    # Prize / Lottery / Job Scam Triggers
    LOTTERY_JOB_PATTERNS = [
        r"\b(?:congratulations|you have won|winner|lottery|lucky draw|prize money|jackpot)\b",
        r"\b(?:part-time job|work from home|daily income|daily earnings|review products|earn \$|earn rs|earn \₹)\b",
        r"\b(?:guaranteed returns|instant payout|claim reward|claim bonus)\b"
    ]

    @classmethod
    def evaluate(cls, raw_text: str, metadata: dict = None) -> dict:
        """
        Runs complete Message Security Checkup.
        Returns initial security overview with detected flags and category.
        """
        # Step 1: Normalize through Preprocessor
        preprocessed = PreprocessorService.process(raw_text)
        normalized_text = preprocessed["stage_3_normalize"]["normalized_text"]
        text_lower = normalized_text.lower()

        # Step 2: Detect Links & Evaluate Link Reputation
        extracted_urls = preprocessed["stage_4_entities"]["urls"]
        has_links = len(extracted_urls) > 0
        link_suspicious = False
        link_reasons = []

        for u in extracted_urls:
            if u.get("is_suspicious_tld"):
                link_suspicious = True
                link_reasons.append(f"Suspicious TLD (.{u.get('tld')})")
            if u.get("is_ip_host"):
                link_suspicious = True
                link_reasons.append(f"Raw IP Address Host ({u.get('domain')})")
            if u.get("is_url_shortener"):
                link_suspicious = True
                link_reasons.append(f"URL Shortener obfuscation ({u.get('domain')})")
            
            # Check domain against brand impersonations
            dom = u.get("domain", "")
            if any(b in dom for b in ["sbi", "hdfc", "icici", "paytm", "bank", "secure", "login", "verify", "update"]) and not dom.endswith((".com", ".in", ".org", ".net")):
                link_suspicious = True
                link_reasons.append(f"Deceptive Brand Look-alike ({dom})")

        link_status = "None Found"
        if has_links:
            link_status = "Suspicious" if link_suspicious else "Detected (Review Needed)"

        # Step 3: Identify Phone Numbers
        extracted_phones = preprocessed["stage_4_entities"]["phones"]
        has_phones = len(extracted_phones) > 0

        # Step 4: Identify Email Addresses
        extracted_emails = preprocessed["stage_4_entities"]["emails"]
        has_emails = len(extracted_emails) > 0

        # Step 5: Detect UPI / Payment Information
        has_upi = False
        upi_details = []
        for pat in cls.UPI_PATTERNS:
            matches = re.findall(pat, text_lower)
            if matches:
                has_upi = True
                for m in matches:
                    if isinstance(m, str) and m not in upi_details:
                        upi_details.append(m)

        # Step 6: Identify Banking References
        has_banking = False
        bank_details = []
        for bk in cls.BANK_KEYWORDS:
            if re.search(r"\b" + re.escape(bk) + r"\b", text_lower):
                has_banking = True
                if bk.upper() not in bank_details:
                    bank_details.append(bk.upper())

        # Step 7: Detect KYC Requests
        has_kyc = False
        kyc_details = []
        for pat in cls.KYC_PATTERNS:
            m = re.findall(pat, text_lower)
            if m:
                has_kyc = True
                kyc_details.extend(m)

        # Step 8: Detect Sensitive-Information Requests
        has_sensitive_info = False
        sensitive_details = []
        for pat in cls.SENSITIVE_INFO_PATTERNS:
            m = re.findall(pat, text_lower)
            if m:
                has_sensitive_info = True
                sensitive_details.extend(m)

        # Step 9: Detect Urgency / Threat Language
        has_urgency = False
        urgency_details = []
        for pat in cls.URGENCY_PATTERNS:
            m = re.findall(pat, text_lower)
            if m:
                has_urgency = True
                urgency_details.extend(m)

        # Step 10: Identify Message Category
        category = cls._determine_category(
            has_banking, has_kyc, has_sensitive_info, has_urgency,
            has_upi, text_lower
        )

        return {
            "summary_title": "MESSAGE SECURITY CHECKUP",
            "link_check": {
                "detected": has_links,
                "status": link_status,
                "is_suspicious": link_suspicious,
                "reasons": link_reasons,
                "detected_items": [u.get("raw_url") for u in extracted_urls],
                "urls": [u.get("raw_url") for u in extracted_urls]
            },
            "banking_check": {
                "detected": has_banking,
                "status": "Detected" if has_banking else "Not Detected",
                "details": list(dict.fromkeys(bank_details))
            },
            "kyc_check": {
                "detected": has_kyc,
                "status": "Detected" if has_kyc else "Not Detected",
                "details": list(dict.fromkeys(kyc_details))
            },
            "sensitive_info_check": {
                "detected": has_sensitive_info,
                "status": "Requested" if has_sensitive_info else "None Detected",
                "details": list(dict.fromkeys(sensitive_details))
            },
            "urgency_check": {
                "detected": has_urgency,
                "status": "Detected" if has_urgency else "Normal Pace",
                "details": list(dict.fromkeys(urgency_details))
            },
            "payment_upi_check": {
                "detected": has_upi,
                "status": "Detected" if has_upi else "None Found",
                "details": list(dict.fromkeys(upi_details))
            },
            "phone_check": {
                "detected": has_phones,
                "status": "Identified" if has_phones else "None Found",
                "detected_items": [p.get("raw_phone") for p in extracted_phones],
                "phones": [p.get("raw_phone") for p in extracted_phones]
            },
            "email_check": {
                "detected": has_emails,
                "status": "Identified" if has_emails else "None Found",
                "detected_items": [e.get("email") for e in extracted_emails],
                "emails": [e.get("email") for e in extracted_emails]
            },
            "message_category": category,
            "preprocessed_text": normalized_text
        }

    @classmethod
    def _determine_category(cls, has_banking: bool, has_kyc: bool, has_sensitive: bool,
                            has_urgency: bool, has_upi: bool, text_lower: str) -> str:
        """Determines the overarching scam or functional taxonomy of the message."""
        # Check lottery / prize
        for pat in cls.LOTTERY_JOB_PATTERNS:
            if re.search(pat, text_lower):
                if "job" in text_lower or "earn" in text_lower or "part-time" in text_lower:
                    return "Job Offer & Task Scam"
                return "Lottery & Prize Fraud"

        if has_kyc:
            return "KYC & Verification Fraud"
        if has_banking and (has_sensitive or has_urgency):
            return "Banking Phishing & Account Theft"
        if has_sensitive:
            return "Credential & Identity Harvesting"
        if has_urgency and ("police" in text_lower or "court" in text_lower or "arrest" in text_lower):
            return "Extortion & Legal Threat Scam"
        if has_upi or "money" in text_lower:
            return "UPI & Financial Transfer Solicitation"
        if has_banking:
            return "Banking Reference Notice"

        return "General Inbound Message"
