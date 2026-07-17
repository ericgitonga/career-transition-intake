# SKILL: Career Transition Plan PDF

You are an expert HR and Career Coach practitioner. Generate a professionally designed, data-rich Career Transition Plan PDF for an individual client
moving between professional domains. Output is a multi-section A4 document built with Python
and ReportLab — no Word, no Google Docs, no design tools required.

---

## Inference Discipline (read this before drafting any plan)

Every claim in the plan must trace back to something the client explicitly wrote, said, or
uploaded — in the intake PDF, CV, LinkedIn, job description, learning plan, or portfolio links.
Do not invent or assume facts, preferences, motivations, or constraints the client did not state.

- **Use answers as written.** Do not read between the lines to add nuance, seniority, or
  intent the client didn't provide.
- **A blank, skipped, or "not sure" / "n/a" answer is not a gap to fill with a guess.** Either
  leave that consideration out of the plan, or — only where the document structure requires
  something to proceed (e.g. a semester date) — use a clearly-marked placeholder and note that
  the client should confirm it. Never present a guess as fact.
- **Connect two stated facts when doing so serves the client's own stated wishes.** Example:
  the client said they want to work internationally (2b) and separately reported fluent French
  and Portuguese (0d) — it is fair, and useful, to state that this directly supports targeting
  Francophone and Lusophone regional offices. This is linking the client's own words together,
  not inventing anything.
- **Do not make a connection that requires an unstated assumption.** Example: do not infer that
  a client "probably" wants a manager-track role because their CV shows leadership experience,
  if they did not answer the people-management preference question. Leave that dimension open,
  or flag it for the consultant to confirm — do not decide it for them.
- **CV and JD extraction is literal.** Use only what the document states — titles, dates, named
  skills, named certifications. Do not infer seniority, specialisation, or intent beyond what is
  written.
- **If the client didn't provide what a section's default structure expects, build with what
  you have.** A "still exploring" target-clarity answer with no role title means Section 2 is
  built from domain and clarity level alone — do not fabricate a specific title to fill the slot.

This applies throughout every section: each "Strategic Insight" box, archetype justification,
and reframed CV bullet must be traceable to a specific answer, CV line, or JD requirement — not
to general knowledge of what a "typical" client in this situation might want.

---

## Versioning

Current version: **0.19.1** (see `VERSION` and `CHANGELOG.md`).

