# SMART SCAM MESSAGE DETECTION SYSTEM
> **Architecture:** MVC + 3-Tier Layered Architecture  
> **Module 1:** User Account & Authentication `[Active & Operational]`  
> **Module 2:** Smart Message Scanner `[Active & Operational]`  
> **Module 3:** Message Security Checkup 🔎 `[Active & Operational]`  
> **Module 4:** Scam Indicator Report 🚨 `[Active & Operational]`  
> **Module 5:** AI Scam Classification 🤖 `[Active & Operational]`  
> **Module 6:** Risk Assessment & Threat Scoring 📊 `[Active & Operational]`  
> **Tech Stack:** HTML5 &bull; Vanilla CSS &bull; JavaScript &bull; Python Flask &bull; MySQL &bull; Local DistilBERT Model

---

## 🏛️ System Architecture

The system is constructed strictly following the **3-Tier / Layered Architecture** with **MVC** pattern separation:

```
[ Tier 1: Presentation Layer (View & Controller) ]
  ├── Templates: Semantic HTML5 (Jinja2)
  ├── Styles: Vanilla CSS Enterprise System (Navy, Slate, Off-White, Teal, Safe, Warning, Danger)
  ├── Client Logic: Vanilla JavaScript (Live Counters, Checkup Interactivity, Tabs)
  └── Controllers: Flask Blueprints (auth, profile, dashboard, scanner, checkup, indicators)
                    │
                    ▼
[ Tier 2: Business Logic Layer (Service) ]
  ├── AuthService: User registration, credential verification, PBKDF2/scrypt hashing
  ├── UserService: Profile modification, secure password rotation, session revocation
  ├── ScannerService: Multi-channel input ingestion, live validation, persistent storage
  ├── SecurityCheckupService (Module 3): 8-factor security checklist screening engine
  ├── ScamIndicatorService (Module 4): Granular 🔴/🟠 threat warning signs & count aggregator
  └── Threat Detection Engine (Upcoming: Rule-Based Engine + Local DistilBERT Transformer)
                    │
                    ▼
[ Tier 3: Data Access Layer (Model / DAO) ]
  ├── DatabaseManager: MySQL 8.0+ Connection Manager (with SQLite auto-fallback)
  ├── UserModel: User entities, sessions, audit logs
  ├── MessageModel: Ingested scam message payloads, extracted entities, threat verdicts
  └── Database: MySQL Database `smart_scam_detection` (schema.sql)
```

---

## 🎨 Enterprise UI Design Palette

Aligned with the exact specifications:

| Role | Color Name | Hex Code | Visual Application |
|---|---|---|---|
| **Primary Navy** | Navy | `#172B4D` | Top Navigation Header, Brand Badges, Headings |
| **Secondary Slate** | Slate | `#344563` | Subtitles, Table Headers, Inactive Elements |
| **Background** | Off-White | `#F7F8FA` | Full-page background |
| **Card** | Pure White | `#FFFFFF` | 8–12px radius, thin `#D9DEE7` border, subtle elevation |
| **Primary Action** | Teal | `#00897B` | Primary buttons, active highlights, key CTAs |
| **Safe** | Forest Green | `#2E7D32` | Verified status, safe verdicts, strong passwords |
| **Warning** | Amber | `#F9A825` | Moderate risks, suspicious warnings, pending states |
| **Danger** | Red | `#C62828` | High risk scam, failed attempts, session termination |
| **Text Primary** | Navy | `#091E42` | Body text, titles, labels |
| **Text Secondary** | Gray | `#5E6C84` | Captions, hints, timestamps |
| **Border** | Light Gray | `#D9DEE7` | Card borders, input field borders, dividers |

---

## 🚀 Module 1: User Account & Authentication Features
1. **User Registration:** Multi-field input, real-time password strength meter, PBKDF2/scrypt hashing.
2. **User Login & Session Management:** Unified identifier, Remember Me, active multi-device tracking, session revocation.
3. **Profile Management:** View/edit personal details, immutable username and email audit tracking.
4. **Password Change:** Cryptographic verification of existing password, strength validation.
5. **Security Audit Trail:** Tracks all successful, failed, and blocked authentication events.

---

