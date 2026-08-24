import re
from url_analyzer import extract_urls, analyze_url

# Predefined Threat Dictionaries
URGENCY_KEYWORDS = [
    r'immediate', r'urgent', r'action required', r'suspended', r'blocked', 
    r'within \d+ hours', r'last notice', r'final warning', r'alert', r'hurry',
    r'expire'
]

FINANCIAL_KEYWORDS = [
    r'bank account', r'transfer', r'wire', r'bitcoin', r'btc', r'crypto', 
    r'refund', r'payment', r'invoice', r'tax return', r'inheritance',
    r'giveaway', r'western union'
]

CREDENTIAL_KEYWORDS = [
    r'verify your identity', r'login', r'password', r'security code', 
    r'auth', r'ssn', r'social security', r'credit card', r'pin code'
]

IMPERSONATION_KEYWORDS = [
    r'chase', r'paypal', r'amazon', r'irs', r'usps', r'fedex', r'ups', 
    r'microsoft', r'apple', r'geeksquad'
]

def analyze_message(text: str, channel: str):
    """
    Core NLP & Heuristic detection engine.
    Analyzes message and outputs Risk Score (0-100), categories, and highlights.
    """
    text_lower = text.lower()
    
    risk_factors = {
        'urgency': 0,
        'financial': 0,
        'credential': 0,
        'impersonation': 0,
        'url_risk': 0
    }
    
    highlights = []
    
    # 1. Keyword Heuristics
    for pattern in URGENCY_KEYWORDS:
        for match in re.finditer(pattern, text_lower):
            risk_factors['urgency'] += 20
            highlights.append({
                "text": text[match.start():match.end()],
                "reason": "Urgency Trigger: Scammers use time pressure to force mistakes.",
                "type": "urgency"
            })
            
    for pattern in FINANCIAL_KEYWORDS:
        for match in re.finditer(pattern, text_lower):
            risk_factors['financial'] += 20
            highlights.append({
                "text": text[match.start():match.end()],
                "reason": "Financial Lure: Requests for or promises of money/crypto.",
                "type": "financial"
            })
            
    for pattern in CREDENTIAL_KEYWORDS:
        for match in re.finditer(pattern, text_lower):
            risk_factors['credential'] += 30
            highlights.append({
                "text": text[match.start():match.end()],
                "reason": "Credential Harvesting: Asking for logins, passwords, or verification.",
                "type": "credential"
            })
            
    for pattern in IMPERSONATION_KEYWORDS:
        for match in re.finditer(pattern, text_lower):
            risk_factors['impersonation'] += 20
            highlights.append({
                "text": text[match.start():match.end()],
                "reason": "Impersonation Target: Commonly spoofed brand or authority.",
                "type": "impersonation"
            })
            
    # 2. URL Analysis
    urls = extract_urls(text)
    url_reports = []
    for u in urls:
        report = analyze_url(u)
        url_reports.append(report)
        risk_factors['url_risk'] += report['risk_score']
        highlights.append({
            "text": u,
            "reason": f"URL Risk: {', '.join(report['flags']) if report['flags'] else 'Contains external link.'}",
            "type": "url"
        })
        
    # Normalize risk factors to max 100 per category
    for k in risk_factors:
        risk_factors[k] = min(100, risk_factors[k])
        
    # Calculate Overall Risk Score
    # Weighted average: URLs and Credentials are most dangerous
    base_score = (
        (risk_factors['urgency'] * 0.15) +
        (risk_factors['financial'] * 0.15) +
        (risk_factors['credential'] * 0.30) +
        (risk_factors['impersonation'] * 0.15) +
        (risk_factors['url_risk'] * 0.25)
    )
    
    # Contextual boosts
    # If a message has impersonation + urgency + url, it's highly likely phishing
    if risk_factors['impersonation'] > 0 and risk_factors['url_risk'] > 0:
        base_score += 20
        
    if risk_factors['urgency'] > 0 and risk_factors['credential'] > 0:
        base_score += 20
        
    final_score = min(100, int(base_score))
    
    # Determine Status
    if final_score < 20:
        status = "Safe"
    elif final_score < 50:
        status = "Suspicious"
    else:
        status = "Dangerous"
        
    # Generate Action Recommendations
    actions = []
    if final_score > 50:
        actions.append("DO NOT click any links or download attachments.")
        actions.append("DO NOT reply or provide personal information.")
    if risk_factors['impersonation'] > 0:
        actions.append("Verify independently: Navigate to the official website yourself rather than using the provided link.")
    if risk_factors['financial'] > 0:
        actions.append("Never wire money or send crypto to unknown parties.")
    if final_score <= 20:
        actions.append("Message appears normal, but always stay vigilant.")

    # Deduplicate highlights
    unique_highlights = []
    seen = set()
    for h in highlights:
        key = h["text"].lower()
        if key not in seen:
            seen.add(key)
            unique_highlights.append(h)

    return {
        "risk_score": final_score,
        "status": status,
        "factors": risk_factors,
        "highlights": unique_highlights,
        "urls": url_reports,
        "recommendations": actions
    }
