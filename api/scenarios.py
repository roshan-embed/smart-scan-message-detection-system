SCENARIOS = [
    {
        "id": 1,
        "category": "Smishing (Bank)",
        "channel": "SMS",
        "title": "Bank Account Suspended",
        "message": "CHASE ALERT: Your online access has been temporarily suspended due to suspicious activity. Verify your identity immediately at https://chase-secure-verify-auth.com/login to restore access."
    },
    {
        "id": 2,
        "category": "Phishing (Delivery)",
        "channel": "SMS",
        "title": "USPS Package Delivery Failed",
        "message": "USPS: We attempted to deliver your package today but were unsuccessful because of an incomplete address. Please update your delivery details here: https://usps-tracking-dept.top/reschedule. Failure to do so will result in the package being returned."
    },
    {
        "id": 3,
        "category": "Legitimate",
        "channel": "SMS",
        "title": "Standard 2FA Code",
        "message": "Your PayPal security code is: 843921. It expires in 10 minutes. Don't share this code with anyone."
    },
    {
        "id": 4,
        "category": "Crypto Scam",
        "channel": "Social Media",
        "title": "Crypto Giveaway Double",
        "message": "Elon Musk is giving back to the community! Send between 0.1 and 10 BTC to the address below and we will send double back to you instantly! Limited time offer. Hurry! Visit www.tesla-crypto-event.net."
    },
    {
        "id": 5,
        "category": "Job Scam",
        "channel": "WhatsApp",
        "title": "Easy Work From Home",
        "message": "Hello, I am a recruiter from Amazon. We have remote part-time positions available. You can earn $200-$500 per day by just liking products. No experience needed. Contact me via Telegram @AmazonHR_Bot to start immediately!"
    },
    {
        "id": 6,
        "category": "Impersonation",
        "channel": "Email",
        "title": "CEO Wire Transfer Request",
        "message": "Are you at your desk? I need you to process an urgent wire transfer for a new vendor acquisition before the end of the day. Do not discuss this with anyone else as it is confidential. Let me know when you are ready and I will send the bank details."
    },
    {
        "id": 7,
        "category": "Tech Support",
        "channel": "Email",
        "title": "GeekSquad Subscription Renewal",
        "message": "Dear Customer, your annual subscription to GeekSquad Antivirus has been auto-renewed for $399.99. The amount will be deducted from your account within 24 hours. If you did not authorize this, please call our support team immediately at +1-888-555-0192 to claim a refund."
    },
    {
        "id": 8,
        "category": "Legitimate",
        "channel": "Email",
        "title": "Dinner Reservation Confirmation",
        "message": "Hi John, your table for 4 at The Rustic Spoon is confirmed for Friday at 7:00 PM. We look forward to seeing you!"
    },
    {
        "id": 9,
        "category": "Romance / Catfishing",
        "channel": "Social Media",
        "title": "Unexpected inheritance plea",
        "message": "My dearest, I am so sorry to ask but my father just passed away and left a large inheritance locked in a foreign bank. I need $2000 to pay the legal fees to release it. As soon as I get it, I will pay you back double and come visit you. Please send via western union."
    }
]

def get_scenarios():
    return SCENARIOS