## 🛡️ Module 2: Smart Message Scanner Features
1. **Multi-Channel Input Gateway:**
   - **SMS:** Sender ID/number, SMS-tailored textarea with GSM-7 160-character segment counter.
   - **WhatsApp:** Sender contact/number, forwarded chat format support.
   - **Email:** Sender email address, Subject line, and rich email body text area.
2. **Real-Time Live Character Counter:**
   - Live character counter (0 to 10,000 max capacity) with color-coded buffer warning bar.
   - Live word counter and dynamic SMS segment calculator.
3. **Clear Message Trigger:** Instant reset button that safely clears form inputs and resets counters.
4. **Quick Sample Scam Loader:** One-click demo loader providing realistic bank KYC SMS, WhatsApp lottery, and email phishing patterns for immediate evaluation.
5. **Direct Engine Hand-off:** Automatically executes **Module 3: Message Security Checkup** and **Module 4: Scam Indicator Report** on every scan, displaying both right inside the results view!

---

## 🔎 Module 3: Message Security Checkup Features
**Purpose:** Give the user an initial security overview of the submitted message.

### Features:
1. **Detect Links:** Identifies web links, IP hosts, and URL shorteners; evaluates domain reputation (`Suspicious`, `Detected`, `None Found`).
2. **Identify Phone Numbers:** Identifies callback telephone numbers, toll-free lines, and international dial codes.
3. **Identify Email Addresses:** Extracts and validates embedded contact emails.
4. **Detect UPI / Payment Information:** Scans for UPI VPAs (`@okhdfcbank`, `@paytm`, `@ybl`) and fund transfer prompts.
5. **Identify Banking References:** Flags Indian and international banking institutions (SBI, HDFC, ICICI, Axis, PNB, etc.).
6. **Detect Sensitive-Information Requests:** Flags solicitations for OTPs, ATM PINs, MPINs, passwords, and CVVs.
7. **Detect Urgency / Threat Language:** Detects coercive psychological pressure (`immediate action`, `suspended`, `24 hours`, `legal action`).
8. **Identify Message Category:** Classifies message intent (`KYC & Verification Fraud`, `Banking Phishing`, `Lottery & Prize Fraud`, etc.).

### UI Example:
```
MESSAGE SECURITY CHECKUP

🔗 Link Found
⚠ Suspicious

🏦 Banking Content
✓ Detected

📄 KYC Request
⚠ Detected

🔐 Sensitive Information
⚠ Requested

⚡ Urgency
⚠ Detected
```

---

## 🚨 Module 4: Scam Indicator Report Features
**Purpose:** Show the user the specific warning signs found in the message.

### Features:
1. **Suspicious Link Indicator:** Flags phishing URLs, suspicious TLDs (`.xyz`, `.top`), IP hosts, and URL shorteners.
2. **Urgency Indicator:** Detects artificial panic cues and countdown threats.
3. **KYC Scam Indicator:** Unsolicited mandates to update or verify identity documents.
4. **OTP Request Indicator:** Confirms confidential token requests.
5. **Prize / Lottery Indicator:** Flags fake rewards, lucky draw jackpots, and task job offers.
6. **Payment / UPI Indicator:** Flags requests for upfront fees, processing charges, or UPI transactions.
7. **Account-Blocking Threat:** Identifies threats of account termination, freezing, or suspension.
8. **Personal-Information Request:** Flags requests for government IDs (Aadhaar, PAN, SSN) or mothers' maiden names.

### UI Example:
```
SCAM INDICATORS FOUND

🔴 Suspicious Link
🔴 Urgency
🔴 KYC Request
🟠 Banking Reference
🟠 Account Threat

5 warning signs detected
```

---

## 🤖 Module 5: AI Scam Classification Features
**Purpose:** Use the local AI model to classify the message.

### Features:
1. **Local DistilBERT Model:** Transformer neural network inference running 100% locally on host without external AI APIs or cloud dependencies.
2. **Scam Prediction:** Classifies phishing, banking fraud, urgency, and task scams as `SCAM`.
3. **Safe Prediction:** Accurately classifies legitimate conversational, business, and personal messages as `SAFE`.
4. **AI Confidence Score:** Computes calibrated posterior probabilities scaled to 0-100% certainty.
5. **Classification Result & Visual Telemetry:** Generates ASCII confidence bar (`██████████████████░░  91%`), visual color-coded progress meter, inference latency in ms, and attended semantic tokens.

