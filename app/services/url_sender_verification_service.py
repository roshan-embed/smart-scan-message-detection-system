import re
from urllib.parse import urlparse

class URLSenderVerificationService:
    """
    Module 4: URL & Sender Verification 🔗
    Business Logic Tier Service
    
    Investigates who/where the message is coming from, independent of message text:
    - URL Analysis: HTTPS check, Shortened URL detection, IP-based URL detection, Domain pattern analysis
    - Sender Analysis: Phone number format, Email format, Header authenticity, Unknown sender warning
    """

    KNOWN_SHORTENERS = {
        "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", 
        "buff.ly", "cutt.ly", "rb.gy", "rebrand.ly", "shorturl.at",
        "qr.ae", "trib.al", "tiny.cc", "soo.gd", "s.id", "bl.ink"
    }

    HIGH_RISK_TLDS = {
        "xyz", "top", "online", "site", "club", "buzz", "ru", "cn", "live", 
        "tk", "ml", "ga", "cf", "gq", "work", "loan", "win", "stream", "bid", "vip"
    }

    TARGETED_BRANDS = [
        "sbi", "hdfc", "icici", "pnb", "bob", "axis", "paytm", "phonepe", 
        "gpay", "google", "apple", "netflix", "amazon", "income-tax", "uidai", "kyc"
    ]

    FREE_EMAIL_PROVIDERS = {
        "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "rediffmail.com", "aol.com"
    }

    @classmethod
    def verify_url(cls, raw_url: str) -> dict:
        """
        Inspects a specific URL against cybersecurity indicators.
        Matches the exact output specification:
        HTTPS:          ❌ / ✓
        Shortened:      ❌ / ✓
        IP Address:     ❌ / ✓
        Domain Pattern: ⚠ Suspicious / ✓ Benign
        URL Status:     HIGH RISK / SUSPICIOUS / SAFE
        """
        if not raw_url or not raw_url.strip():
            return None

        url = raw_url.strip()
        if not url.startswith(("http://", "https://")):
            # Prepend http:// for parsing if scheme missing
            parsed = urlparse("http://" + url)
            has_scheme = False
        else:
            parsed = urlparse(url)
            has_scheme = True

        scheme = parsed.scheme.lower() if has_scheme else "none"
        has_https = (scheme == "https")
        netloc = parsed.netloc.lower() or parsed.path.lower().split("/")[0]

        # Strip port if present
        host = netloc.split(":")[0]

        # 1. IP Address Check
        ip_pattern = r"^(?:\d{1,3}\.){3}\d{1,3}$"
        is_ip_address = bool(re.match(ip_pattern, host))

        # 2. Shortened URL Detection
        is_shortened = any(host == s or host.endswith("." + s) for s in cls.KNOWN_SHORTENERS)

        # 3. Domain Analysis & TLD Check
        parts = host.split(".")
        tld = parts[-1] if len(parts) > 1 else ""
        is_high_risk_tld = tld in cls.HIGH_RISK_TLDS

        # 4. Domain Patterns (Brand Spoofing, Hyphen-heavy, Subdomain flooding)
        domain_patterns = []
        is_suspicious_pattern = False

        if is_high_risk_tld:
            domain_patterns.append(f"High-risk TLD (.{tld}) with high fraud prevalence")
            is_suspicious_pattern = True

        # Check for brand spoofing (e.g. sbi-kyc-update.xyz or netbanking-hdfc.com)
        found_brands = [b for b in cls.TARGETED_BRANDS if b in host]
        if found_brands and not any(host.endswith(f".{b}.co.in") or host.endswith(f".{b}.com") for b in found_brands):
            domain_patterns.append(f"Impersonation keyword detected: '{found_brands[0].upper()}' in unverified domain")
            is_suspicious_pattern = True

        # Excessive hyphens (common scam tactic to look official)
        if host.count("-") >= 2:
            domain_patterns.append(f"Excessive hyphenation ({host.count('-')} hyphens)")
            is_suspicious_pattern = True

        # Subdomain nesting (e.g. secure.login.bank.sbi.fake-site.com)
        if len(parts) >= 4 and not is_ip_address:
            domain_patterns.append(f"Multi-level nested subdomains ({len(parts)} segments)")
            is_suspicious_pattern = True

        # 5. Compute Final URL Status
        risk_points = 0
        if not has_https:
            risk_points += 25
        if is_ip_address:
            risk_points += 40
        if is_shortened:
            risk_points += 30
        if is_suspicious_pattern:
            risk_points += 40

        if risk_points >= 40:
            url_status = "HIGH RISK"
            status_badge = "badge-danger"
            status_color = "#EF4444"
        elif risk_points >= 20:
            url_status = "SUSPICIOUS"
            status_badge = "badge-warning"
            status_color = "#F59E0B"
        else:
            url_status = "SAFE"
            status_badge = "badge-safe"
            status_color = "#10B981"

        return {
            "url": raw_url,
            "domain": host,
            "tld": tld,
            "has_https": has_https,
            "https_display": "✓ Secure (HTTPS)" if has_https else "❌ Not Secure (HTTP)",
            "https_icon": "check" if has_https else "x",
            "is_shortened": is_shortened,
            "shortened_display": "⚠ Yes (Masked Destination)" if is_shortened else "✓ No (Direct URL)",
            "shortened_icon": "alert-triangle" if is_shortened else "check",
            "is_ip_address": is_ip_address,
            "ip_display": "⚠ Yes (Raw IP Hostname)" if is_ip_address else "✓ No (Registered Domain)",
            "ip_icon": "alert-triangle" if is_ip_address else "check",
            "is_suspicious_pattern": is_suspicious_pattern,
            "pattern_display": "⚠ Suspicious" if is_suspicious_pattern else "✓ Benign",
            "domain_patterns": domain_patterns if domain_patterns else ["Standard domain structure"],
            "url_status": url_status,
            "status_badge": status_badge,
            "status_color": status_color,
            "risk_points": risk_points
        }

    @classmethod
    def verify_sender(cls, sender_info: str, channel: str = "sms") -> dict:
        """
        Inspects message sender attributes:
        - Phone number format & virtual VoIP indicators
        - Email domain & spoofing risk
        - Alphanumeric header authenticity (e.g. ALERT-SBI)
        - Unknown sender warning
        """
        if not sender_info or not sender_info.strip():
            return {
                "sender_raw": "Unknown / Unspecified",
                "sender_type": "Unknown",
                "unknown_sender_warning": True,
                "warning_message": "Sender identity missing or suppressed",
                "sender_status": "SUSPICIOUS",
                "status_badge": "badge-warning",
                "details": ["Sender identity was not provided with message"]
            }

        sender = sender_info.strip()
        details = []
        is_unknown = False
        is_suspicious = False

        # 1. Email Sender Check
        if "@" in sender:
            sender_type = "Email Address"
            parts = sender.split("@")
            domain = parts[1].lower() if len(parts) > 1 else ""
            
            # Check free email claiming official bank/gov business
            if domain in cls.FREE_EMAIL_PROVIDERS:
                details.append(f"Consumer free webmail provider (@{domain}) used for official business")
                is_suspicious = True
            elif any(domain.endswith("." + t) for t in cls.HIGH_RISK_TLDS):
                details.append(f"High-risk domain extension (@{domain})")
                is_suspicious = True
            else:
                details.append(f"Domain: {domain} (Standard corporate/business mail format)")

        # 2. Phone Number Check
        elif re.search(r"\d{7,}", sender.replace(" ", "").replace("-", "")):
            sender_type = "Phone Number"
            digits = re.sub(r"\D", "", sender)
            if sender.startswith("+"):
                details.append("International dialing prefix format verified")
            if len(digits) == 10:
                details.append("10-digit mobile number format")
            elif len(digits) > 10:
                details.append(f"International telephone format ({len(digits)} digits)")
            
            # Unsaved personal number posing as institution
            details.append("Personal unverified mobile number (Institutions use alphanumeric headers)")

        # 3. Alphanumeric Header (e.g. ALERT-SBI, VK-HDFCBK)
        else:
            sender_type = "Alphanumeric Header"
            # In India / TRAI, legitimate headers have 2-letter prefix + hyphen + 6-letter sender e.g. VK-SBIINB
            header_pattern = r"^[A-Za-z]{2}-[A-Za-z0-9]{6}$"
            if re.match(header_pattern, sender):
                details.append("Standard telecom regulated sender header format (e.g. VK-SBIINB)")
            else:
                details.append("Non-standard / unverified custom sender string (High spoofing risk)")
                is_suspicious = True

        sender_status = "HIGH RISK" if is_suspicious else "SAFE"
        return {
            "sender_raw": sender,
            "sender_type": sender_type,
            "unknown_sender_warning": is_unknown,
            "sender_status": sender_status,
            "status_badge": "badge-danger" if is_suspicious else "badge-safe",
            "details": details
        }

    @classmethod
    def verify_message_sources(cls, text: str, sender_info: str = "") -> dict:
        """
        Comprehensive extraction and verification of all URLs and Senders found in a message.
        """
        # Extract URLs
        url_pattern = r"(?:https?:\/\/|www\.)[^\s<>{}\[\]]+|(?:[a-zA-Z0-9-]+\.)+(?:com|org|net|xyz|info|top|online|ru|cn|biz|me|live|cc|tk|ml|ga|cf|gq)(?:\/[^\s<>{}\[\]]*)?"
        found_urls = re.findall(url_pattern, text or "")
        
        verified_urls = []
        for u in set(found_urls):
            clean_u = u.rstrip(".,;!?:)'\"")
            if clean_u:
                verified_urls.append(cls.verify_url(clean_u))

        # Evaluate Sender
        verified_sender = cls.verify_sender(sender_info)

        # Compute Highest URL Threat
        has_high_risk_url = any(u["url_status"] == "HIGH RISK" for u in verified_urls)
        has_suspicious_url = any(u["url_status"] == "SUSPICIOUS" for u in verified_urls)

        overall_url_status = "HIGH RISK" if has_high_risk_url else ("SUSPICIOUS" if has_suspicious_url else ("SAFE" if verified_urls else "NO URLS"))

        return {
            "urls": verified_urls,
            "url_count": len(verified_urls),
            "overall_url_status": overall_url_status,
            "has_suspicious_url": (has_high_risk_url or has_suspicious_url),
            "sender": verified_sender
        }
