import re
from urllib.parse import urlparse

# Suspicious Top Level Domains often used in phishing
SUSPICIOUS_TLDS = ['.xyz', '.top', '.click', '.run', '.vip', '.work', '.info', '.cc', '.ru']

# Known popular brands often typosquatted
POPULAR_BRANDS = ['paypal', 'amazon', 'apple', 'chase', 'wellsfargo', 'netflix', 'microsoft', 'google']

def extract_urls(text):
    """Extract URLs from a given text block."""
    url_pattern = re.compile(
        r'(?:(?:https?|ftp)://)?'
        r'(?:\S+(?::\S*)?@)?'
        r'(?:'
        r'(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])'
        r'(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}'
        r'(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))'
        r'|'
        r'(?:(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)'
        r'(?:\.(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)*'
        r'(?:\.(?:[a-z\u00a1-\uffff]{2,}))'
        r'\.?'
        r')'
        r'(?::\d{2,5})?'
        r'(?:[/?#]\S*)?',
        re.IGNORECASE
    )
    return re.findall(url_pattern, text)

def analyze_url(url):
    """Analyze a single URL for phishing characteristics."""
    if not url.startswith('http'):
        parsed_url = urlparse('http://' + url)
    else:
        parsed_url = urlparse(url)
        
    domain = parsed_url.netloc.lower()
    
    # Strip port if present
    if ':' in domain:
        domain = domain.split(':')[0]
        
    analysis = {
        'url': url,
        'domain': domain,
        'risk_score': 0,
        'flags': []
    }
    
    # 1. IP Address check (often used instead of domains)
    ip_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
    if ip_pattern.match(domain):
        analysis['risk_score'] += 40
        analysis['flags'].append("IP Address used instead of domain name")
        
    # 2. Suspicious TLD check
    tld = '.' + domain.split('.')[-1] if '.' in domain else ''
    if tld in SUSPICIOUS_TLDS:
        analysis['risk_score'] += 30
        analysis['flags'].append(f"Suspicious Top-Level Domain ({tld})")
        
    # 3. Multiple subdomains (e.g. login.paypal.com.secure.com)
    parts = domain.split('.')
    if len(parts) > 3 and not (domain.endswith('.co.uk') or domain.endswith('.com.au')):
        analysis['risk_score'] += 20
        analysis['flags'].append("Unusually high number of subdomains")
        
    # 4. Brand Typosquatting / Impersonation check
    for brand in POPULAR_BRANDS:
        if brand in domain and domain != f"{brand}.com":
            # Very basic check: brand name appears, but it's not the exact official domain
            # Often looks like: secure-chase.com, paypal-login.com
            analysis['risk_score'] += 40
            analysis['flags'].append(f"Potential Brand Spoofing (contains '{brand}')")
            
    # 5. Length of URL
    if len(url) > 75:
        analysis['risk_score'] += 10
        analysis['flags'].append("Unusually long URL (often used to hide actual destination)")
        
    # 6. Shorteners
    shorteners = ['bit.ly', 'tinyurl.com', 't.co', 'goo.gl', 'is.gd']
    if any(s in domain for s in shorteners):
        analysis['risk_score'] += 25
        analysis['flags'].append("URL Shortener used (hides the actual destination)")

    # Cap risk score at 100
    analysis['risk_score'] = min(100, analysis['risk_score'])
    
    return analysis
