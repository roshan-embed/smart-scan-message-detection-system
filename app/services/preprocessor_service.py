import re
import html
import unicodedata
from urllib.parse import urlparse

class PreprocessorService:
    """
    Business Logic Tier: Message Preprocessing & Normalization Engine
    Prepares raw unstructured message text across SMS, WhatsApp, and Email
    for rule-based heuristics and local DistilBERT neural classification.
    """

    # Common English contractions mapping
    CONTRACTIONS = {
        "ain't": "am not", "aren't": "are not", "can't": "cannot", "can't've": "cannot have",
        "'cause": "because", "could've": "could have", "couldn't": "could not",
        "didn't": "did not", "doesn't": "does not", "don't": "do not", "hadn't": "had not",
        "hasn't": "has not", "haven't": "have not", "he'd": "he would", "he'll": "he will",
        "he's": "he is", "how'd": "how did", "how'll": "how will", "how's": "how is",
        "i'd": "i would", "i'll": "i will", "i'm": "i am", "i've": "i have",
        "isn't": "is not", "it'd": "it would", "it'll": "it will", "it's": "it is",
        "let's": "let us", "might've": "might have", "must've": "must have", "mustn't": "must not",
        "shan't": "shall not", "she'd": "she would", "she'll": "she will", "she's": "she is",
        "should've": "should have", "shouldn't": "should not", "that's": "that is",
        "there's": "there is", "they'd": "they would", "they'll": "they will", "they're": "they are",
        "they've": "they have", "wasn't": "was not", "we'd": "we would", "we'll": "we will",
        "we're": "we are", "we've": "we have", "weren't": "were not", "what'll": "what will",
        "what're": "what are", "what's": "what is", "what've": "what have", "where's": "where is",
        "who'll": "who will", "who's": "who is", "who've": "who have", "won't": "will not",
        "would've": "would have", "wouldn't": "would not", "you'd": "you would", "you'll": "you will",
        "you're": "you are", "you've": "you have", "u": "you", "ur": "your", "pls": "please",
        "plz": "please", "txt": "text", "msg": "message", "acc": "account", "info": "information"
    }

    # Cyrillic and deceptive look-alike homoglyphs mapped to Latin counterparts
    HOMOGLYPH_MAP = {
        'а': 'a', 'А': 'A', 'с': 'c', 'С': 'C', 'е': 'e', 'Е': 'E',
        'о': 'o', 'О': 'O', 'р': 'p', 'Р': 'P', 'х': 'x', 'Х': 'X',
        'у': 'y', 'У': 'Y', 'і': 'i', 'І': 'I', 'ј': 'j', 'Ј': 'J',
        'ѕ': 's', 'Ѕ': 'S', 'в': 'b', 'В': 'B', 'м': 'm', 'М': 'M',
        'н': 'h', 'Н': 'H', 'к': 'k', 'К': 'K', 'т': 't', 'Т': 'T'
    }

    # Standard offline stopwords list for lexical analysis
    STOPWORDS = {
        "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
        "any", "are", "as", "at", "be", "because", "been", "before", "being", "below",
        "between", "both", "but", "by", "could", "did", "do", "does", "doing", "down",
        "during", "each", "few", "for", "from", "further", "had", "has", "have", "having",
        "he", "her", "here", "hers", "herself", "him", "himself", "his", "how", "i",
        "if", "in", "into", "is", "it", "its", "itself", "just", "me", "more", "most",
        "my", "myself", "no", "nor", "not", "now", "of", "off", "on", "once", "only",
        "or", "other", "our", "ours", "ourselves", "out", "over", "own", "same", "she",
        "should", "so", "some", "such", "than", "that", "the", "their", "theirs", "them",
        "themselves", "then", "there", "these", "they", "this", "those", "through", "to",
        "too", "under", "until", "up", "very", "was", "we", "were", "what", "when",
        "where", "which", "while", "who", "whom", "why", "with", "would", "you", "your",
        "yours", "yourself", "yourselves"
    }

    SUSPICIOUS_TLDS = {
        "xyz", "top", "online", "club", "live", "site", "vip", "icu", "click", "buzz",
        "gq", "ml", "cf", "ga", "tk", "work", "loan", "link", "win", "bid", "monster"
    }

    # ---------------- 1. Text Cleaning ---------------- #

    @classmethod
    def clean_text(cls, raw_text: str) -> dict:
        """
        Removes unnecessary characters, unescapes HTML, strips zero-width obfuscation,
        and sanitizes raw message payloads.
        """
        if not raw_text:
            return {"cleaned_text": "", "removed_elements": []}

        removed_elements = []

        # Step 1: Decode HTML entities (&amp; -> &, &lt; -> <, etc.)
        decoded = html.unescape(raw_text)
        if decoded != raw_text:
            removed_elements.append("Decoded HTML Entities")

        # Step 2: Strip HTML tags (<a href=...>...</a>, <br>, <div>)
        tag_pattern = r"<[^>]+>"
        if re.search(tag_pattern, decoded):
            removed_elements.append("Stripped HTML/XML tags")
        without_tags = re.sub(tag_pattern, " ", decoded)

        # Step 3: Remove zero-width characters (ZWSP, ZWNJ, ZWJ, BOM, soft hyphens)
        zero_width_pattern = r"[\u200B\u200C\u200D\uFEFF\u00AD]"
        if re.search(zero_width_pattern, without_tags):
            removed_elements.append("Removed invisible zero-width characters (anti-obfuscation)")
        without_zw = re.sub(zero_width_pattern, "", without_tags)

        # Step 4: Remove non-printable control characters (except standard newlines and tabs)
        control_char_pattern = r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]"
        if re.search(control_char_pattern, without_zw):
            removed_elements.append("Removed non-printable ASCII control characters")
        without_control = re.sub(control_char_pattern, "", without_zw)

        # Step 5: Normalize multiple spaces and multiple newlines
        cleaned = re.sub(r"[ \t]+", " ", without_control)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        cleaned = cleaned.strip()

        return {
            "cleaned_text": cleaned,
            "removed_elements": removed_elements
        }

    # ---------------- 2. Text Normalization ---------------- #

    @classmethod
    def normalize_text(cls, text: str) -> dict:
        """
        Converts text to standard representation:
        - Resolves unicode homoglyphs (Cyrillic look-alikes used by scammers).
        - Unicode NFKC decomposition.
        - Expands colloquial contractions and SMS acronyms.
        - Produces both standard case-preserved and canonical lower-cased versions.
        """
        if not text:
            return {"normalized_text": "", "lowercased_text": "", "homoglyphs_replaced": 0, "contractions_expanded": 0}

        # 1. Unicode NFKC normalization
        nfkc_text = unicodedata.normalize("NFKC", text)

        # 2. Defang & Homoglyph normalization (e.g., 'pаypаl' with Cyrillic 'а' -> 'paypal')
        homoglyphs_count = 0
        char_list = []
        for char in nfkc_text:
            if char in cls.HOMOGLYPH_MAP:
                char_list.append(cls.HOMOGLYPH_MAP[char])
                homoglyphs_count += 1
            else:
                char_list.append(char)
        homoglyph_clean = "".join(char_list)

        # 3. Defang brackets around URLs (e.g. hxxp[://], domain[.]com)
        defanged_normalized = re.sub(r"\[\s*:\s*//\s*\]", "://", homoglyph_clean)
        defanged_normalized = re.sub(r"\[\s*\.\s*\]", ".", defanged_normalized)

        # 4. Expand contractions
        words = defanged_normalized.split()
        expanded_words = []
        contractions_count = 0
        for w in words:
            # Check lowercase version
            w_lower = w.lower()
            # Clean punctuation for lookup
            clean_word = re.sub(r"^[^\w']+|[^\w']+$", "", w_lower)
            if clean_word in cls.CONTRACTIONS:
                expansion = cls.CONTRACTIONS[clean_word]
                # Preserve leading/trailing punctuation if any
                expanded = w.lower().replace(clean_word, expansion)
                expanded_words.append(expanded)
                contractions_count += 1
            else:
                expanded_words.append(w)

        normalized_text = " ".join(expanded_words)
        lowercased_text = normalized_text.lower()

        return {
            "normalized_text": normalized_text,
            "lowercased_text": lowercased_text,
            "homoglyphs_replaced": homoglyphs_count,
            "contractions_expanded": contractions_count
        }

    # ---------------- 3. Extract URLs ---------------- #

    @classmethod
    def extract_urls(cls, text: str) -> list[dict]:
        """
        Extracts, validates, and breaks down all embedded URLs, IP addresses, and raw domains.
        """
        if not text:
            return []

        # Matches standard schemas, www prefixes, and naked domains with popular/scam TLDs
        url_pattern = r"(?:https?:\/\/|hxxps?:\/\/|www\.)[^\s<>{}\[\]\"']+|(?:\b[a-zA-Z0-9-]{2,}\.)+(?:com|org|net|xyz|top|online|ru|cn|biz|me|live|cc|tk|ml|ga|cf|gq|info|co|io|site|club)(?:\/[^\s<>{}\[\]\"']*)?|\b(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?(?:\/[^\s<>{}\[\]\"']*)?"
        matches = re.finditer(url_pattern, text, re.IGNORECASE)

        extracted = []
        seen = set()

        for match in matches:
            raw_url = match.group(0).rstrip(".,;!?:)'\"")
            if raw_url.lower() in seen:
                continue
            seen.add(raw_url.lower())

            # Normalize scheme if missing
            parsed_target = raw_url
            if not re.match(r"^https?:\/\/", parsed_target, re.IGNORECASE):
                parsed_target = "http://" + parsed_target

            try:
                parsed = urlparse(parsed_target)
                domain = parsed.netloc.split(":")[0].lower()
                tld = domain.split(".")[-1] if "." in domain else ""
                is_suspicious_tld = tld in cls.SUSPICIOUS_TLDS
                is_ip_address = bool(re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", domain))
                is_shortener = domain in {"bit.ly", "tinyurl.com", "t.co", "is.gd", "cutt.ly", "rb.gy", "shorturl.at"}

                extracted.append({
                    "raw_url": raw_url,
                    "domain": domain,
                    "tld": tld,
                    "scheme": parsed.scheme or "http",
                    "path": parsed.path or "/",
                    "is_ip_host": is_ip_address,
                    "is_suspicious_tld": is_suspicious_tld,
                    "is_url_shortener": is_shortener
                })
            except Exception:
                extracted.append({
                    "raw_url": raw_url,
                    "domain": raw_url,
                    "tld": "unknown",
                    "scheme": "http",
                    "path": "/",
                    "is_ip_host": False,
                    "is_suspicious_tld": False,
                    "is_url_shortener": False
                })

        return extracted

    # ---------------- 4. Extract Phone Numbers ---------------- #

    @classmethod
    def extract_phone_numbers(cls, text: str) -> list[dict]:
        """
        Extracts phone numbers, international prefixes, and shortcodes.
        """
        if not text:
            return []

        # Matches international + local phone variations
        phone_pattern = r"(?:\+?\d{1,4}[ -]?)?(?:\(?\d{2,5}\)?[ -]?)?\d{3,5}[ -]?\d{3,5}"
        candidates = re.finditer(phone_pattern, text)

        phones = []
        seen = set()

        for match in candidates:
            raw_phone = match.group(0).strip()
            digits_only = re.sub(r"\D", "", raw_phone)
            # Legitimate telephone numbers typically range between 7 and 15 digits (E.164)
            if 7 <= len(digits_only) <= 15:
                if digits_only in seen:
                    continue
                seen.add(digits_only)

                is_international = raw_phone.startswith("+")
                is_toll_free = bool(re.search(r"800|888|877|866|855", digits_only[:6]))

                phones.append({
                    "raw_phone": raw_phone,
                    "normalized_digits": digits_only,
                    "digit_count": len(digits_only),
                    "is_international": is_international,
                    "is_toll_free": is_toll_free
                })

        return phones

    # ---------------- 5. Extract Email Addresses ---------------- #

    @classmethod
    def extract_emails(cls, text: str) -> list[dict]:
        """Extracts email addresses with domain validation."""
        if not text:
            return []

        email_pattern = r"\b([A-Za-z0-9._%+-]+)@([A-Za-z0-9.-]+\.[A-Z|a-z]{2,})\b"
        matches = re.finditer(email_pattern, text)

        emails = []
        seen = set()

        for match in matches:
            full_email = match.group(0).lower()
            if full_email in seen:
                continue
            seen.add(full_email)

            username = match.group(1).lower()
            domain = match.group(2).lower()
            tld = domain.split(".")[-1]

            emails.append({
                "email": full_email,
                "username": username,
                "domain": domain,
                "tld": tld,
                "is_suspicious_tld": tld in cls.SUSPICIOUS_TLDS
            })

        return emails

    # ---------------- 6. Tokenization ---------------- #

    @classmethod
    def tokenize_text(cls, text: str) -> dict:
        """
        Tokenizes text into words, punctuation, and entities.
        Identifies stopwords, calculates lexical diversity, and prepares
        tokens for local DistilBERT WordPiece / BPE embedding.
        """
        if not text:
            return {
                "tokens": [], "token_count": 0, "vocabulary_size": 0,
                "stopword_count": 0, "lexical_diversity": 0.0,
                "distilbert_tokens_preview": []
            }

        # Token pattern: matches words, numbers, punctuation, or symbols
        token_pattern = r"[A-Za-z0-9]+(?:'[a-zA-Z]+)?|[^\w\s]"
        raw_tokens = re.findall(token_pattern, text)

        tokens_data = []
        unique_words = set()
        stopword_count = 0

        for idx, t in enumerate(raw_tokens):
            t_lower = t.lower()
            is_punct = bool(re.match(r"^[^\w\s]$", t))
            is_num = bool(re.match(r"^\d+$", t))
            is_stopword = t_lower in cls.STOPWORDS and not is_punct and not is_num

            if is_stopword:
                stopword_count += 1
            if not is_punct:
                unique_words.add(t_lower)

            tokens_data.append({
                "index": idx,
                "token": t,
                "is_stopword": is_stopword,
                "is_punctuation": is_punct,
                "is_numeric": is_num
            })

        total_tokens = len(raw_tokens)
        vocab_size = len(unique_words)
        lexical_diversity = round(vocab_size / total_tokens, 4) if total_tokens > 0 else 0.0

        # DistilBERT format preview ([CLS] + tokens truncated to max length + [SEP])
        bert_preview = ["[CLS]"] + [t["token"] for t in tokens_data[:64]] + ["[SEP]"]

        return {
            "tokens": tokens_data,
            "token_count": total_tokens,
            "vocabulary_size": vocab_size,
            "stopword_count": stopword_count,
            "lexical_diversity": lexical_diversity,
            "distilbert_tokens_preview": bert_preview
        }

    # ---------------- 7. Full Unified Preprocessing Pipeline ---------------- #

    @classmethod
    def process(cls, raw_text: str, metadata: dict = None) -> dict:
        """
        Unified 5-Stage Preprocessing Pipeline:
        Stage 1: Raw Ingestion
        Stage 2: Cleaning & Deobfuscation
        Stage 3: Normalization & Canonicalization
        Stage 4: Entity Extraction (URLs, Phones, Emails)
        Stage 5: Tokenization & DistilBERT Format Encoding
        """
        # Stage 1: Clean
        clean_res = cls.clean_text(raw_text)
        cleaned_text = clean_res["cleaned_text"]

        # Stage 2: Normalize
        norm_res = cls.normalize_text(cleaned_text)
        normalized_text = norm_res["normalized_text"]
        lowercased_text = norm_res["lowercased_text"]

        # Stage 3: Entity Extraction (performed on normalized text to defeat homoglyph evasion)
        urls = cls.extract_urls(normalized_text)
        phones = cls.extract_phone_numbers(normalized_text)
        emails = cls.extract_emails(normalized_text)

        # Stage 4: Tokenization
        token_res = cls.tokenize_text(normalized_text)

        return {
            "stage_1_raw": raw_text,
            "stage_2_clean": {
                "cleaned_text": cleaned_text,
                "removed_elements": clean_res["removed_elements"]
            },
            "stage_3_normalize": {
                "normalized_text": normalized_text,
                "lowercased_text": lowercased_text,
                "homoglyphs_replaced": norm_res["homoglyphs_replaced"],
                "contractions_expanded": norm_res["contractions_expanded"]
            },
            "stage_4_entities": {
                "urls": urls,
                "url_count": len(urls),
                "phones": phones,
                "phone_count": len(phones),
                "emails": emails,
                "email_count": len(emails)
            },
            "stage_5_tokenization": token_res
        }
