Onboarding Journey — Business Infinity (detailed, reassurance‑first)

This is the canonical onboarding journey for a new founder entering Business Infinity’s perpetual boardroom. The design principle is simple: low friction + maximum trust. Each step explains what happens, why it matters, the founder experience, and the specific reassurances and compliance proofs we surface so the founder feels safe handing over read‑only access and artifacts.

---

1. Welcome gateway (0:00–0:30 — instant)

- What happens  
  - Founder lands on the entry screen and sees a calm, executive welcome card with company name auto‑filled (if available).  
  - Primary action: “Continue with LinkedIn” or “Continue with Email”.

- Why it matters  
  - Signals a premium, personal experience immediately; reduces friction.

- Founder experience & reassurance script (displayed)  
  - “Welcome — this is your private boardroom. We’ll only read data you allow and never change anything without permission.”  
  - Small privacy note visible: “Read‑only connections by default; you remain in control.”

- Compliance proof to show here (visible micro‑links / badges)  
  - Authentication security: OAuth badge and short line: “Secure sign‑on via LinkedIn / SSO”.  
  - Privacy summary: one‑line pointer: “We follow industry best practices; details available in Security & Compliance.”

---

2. Identity capture via LinkedIn (0:30–1:30)

- What happens  
  - OAuth handshake with LinkedIn to pull profile, company, job title, company link, and recent posts (with permission prompts).  
  - App shows exactly which fields will be read before user consents.

- Why it matters  
  - Removes manual form‑filling; gives the boardroom a voice that already knows the founder’s public identity.

- Founder experience & reassurance script (displayed)  
  - “We will only read these fields; nothing is posted to LinkedIn. You can revoke access anytime.”  
  - Inline note: “We parse recent public posts to learn your voice — read‑only.”

- Compliance proof to show here  
  - Consent log sample: a one‑line, time‑stamped preview showing the exact consent the founder just gave.  
  - Data minimization note: short bullet: “Only core profile + last 20 public posts are used.”

---

3. Auto‑discovery: website & public filings (1:30–2:30)

- What happens  
  - System detects website URL from LinkedIn or founder pastes it. Automated parse extracts tagline, product summary, team page, logos, press, and links to public filings.  
  - If filings/annual reports are public, the system pulls links (read‑only links) and flags them for CFO review.

- Why it matters  
  - Anchors the boardroom in the company’s public narrative and compliance record.

- Founder experience & reassurance script  
  - “We only fetch public content; we will ask before you upload any private documents.”  
  - Preview: parsed key lines from the home page and a check: “Does this represent you?” (quick confirm button).

