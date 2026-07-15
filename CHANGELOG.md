# Changelog

All notable changes to this project are documented here. Versioning follows
[Semantic Versioning](https://semver.org): MAJOR.MINOR.PATCH. This project is
pre-1.0 (initial development) — the major version stays at `0` until a stable,
production-ready release is declared. MINOR bumps cover new features and
user-facing changes; PATCH bumps cover fixes, docs, and housekeeping.

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