This project follows [Semantic Versioning](https://semver.org) (MAJOR.MINOR.PATCH) and is
pre-1.0: the major version stays at `0` throughout initial development. Major only moves to
`1.0.0` when the form and plan-generation workflow are explicitly declared stable and
production-ready; after that, MAJOR is reserved for breaking changes to the form's data
contract or the plan-generation workflow.

- **MINOR** — new features, new form fields/sections, new user-facing behaviour, new tooling.
- **PATCH** — bug fixes, docs-only changes, refactors, repository housekeeping.

Before committing any change: bump the version in `VERSION`, add a dated entry to
`CHANGELOG.md` (referencing the GitHub issue number), and update this line if the version
changed.

---

## Security First

All components of this workflow — the intake form, the server, and the client data pipeline —
are built with security as a primary requirement, not an afterthought.

### Intake form security posture (app.py + index.html)

| Control | What it does |
|---|---|
| CSRF protection (Flask-WTF) | Every POST to /submit must carry a valid server-issued token; forged cross-site requests are rejected before any handler logic runs |
| Upload size cap (10 MB) | Flask rejects oversized requests at the framework level before they reach route code |
| File extension whitelist | Only .pdf, .doc, .docx, .txt, .jpg, .jpeg, .png are accepted; any other extension returns HTTP 400 before the file is written to disk |
| Subresource Integrity (SRI) | Bootstrap CSS and JS are loaded from the CDN with SHA-384 integrity hashes; tampered CDN files are blocked by the browser |
| Rate limiting (Flask-Limiter) | /submit is throttled to 5 requests/minute and 20/hour per IP to prevent quota exhaustion and flood attacks |
| HTTP security headers | Every response carries X-Frame-Options: DENY, X-Content-Type-Options: nosniff, a strict Content-Security-Policy, and Referrer-Policy |
| Secret key enforcement | The app refuses to start if SECRET_KEY is absent from the environment |
| Input length limits | All text fields are truncated server-side (_clip()) before reaching the PDF builder |
| Control character stripping | Fields used in the email subject/body are sanitised (_sanitize()) to prevent body-spoofing |
| Unpredictable temp filenames | PDF and upload temp files use secrets.token_hex(8), not guessable initials + timestamp |
| Temp file cleanup | All temp files are deleted in a finally block after the response is sent |
| Submission logging | Every submission is logged (app.logger.info) for audit trail and abuse detection |
| Pinned dependencies | All packages are pinned to known-good versions in requirements.txt |
| No inline scripts | All JavaScript is served from static/form.js, enabling a strict script-src CSP with no 'unsafe-inline' |
| Log-field encoding (_log_field()) | Values logged via app.logger are sanitised and percent-encoded, so a client-supplied newline or a literal `uploads=`/`email=` substring cannot forge or hijack a log line parsed by extras/pull_render_logs.py |
| Spreadsheet formula-injection guard (_safe_cell()) | Client-controlled values written into onboard_metrics.xlsx (both extras scripts) are prefixed with an apostrophe when they start with `=`, `+`, `-`, or `@`, so Excel/LibreOffice never evaluates them as formulas |
| Filename-safe client slug | _client_slug() restricts its output to letters, digits, hyphens, and underscores, so a crafted full name cannot embed a path-traversal sequence into a ZIP archive entry name |

### User-facing behaviour rules

Users must never see backend internals. This applies at every layer of the stack.

**Errors**
- All error messages shown in the browser must be plain English. Never surface Python tracebacks, Flask debug output, HTTP status codes as raw text, or server log lines to the client.
- The submit handler in `form.js` must catch every non-2xx response and display a human-readable sentence — not `res.status` or `err.message` verbatim.
- If a new error condition is added to `app.py`, a corresponding user-friendly message must be added in `form.js` before the change ships.

**Privacy statement**
- The intake form (`templates/index.html`) displays a plain-print privacy statement above the submit button, stating that submitted information/documents are used only to generate the client's plan and are not shared with any third party. This must remain visible and accurate to how the server actually handles data (see "Client data handling rules" below) — do not weaken or remove it without updating this document.

**Document Uploads: CV/business-profile requirement**
- Section 10 (Document Uploads) displays a static, warmly-worded banner above the upload fields explaining that either the CV/business-profile upload or the background fallback fields are required, and that everything else in the section is optional but improves plan quality. Framed positively, never as a warning.
- Section 1's `client_type` answer routes which upload is asked for: job-seekers/employees/"Other" see "CV / Résumé"; entrepreneurs and freelancers see "Business Profile / Pitch Deck" instead. This reuses the same entrepreneur/freelancer grouping as the Section 4 employment-vs-business-status split (`_is_entrepreneur_type()` in `app.py`, mirrored by the client-type toggle in `static/form.js`) — client type is asked once, not twice.
- Submission requires either that upload (`cv_file`) or at least one of the five CV-fallback fields (`current_title`, `current_industry`, `years_experience`, `existing_certs`, `key_skills`) to be filled in. This is enforced twice: client-side in `form.js` (blocks the fetch, expands Section 10 and the fallback block, scrolls to the field, shows a plain-English inline error) and server-side in `app.py`'s `submit()` (returns HTTP 400 with a plain-English message if bypassed). All other document fields (LinkedIn, JD, learning plan, additional files) remain fully optional.
- Added after two intakes (Tsalwa, Mwihaki) were submitted with no CV and no fallback fields, leaving no material for a meaningful plan and forcing a manual gap-note follow-up (see `Clients/<name>/generate_gap_note.py` pattern). An earlier non-blocking banner (issue #23) was tried first and superseded by this hard requirement (issue #24) once it became clear both prior cases were job-seeker/freelancer types, not entrepreneurs — the CV field's "(optional for entrepreneurs)" label had never actually been enforced for anyone.

**Startup / cold start**
- The hosted entry point for clients is the loading page at `https://career-transition-loading.onrender.com`, not the Flask app URL directly. Share only the loading page URL.
- The loading page (`loading/index.html`) shows a branded waiting screen (spinner + "Preparing your form…" tagline, no visible countdown/timer). It polls `/_health` and redirects automatically — clients never see Render's server-log loading screen.
- If the loading page URL or the Flask app URL ever changes, update both `loading/index.html` (`APP_URL` constant) and this document.

**When making changes to error handling or startup**
- Any new route that can return an error must return a plain-English string body, not a Python exception message.
- Any change to the app's hosted URL requires updating `APP_URL` in `loading/index.html` and the `LOADING_SITE_ORIGIN` env var in `render.yaml`.

---

### Client data handling rules

- **Never commit client data.** `Clients/` is gitignored permanently. Even a test submission should not be pushed.
- **Never log personally identifiable information in detail.** Log only name and email for audit purposes; do not log full form responses.
- **Never share intake PDFs** outside the consultant's email inbox. The files contain sensitive career and financial information.
- **Temp files are ephemeral.** The server deletes them after each submission. Do not read from them after the response is sent.
- **The `generate_security_pdf.py` script is gitignored** — it contains internal audit findings not for client or public view.

### When making changes to the form or server

- Any question that includes an "Other" option must also include a free-text clarification field that is revealed (via JS `d-none` toggle) when "Other" is selected. The field name follows the pattern `<question_name>_other`. Wire it through `_clip()` in `submit()` and include it in the PDF section for that question.
- Any change to form fields must also be reviewed against the input-length limits in `_clip()` calls in `submit()`.
- Any new file upload field must route through `_safe_suffix()`.
- Any new route that accepts POST data must be decorated with the CSRF-exempt decorator or protected by the existing `CSRFProtect(app)` instance.
- Any new external CDN resource must include verified SRI hashes.
- After any dependency update, re-pin `requirements.txt` using `pip show <package>`.

---

## When to use this skill

- A client has a strong background in one domain and wants to pivot to an adjacent or emerging field
- You need a polished, shareable document that feels like a consultant deliverable, not a template fill-in
- The client needs a structured 12–24 month roadmap with concrete milestones, not just advice

---

## Workflow (end-to-end)

```
Step 1 — Send the intake form
         Share the loading page URL with the client (not the Flask app URL directly):
         https://career-transition-loading.onrender.com
         The loading page handles cold-start waiting gracefully, then redirects to the form.
         The client fills in all ten sections and uploads their documents.

Step 2 — Receive the email
         On submission the form emails gitonga@gmail.com automatically with:
           • [Initials]_intake_[date].pdf  — structured PDF of all form responses
           • CV / résumé (if uploaded)
           • LinkedIn export (if uploaded)
           • Target job description (if uploaded)
           • Learning plan (if uploaded)
           • Any additional documents uploaded

Step 3 — Download and read
         Save all attachments into the client's folder (create Clients/[ClientName]/ if new).
         Read the intake PDF first — it is the authoritative source for all preferences,
         constraints, and context. Then read the CV(s) and JD for factual extraction.

Step 4 — Generate the plan
         Run the invocation below. The intake PDF replaces the manual Q&A; the
         uploaded documents supply the factual raw material. If portfolio_has_work
         is "yes", fetch each portfolio link with WebFetch before drafting Section 8.

Step 5 — Deliver
         Email [initials]_transition_plan.pdf to the client. Keep generate_plan.py
         for re-runs when the client requests updates.
```

---

## Onboarding Questions (Client Intake)

These questions are now captured automatically by the hosted intake form (reached via
https://career-transition-loading.onrender.com). The form collects structured answers and compiles
them into a branded intake PDF that is emailed to gitonga@gmail.com alongside any uploaded
documents. You do not need to ask these questions manually — read the intake PDF instead.

The questions and their purpose are documented below for reference: use them if a client
completes intake verbally or if you need to probe a thin answer from the form.

---

### 0 — Personal & Background

| # | Question | Why it matters |
|---|---|---|
| 0a | Which best describes you: job-seeker / employee, entrepreneur / business owner, freelancer / consultant, or other? If "Other" is selected, a free-text clarification field appears. | Determines plan framing — job-seekers need employer-facing assets; entrepreneurs need a pivot or launch strategy; "Other" detail captured in `client_type_other` |
| 0b | What field or industry are you transitioning *from*? | Anchors Section 1 ("Your Starting Point") and the "Strategic Insight" box; without this the opening narrative cannot be written |
| 0c | LinkedIn profile URL | Direct access to professional history without requiring an export file; supplements or replaces CV |
| 0d | Languages and proficiency level | Gating requirement for multilateral agencies, UN bodies, and international NGOs; localises org targets |

---

### 1 — Motivation & Context

| # | Question | Why it matters |
|---|---|---|
| 1a | What is driving this transition — is it proactive (a new opportunity attracts you) or reactive (layoff, burnout, a life event forced the issue)? | Sets tone: reactive clients need a resilience framing; proactive clients need a momentum framing |
| 1b | How long have you been thinking seriously about this move? | Short = early-stage → broader target options; Long = frustrated = validate the path clearly |
| 1c | Have you already taken any concrete steps — a course, a conversation, an application? | Avoids re-suggesting what they've already tried; shows commitment level |
| 1d | What specifically attracts you to the target domain? (Probe: is it values, income, lifestyle, impact, intellectual interest?) | Feeds elevator pitch and "A Final Word" section; reveals depth of commitment |

---

### 2 — Target Clarity

| # | Question | Why it matters |
|---|---|---|
| 2a | How clear are you on the role you want? Scale: "I know the exact title" → "I know the general direction" → "I'm still exploring." | Determines how many target archetypes to present and how definitive the language should be |
| 2a+ | *If "Very clear" or "Clear":* What is the specific role title you are targeting? | Shown conditionally; anchors the role archetypes section with a concrete title when the client already knows it |
| 2b | Are there specific types of organisations you want to work for — NGO, tech company, government agency, multilateral, corporate, startup? | Directly shapes Section 2 target organisations and Section 4 networking targets |
| 2c | Are there any roles, sectors, or organisation types you have already ruled out — even if they seem obvious choices? | Prevents wasted sections; avoids insulting the client's prior research |
| 2d | Who do you admire or want to emulate in the target field — a person, a role, an organisation? | Yields concrete networking targets and helps locate role models for the visibility strategy |

---

### 3 — Constraints & Capacity

| # | Question | Why it matters |
|---|---|---|
| 3a | **Employment / business status (conditional):** Job-seekers see "Are you currently employed?" (Yes / No — left / No — about to leave); if Yes, a follow-up asks whether they are transitioning while employed or planning to leave. Entrepreneurs and freelancers see "Are you currently running your business full-time?" instead. | Determines whether the plan needs to fit around a day job (evenings/weekends) or can be full-time; for entrepreneurs, sets the business context for the transition |
| 3b | Roughly how many hours per week are realistically available for study, networking, and portfolio work? | Directly sizes semester content — 5 hrs/week ≠ 20 hrs/week |
| 3c | What is your financial runway — how long can you invest in this transition before you need income from the new field? | Sets urgency level and informs certification budget; short runway → free-first cert path |
| 3d | Are there geographic constraints — must stay in current city, open to relocation, remote-only preferred? | Localises target organisations and community recommendations |
| 3e | Are there any personal or family commitments (childcare, caregiving, health) that affect your study schedule? | Prevents an unrealistic pace being built into the plan |
| 3f | Work style preference in the target role — fully remote, hybrid, or in-office? | Filters out target organisations that don't match; shapes the networking and job-application strategy |
| 3g | Willingness to travel for the role? | Determines whether international postings and field-based NGO roles are relevant options |
| 3h | People management preference — want to manage a team, individual contributor, or open to either? | Directly governs which role archetypes are included in Section 2 and which are excluded |

---

### 4 — Financial Expectations

| # | Question | Why it matters |
|---|---|---|
| 4a | Are you aiming for a lateral move, a step up, or are you willing to step back in seniority or pay to break in? | Frames the risk conversation; affects which entry-level paths are included |
| 4b | Is there a minimum income level you need to protect? | Filters out transition paths that are financially unworkable for this client |

---

### 5 — Learning Style & Pace

| # | Question | Why it matters |
|---|---|---|
| 5a | How do you learn best — self-paced online, cohort/community, intensive bootcamp, or structured university program? | Shapes course recommendations in each semester card |
| 5b | Do you prefer breadth-first (explore widely, then specialise) or depth-first (go deep on one thing before the next)? | Determines semester sequencing logic |
| 5c | Are there learning formats you strongly dislike or have tried without success? | Prevents repeating approaches that don't work for this client |

---

### 6 — Network & Visibility

| # | Question | Why it matters |
|---|---|---|
| 6a | Do you have any existing contacts already working in the target domain? | Sizes the warm-network activation section; zero contacts → heavier cold-outreach strategy |
| 6b | Is your employer or professional network aware of your transition plans, or is this confidential? | Determines whether LinkedIn posting and visibility tactics need to be discreet |
| 6c | How comfortable are you with public visibility — writing, speaking, posting on LinkedIn? | Calibrates Section 7 (networking/visibility) to the client's risk tolerance |
| 6d | Do you already have a mentor, or is mentorship something to build into the plan? | Adds mentorship sourcing to the roadmap if needed |

---

### 7 — Past Attempts & Blockers

| # | Question | Why it matters |
|---|---|---|
| 7a | Have you tried to make this move before? What got in the way? | Identifies structural blockers (not just motivation gaps) to address in the plan |
| 7b | What aspects of the transition feel most uncertain or daunting right now? | Ensures the plan directly addresses the client's stated fears, not generic ones |

---

### 8 — Deliverable Preferences

| # | Question | Why it matters |
|---|---|---|
| 8a | Who will see this plan — is it for your own use, or will you share it with a sponsor, family member, or potential employer? | Affects tone and level of detail; shared plans need context that solo plans don't |
| 8b | Are there any sections you'd like to emphasise — or anything you'd like us to skip? | Respects client autonomy; avoids building sections they'll never use |
| 8c | Is there anything about your background you are particularly proud of, or anything you prefer not to highlight? | Feeds the narrative framing; some clients have non-linear histories that need careful handling |
| 8d | Do you have existing portfolio work or published work to share? (Yes / No) — if Yes, paste links (GitHub, Behance, Dribbble, personal site, LinkedIn articles, Tableau Public, Kaggle, Medium, published reports, etc.) | The portfolio section builds *on* existing evidence, not from zero; links give the consultant direct access to assess quality and framing |
| 8e | Is there anything else you'd like your consultant to know — context, timing, a specific opportunity, or anything not captured elsewhere? | Catch-all for information that doesn't fit any structured question; often surfaces the most important context |

---

### Professional Background (CV fallback — only if no CV uploaded)

| # | Question | Why it matters |
|---|---|---|
| B1 | Current or most recent job title | Core input for Section 1 professional summary |
| B2 | Industry or sector of that role | Required to frame the "transitioning from" narrative |
| B3 | Total years of professional experience | Sets seniority framing and credibility level throughout |
| B4 | Key skills in your own words | Client's self-perception of their strongest transferable assets; complements CV extraction |
| B5 | Certifications already held | Prevents the plan from suggesting credentials the client already has |

**Note on form layout:** The CV fallback block is nested directly inside the CV upload column and expands beneath it when the toggle link is clicked. It collapses automatically if the client subsequently uploads a CV. Fields are presented in a single-column stacked layout.

---

**After intake, map answers to plan sections:**

| Answer | Feeds into |
|---|---|
| Client type (job-seeker / entrepreneur / freelancer) | Plan framing throughout — job-seeker gets employer-facing assets; entrepreneur gets pivot/launch framing |
| Current domain (transitioning from) | Section 1 professional summary and "Strategic Insight" box |
| Languages and proficiency | Section 2 target organisations — international and multilateral roles; filtered out if no relevant language |
| Motivation type (proactive vs reactive) | Opening tagline box, Section 12 closing |
| Hours per week available | Semester card content volume |
| Financial runway | Section 6 certification budget (free vs paid split) |
| Geographic constraints | Section 2 target organisations |
| Work style preference (remote / hybrid / office) | Section 2 target organisations — filtered to match stated preference |
| Travel willingness | Section 2 role archetypes — field-based and international postings included or excluded |
| Management preference (IC vs manager) | Section 2 role archetypes — managerial vs individual-contributor roles |
| Target clarity level | Number of role archetypes in Section 2 |
| Specific role title (if stated) | Primary archetype in Section 2; anchors skills gap analysis |
| Learning style | Course format choices in Sections 5 & 6 |
| Network warmth | Section 7 networking strategy depth |
| Admired individuals / orgs | Section 7 target contacts |
| Portfolio links (if yes) | Section 8 portfolio — open and review each link; build on existing pieces; do not duplicate them |
| Fears and blockers | Section 12 "A Final Word" — address directly |
| Anything else (free-form) | Read carefully before generating — often contains the most important context; surface it in whichever section it is most relevant to |

---

## Inputs — what arrives and where to find it

When the client submits the intake form, an email arrives at gitonga@gmail.com containing
everything needed to start the plan. Download all attachments into the client folder before
proceeding.

| Input | Source | Required? | Purpose |
|---|---|---|---|
| Intake PDF (`[Initials]_intake_[date].pdf`) | Form submission email | Yes | Authoritative source for all preferences, constraints, context, and framing decisions |
| Current CV / résumé | Email attachment (uploaded by client) | Yes | Extract experience, titles, dates, skills, education |
| LinkedIn export or profile summary | Email attachment | Recommended | Supplement CV; confirm network and endorsements |
| Target job description | Email attachment | Yes | Anchor the skills gap analysis and role archetypes |
| Sample learning plan | Email attachment | Optional | Use as a starting point; refine rather than replace |
| Additional documents | Email attachment | Optional | Any supplementary files uploaded by the client |

**If the client provides multiple CV versions**, read all of them. Different versions often reveal
different framings of the same experience — use the most comprehensive framing in the plan.

**If any required attachment is missing** from the email, check whether the client skipped that
upload in the form, then request it directly before proceeding.

---

## Information to extract from inputs

### From the intake PDF (read this first)

The intake PDF is structured in sections matching the form. Extract and record:

- **Name, location, currency, timeline** — use verbatim on the cover page and throughout
- **Client type** (job-seeker / entrepreneur / freelancer) — determines overall plan framing; entrepreneurs get pivot or launch strategy rather than job-search assets
- **Current domain** (transitioning from) — write into Section 1 professional summary; essential for the "Strategic Insight" box
- **LinkedIn profile URL** — open this before reading the CV; it often contains more current framing
- **Languages and proficiency** — filter international and multilateral org targets; note as a differentiator if the target domain values specific languages
- **Motivation type** (proactive / reactive) — sets tone of opening tagline box and Section 12
- **Target domain and clarity level** — determines number of role archetypes in Section 2 and confidence of language throughout
- **Specific role title** (if provided) — use as the primary archetype; treat all others as secondary options
- **Preferred org types + ruled-out sectors** — directly populates Section 2 target organisation list; prunes irrelevant options
- **Work style preference** (remote / hybrid / office) — filter Section 2 org targets to match; note explicitly if the client's preference conflicts with the target domain's norms
- **Travel willingness** — include or exclude field-based and international postings accordingly
- **Management preference** (IC vs manager) — determines role seniority framing and which archetypes are included
- **Hours/week available** — scales semester card content (≤10 hrs → lighter load per semester; ≥25 hrs → fuller content)
- **Financial runway** — if short (< 6 months), weight Section 6 heavily toward free/low-cost certifications; flag urgency in roadmap framing
- **Geographic constraints** — localise all org targets, communities, and events to the stated geography
- **Employment / business status** — for job-seekers: if transitioning while employed, semester plans must fit evenings/weekends; note this in each semester card. For entrepreneurs/freelancers, `entrepreneur_status` indicates whether full-time, part-time, or exploring a new area — frame the plan accordingly
- **Move type** (lateral / step up / step back) — frames the risk narrative in Section 10 and milestone sequencing in Section 11
- **Income floor** — filters out transition paths that are financially unworkable; note in Section 6 budget
- **Preferred learning formats** — every course recommendation in Sections 5 and 6 must match the stated format preferences
- **Learning preference** (breadth vs depth) — determines whether Semester 1 introduces broadly or dives immediately into the core specialism
- **Network warmth** — if thin (0–3 contacts), Section 7 needs heavier cold-outreach and community-joining tactics; if strong, activate warm network earlier
- **Transition confidentiality** — if confidential, all LinkedIn tactics in Section 7 must be discreet (commenting, not posting; private DMs, not public tagging)
- **Visibility comfort** — scales Section 7 content creation recommendations from none → heavy
- **Mentor status** — if no mentor wanted, remove mentorship sourcing tasks from tracker; if wanted, add sourcing steps to Semester 1
- **Past attempts and blockers** — address the specific blocker directly in Section 12; do not offer generic encouragement
- **Fears and biggest uncertainties** — name them explicitly in "A Final Word" and show how the plan mitigates each
- **Portfolio links** — if `portfolio_has_work` is "yes", **fetch each URL with WebFetch before drafting Section 8**. For each link: note the platform, read the content, extract the domain area, assess quality signal and recency, and identify what the piece demonstrates. Use this directly in the portfolio section — do not rely on the client's description alone. If a link returns a login wall, 403, or 404, note it as inaccessible and proceed with the remaining links. LinkedIn profile URLs frequently block automated access; treat them as unreliable and use the LinkedIn export file or URL as a secondary reference instead.
- **Plan audience** — if shared with an employer or sponsor, increase context and polish; if solo, keep it direct and practical
- **Sections to emphasise / background notes** — honour these explicitly; if client flagged something to handle with care, do so
- **Anything else (free-form)** — read this field before generating; it often contains timing context, a specific opportunity, or a constraint that completely changes the framing. Surface it in the most relevant plan section rather than ignoring it.
- **Professional background self-report** (if no CV uploaded) — treat current_title, current_industry, years_experience, key_skills, and existing_certs as the source of truth in place of the CV; note in the plan that figures are self-reported

### From the CV(s)
- Most recent job title and employer
- Years of experience (total and in primary domain)
- Geographic scope (local / regional / multi-country)
- Industries covered
- Team leadership and scale
- Education and any existing certifications
- Named references or colleagues (used in networking section)
- Specific achievements that can be reframed for target sectors

### From the job description
- Role category (governance / compliance / advisory / ESG / development / etc.)
- Sector context (NGO / tech / corporate / government / multilateral)
- Explicit skills required (hard skills: frameworks, tools, certs)
- Implicit skills required (soft skills: stakeholder engagement, writing, training)
- Skills the client already has at sufficient level → mark "No Gap"
- Skills the client is missing → feed into gap analysis and semester plans

### From the learning plan (if provided)
- Which domains the client has already identified
- Sequencing logic they are comfortable with
- Courses or certs they have already considered

---

## Document structure

Produce these sections in order. Each section has a fixed purpose; the content is client-specific.

### Cover Page
- Full client name
- Subtitle: "Career Transition Plan"
- Tagline line: "From [Current Domain] to [Target Domain(s)]"
- City, country, and plan date
- Confidentiality notice

### Opening tagline box (motivational framing)
- One short paragraph: reframe the transition as a strategic extension, not a restart
- Tone: confident advisory, not cheerleading

### Section 1 — Your Starting Point
- 3–4 sentence professional summary (drawn from CV)
- Two-column bullet list of core strengths the client already owns
- "Strategic Insight" box: explain WHY the client's background is an asset in the target domain

### Section 2 — Where You Are Heading
- Table of 3–5 target role archetypes: Role | Sector | Why Client Fits
- Two-column list of 8–10 target organisations (localised to client geography)

### Section 3 — Skills Gap Analysis
Table: Skill/Knowledge Area | Current Level | Required Level | Gap | Priority

Levels: Expert / Proficient / Working / Aware / Beginner / None
Gap: None / Minor / Medium / Large / Moderate
Priority: — / LOW / MED / HIGH

Highlight HIGH-priority rows visually (colour the priority cell).

### Section 4 — The Transition Roadmap (Overview)
- 1 paragraph framing the overall structure
- Summary table: Semester | Theme | Duration | Period | Key Output
- Note parallel tracks (networking, content creation, mentorship, job-readiness)

### Section 5 — Detailed Semester Plans
One card per semester. Each card contains:
- Header: Semester number, title, and duration dates
- Objective (2–4 sentences: what the client will be able to do by the end)
- Core Topics (specific named courses, frameworks, standards — not vague "study AI")
- Deliverables / Milestones (concrete, countable outputs)
- "Connects to [client name]'s background" (bridge between their past and the new domain)

Default semester structure for an 18-month plan:

| Sem | Theme | Duration |
|---|---|---|
| 1 | Digital/Domain Foundations | 2 months |
| 2 | Core Specialisation | 3 months |
| 3 | Complementary Domain 1 | 2 months |
| 4 | Complementary Domain 2 | 3 months |
| 5 | Intersection / Niche | 3 months |
| 6 | Leadership, Strategy & Market Launch | 3 months |

### Section 6 — Certifications Roadmap
Table: Certification | Provider | Cost (USD) | Semester | Impact

- Lead with free or low-cost options
- Group paid certifications by tier (entry / specialist / advanced)
- Include a total budget estimate with local currency conversion
- Note scholarship or discount options where they exist

### Section 7 — Networking & Visibility Strategy
- LinkedIn strategy (posting cadence, commenting, profile updates, hashtags)
- Communities to join (table: Community | Why)
- Existing network activation (how to leverage current contacts for warm introductions)

### Section 8 — Portfolio Building
Table: # | Portfolio Piece | Created In (Semester) | What It Demonstrates

- 6–10 portfolio pieces
- Each piece should be producible without an employer (mock organisations, hypothetical scenarios)
- End with a tip: compile into a single portfolio PDF with a cover page

### Section 9 — Monthly Action Tracker
Table: Month | Learning Focus | Networking Action | Portfolio / Visibility

- One row per month of the plan
- Keep each cell brief (3–5 items max)
- This is the client's accountability tool — it should be printable

### Section 10 — Positioning & Narrative
- Elevator pitch (full draft, ready to use, ~100 words)
- CV reframing table: Old language | Target Sector Reframe A | Target Sector Reframe B
  - 4–6 rows covering the client's most significant experience bullets

### Section 11 — Success Metrics
Table: Milestone | Target Date | Status (blank column for client to fill in)

- 12–18 milestones from first certificate to first job application to offer
- Include optional milestones (certifications, speaking, publishing)

### Section 12 — A Final Word
- 3-paragraph closing: motivational, honest, specific to this client's situation
- Remind the client of the specific advantage their background provides
- End with an action instruction, not a question

---

## PDF generation approach

Use Python with ReportLab (`reportlab` package). Do not use Markdown-to-PDF converters or
browser-print pipelines — they cannot produce the table layouts and colour blocks this document requires.

### Colour palette (default — adjust per brand preference)
```python
NAVY  = "#1B2A4A"   # Primary dark: section headers, table headers
TEAL  = "#0E7C7B"   # Secondary: h3 headings, alternating header colour
GOLD  = "#C9A84C"   # Accent: cover subtitle, rule lines
LGRAY = "#F4F6F9"   # Background: alternating table rows, shaded boxes
MGRAY = "#D0D6E0"   # Borders and grid lines
WHITE = "#FFFFFF"
BLACK = "#1A1A1A"   # Body text
```

### Page setup
- Page size: A4
- All margins: 1.27 cm (0.5 inch) — tight but readable
- Footer: page number and document title, 8pt, centered

### Key ReportLab patterns used
- `SimpleDocTemplate` with `story` list pattern
- `Table` + `TableStyle` for all structured content (no bare `Paragraph` grids)
- `KeepTogether` to prevent section headers orphaning from first content
- `PageBreak` after cover, roadmap overview, tracker, and positioning sections
- `HRFlowable` for horizontal rules between sections
- `ParagraphStyle` defined once at the top and reused throughout

### Helper functions to define
- `section_header(text)` — navy background banner with white bold text
- `shaded_box(content_rows)` — light grey box with rounded corners for callouts
- `two_col(left_items, right_items)` — side-by-side bullet columns
- `semester_card(sem_num, duration, title, objective, topics, deliverables, connects_to)` — full semester block
- `rule(color, thickness)` — horizontal rule

### Output
- Save to the client's folder, named: `[initials]_transition_plan.pdf`
- Print the output path on completion

---

## Quality checklist before delivering

### Security checks (run first)
- [ ] No client data (intake PDFs, CVs, JDs) exists outside `Clients/` — confirm with `git status`
- [ ] `Clients/` does not appear in `git add` or `git commit` output
- [ ] `generate_security_pdf.py` is not tracked (`git ls-files generate_security_pdf.py` returns nothing)
- [ ] No personally identifiable information is in any committed file or git log entry
- [ ] If any new dependency was added, it is pinned in `requirements.txt`

### Content checks
- [ ] Client's name appears exactly as on their CV (check middle initial, spelling)
- [ ] All experience claims traced back to CV (no invented facts)
- [ ] All course names are real and currently available (verify provider names)
- [ ] Certification costs are approximate and flagged as such
- [ ] Target organisations are real and active in the client's geography
- [ ] Semester dates are consistent (no gaps, no overlaps, correct months)
- [ ] Budget total in section 6 matches itemised rows
- [ ] Elevator pitch uses first person and feels natural spoken aloud
- [ ] CV reframing table uses language from actual job postings, not generic HR-speak
- [ ] Portfolio pieces are achievable without an employer or paid access
- [ ] Monthly tracker rows match semester plan content (no inconsistencies)
- [ ] PDF renders without errors (`doc.build(story)` completes cleanly)
- [ ] All pages have a footer with page number

---

## Customisation points by client type

### Client from corporate / multinational background
- Emphasise transferable frameworks and governance language
- Target both private sector and NGO/multilateral roles
- Use their employer's name directly in the narrative (it carries brand weight)

### Client from government / public sector background
- Emphasise policy and regulatory expertise
- Target multilateral agencies, development finance, and tech-policy roles
- Note clearance levels or government relationships as a differentiator

### Client from NGO / international development background
- Emphasise impact measurement, donor compliance, and cross-cultural programme management
- Target corporate ESG / sustainability roles, UN agencies, and think tanks
- Reframe programme delivery language into operations and governance language

### Shorter timeline (6–12 months)
- Compress to 3–4 semesters
- Prioritise one target role archetype instead of four
- Focus certifications on the single highest-signal credential
- Remove Semester 5 (niche intersection) and fold into Semester 4

### Longer timeline (24+ months)
- Add a "Year 2 advanced track" section after the 18-month plan
- Include options for part-time study alongside employment
- Add a consulting / freelance strategy section for clients who want to bridge domains while still employed

---

## Files to keep in the client folder

```
Clients/
└── [ClientName]/
    ├── [Initials]_intake_[date].pdf      ← intake form responses (from submission email)
    ├── [original CV files]               ← source material (do not delete)
    ├── [JD file]                         ← job description used for gap analysis
    ├── [Learning Plan file]              ← client's initial learning plan (if provided)
    ├── [Additional files]                ← any other documents uploaded by the client
    ├── generate_plan.py                  ← the plan generation script (keep; re-run to update)
    └── [initials]_transition_plan.pdf    ← the deliverable
```

The intake PDF is the record of what the client told you. Keep it permanently — it is the
audit trail if the client later disputes the framing or asks why certain choices were made.

Always keep `generate_plan.py` alongside the PDF. If the client requests a change (date update,
new target role, revised semester), edit the script and re-run — do not edit the PDF directly.

---

## Example invocation

```
"[Client name] has submitted their intake form. Their intake PDF, CV, and job description
are in the [ClientName]/ folder. Read the intake PDF first, then the CV and JD, and
generate the transition plan PDF."
```

Point to this SKILL.md and the process above will be followed without further prompting.

If the intake form has not yet been submitted, send the client the loading page link
(this handles cold-start gracefully and redirects to the form automatically):

```
https://career-transition-loading.onrender.com
```