### UI Example:
```
AI ANALYSIS

Prediction: SCAM

Confidence
██████████████████░░  91%

Model:
Local DistilBERT
```

---

## 📊 Module 6: Risk Assessment & Threat Scoring Features
**Purpose:** Calculate the overall risk of the message by combining the Rule-Based Scam Indicators and Local DistilBERT AI Prediction into a calibrated Final Risk Score.

### Multi-Tier Ensemble Flow:
```
Scam Indicators
       +
AI Prediction
       ↓
Risk Assessment
       ↓
Final Risk Score
```

### Exact Specification Example:
```
Rule-based score     70/100
AI confidence        91%
                     ↓
Final Risk Score     87/100

HIGH RISK
```

### Risk Levels & Threat Tiers:
- 🟢 **0–30 — Safe:** Normal, legitimate communication. No deceptive patterns or malicious payloads.
- 🟡 **31–60 — Suspicious:** Moderate threat level. Contains unverified external references or suspicious patterns requiring caution.
- 🔴 **61–100 — High Risk:** Severe threat! High probability of credential harvesting, fraud, or phishing.

### Features:
1. **Rule-Based Score Aggregation:** Sums calibrated points from Module 4 indicators (Suspicious Link, KYC Scam, OTP Solicitation, Account Threats, Urgency, Banking References).
2. **AI Threat Contribution:** Fuses DistilBERT posterior probability and confidence percentage.
3. **Ensemble Risk Fusion Engine:** Evaluates $Final = \text{round}(0.20 \times \text{Rule} + 0.80 \times \text{AI})$ with critical threat safety floor.
4. **Visual 3-Zone Meter:** Color-coded gauge and pin marker indicating exact position across Safe, Suspicious, and High Risk zones.
5. **Actionable Safety Protocol:** Contextual defense steps (e.g. do not click links, never share OTP, report to cybercrime authorities).

---

## 📋 The 12-Module System Roadmap

1. **Module 01: User Account & Authentication** &mdash; `[ACTIVE & OPERATIONAL]`
2. **Module 02: Smart Message Scanner** &mdash; `[ACTIVE & OPERATIONAL]`
3. **Module 03: Message Security Checkup 🔎** &mdash; `[ACTIVE & OPERATIONAL]`
4. **Module 04: Scam Indicator Report 🚨** &mdash; `[ACTIVE & OPERATIONAL]`
5. **Module 05: AI Scam Classification 🤖** &mdash; `[ACTIVE & OPERATIONAL]`
6. **Module 06: Risk Assessment & Threat Scoring 📊** &mdash; `[ACTIVE & OPERATIONAL]`
7. **Module 07: Hybrid Threat Scoring & Fusion Engine** &mdash; `[PLANNED]`
8. **Module 08: Scam Category & Intent Classifier** &mdash; `[PLANNED]`
9. **Module 09: Detection Results & Threat Indicators** &mdash; `[PLANNED]`
10. **Module 10: Threat Blacklist & Pattern Registry** &mdash; `[PLANNED]`
11. **Module 11: System Security & Audit Trail** &mdash; `[PLANNED]`
12. **Module 12: Engine Settings & Admin Controls** &mdash; `[PLANNED]`

---

## 💻 Running & Debugging in VS Code

1. Open this project directory in VS Code:
   ```
   C:\Users\HP\.gemini\antigravity-ide\scratch\smart_scam_detection
   ```
2. Press **`F5`** (or go to **Run and Debug** &rarr; select **"Python: Smart Scam Detection (Flask)"**).
3. The server starts directly inside VS Code's integrated terminal with full breakpoint and hot-reloading support!
4. Navigate to: `http://127.0.0.1:5000/scanner/`

---

## 💻 Pre-seeded Evaluation Accounts
For immediate testing out of the box:
- **Administrator:**
  - Email: `admin@scamdetect.internal`
  - Password: `Admin@12345!`
- **Security Analyst:**
  - Email: `analyst@scamdetect.internal`
  - Password: `Analyst@12345!`
