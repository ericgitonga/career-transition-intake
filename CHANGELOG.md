# Changelog

All notable changes to this project are documented here. Versioning follows
[Semantic Versioning](https://semver.org): MAJOR.MINOR.PATCH. This project is
pre-1.0 (initial development) — the major version stays at `0` until a stable,
production-ready release is declared. MINOR bumps cover new features and
user-facing changes; PATCH bumps cover fixes, docs, and housekeeping.

## [0.20.2] - 2026-07-17
### Changed
- `generate_design_pdf.py` is now tracked instead of gitignored: a check of
  its content (every email address, every capitalised two-word phrase, every
  SECRET_KEY/API_KEY-shaped string) confirmed it holds no client data or
  real secrets — only project narrative, the approved fictitious Alex Mercer
  example, a generic "Jane Doe" placeholder, and environment-variable
  *names* already documented in tracked SKILL.md and render.yaml, never a
  value. It had been gitignored only by inherited convention (grouped with
  three other generators that do hold private data), not by its own
  content. Its output, `extras/design_process.pdf`, stays gitignored as a
  generated artefact.
- Updated SKILL.md's client-data-handling rules and generate_design_pdf.py's
  own Key Design Decisions section to document this. (closes #33)

tag: `v0.20.2`

## [0.20.1] - 2026-07-17
### Changed
- `generate_design_pdf.py` and `generate_security_pdf.py` now write their
  output (`design_process.pdf`, `security.pdf`) to `extras/` instead of
  `Clients/` — both are internal project documents, not client data, and
  writing them into `Clients/` alongside actual client folders was a source
  of real confusion when looking for the file. Matches the convention
  `generate_feedback_pdf.py` already used. Overwrote a stale
  `extras/design_process.pdf` copy left over from earlier in the project
  with a freshly regenerated one.
- Updated SKILL.md's client-data-handling rules to reflect the new location
  and `generate_design_pdf.py`'s own Key Design Decisions section to
  document the move. (closes #32)

tag: `v0.20.1`

## [0.20.0] - 2026-07-17
### Added
- Extracted a shared `report_builder.py` (root, tracked) holding all ReportLab
  palette, paragraph styles, layout helpers, and per-section rendering logic
  that used to be duplicated at the top of every client's own
  `generate_plan.py` (~250 lines of identical boilerplate each). Added a
  thin root-level `generate_plan.py` CLI (`python3 generate_plan.py
  "<Client Name>"`) that loads `Clients/<Name>/plan_data.py`'s `PLAN` dict
  and calls `report_builder.build_plan()`.
- Defined the `plan_data.py` schema: fixed-shape sections (2, 3, 5, 8, 9, 11)
  as structured lists of dicts; freeform sections (1, 4, 6, 7, 10, 12) as a
  generic `blocks` list (paragraph / shaded_box / two_col / table) rendered
  by one shared `render_blocks()` — no per-client ReportLab code anywhere.
- Migrated Alex Mercer's plan to `Clients/Alex Mercer/plan_data.py` as the
  round-trip proof and removed the old per-client `generate_plan.py`; the
  rendered PDF is byte-for-byte equivalent in content (17 pages, 5,252 words,
  confirmed via `pdftotext` diff — the only differences were word-wrap order
  inside the Monthly Action Tracker table, not missing content).
- Existing real clients' `generate_plan.py` scripts are left as delivered
  (not retroactively migrated); new clients use the shared engine going
  forward.
- Updated SKILL.md (PDF generation approach, workflow steps 4–5, files to
  keep in the client folder) to document the new architecture and updated
  generate_design_pdf.py/design_process.pdf accordingly. (closes #31)

tag: `v0.20.0`

## [0.19.3] - 2026-07-17
### Changed
- Backfilled the git tags CHANGELOG.md had already been claiming existed
  (v0.18.0, v0.19.0, v0.19.1, v0.19.2) at the commits their issue references
  point to, and pushed them.
- Published a GitHub Release for every version from v0.1.0 through v0.19.2
  (31 total), built from each CHANGELOG.md entry's own subheading and
  bullets plus a Full-Changelog compare link to the previous tag.
- Reworded three CHANGELOG.md entries (v0.18.0, v0.19.0, v0.19.2) that had
  named real clients as the motivating example behind a fix, replacing the
  names with a generic description, and edited the matching GitHub Release
  bodies to match. Also scrubbed the equivalent mentions from
  generate_design_pdf.py, since a gitignored file is not the same as a safe
  one.
- SKILL.md now requires a pushed git tag and a published GitHub Release as
  the last step of every version bump, and explicitly prohibits naming a
  real client anywhere — tracked or gitignored, published or purely local.
  Alex Mercer, the fictitious demo client, is the one standing exception and
  is now the reference example wherever SKILL.md needs to point to a
  concrete case.
- Added `Clients/Alex Mercer/generate_gap_note.py`, producing a fictitious
  `gap.pdf` for a hypothetical thin intake (no CV, no JD), so the gap-note
  pattern referenced in SKILL.md's Document Uploads rule has a nameable
  example instead of pointing at a real client's folder.
- Documented all three decisions in generate_design_pdf.py's Key Design
  Decisions section and regenerated design_process.pdf. (closes #29)

tag: `v0.19.3`

## [0.19.2] - 2026-07-17
### Changed
- Added a standing content rule to SKILL.md: every acronym or abbreviation a
  client would not already know must be spelled out in full (acronym in
  parentheses) the first time it appears anywhere in a generated plan, by
  reading order, and used as the acronym alone afterwards, including inside
  tables. Terms already standard in this workflow's vocabulary (CV, NGO, CEO,
  PDF, currency codes) are exempt. Added a matching quality-checklist item.
- Documented the decision in generate_design_pdf.py's Key Design Decisions
  section and regenerated design_process.pdf.
- Fixed a client plan generated before this rule existed, where several
  acronyms were either never expanded or expanded out of reading order.
  (closes #28)

tag: `v0.19.2`

## [0.19.1] - 2026-07-15
### Changed
- Reworded the two smaller "Preferred organisation stage" checkbox labels in
  Section 2 of the intake form: "Early-stage startup (seed / Series A)" →
  "Early-stage business"; "Growth-stage startup (Series B+)" → "Growth-stage
  business". The dropped parenthetical was US venture-capital funding-round
  terminology that doesn't reflect the primary client base (Kenya-based),
  where most target employers aren't venture-funded in that sense. The five
  underlying tiers and their team-size/maturity descriptions are unchanged.
  (closes #25)

tag: `v0.19.1`

## [0.19.0] - 2026-07-15
### Changed
- Section 10's non-blocking encouragement banner (0.18.0 / #23) is superseded
  by an actual requirement: submission now needs either a CV/business-profile
  upload or at least one CV-fallback field filled in, enforced both
  client-side (`form.js`) and server-side (`app.py`, HTTP 400 with a
  plain-English message if bypassed).
- The CV field now reuses Section 1's existing `client_type` answer (no new
  question) to relabel itself: job-seekers/employees/"Other" see "CV /
  Résumé"; entrepreneurs and freelancers see "Business Profile / Pitch Deck"
  — the same grouping already used for Section 4's employment-vs-business
  split, factored into a shared `_is_entrepreneur_type()` helper in
  `app.py`.
- Motivated by discovering that both prior thin-data intakes were
  job-seeker/freelancer types, not entrepreneurs — the old "(optional for
  entrepreneurs)" label had never actually been enforced for anyone.
  (closes #24)

tag: `v0.19.0`

## [0.18.0] - 2026-07-15
### Added
- Static, non-blocking encouragement banner in Section 10 (Document Uploads),
  inviting clients to fill in a CV, target job description, or the CV
  fallback fields — framed positively ("the more we have, the better the
  plan"), never as a warning or a requirement. No validation gating was
  added; submission is unaffected. Added after two prior intakes arrived
  with neither a CV nor the fallback fields filled in, which meant no
  meaningful plan could be generated and a manual gap-note follow-up was
  needed instead. (closes #23)

tag: `v0.18.0`

## [0.17.0] - 2026-07-15
### Security
- Second security audit, covering everything changed since the S-01–S-15
  hardening pass: S-16 log-line forgery / field-hijack in the submission log
  (fixed via sanitizing and percent-encoding logged fields, `_log_field()`);
  S-17 spreadsheet formula injection in `onboard_metrics.xlsx` (fixed via a
  leading-apostrophe guard, `_safe_cell()`, in both `extras/` scripts); S-18
  a real Render service ID hardcoded in a public, tracked script (replaced
  with a placeholder); S-19 client slug not restricted to safe filename
  characters, allowing path-like sequences into ZIP archive entry names
  (fixed by restricting `_client_slug()` to letters/digits/hyphen/underscore).
  Also removed a stale, superseded `loading.html` left at the repo root.
  (closes #22)

tag: `v0.17.0`

## [0.16.1] - 2026-07-15
### Changed
- Added an "Inference Discipline" section to SKILL.md: every claim in the
  generated plan must trace back to something the client explicitly stated;
  connections between two stated facts are encouraged, but no assumption may
  be invented to fill an unstated gap. (closes #21)

tag: `v0.16.1`

## [0.16.0] - 2026-07-15
### Added
- Semantic versioning introduced: `VERSION` file, this changelog, retroactive
  version tags across the full commit history, and a versioning policy
  documented in `SKILL.md`. (closes #20)
- Current version displayed at the bottom of the intake form's header,
  read live from `VERSION` via a new `app_version` template variable.

tag: `v0.16.0`

## [0.15.0] - 2026-07-15
### Added
- Privacy statement on the intake form clarifying submitted data is used only
  to generate the client's plan and is not shared with any third party.
  (closes #19)

commit: `75947c2`

## [0.14.0] - 2026-07-14
### Added
- Submission metrics system: hidden time-on-form field captured on submit;
  local scripts to pull Render logs and log processed-plan turnaround into a
  tracked spreadsheet. (closes #18)

commits: `3d79d41`, `47905ae`, `44a5f74`

## [0.13.1] - 2026-07-14
### Added
- Free-text clarification field shown when "Other" is selected for client
  type. (closes #17)

commit: `c9bb4f6`

## [0.13.0] - 2026-07-14
### Added
- Client-type conditional logic (job-seeker / entrepreneur / freelancer)
  driving employment vs. business-status questions; improved
  organisation-stage descriptions. (closes #16)

commit: `bc6b1d5`

## [0.12.1] - 2026-07-14
### Changed
- Plan generator instructed to fetch each portfolio link via WebFetch before
  drafting the portfolio section. (closes #15)

commit: `fc9b16e`

## [0.12.0] - 2026-07-14
### Changed
- Portfolio textarea replaced with dynamic add/remove link fields. (closes #14)

commit: `1b6bf91`

## [0.11.1] - 2026-07-14
### Fixed
- CV fallback block position corrected; added a free-form notes field.
  (closes #13)

commit: `1cb141a`

## [0.11.0] - 2026-07-14
### Added
- Client segmentation, CV fallback block, and work-style / travel /
  management-preference fields.

commit: `7c4ec23`

## [0.10.1] - 2026-07-12
### Changed
- SKILL.md wording clarified.

commit: `693c595`

## [0.10.0] - 2026-07-11
### Changed
- Intake files now named by client slug; uploads bundled into a single ZIP
  attachment.

commit: `61bc1a2`

## [0.9.1] - 2026-07-11
### Changed
- User-facing message wording edits; user-facing behaviour rules documented in
  SKILL.md; design_process.pdf updated with loading-screen UX notes;
  cold-start feedback captured; private PDF generators and report files
  untracked from git.

commits: `d6a1191`, `ffc89d1`, `12650ad`, `8bf4c0a`, `1934952`

## [0.9.0] - 2026-07-11
### Added
- Clean branded loading screen replacing Render's default cold-start page;
  moved to its own static subdirectory.

commits: `4d20731`, `5736c2f`

## [0.8.0] - 2026-07-10
### Changed
- Round 1 client feedback applied: form flow adjustments, a new question, UX
  copy improvements, and better error handling.

commit: `2ba1e8c`

## [0.7.1] - 2026-07-10
### Changed
- Design process report updated with security content; added `extras/` folder
  for local-only tooling.

commits: `c8a2ae6`, `22517ab`

## [0.7.0] - 2026-07-10
### Security
- All 15 findings from the internal security audit resolved (CSRF, rate
  limiting, upload validation, security headers, etc.); `SECRET_KEY`
  auto-generated locally when absent from the environment; private audit
  script gitignored.

commits: `980f026`, `5d4301d`, `8485fc4`

## [0.6.0] - 2026-07-10
### Added
- Self-hosting guide generator (`generate_selfhosting_pdf.py`); docstrings
  added throughout `generate_design_pdf.py`.

commits: `caf552d`, `b9bc80e`

## [0.5.1] - 2026-07-10
### Removed
- Leftover Gradio references cleaned up; SKILL.md updated for the hosted Flask
  form.

commit: `7773cd5`

## [0.5.0] - 2026-07-10
### Added
- Design-process report generator (`generate_design_pdf.py`) producing an
  internal record of the project's design decisions.

commit: `fdd986a`

## [0.4.1] - 2026-07-10
### Added
- Hosting guide (`hosting.pdf`) added to the repo; docs updated for the Flask
  + Resend stack; docstrings added throughout `app.py` and
  `generate_hosting_pdf.py`.

commits: `7b18c00`, `2d7a132`

## [0.4.0] - 2026-07-09
### Changed
- Form UI refresh: dark theme applied, header text updated, multi-file upload
  field added; Email Settings section and headshot upload field removed.

commits: `9ab0104`, `82383df`, `5306675`

## [0.3.0] - 2026-07-09
### Changed
- Email delivery switched from SMTP to the Resend API, fixing an SMTP worker
  timeout; App Password setup guide added as an SMTP fallback reference.

commits: `c4a29af`, `9e00762`

## [0.2.0] - 2026-07-09
### Changed
- Hosting migrated from Hugging Face Spaces through Google Cloud Run to
  Render; Gradio replaced entirely with Flask after repeated
  platform-specific crashes (dependency pinning, a localhost-check bypass,
  boolean-schema patches, and more along the way).

commits: `6310f7a`, `7e4c88c`, `539ba22`, `852f9e4`, `963c651`, `08fabc6`,
`a5aa717`, `6eb4473`, `ffc6cf9`, `8f9722b`, `29d314a`, `5e4fb06`, `de53d0a`

## [0.1.1] - 2026-07-09
### Changed
- Client data moved under `Clients/`; `.gitignore` and SKILL.md updated;
  `hosting.md` and `generate_hosting_pdf.py` added to `.gitignore`.

commits: `36a56c2`, `bca30b6`, `d47a625`

## [0.1.0] - 2026-07-09
### Added
- Initial onboarding intake form and Hugging Face deploy workflow.

commit: `fa58da1`