- Compliance proof to show here  
  - Source attribution snapshot — a small visible badge indicating origin (e.g., “Parsed from: https://… — public”).  
  - Read‑only confirmation — clear label: “This was read from your public site; no writes occurred.”

---

4. Pitch deck upload (optional, 2:30–4:00)

- What happens  
  - Prompt to upload the founder’s existing pitch deck (PDF/PPT/drive link).  
  - System parses slides into canonical sections and presents a summarised slide map.

- Why it matters  
  - The founder’s deck becomes the central artifact the boardroom uses to align narrative + numbers.

- Founder experience & reassurance script  
  - “Upload your deck to make onboarding faster. Files are stored encrypted and only accessible in read‑only mode to boardroom agents.”  
  - Option: “I’d rather not upload now” (skips to next step).

- Compliance proof to show here  
  - Encryption badge: “Stored encrypted at rest (AES‑256 equivalent).”  
  - Access control note: “Only authorized boardroom agents can read this file; audit log available.”  
  - Sample audit entry: timestamp + action (“deck uploaded; parsed; user confirmed”).

---

5. Optional filings & annual reports ingestion (optional, 4:00–5:00)

- What happens  
  - Founder can paste links to public filings or upload PDFs of annual reports. System parses financial line items and compliance notes.

- Why it matters  
  - Gives CFO‑agent hard numbers for runway and risk analysis immediately.

- Founder experience & reassurance script  
  - “Public filings are powerful anchors. We will never alter these documents — only read and summarize.”  
  - If uploads are private, the interface shows explicit consent and retention policy.

- Compliance proof to show here  
  - Chain of custody preview: shows that the files are ingested and hashed (SHA hash snippet) so the founder can verify unchanged content.  
  - Retention policy: one‑liner: “Private files retained X days by default; export or delete anytime.”

---

6. Connect core systems — read‑only first (ERP/CRM/MES/HRIS) (5:00–8:30)

- What happens (fast, guided)  
  - Founder is offered connectors (Salesforce, HubSpot, NetSuite, Odoo, SAP, Workday, etc.) in a single screen.  
  - Each connector has a CTA: “Connect (read‑only)”. OAuth dialogs explain exact scopes requested.  
  - For systems without connectors, an encrypted CSV upload option is offered with a template.

- Why it matters  
  - Live signals (pipeline, revenue, burn, production throughput) enable the perpetual boardroom to be useful from day one.

- Founder experience & reassurance script (displayed at connector step)  
  - “We request read‑only scope only. No writes or edits. You remain in control.”  
  - Each connector lists scopes in plain English (e.g., “Read: Opportunities, Accounts, Contacts”).  
  - Visual indicator: green lock + “Read‑only” badge for each connected system.

- Compliance proof to show here  
  - Permissions snapshot: shows the OAuth scopes granted and a button to “Revoke access”.  
  - Security posture: short note: “Connections use TLS; tokens are stored encrypted; we undergo third‑party penetration tests.” (see full Security & Compliance brochure).  
  - Audit log entry: immediate log of connection created with timestamp.

- UX fallback for speed  
  - If founder declines connectors, they can opt for “Quick baseline” via website + deck parsing only; agents operate on inferred metrics until live feeds are added.

---

7. LinkedIn posts & voice profile ingestion (8:30–9:00)

- What happens  
  - System reads the last N public LinkedIn posts (consented in Step 2) and creates a short “Voice Profile”: themes, tone, and high‑engagement topics.

- Why it matters  
  - Ensures the boardroom speaks in the founder’s authentic voice when refining deck and investor comms.

- Founder experience & reassurance script  
  - “We only analyze public posts to learn voice and priorities — nothing is published anywhere.”  
  - Quick preview of extracted themes with an “edit” button.

- Compliance proof to show here  
  - Transparency log: shows the posts parsed and a “remove” action per post if the founder wants it excluded.

---

8. Instant founder dossier & first baseline (9:00–9:30)

- What happens  
  - System synthesizes inputs into three artifacts delivered in the chat and dashboard: Founder Dossier, Company Profile Brief, Live Data Baseline (if connectors added).  
  - CEO‑agent posts a short humanized summary in the boardroom chat.

- Why it matters  
  - The founder gets immediate, tangible value in under 10 minutes.

- Founder experience & reassurance script (chat message)  
  - CEO‑agent: “Your boardroom is assembled. We’ve created your Founder Dossier and Company Brief. From here on, we observe and advise; nothing will be changed without your permission.”  
  - Quick CTA: “Invite your co‑founder / legal counsel to view these artifacts (view only).”

- Compliance proof to show here  
  - Audit trail access: clickable “View audit trail” showing every ingestion action with timestamps.  
  - Data export & delete: buttons to download artifacts or request deletion; clear SLA for deletion.

---

9. Governance defaults & privacy choices (9:30–9:50)

- What happens  
  - A guided micro‑wizard sets default governance behaviors: who can view what, notification cadence, and escalation rules.  
  - Default is conservative: founder only, read‑only for invited viewers; notification cadence = weekly.

- Why it matters  
  - Gives control and psychological safety; reduces accidental exposure.

- Founder experience & reassurance script  
  - “By default your data is private to you. Invite team members selectively. You can change these settings any time.”  
  - Small “why we ask” tooltips explain each permission.

- Compliance proof to show here  
  - Role‑based access control (RBAC) snapshot — explains roles and what each role can do.  
  - Consent record: a short log entry showing governance defaults set.

---

10. Quick orientation message & next steps (9:50–10:00)

- What happens  
  - CEO‑agent writes a short orientation in chat with three suggested quick actions: (A) “Ask CFO to build a runway model”, (B) “Ask CMO for a GTM voice brief”, (C) “Schedule a deep review (optional)”.  
  - The founder confirms one quick action or defers.

- Why it matters  
  - Leaves founder with a clear first‑move choice and the reassurance that deeper sessions are optional.

- Founder experience & reassurance script (displayed)  
  - CEO‑agent: “You’re inside the boardroom. We’ll surface weekly insights and urgent risks proactively. When you’re ready for a full review, we’ll convene. Until then, we watch, learn, and advise.”

- Compliance proof to show here  
  - Summary email (optional) containing the founder dossier and links to Security & Compliance documents and the audit trail.

---

Continuous reassurance & compliance posture (post‑onboarding)

- Reassurance cadence (what founders see ongoing)  
  - Audit trail availability: always accessible in the boardroom UI.  
  - Revoke access button: visible in settings for every connector and data source.  
  - Data export & delete: one‑click download/export of all data and one‑click deletion request.  
  - Monthly security summary: optional email describing latest security scans and any compliance updates.

- Compliance & security posture (what to prepare and show)  
  - Technical controls to present: OAuth, TLS in transit, encryption at rest, tokenized credentials, RBAC, detailed audit logs, data retention policy.  
  - Organizational controls to present: least‑privilege access model, vendor risk assessments, incident response plan, employee background checks for any humans with access.  
  - Certifications & third‑party attestations (if available): SOC 2 Type II, ISO 27001, GDPR compliance statement, PCI or HIPAA statements if relevant. If you don’t have a certification yet, show evidence of controls and a roadmap to certification.  
  - Pen test & third‑party scans: summary of most recent penetration test and remediation status; if not yet done, show planned schedule.  
  - Privacy policy & DPA: clear, founder‑friendly summary and downloadable DPA template for enterprise customers.

- What to show the founder as “proof” (practical deliverables)  
  - Security & Compliance page in app with: certifications (badges), latest pen‑test summary, encryption details, data retention rules, contact for security team.  
  - Audit log viewer where the founder can see who accessed what and when.  
  - Connector permissions page where the founder can revoke tokens and see scope.  
  - Sample hashed file (for any uploaded filings): shows file hash to prove integrity.

---

Optional: Fast trust accelerators (for very security‑conscious founders)

- Live demo of “revoke access” with an auditor account so founders see revocation is instantaneous.  
- Invite the founder’s security or legal contact to a short walk‑through of the security page.  
- Offer a short SOC‑like checklist summary tailored to the founder’s geography (e.g., GDPR notes for EU founders, data residency options where supported).

---

Final UX copy examples (what the founder sees at each key micro‑moment)

- On LinkedIn auth prompt: “We’ll read your profile and recent public posts to tailor the boardroom voice. Nothing will be posted or changed.”  
- On connectors screen: “Connect systems in read‑only mode so the boardroom can advise using live data. You can revoke access anytime.”  
- After upload of a private filing: “We have received your filing. It is encrypted, hashed, and stored for X days by default. You can download or delete it at any time.”  
- On first baseline delivery: “Your Founder Dossier and Live Baseline are ready. No writes were made. Everything is logged and auditable.”

---

Implementation checklist for product & security teams

- Product hooks  
  - LinkedIn/OAuth integration with explicit consent UI.  
  - Website parser and slide/parsing pipeline.  
  - File upload with client‑side hashing and server‑side encrypted storage.  
  - Pre‑built OAuth read‑only connectors for major ERP/CRM/MES/HRIS.  
  - Audit log store and UI access for founders.  
  - RBAC and settings UX for invites, revoke, and export.

- Security & compliance tasks to publish to founders  
  - Document TLS, encryption at rest, token handling, and pen test cadence.  
  - Publish privacy policy, DPA template, and regional data handling notes.  
  - Maintain a visible incident contact and a short incident response summary.  
  - If available, attach SOC 2 / ISO 27001 evidence or a roadmap with timelines.

---

Closing note (founder reassurance)

- Final friendly message to display in the boardroom after onboarding:  
  - “Welcome to your perpetual boardroom. From now on we watch, advise, and protect. You invited us in; you can leave anytime. If security or privacy is ever a concern, click Revoke Access or contact security@businessinfinity — we’ll respond within X hours.”

---