"""
Generate extras/design_process.pdf — a comprehensive record of the design
process, technical decisions, security architecture, and cost analysis for
the Career Transition client onboarding form.

The report covers ten numbered sections:
  1   Executive Summary
  2   Project Brief & Objectives
  3   Platform Selection Journey
  4   Technical Architecture
  5   Security Architecture (audit findings + remediation)
  6   UI / UX Design
  7   Key Design Decisions
  8   Development Phases & Effort Breakdown
  9   Cost Analysis (Nairobi + Global markets, security-adjusted)
  10  Final Deliverable

Usage:
    python generate_design_pdf.py
    # → extras/design_process.pdf
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Preformatted,
    HRFlowable, KeepTogether, Table, TableStyle, PageBreak,
)

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "extras", "design_process.pdf")

NAVY    = colors.HexColor("#1B2A4A")
TEAL    = colors.HexColor("#0E7C7B")
GOLD    = colors.HexColor("#C9A84C")
MGRAY   = colors.HexColor("#D0D6E0")
BLACK   = colors.HexColor("#1A1A1A")
WHITE   = colors.white
CODE_BG = colors.HexColor("#EAEEF4")
LIGHT   = colors.HexColor("#F7F9FC")
RED     = colors.HexColor("#C0392B")
GREEN   = colors.HexColor("#1A7A4A")
AMBER   = colors.HexColor("#E67E22")

W, H    = A4
MARGIN  = 1.5 * cm
INNER_W = W - 2 * MARGIN


# ── Styles ────────────────────────────────────────────────────────────────────

def styles():
    """Build and return all named paragraph styles used throughout the document.

    Centralising styles here prevents scattered ParagraphStyle definitions
    across layout functions and makes typography changes straightforward.
    The inner helper ``S`` is a shorthand so each style fits on one line.

    Returns:
        A dictionary mapping short string keys to ParagraphStyle instances:
          - ``"title"``    — large white centred title for the cover block.
          - ``"subtitle"`` — gold centred sub-title for the cover block.
          - ``"meta"``     — small grey centred metadata (author, date).
          - ``"h2"``       — navy bold heading for major sub-topics.
          - ``"h3"``       — teal bold heading for sub-section labels.
          - ``"body"``     — justified body text for descriptive paragraphs.
          - ``"bullet"``   — indented body text for bullet-point lists.
          - ``"code"``     — monospaced Courier for inline code snippets.
          - ``"note"``     — small oblique grey text for caveats and asides.
          - ``"bold"``     — teal bold text for summary/emphasis lines.
          - ``"label"``    — navy bold for field-label style text in tables.
          - ``"cell"``     — standard Helvetica for table body cells.
          - ``"cell_bold"``— bold Helvetica for emphasised table body cells.
          - ``"th"``       — white bold for table header cells (navy background).
          - ``"good"``     — green bold for positive outcome cells (✓ rows).
          - ``"bad"``      — red bold for negative outcome cells (✗ rows).
          - ``"total"``    — navy bold for cost-summary totals.
    """
    def S(name, **kw):
        """Shorthand constructor that forwards keyword arguments to ParagraphStyle.

        Args:
            name: Internal style name (must be unique within a ReportLab document).
            **kw: Any keyword arguments accepted by ParagraphStyle.

        Returns:
            A configured ParagraphStyle instance.
        """
        return ParagraphStyle(name, **kw)

    return {
        "title":    S("title",  fontName="Helvetica-Bold",   fontSize=22, textColor=WHITE,
                      leading=28, alignment=TA_CENTER),
        "subtitle": S("sub",    fontName="Helvetica-Bold",   fontSize=13, textColor=GOLD,
                      leading=18, alignment=TA_CENTER),
        "meta":     S("meta",   fontName="Helvetica",         fontSize=9,  textColor=MGRAY,
                      leading=13, alignment=TA_CENTER),
        "h2":       S("h2",     fontName="Helvetica-Bold",   fontSize=13, textColor=NAVY,
                      leading=18, spaceBefore=12, spaceAfter=4),
        "h3":       S("h3",     fontName="Helvetica-Bold",   fontSize=10.5, textColor=TEAL,
                      leading=14, spaceBefore=8, spaceAfter=3),
        "body":     S("body",   fontName="Helvetica",         fontSize=9.5, textColor=BLACK,
                      leading=14, spaceAfter=5, alignment=TA_JUSTIFY),
        "bullet":   S("bullet", fontName="Helvetica",         fontSize=9.5, textColor=BLACK,
                      leading=14, spaceAfter=3, leftIndent=14),
        "code":     S("code",   fontName="Courier",           fontSize=8.5, textColor=BLACK,
                      leading=13, leftIndent=8, rightIndent=8),
        "note":     S("note",   fontName="Helvetica-Oblique", fontSize=8.5,
                      textColor=colors.HexColor("#555555"), leading=12, spaceAfter=5),
        "bold":     S("bold",   fontName="Helvetica-Bold",    fontSize=10,  textColor=TEAL,
                      leading=14, spaceAfter=6),
        "label":    S("label",  fontName="Helvetica-Bold",    fontSize=9,   textColor=NAVY,
                      leading=12),
        "cell":     S("cell",   fontName="Helvetica",         fontSize=9,   textColor=BLACK,
                      leading=12),
        "cell_bold":S("cb",     fontName="Helvetica-Bold",    fontSize=9,   textColor=BLACK,
                      leading=12),
        "th":       S("th",     fontName="Helvetica-Bold",    fontSize=9,   textColor=WHITE,
                      leading=12),
        "good":     S("good",   fontName="Helvetica-Bold",    fontSize=9,   textColor=GREEN,
                      leading=12),
        "bad":      S("bad",    fontName="Helvetica-Bold",    fontSize=9,   textColor=RED,
                      leading=12),
        "total":    S("total",  fontName="Helvetica-Bold",    fontSize=10,  textColor=NAVY,
                      leading=14, spaceAfter=4),
    }


# ── Helpers ───────────────────────────────────────────────────────────────────

def rule(color=GOLD, thickness=1, before=6, after=8):
    """Create a horizontal rule flowable for visual separation between sections.

    Used in two roles: a thick gold rule immediately after the cover block
    to anchor the document's brand identity, and thin grey rules between
    numbered sections to provide breathing room without heavy visual weight.

    Args:
        color:     ReportLab color for the rule line. Defaults to GOLD.
        thickness: Line thickness in points. Defaults to 1.
        before:    Vertical space in points above the rule. Defaults to 6.
        after:     Vertical space in points below the rule. Defaults to 8.

    Returns:
        A ReportLab HRFlowable spanning the full content width (100%).
    """
    return HRFlowable(width="100%", thickness=thickness, color=color,
                      spaceBefore=before, spaceAfter=after)


def section_header(text, s):
    """Create a full-width navy banner that opens each numbered document section.

    The banner matches the visual language used in the intake PDF itself,
    reinforcing the brand identity within the report. Text is rendered in
    bold white on a navy background spanning the full content width (INNER_W).

    Args:
        text: The section title to display, including its number prefix
              (e.g. "1. Executive Summary"). Supports basic HTML tags.
        s:    The styles dictionary returned by ``styles()``. Accepted for
              API consistency with other helpers, though this function
              defines its own inline ``"sh"`` style.

    Returns:
        A ReportLab Table flowable styled as a full-width navy banner.
    """
    p = Paragraph(text, ParagraphStyle(
        "sh", fontName="Helvetica-Bold", fontSize=11,
        textColor=WHITE, leading=14))
    t = Table([[p]], colWidths=[INNER_W])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), NAVY),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))
    return t


def sub_header(text, s):
    """Create a teal-accented sub-section label for platform phases and architecture topics.

    Visually lighter than ``section_header`` — a light grey background with a
    3-point teal left border — so it nests clearly within a numbered section
    without competing with the navy section banner above it.

    Args:
        text: The sub-section label text. Supports basic HTML tags.
        s:    The styles dictionary returned by ``styles()``. Accepted for
              API consistency; this function defines its own inline ``"ssh"`` style.

    Returns:
        A ReportLab Table flowable with a teal left border and light background.
    """
    p = Paragraph(text, ParagraphStyle(
        "ssh", fontName="Helvetica-Bold", fontSize=10,
        textColor=TEAL, leading=14))
    t = Table([[p]], colWidths=[INNER_W])
    t.setStyle(TableStyle([
        ("LINEAFTER",     (0, 0), (0, -1), 0, WHITE),
        ("LINEBEFORE",    (0, 0), (0, -1), 3, TEAL),
        ("BACKGROUND",    (0, 0), (-1, -1), LIGHT),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
    ]))
    return t


def phase_table(rows, s, col_widths=None):
    """Build a styled data table with a navy header row and alternating body rows.

    Used for three distinct tables in the document:
      - Platform comparison summary (Section 3): outcome cells containing ✓ or ✗
        are automatically coloured green or red respectively.
      - Effort breakdown by phase (Section 8): phase name, description, hours.
      - Cost analysis tables (Section 9): discipline, rate, hours, subtotal.

    The first element of ``rows`` is treated as the header row and rendered with
    white bold text on a navy background. Subsequent rows alternate between two
    light grey shades for readability. The table repeats the header row on page
    breaks (``repeatRows=1``).

    Cells whose string value starts with "✓" are rendered in green bold; cells
    starting with "✗" are rendered in red bold. All other cells use the standard
    ``"cell"`` style.

    Args:
        rows:       List of lists where the first list is column headers and the
                    remaining lists are data rows. All values are converted to
                    strings via ``str()``.
        s:          The styles dictionary returned by ``styles()``.
        col_widths: Optional list of column widths in points that must sum to
                    INNER_W. If None, a single column spanning INNER_W is used.

    Returns:
        A fully styled ReportLab Table flowable.
    """
    if col_widths is None:
        col_widths = [INNER_W]
    header, *data = rows
    table_data = [
        [Paragraph(str(c), s["th"]) for c in header]
    ] + [
        [Paragraph(str(c), s["cell"]) if not str(c).startswith("✓") and not str(c).startswith("✗")
         else Paragraph(str(c), s["good"] if str(c).startswith("✓") else s["bad"])
         for c in row]
        for row in data
    ]
    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  NAVY),
        ("BACKGROUND",    (0, 1), (-1, -1), LIGHT),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [LIGHT, colors.HexColor("#EDF0F5")]),
        ("GRID",          (0, 0), (-1, -1), 0.4, MGRAY),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 7),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 7),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def b(text):
    """Wrap a string in ReportLab-compatible bold HTML tags.

    ReportLab's Paragraph renderer supports a limited subset of HTML inline
    tags. This helper avoids repeating the ``<b>...</b>`` pattern when
    bolding sub-headings or key terms inline within a Paragraph string,
    keeping call sites readable.

    Args:
        text: The plain string to wrap.

    Returns:
        The string enclosed in ``<b>`` and ``</b>`` tags.
    """
    return f"<b>{text}</b>"


def bullet(text, s):
    """Create a single indented bullet-point Paragraph.

    Prepends a unicode bullet character and applies the ``"bullet"`` style,
    which adds a left indent so the text aligns neatly after the bullet.
    Supports inline HTML tags (e.g. ``<b>``, ``<i>``) within ``text``.

    Args:
        text: The bullet item content. May contain inline HTML markup.
        s:    The styles dictionary returned by ``styles()``.

    Returns:
        A ReportLab Paragraph flowable with a bullet prefix and left indent.
    """
    return Paragraph(f"• {text}", s["bullet"])


# ── Document body ─────────────────────────────────────────────────────────────

def build_story(s):
    """Assemble the complete ordered list of ReportLab flowables for the document.

    Constructs the full narrative of the design process report in ten numbered
    sections, preceded by a navy cover block:

      Cover     — Title, subtitle, author, date on a full-width navy block.
      Section 1 — Executive Summary: project overview, architecture, and security
                  hardening programme.
      Section 2 — Project Brief & Objectives: requirements including security-by-design
                  and production-grade hardening criteria.
      Section 3 — Platform Selection Journey: four sub-sections covering each platform
                  evaluated and the decision rationale for each.
      Section 4 — Technical Architecture: Flask + Gunicorn, ReportLab, Resend, Render,
                  and a dedicated security controls sub-section.
      Section 5 — Security Architecture: audit scope, all 15 findings (summary table),
                  and remediation approach across three phases.
      Section 6 — UI / UX Design: colour palette, accordion form structure, and AJAX
                  submission flow with CSP and SRI context.
      Section 7 — Key Design Decisions: nine named architectural choices including three
                  security-focused decisions.
      Section 8 — Development Phases & Effort: 20-row phase table including five security
                  phases; total effort 57 hours.
      Section 9 — Cost Analysis: Nairobi and global market rates with a dedicated security
                  audit & hardening row; adjusted totals and four-row summary table.
      Section 10 — Final Deliverable: complete enumerated list of all repository artefacts.

    Args:
        s: The styles dictionary returned by ``styles()``.

    Returns:
        A list of ReportLab flowables suitable for passing directly to
        ``SimpleDocTemplate.build()``.
    """
    story = []

    # ── Cover ─────────────────────────────────────────────────────────────────
    cover = Table([
        [Paragraph("CAREER TRANSITION PLANNING SERVICE", s["title"])],
        [Spacer(1, 0.3 * cm)],
        [Paragraph("Client Onboarding Form", s["subtitle"])],
        [Paragraph("Design Process &amp; Project Report", s["subtitle"])],
        [Spacer(1, 0.4 * cm)],
        [Paragraph("Prepared by: Eric Gitonga  ·  July 2026", s["meta"])],
        [Paragraph("Confidential — Internal Reference Document", s["meta"])],
    ], colWidths=[INNER_W])
    cover.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), NAVY),
        ("TOPPADDING",    (0, 0), (-1, -1), 20),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 20),
        ("LEFTPADDING",   (0, 0), (-1, -1), 20),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 20),
    ]))
    story += [cover, Spacer(1, 0.5 * cm), rule(GOLD, 2, 2, 10)]

    # ── 1. Executive Summary ───────────────────────────────────────────────────
    story.append(KeepTogether([section_header("1. Executive Summary", s), Spacer(1, 0.2 * cm)]))
    story.append(Paragraph(
        "This document records the complete design process, technical decision-making, and "
        "iterative development journey that produced the Career Transition client onboarding "
        "form — a professionally branded, dark-themed web application that collects structured "
        "intake responses from clients, compiles them into a PDF, and delivers the document "
        "automatically to the consultant by email.",
        s["body"],
    ))
    story.append(Paragraph(
        "The project moved through several platform and technology iterations before arriving "
        "at its final architecture: a Python Flask application served by Gunicorn, hosted on "
        "Render, with email delivery via the Resend transactional API. The final product "
        "requires zero manual intervention from the consultant once deployed — a client "
        "completes the form, clicks Submit, and the PDF lands in the consultant's inbox.",
        s["body"],
    ))
    story.append(Paragraph(
        "Following functional deployment, a comprehensive security audit identified 15 "
        "vulnerabilities spanning four severity tiers (4 HIGH, 7 MEDIUM, 4 LOW). All 15 were "
        "addressed in a phased hardening programme, elevating the application from an "
        "unprotected prototype to a production-grade service with CSRF protection, rate "
        "limiting, file type enforcement, a strict Content Security Policy, Subresource "
        "Integrity for CDN resources, HTTP security headers, pinned dependencies, and "
        "structured audit logging. Security is now a first-class design principle in this "
        "codebase, documented in detail in a separate internal audit report (extras/security.pdf).",
        s["body"],
    ))
    story.append(Paragraph(
        "A subsequent round of user testing identified that Render's built-in cold-start "
        "loading screen — displaying server log output to the client — was confusing and "
        "inappropriate for a professional service. A companion Render Static Site was added "
        "as the canonical client-facing entry point: a branded loading page with an animated "
        "progress bar and estimated countdown that polls the Flask app and redirects "
        "automatically once it is ready. User-facing error messaging and startup behaviour "
        "were simultaneously formalised in SKILL.md as first-class design principles.",
        s["body"],
    ))
    story.append(Spacer(1, 0.2 * cm))
    story.append(rule(MGRAY, 0.5))

    # ── 2. Project Brief ───────────────────────────────────────────────────────
    story.append(KeepTogether([section_header("2. Project Brief &amp; Objectives", s), Spacer(1, 0.2 * cm)]))
    story.append(Paragraph(
        "The brief was to build a structured digital intake form for a career transition "
        "coaching practice. Clients completing the form would provide information across "
        "ten thematic areas: personal information (including client type, current domain, "
        "languages, and LinkedIn URL), motivation and context, target role clarity, "
        "constraints and capacity (including work style and travel preferences), financial "
        "expectations, learning style, network and visibility, past attempts and blockers, "
        "deliverable preferences (including existing portfolio evidence), and document "
        "uploads with a CV fallback for clients who cannot supply a CV at intake.",
        s["body"],
    ))
    story.append(Paragraph(b("Key requirements:"), s["h3"]))
    for item in [
        "Structured, multi-section form with clear visual hierarchy",
        "Branded PDF output matching the practice's navy / teal / gold colour palette",
        "Automatic email delivery to the consultant upon submission — no manual steps",
        "Support for document uploads (CV, LinkedIn export, job description, etc.)",
        "Publicly hosted on a permanent URL with zero ongoing maintenance burden",
        "Professional appearance that reflects well on the practice to clients",
        "No technical knowledge required from the client — the form must be self-contained",
        "<b>Security by design</b> — no credentials exposed in code or templates; all secrets "
        "in environment variables; CSRF protection, rate limiting, and file validation enforced "
        "at the server level before any business logic runs",
        "<b>Production-grade hardening</b> — Subresource Integrity hashes on all CDN resources, "
        "HTTP security headers on every response, pinned dependencies, cryptographically random "
        "temp filenames, control-character stripping, and structured submission logging",
    ]:
        story.append(bullet(item, s))
    story.append(Spacer(1, 0.2 * cm))
    story.append(rule(MGRAY, 0.5))

    # ── 3. Platform Selection ──────────────────────────────────────────────────
    story.append(KeepTogether([section_header("3. Platform Selection Journey", s), Spacer(1, 0.2 * cm)]))
    story.append(Paragraph(
        "Arriving at the final hosting stack required evaluating and, in most cases, "
        "fully implementing three distinct platforms before settling on the solution that "
        "met all requirements. Each iteration produced real, working code and surfaced "
        "constraints that informed the next decision.",
        s["body"],
    ))

    story.append(KeepTogether([sub_header("Phase 1 — Hugging Face Spaces (Gradio)", s), Spacer(1, 0.15 * cm)]))
    story.append(Paragraph(
        "The initial platform choice was Hugging Face Spaces with a Gradio interface — a "
        "well-established combination for rapid Python-based web UIs with free hosting. "
        "The form was built using Gradio's component library with the practice's colour "
        "scheme applied via custom CSS.",
        s["body"],
    ))
    story.append(Paragraph(b("Issues encountered:"), s["h3"]))
    for item in [
        "<b>colorTo parameter rejected</b> — HF Spaces only accepts a specific set of named colours; "
        "'teal' was not in the list. Fixed by switching to 'indigo'.",
        "<b>HfFolder import error</b> — huggingface_hub ≥ 0.25.0 removed the HfFolder class that "
        "Gradio 4.44.0 still depended on. Resolved by pinning huggingface_hub < 0.25.0.",
        "<b>CSS / theme API change</b> — Gradio 4.x moved the css and theme arguments from "
        "launch() to Blocks(). Fixed by restructuring the instantiation call.",
        "<b>ZeroGPU lock</b> — the Space was accidentally assigned ZeroGPU hardware; downgrading "
        "to CPU-basic requires a Pro subscription. The Space had to be deleted and rebuilt.",
        "<b>Policy change</b> — immediately after rebuilding, Hugging Face announced that Gradio "
        "Spaces require a paid plan. Free hosting was no longer available on this platform.",
    ]:
        story.append(bullet(item, s))
    story.append(Paragraph(
        "<i>Decision: Abandon Hugging Face Spaces. Seek an alternative hosting provider.</i>",
        s["note"],
    ))

    story.append(KeepTogether([sub_header("Phase 2 — Google Cloud Run (Aborted)", s), Spacer(1, 0.15 * cm)]))
    story.append(Paragraph(
        "Google Cloud Run was briefly considered and a Dockerfile and GitHub Actions "
        "deployment workflow were created. The client reviewed the setup requirements "
        "(GCP project creation, IAM roles, service account key management, GitHub secrets) "
        "and concluded the operational overhead was disproportionate for a low-traffic "
        "intake form. The implementation was abandoned and all Google-specific artefacts "
        "were removed from the repository.",
        s["body"],
    ))
    story.append(Paragraph(
        "<i>Decision: Abandon Cloud Run. Move to Render, which provides equivalent "
        "deployment automation with significantly less configuration.</i>",
        s["note"],
    ))

    story.append(KeepTogether([sub_header("Phase 3 — Render with Gradio", s), Spacer(1, 0.15 * cm)]))
    story.append(Paragraph(
        "Render's Python web service was configured with render.yaml, Gradio was retained "
        "as the UI framework, and the app deployed. A cascade of compatibility issues "
        "followed, each requiring investigation and a targeted fix:",
        s["body"],
    ))
    for item in [
        "<b>Blank page (Gradio 5.x)</b> — Render's reverse proxy was incompatible with Gradio 5's "
        "frontend asset serving. Downgraded to Gradio 4.44.1.",
        "<b>Python 3.14 / audioop removal</b> — Render defaulted to Python 3.14 where the audioop "
        "module (a pydub transitive dependency) was removed. Fixed by adding a .python-version "
        "file pinning 3.11.9.",
        "<b>gradio-client boolean schema bug</b> — gradio-client 1.3.0 passed boolean values to a "
        "function that expected a string, crashing every request. Resolved by monkey-patching "
        "json_schema_to_python_type with a try/except guard.",
        "<b>Starlette API change</b> — starlette 1.3.1 broke the TemplateResponse call pattern "
        "used by Gradio 4.x. Fixed by pinning fastapi == 0.115.0 to force starlette 0.38.x.",
        "<b>Localhost health-check block</b> — Render's network policy blocks loopback connections; "
        "Gradio's post-startup self-ping to 127.0.0.1 always failed. Patched by replacing "
        "url_ok with a lambda that always returns True.",
    ]:
        story.append(bullet(item, s))
    story.append(Paragraph(
        "Even after all patches, the accumulation of monkey-patches against an ageing "
        "framework represented unacceptable technical debt.",
        s["body"],
    ))
    story.append(Paragraph(
        "<i>Decision: Replace Gradio entirely. Rewrite the application in Flask.</i>",
        s["note"],
    ))

    story.append(KeepTogether([sub_header("Phase 4 — Flask on Render (Final)", s), Spacer(1, 0.15 * cm)]))
    story.append(Paragraph(
        "The application was rewritten from scratch in Flask. The form UI was rebuilt in "
        "Bootstrap 5 with a full dark theme, all Gradio dependencies were removed, and "
        "the PDF generation logic (ReportLab) was retained and refined. The Flask app "
        "deployed cleanly on the first attempt. One remaining issue — Render blocking "
        "outbound SMTP on port 587 — was resolved by replacing smtplib with the Resend "
        "transactional email API, which sends over HTTPS and is never blocked by hosting "
        "providers.",
        s["body"],
    ))
    story.append(Spacer(1, 0.1 * cm))

    story.append(Paragraph(b("Platform comparison summary:"), s["h3"]))
    story.append(phase_table(
        [
            ["Platform", "Outcome", "Blocking Issue"],
            ["Hugging Face Spaces", "✗ Abandoned", "Paid plan required; ZeroGPU lock"],
            ["Google Cloud Run",    "✗ Aborted",   "Excessive operational complexity"],
            ["Render + Gradio",     "✗ Abandoned", "Cascade of framework compatibility bugs"],
            ["Render + Flask",      "✓ Deployed",  "None — production-stable"],
        ],
        s,
        col_widths=[INNER_W * 0.28, INNER_W * 0.22, INNER_W * 0.50],
    ))
    story.append(Spacer(1, 0.2 * cm))
    story.append(rule(MGRAY, 0.5))

    # ── 4. Technical Architecture ──────────────────────────────────────────────
    story.append(PageBreak())
    story.append(KeepTogether([section_header("4. Technical Architecture", s), Spacer(1, 0.2 * cm)]))

    story.append(sub_header("Backend — Flask + Gunicorn", s))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(
        "Flask was chosen for its simplicity, minimal footprint, and zero compatibility "
        "issues on Render. Gunicorn serves as the production WSGI server, started with "
        "the command specified in render.yaml:",
        s["body"],
    ))
    story.append(Paragraph("gunicorn app:app --bind 0.0.0.0:$PORT", s["code"]))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(
        "The application has two routes: GET / serves the intake form; POST /submit "
        "processes the submission, generates the PDF, attempts email delivery, and "
        "returns the PDF as a file download. The email outcome (sent / failed / skipped) "
        "is communicated back to the browser via an X-Email-Status response header.",
        s["body"],
    ))

    story.append(sub_header("PDF Generation — ReportLab Platypus", s))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(
        "The PDF is generated programmatically using ReportLab's Platypus layout engine. "
        "Each submission produces a multi-page A4 document featuring a navy cover block "
        "with the client's name and submission date, nine labelled intake sections, "
        "question/answer pairs with bold navy labels and indented answers, and a per-page "
        "footer. Multi-select fields are joined as comma-separated strings; blank fields "
        "render as an em-dash.",
        s["body"],
    ))

    story.append(sub_header("Email Delivery — Resend", s))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(
        "Email is sent via the Resend transactional API using the resend Python SDK. "
        "Resend operates over HTTPS (port 443) rather than SMTP (port 587), making it "
        "immune to port-blocking policies on cloud hosting platforms. The API key is "
        "stored as a Render environment variable and is never present in the codebase. "
        "All uploaded documents are attached alongside the generated PDF.",
        s["body"],
    ))

    story.append(sub_header("Hosting — Render", s))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(
        "Render's Python web service provides a permanent public URL, automatic TLS, "
        "and GitHub-triggered continuous deployment at no cost on the free tier. "
        "render.yaml codifies the service configuration so the hosting setup is "
        "reproducible and version-controlled.",
        s["body"],
    ))

    story.append(sub_header("Loading Page — Render Static Site", s))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(
        "Render's free-tier web service spins down after 15 minutes of inactivity and "
        "displays its own 'APPLICATION LOADING' screen — showing server log output — while "
        "the instance restarts. This screen is served by Render's reverse proxy before "
        "gunicorn binds to the port and cannot be replaced from within application code.",
        s["body"],
    ))
    story.append(Paragraph(
        "To replace this experience, a companion Render Static Site (career-transition-loading) "
        "was added alongside the Flask web service in render.yaml. Static sites on Render have "
        "no cold start and serve files instantly. The loading page (loading/index.html) shows a "
        "branded dark-theme waiting screen with a spinner and a simple 'Preparing your form...' "
        "tagline — no visible countdown or progress bar, following the understated style of "
        "similar branded loading screens (e.g. PDF Drive). It polls the Flask app's /_health "
        "endpoint every three seconds via the Fetch API and redirects automatically on a 200 "
        "response. The canonical client-facing URL is the loading page; the Flask app URL is "
        "never shared directly.",
        s["body"],
    ))
    story.append(Paragraph(
        "The /_health endpoint returns {\"status\":\"ok\"} with an Access-Control-Allow-Origin "
        "header scoped to the loading site's origin, configurable via the LOADING_SITE_ORIGIN "
        "environment variable. This permits the cross-origin Fetch poll without relaxing CORS "
        "across the rest of the application.",
        s["body"],
    ))

    story.append(sub_header("Security Controls — Flask-WTF, Flask-Limiter, CSP", s))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(
        "The application implements all 15 findings from the security audit (detailed in "
        "Section 5). The key controls are layered from outermost to innermost:",
        s["body"],
    ))
    for item in [
        "<b>CSRF tokens (Flask-WTF CSRFProtect)</b> — validated on every POST before any "
        "handler logic runs; requests without a valid server-issued token are rejected with HTTP 400",
        "<b>Upload size cap (MAX_CONTENT_LENGTH = 10 MB)</b> — enforced at the Flask framework "
        "level; oversized requests return HTTP 413 before reaching route code",
        "<b>File extension whitelist (_safe_suffix())</b> — only .pdf, .doc, .docx, .txt, .jpg, "
        ".jpeg, .png are accepted; any other extension returns HTTP 400 before the file is written",
        "<b>Rate limiting (Flask-Limiter)</b> — /submit throttled to 5 requests/minute and "
        "20/hour per IP to prevent Resend quota exhaustion and gunicorn saturation",
        "<b>HTTP security headers (@after_request hook)</b> — every response carries "
        "X-Frame-Options: DENY, X-Content-Type-Options: nosniff, a strict Content-Security-Policy, "
        "and Referrer-Policy: strict-origin-when-cross-origin",
        "<b>Subresource Integrity (SRI)</b> — Bootstrap CSS and JS loaded from the CDN include "
        "SHA-384 integrity hashes; tampered CDN files are blocked by the browser before execution",
        "<b>Input length limits (_clip())</b> — all text inputs truncated server-side before "
        "reaching the ReportLab PDF builder, preventing memory exhaustion via crafted payloads",
        "<b>Control-character stripping (_sanitize())</b> — fields used in the email subject and "
        "body are sanitised to prevent body-spoofing via injected newlines",
        "<b>Random temp filenames (secrets.token_hex(8))</b> — generated PDFs and uploads use "
        "cryptographically unpredictable names, not guessable initials + timestamp",
        "<b>Temp file cleanup (finally block)</b> — all temp files deleted after the response "
        "is built regardless of whether an exception occurred",
        "<b>Structured submission logging (app.logger)</b> — every submission is logged with "
        "name, email, target domain, upload count, and email outcome for audit and abuse detection",
        "<b>Pinned dependencies</b> — all six packages pinned to known-good versions in "
        "requirements.txt; no silent supply-chain updates on each Render deploy",
        "<b>Static JS (static/form.js)</b> — all JavaScript served from a separate file, enabling "
        "a strict script-src CSP with no 'unsafe-inline'",
    ]:
        story.append(bullet(item, s))
    story.append(Spacer(1, 0.1 * cm))
    story.append(rule(MGRAY, 0.5))

    # ── 5. Security Architecture ───────────────────────────────────────────────
    story.append(PageBreak())
    story.append(KeepTogether([section_header("5. Security Architecture", s), Spacer(1, 0.2 * cm)]))

    story.append(sub_header("5.1  Audit Scope and Methodology", s))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(
        "A structured code review of all four in-scope files — app.py, "
        "templates/index.html, requirements.txt, and render.yaml — was conducted against "
        "the OWASP Top 10 and common Flask deployment pitfalls. The review covered "
        "injection vectors, authentication and session management, sensitive data "
        "exposure, security misconfiguration, cross-site scripting, insecure "
        "deserialization, use of components with known vulnerabilities, and insufficient "
        "logging and monitoring. No automated scanning tools were used; all findings "
        "were identified through manual inspection.",
        s["body"],
    ))
    story.append(Paragraph(
        "The audit found no critical vulnerabilities (no remote code execution, SQL "
        "injection, or hardcoded secrets). All 15 findings address real attack surfaces "
        "— from missing CSRF protection enabling forged submissions, to temp files "
        "accumulating on disk across every request — that would be exploitable on a "
        "public-facing form handling sensitive personal and career information.",
        s["body"],
    ))

    story.append(sub_header("5.2  Findings Summary", s))
    story.append(Spacer(1, 0.1 * cm))
    story.append(phase_table(
        [
            ["ID",    "Finding",                              "Severity", "File"],
            ["S-01",  "No CSRF protection",                  "HIGH",     "app.py"],
            ["S-02",  "No upload size limit",                "HIGH",     "app.py"],
            ["S-03",  "No file content validation",          "HIGH",     "app.py"],
            ["S-04",  "CDN resources without SRI hashes",    "HIGH",     "index.html"],
            ["S-05",  "No rate limiting",                    "MEDIUM",   "app.py"],
            ["S-06",  "Exception details leaked to client",  "MEDIUM",   "app.py"],
            ["S-07",  "Temp files never deleted",            "MEDIUM",   "app.py"],
            ["S-08",  "No HTTP security headers",            "MEDIUM",   "app.py"],
            ["S-09",  "No SECRET_KEY set",                   "MEDIUM",   "app.py"],
            ["S-10",  "Unpinned dependencies",               "MEDIUM",   "requirements.txt"],
            ["S-11",  "No input length limits",              "MEDIUM",   "app.py"],
            ["S-12",  "Control chars in email fields",       "LOW",      "app.py"],
            ["S-13",  "Predictable temp filename",           "LOW",      "app.py"],
            ["S-14",  "Extension derived from user input",   "LOW",      "app.py"],
            ["S-15",  "No submission logging",               "LOW",      "app.py"],
        ],
        s,
        col_widths=[INNER_W*0.10, INNER_W*0.44, INNER_W*0.16, INNER_W*0.30],
    ))
    story.append(Spacer(1, 0.1 * cm))

    story.append(sub_header("5.3  Remediation Approach", s))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(
        "All 15 findings were remediated in three phases ordered by severity. "
        "Phase 1 (1–2 hours) addressed all four HIGH findings plus two MEDIUM findings "
        "(S-08 security headers and S-09 SECRET_KEY) that were tightly coupled to the "
        "Phase 1 infrastructure changes. Phase 2 (2–3 hours) addressed the remaining "
        "five MEDIUM findings. Phase 3 (1–2 hours) closed all four LOW findings. "
        "Total hardening effort: approximately 6–9 hours, with all 15 findings resolved "
        "in a single deployable commit.",
        s["body"],
    ))
    story.append(Paragraph(
        "As part of Phase 1, all JavaScript was extracted from the inline &lt;script&gt; block "
        "in index.html into a separate static/form.js file. This structural change was a "
        "prerequisite for enforcing a strict Content-Security-Policy with no 'unsafe-inline' "
        "in script-src — a meaningful XSS mitigation that would have been impossible "
        "while any inline script remained in the template.",
        s["body"],
    ))
    story.append(Paragraph(
        "Note: the full audit report with per-finding code samples, impact assessments, "
        "and a phased refactor plan is stored in extras/security.pdf "
        "(gitignored — internal use only).",
        s["note"],
    ))
    story.append(rule(MGRAY, 0.5))

    # ── 6. UI/UX Design ───────────────────────────────────────────────────────
    story.append(KeepTogether([section_header("6. UI / UX Design", s), Spacer(1, 0.2 * cm)]))
    story.append(Paragraph(
        "The interface was built with Bootstrap 5.3 using the data-bs-theme='dark' "
        "attribute for baseline dark-mode component styling, augmented with custom CSS "
        "to match the practice's brand identity.",
        s["body"],
    ))

    story.append(Paragraph(b("Colour palette:"), s["h3"]))
    for item in [
        "<b>Navy #1B2A4A</b> — primary background for banners, accordion headers, and the cover block",
        "<b>Teal #0E7C7B</b> — interactive elements: submit button, focus rings, sub-headings",
        "<b>Gold #C9A84C</b> — accent colour for form labels and decorative rules",
        "<b>Body #0d1117</b> — page background (deep dark, matching the GitHub dark theme register)",
        "<b>Panel #161b22</b> — accordion item backgrounds, distinct from page without harshness",
    ]:
        story.append(bullet(item, s))

    story.append(Paragraph(b("Form structure:"), s["h3"]))
    story.append(Paragraph(
        "The form is organised as a ten-section Bootstrap accordion, with Section 1 "
        "(Personal Information) expanded by default. Sections 2 through 10 (Document "
        "Uploads) are collapsed and opened on demand, reducing visual overwhelm for what "
        "is a substantial intake questionnaire. Field types were chosen to match the "
        "nature of each question: radio buttons for mutually exclusive choices, "
        "checkboxes for multi-select options, a range slider for hours per week, and "
        "textareas for open-ended narrative responses.",
        s["body"],
    ))
    story.append(Paragraph(b("Conditional and progressive disclosure:"), s["h3"]))
    story.append(Paragraph(
        "Two progressive disclosure patterns reduce form complexity. First, a 'Specific "
        "role title' text field in Section 3 is hidden by default and revealed only when "
        "the client selects 'Very clear' or 'Clear' on the target clarity radio — clients "
        "who are still exploring are not asked for a title they do not yet have. Second, "
        "the Document Uploads section includes a CV fallback block, hidden by default and "
        "toggled via a link beneath the CV upload field. When expanded, it captures "
        "current/last title, industry, years of experience, certifications, and key skills "
        "in free text — sufficient for the consultant to generate the plan without a CV. "
        "Uploading a CV automatically collapses and resets the toggle. Both behaviours are "
        "implemented in static/form.js, preserving the strict CSP with no 'unsafe-inline'. "
        "As of 0.19.0 this fallback block is not merely a convenience — it is one of two "
        "ways to satisfy the section's upload requirement (see below).",
        s["body"],
    ))
    story.append(Paragraph(
        "The CV fallback block is nested directly inside the CV upload's Bootstrap column "
        "rather than placed as a full-width col-12 after the LinkedIn fields. This ensures "
        "it expands visually beneath the CV upload, not beneath the LinkedIn export input. "
        "Because the fallback is constrained to a col-md-6 parent, its internal layout uses "
        "single-column stacked fields (mb-2 divs) rather than a two-column grid.",
        s["body"],
    ))
    story.append(Paragraph(b("Document Uploads: CV/business-profile requirement:"), s["h3"]))
    story.append(Paragraph(
        "A static, warmly-worded banner sits above the upload fields in Section 10, "
        "explaining that either the CV/business-profile upload or the background fallback "
        "fields are required, and that everything else in the section is optional but "
        "improves plan quality — framed positively, never as a warning. Section 1's "
        "client_type answer routes which upload is requested: job-seekers, employees, and "
        "'Other' see 'CV / Résumé'; entrepreneurs and freelancers see 'Business Profile / "
        "Pitch Deck' instead, reusing the same grouping already used for Section 4's "
        "employment-vs-business-status split (factored into a shared "
        "_is_entrepreneur_type() helper in app.py, mirrored by the client-type toggle in "
        "static/form.js) — client type is asked once, not twice.",
        s["body"],
    ))
    story.append(Paragraph(
        "Submission requires either the routed upload (cv_file) or at least one of the "
        "five CV-fallback fields to be filled in. This is enforced twice: client-side in "
        "form.js (blocks the fetch call, expands Section 10 and the fallback block, "
        "scrolls to the field, and shows a plain-English inline error) and server-side in "
        "app.py's submit() (returns HTTP 400 with a plain-English message if the "
        "client-side check is bypassed). All other document fields — LinkedIn, job "
        "description, learning plan, additional files — remain fully optional.",
        s["body"],
    ))
    story.append(Paragraph(
        "This was added after two prior thin-data intakes were submitted with neither a "
        "CV nor the fallback fields filled in, leaving the consultant unable to generate a "
        "meaningful plan and forcing a manual gap-note follow-up instead (see the "
        "Clients/Alex Mercer/generate_gap_note.py pattern — a fictitious example, since the "
        "real cases cannot be named here). A first attempt (Issue #23) "
        "added only the non-blocking banner; it was superseded by this hard requirement "
        "(Issue #24) once it became clear both prior cases were job-seeker/freelancer "
        "types, not entrepreneurs — the CV field's old '(optional for entrepreneurs)' "
        "label had never actually been enforced for anyone.",
        s["body"],
    ))

    story.append(Paragraph(b("LinkedIn dual-input pattern:"), s["h3"]))
    story.append(Paragraph(
        "The LinkedIn section offers both a URL field and a file upload. The URL field is "
        "the primary option — zero friction for the client, immediately accessible for the "
        "consultant. The file upload remains for clients who can produce a full LinkedIn "
        "data export (which contains endorsements and connection data not visible on the "
        "profile page). Both are optional; the consultant uses whichever is provided.",
        s["body"],
    ))

    story.append(Paragraph(b("Privacy statement:"), s["h3"]))
    story.append(Paragraph(
        "A plain-print privacy statement is shown above the submit button, in regular "
        "body text rather than fine print, stating that submitted information and "
        "documents are used only to prepare the client's plan and are not shared with, "
        "sold to, or used by any third party. This keeps the form's data-handling promise "
        "visible at the point of submission rather than buried in a separate policy page.",
        s["body"],
    ))

    story.append(Paragraph(b("Submission flow:"), s["h3"]))
    story.append(Paragraph(
        "Form submission is handled entirely via the browser's Fetch API — the page "
        "never reloads. The submit button is disabled and relabelled 'Processing…' during "
        "the server round-trip. On success, the PDF blob is captured from the response, "
        "a temporary object URL is created, and the download is triggered "
        "programmatically. A persistent download link is also shown on the page. The "
        "status banner reports whether email delivery succeeded, failed, or was not "
        "configured, based on the X-Email-Status response header.",
        s["body"],
    ))
    story.append(Paragraph(
        "Form data is submitted as multipart/form-data, including a server-issued CSRF "
        "token rendered into the HTML as a hidden field by Flask-WTF's csrf_token() "
        "template function. The FormData object captures it automatically alongside all "
        "user inputs. All form interaction JavaScript is served from static/form.js "
        "rather than inline in the template, enabling a strict Content-Security-Policy "
        "that prohibits inline script execution — a meaningful defence against "
        "cross-site scripting if an injection point were ever introduced.",
        s["body"],
    ))
    story.append(Spacer(1, 0.1 * cm))
    story.append(rule(MGRAY, 0.5))

    # ── 7. Key Design Decisions ────────────────────────────────────────────────
    story.append(KeepTogether([section_header("7. Key Design Decisions", s), Spacer(1, 0.2 * cm)]))

    decisions = [
        ("No client credentials",
         "Removing the email settings section from the client-facing form and moving all "
         "credentials to Render environment variables eliminates a significant friction point "
         "and prevents clients from encountering technical setup requirements that are "
         "irrelevant to their task."),
        ("Resend over SMTP",
         "Gmail SMTP on port 587 is blocked by most cloud hosting providers to prevent spam. "
         "Resend's HTTPS API bypasses this entirely and requires only a single API key "
         "environment variable rather than an email address + App Password pair."),
        ("ReportLab over a template engine",
         "Generating the PDF programmatically with ReportLab gives precise control over "
         "typography, colour, spacing, and layout. PDF-from-HTML approaches (WeasyPrint, "
         "pdfkit) introduce browser rendering dependencies and are heavier to host; "
         "ReportLab is a pure-Python library with no system dependencies."),
        ("Flask over Gradio / FastAPI",
         "Flask is the thinnest viable option: one file, two routes, no framework magic. "
         "It eliminates the compatibility fragility that plagued the Gradio implementation "
         "while keeping the codebase easy to maintain and extend."),
        ("Bootstrap 5 dark theme",
         "Using data-bs-theme='dark' on the root HTML element gives Bootstrap's component "
         "library an appropriate baseline in dark mode, reducing the amount of custom CSS "
         "needed while keeping all interactive states (focus, hover, validation) consistent."),
        ("X-Email-Status response header",
         "Returning email outcome in a response header rather than the response body allows "
         "the PDF to be streamed as the primary response payload while still communicating "
         "delivery status to the JavaScript layer — avoiding the complexity of a two-request "
         "pattern or a JSON envelope around the binary PDF."),
        ("Security as a post-launch priority",
         "Security hardening was conducted as a dedicated phase after functional deployment "
         "rather than interleaved with feature development. This sequencing is deliberate — "
         "hardening a moving target during active feature iteration introduces the risk of "
         "breaking changes in controls not yet under test. A completed, stable feature set "
         "was audited once and hardened comprehensively in a single commit."),
        ("Static JS file over inline script",
         "Extracting the form's JavaScript from an inline &lt;script&gt; block into static/form.js "
         "enables a Content-Security-Policy with no 'unsafe-inline' in script-src. If an "
         "attacker finds an HTML injection point, they cannot execute injected scripts because "
         "the CSP blocks all inline execution. Style-src retains 'unsafe-inline' because "
         "Bootstrap uses inline style attributes for accordion height animations — styles "
         "are far less dangerous than scripts."),
        ("In-memory rate limiting for single-instance deployment",
         "Flask-Limiter defaults to in-memory storage for tracking request counts, which is "
         "appropriate for a single-worker Render free-tier deployment. Request counts are "
         "per-process and reset on restart — acceptable given the low traffic profile of a "
         "private coaching intake form. A Redis backend would be required if the application "
         "were scaled to multiple workers, and is noted as a future upgrade path."),
        ("Companion static loading site for cold-start UX",
         "Render's free-tier instances display a server-log loading screen during cold starts — "
         "output that is confusing and inappropriate for a client-facing professional service. "
         "Because this screen is injected by Render's reverse proxy before any application code "
         "runs, it cannot be replaced through Flask routing or templating. A separate Render "
         "Static Site — which has no cold start — serves as the canonical entry point. It shows "
         "a clean branded waiting screen, polls /_health to detect readiness, and redirects "
         "automatically. The pattern completely hides Render's infrastructure from clients while "
         "staying within the free tier."),
        ("User-facing behaviour as a documented design rule",
         "Tester feedback formalised two principles now codified in SKILL.md: errors shown in "
         "the browser must always be plain English — no Python tracebacks, status codes, or "
         "server log lines — and the loading page URL is the only URL shared with clients. "
         "Documenting these as explicit rules, not just implementation choices, ensures any "
         "future changes to error handling or hosting configuration preserve the same standard."),
        ("Client type segmentation at intake",
         "Adding a 'Which best describes you?' radio in Section 1 (job-seeker, entrepreneur, "
         "freelancer, other) allows the plan generator to apply different framing from the "
         "outset without guessing from the CV. An entrepreneur pivoting to a new business area "
         "needs a launch strategy, not a job-search asset portfolio — the distinction must be "
         "explicit in the intake data, not inferred. The field is captured and surfaced "
         "prominently in the intake PDF."),
        ("Current domain as a required field, not inferred from the CV",
         "The plan's opening section requires knowing the client's source domain to write the "
         "'Strategic Insight' box — why their background is an asset in the target field. "
         "Previously this was extracted from the CV, which meant a thin or missing CV left "
         "the opening narrative unanchored. Making 'Field or industry you are transitioning "
         "from' a dedicated text field in Section 1 guarantees this data is always present, "
         "even when no CV is uploaded."),
        ("CV fallback as graceful degradation, not a reduced experience",
         "Not all clients arrive with a polished CV — entrepreneurs, returners, and those "
         "mid-job-search may have nothing to upload. Rather than making the CV a hard "
         "requirement (which would block some clients) or silently proceeding without it "
         "(which would produce an incomplete plan), the form offers a structured fallback: a "
         "toggle-revealed block that captures the minimum information needed — title, industry, "
         "experience, certifications, skills. The consultant receives everything required "
         "regardless of upload status; the client experiences no friction."),
        ("LinkedIn URL as primary; file upload as secondary",
         "The original form asked for a LinkedIn export PDF — a multi-step process most "
         "clients do not know how to complete and many will skip. A plain profile URL is "
         "zero friction and gives the consultant immediate access to the client's current "
         "professional framing. The file upload is retained for clients who can produce an "
         "export (which includes endorsements and connection data), but the URL is always "
         "preferred. Both are optional; neither blocks submission."),
        ("Work style and travel preferences localise the target organisation list",
         "Section 2 of the plan ('Where You Are Heading') lists 8–10 target organisations. "
         "Without knowing the client's remote/hybrid/office preference and willingness to "
         "travel, the consultant must guess which organisations are viable — a wasted section "
         "if the client is fully remote but the recommended org requires relocation. Capturing "
         "these preferences at intake allows the organisation list to be pre-filtered before "
         "the first draft."),
        ("Portfolio links with dynamic add — structured over free text",
         "The portfolio question in Section 9 uses a yes/no radio followed by a dynamic "
         "link list rather than a free-text textarea. A '+ Add another link' button "
         "appends new URL fields via JavaScript; each field has an × remove button. "
         "This produces a clean list of clickable URLs in the intake PDF rather than a "
         "prose description the consultant must parse. The consultant opens each link "
         "directly rather than guessing what 'three sustainability reports' refers to. "
         "Links are submitted as a list via multiple form fields sharing the name "
         "'portfolio_links' and collected with request.form.getlist() in app.py."),
        ("Free-form catch-all field as a safety net",
         "A final optional textarea at the end of Section 9 asks 'Anything else you'd like "
         "your consultant to know?' No structured question set can anticipate every relevant "
         "detail — timing pressure, a specific live opportunity, a health constraint, a "
         "family decision pending. This field is read first in plan generation and surfaced "
         "wherever it is most relevant, rather than siloed into a single section."),
        ("CV fallback nested inside the CV column",
         "The initial implementation placed the CV fallback as a col-12 div after the "
         "LinkedIn file upload input in the Bootstrap grid, causing it to render beneath "
         "the LinkedIn field rather than the CV field. Moving the fallback inside the CV's "
         "col-md-6 and converting its internal layout to single-column stacked fields "
         "ensures it expands directly beneath the control it relates to, with no layout "
         "ambiguity for the client."),
        ("Semantic versioning, applied retroactively",
         "The project accumulated 53 commits across seven days without any version scheme. "
         "Rather than starting versioning from the current state only, the full commit "
         "history was grouped into logical releases and tagged retroactively (v0.1.0 through "
         "v0.16.0), with a CHANGELOG.md entry for each. The project stays pre-1.0 (major "
         "version 0) throughout initial development per semver convention -- MAJOR is "
         "reserved for a future stable declaration or a breaking change after that point. "
         "This gives past and future changes the same discipline: every change bumps VERSION "
         "and adds a CHANGELOG.md entry before it is committed. The current version is also "
         "read live from VERSION and shown as a small footer line in the form's header, so "
         "the consultant can confirm which build a client used without checking the repo."),
        ("Inference discipline as a hard rule, not a style preference",
         "Every claim in the generated plan must trace to something the client explicitly "
         "wrote, said, or uploaded -- a stated answer, a CV line, a JD requirement. Blank or "
         "'not sure' answers are not filled in with a plausible guess; unanswered questions "
         "leave that dimension of the plan open rather than decided on the client's behalf. "
         "The rule draws a specific line: connecting two things the client already said (a "
         "stated language plus a stated interest in international work, for example) is "
         "encouraged, because it surfaces a link the client made possible by answering both "
         "questions. Inferring something the client never said -- a management preference "
         "from CV leadership experience, when the preference question was left blank -- is "
         "not, because it substitutes the model's assumption for the client's own decision. "
         "This keeps every plan grounded in what the client actually told the consultant, "
         "which matters most for a document the client may share with a sponsor or employer."),
        ("Organisation-stage labels reworded away from US venture-funding jargon",
         "The 'Preferred organisation stage' checkboxes originally labelled the two smaller "
         "tiers 'Early-stage startup (seed / Series A)' and 'Growth-stage startup (Series "
         "B+)'. This is US venture-capital funding-round terminology that assumes a "
         "Silicon-Valley-style financing path as the default lens for organisational maturity "
         "-- a framing that does not fit the primary client base, who are Kenya-based and "
         "targeting a market where most employers are not venture-funded in that sense. The "
         "labels were rewritten to 'Early-stage business' and 'Growth-stage business', "
         "dropping the funding-round parenthetical entirely and relying on the existing "
         "team-size and maturity description text, which was already geography-neutral. The "
         "five underlying tiers and their intent (early / growth / established / large / no "
         "preference) are unchanged -- only the microcopy assumed a funding context that "
         "wasn't universal."),
        ("Security findings verified with a reproduction, not just theorised",
         "The second security audit (S-16 through S-19) reproduced each finding against the "
         "actual running code before it was recorded, rather than relying on code inspection "
         "alone. This surfaced a real gap in the first attempted fix: sanitizing (stripping "
         "control characters from) logged fields stopped newline-based log-line forgery, but "
         "a follow-up reproduction against extras/pull_render_logs.py's own regex showed a "
         "crafted target_domain value could still hijack field boundaries within a single, "
         "un-split log line -- a distinct failure mode that sanitization alone does not "
         "address. Percent-encoding the fields (and decoding them again after the regex "
         "match) closed both paths at once. Each fix was re-verified against the same "
         "reproduction before this report was regenerated, rather than assumed correct from "
         "reading the diff."),
        ("Acronyms spelled out on first appearance, not left for the client to guess",
         "A review of a client plan generated before this rule existed found organisation "
         "acronyms such as IoD (Institute of Directors) and COI (College of Insurance) used "
         "throughout without the client ever being told what they stood for -- and, in two "
         "cases, the full name appeared for the first time in a later section while an earlier "
         "section already used "
         "the bare acronym, so even reading in order did not resolve it. The rule is now "
         "explicit in SKILL.md: every acronym or abbreviation a client would not already know "
         "must be spelled out in full, acronym in parentheses, the first time it appears "
         "anywhere in the document by reading order -- not by section number -- and used as "
         "the acronym alone afterwards, including inside tables. Terms already standard in this "
         "workflow's own vocabulary (CV, NGO, CEO, PDF, and currency codes) are exempt, since "
         "expanding those on every plan would add noise without adding clarity. Because the "
         "roadmap overview (Section 4) is drafted before the certifications and networking "
         "tables that name the same organisations (Sections 6-7), the earliest mention now "
         "wins the expansion and every later section must defer to it."),
        ("Git tags and GitHub Releases made a required step, not an optional record",
         "CHANGELOG.md claimed tags v0.18.0 through v0.19.2 existed, but none of the four had "
         "actually been created or pushed -- the changelog entry and the version-bump commit "
         "had been treated as sufficient on their own, and no GitHub Release had ever been "
         "published for any of the 31 released versions. A changelog entry describes a version; "
         "it does not make that version resolvable to a commit, installable at a point in "
         "history, or visible in GitHub's own Releases UI. The missing tags were backfilled at "
         "the exact commits their changelog entries' issue references point to, and a GitHub "
         "Release was published for every version from v0.1.0 onward, built directly from each "
         "CHANGELOG.md entry's own subheading and bullets rather than from GitHub's PR-derived "
         "--generate-notes output, plus a Full-Changelog compare link to the previous tag. "
         "SKILL.md now makes tagging and releasing an explicit last step of every version bump, "
         "not a separate task to remember later."),
        ("Client names redacted everywhere, tracked or not -- no file treated as safe by default",
         "Publishing 31 GitHub Releases surfaced that three CHANGELOG.md entries (v0.18.0, "
         "v0.19.0, v0.19.2) named real clients as the motivating example behind a form or "
         "plan-generation fix, and this design document repeated the same names for internal "
         "context. The first pass reworded only the public/tracked copies (CHANGELOG.md, the "
         "matching GitHub Releases) on the reasoning that a gitignored file was private enough "
         "to keep the names. That reasoning didn't hold up -- a local file can still be copied, "
         "screen-shared, or committed by accident later, so 'gitignored' is not the same "
         "guarantee as 'never leaves this machine.' All real client names were removed from "
         "this document too, the motivating incidents described generically instead ('two prior "
         "thin-data intakes', 'a client plan generated before this rule existed'), and SKILL.md's "
         "client-data-handling rules now prohibit naming a real client in any file, tracked or "
         "gitignored. The one standing exception is Alex Mercer, a fictitious client folder set "
         "up specifically to demo the service -- safe to name anywhere, and now the reference "
         "example SKILL.md points to wherever a concrete case is useful, including a new "
         "`generate_gap_note.py` producing a fictitious `gap.pdf` for the thin-intake gap-note "
         "pattern that previously had no nameable example."),
        ("One shared report_builder.py replaces a bespoke generate_plan.py per client",
         "Every client folder had its own generate_plan.py, 900-1,200+ lines each, duplicating "
         "roughly 250 lines of identical ReportLab boilerplate -- palette, ParagraphStyle "
         "definitions, and layout helpers like section_header/shaded_box/two_col/semester_card/ "
         "data_table -- before a single word of that client's actual content began. None of that "
         "duplication was ever client-specific; it was copy-pasted fresh for every plan. All of it "
         "was extracted into one tracked, root-level report_builder.py, exposing a single "
         "build_plan(data, output_path) entry point plus one render_section_N() per fixed-shape "
         "section (2, 3, 5, 8, 9, 11 -- the ones with real layout logic of their own, like the "
         "priority-coloured skills-gap table or the semester cards) and a generic render_blocks() "
         "for the freeform sections (1, 4, 6, 7, 10, 12 -- headings, paragraphs, shaded boxes, "
         "two-column lists, and tables in whatever mix a given plan needs). A client folder now "
         "holds only plan_data.py -- a PLAN dict of content, no ReportLab code -- and the "
         "thin root-level generate_plan.py CLI (`python3 generate_plan.py \"<Client Name>\"`) does "
         "the rendering. Alex Mercer's existing plan was migrated to this schema as the round-trip "
         "proof: the rendered PDF matched the original 17 pages and 5,252 words exactly, with the "
         "only pdftotext diff being word-wrap order inside the Monthly Action Tracker table, not "
         "missing content. Existing real clients' generate_plan.py scripts were left as delivered "
         "rather than retroactively migrated; new clients use the shared engine from here on."),
        ("Internal project documents moved out of Clients/ into extras/",
         "design_process.pdf and security.pdf are internal project documents -- a build log and an "
         "audit report -- not client data, but both were being written into Clients/ by their "
         "generator scripts' OUTPUT_PATH, alongside actual client folders. This caused real "
         "confusion when looking for the file: extras/ is where every other non-client-specific, "
         "gitignored project artefact already lives (feedback_01.pdf, costs.pdf, the metrics "
         "spreadsheet), and a stale extras/design_process.pdf copy from an earlier point in the "
         "project already existed there, half-consistent with the actual OUTPUT_PATH. Both "
         "generate_design_pdf.py and generate_security_pdf.py now write to extras/ instead of "
         "Clients/, matching the convention generate_feedback_pdf.py already followed. Neither file "
         "changes tracked status -- extras/ is gitignored just as Clients/ was -- only the directory "
         "changes, so client folders contain only client data."),
        ("generate_design_pdf.py itself is now tracked -- it never held client data to begin with",
         "It had been gitignored alongside generate_security_pdf.py, generate_feedback_pdf.py, and "
         "generate_selfhosting_pdf.py under one 'Private report generators' rule, but a check of its "
         "actual content -- every email address, every capitalised two-word phrase that could be a "
         "name, every SECRET_KEY/API_KEY-shaped string -- turned up nothing but the approved "
         "fictitious Alex Mercer example, a generic 'Jane Doe' CLI usage placeholder, and "
         "environment-variable *names* already documented in tracked SKILL.md and render.yaml, never "
         "a value. The other three scripts hold real client data or unreleased audit detail and stay "
         "gitignored; this one only ever held project process narrative that was private by "
         "inherited convention, not by content. Its output, extras/design_process.pdf, stays "
         "gitignored as a generated artefact -- only the generator script is now public."),
    ]
    for title, body in decisions:
        story.append(Paragraph(b(title), s["h3"]))
        story.append(Paragraph(body, s["body"]))

    story.append(rule(MGRAY, 0.5))

    # ── 8. Development Phases & Effort ─────────────────────────────────────────
    story.append(PageBreak())
    story.append(KeepTogether([section_header("8. Development Phases &amp; Effort Breakdown", s), Spacer(1, 0.2 * cm)]))
    story.append(Paragraph(
        "The following breakdown reflects the actual work performed across the full "
        "lifecycle of the project, including all platform iterations and their associated "
        "debugging, plus the security audit and hardening programme. Hours are estimates "
        "based on typical task durations for work of this nature and complexity.",
        s["body"],
    ))
    story.append(Spacer(1, 0.1 * cm))

    effort_rows = [
        ["Phase", "Description", "Est. Hours"],
        ["Discovery & Scoping",     "Requirements capture, field design, section planning",               "2"],
        ["Form Architecture",       "10-section field map, input type selection, validation rules",       "3"],
        ["HF Spaces Setup",         "Initial Gradio form build, README configuration, first deploy",      "3"],
        ["HF Spaces Debugging",     "colorTo, HfFolder, ZeroGPU, css/theme API fixes",                   "3"],
        ["Cloud Run Spike",         "Dockerfile, GitHub Actions workflow (aborted)",                      "2"],
        ["Render / Gradio Setup",   "render.yaml, Python pin, initial Gradio deploy",                     "2"],
        ["Render / Gradio Debugging","Blank page, audioop, boolean schema, starlette, localhost",         "5"],
        ["Flask Rewrite",           "app.py routes, form handling, Jinja2 template",                      "4"],
        ["ReportLab PDF Engine",    "Cover block, 9 sections, Q&A formatting, footer",                    "3"],
        ["Email Integration",       "SMTP attempt, timeout fix, migration to Resend API",                 "3"],
        ["UI / Dark Theme",         "Bootstrap 5 dark mode, custom CSS, accordion, JS fetch",             "4"],
        ["UI Refinement",           "Section removal, heading copy, multi-file upload, headshot removal", "2"],
        ["Deployment & DevOps",     "render.yaml, env vars, gunicorn config, .python-version",            "2"],
        ["Documentation",           "hosting.pdf, README, docstrings across app.py and generators",       "4"],
        ["Testing & QA",            "End-to-end submission, email delivery, PDF review, edge cases",      "3"],
        ["Security Audit",          "Manual code review of all 4 in-scope files; 15 findings documented in security.pdf", "4"],
        ["Phase 1 Hardening",       "CSRF (Flask-WTF), upload cap, file whitelist, SRI hashes, security headers, SECRET_KEY; JS extracted to static/form.js", "2"],
        ["Phase 2 Hardening",       "Rate limiting (Flask-Limiter), exception handling, temp cleanup, pinned deps, input limits", "3"],
        ["Phase 3 Hardening",       "Control-char stripping (_sanitize), random temp filenames, structured submission logging", "1"],
        ["Security Testing",        "End-to-end verification: CSRF rejection, rate-limit response, file type rejection, CSP and header inspection", "2"],
        ["Round 2 Feedback — Cold-Start UX", "Branded static loading page (loading/index.html), /_health endpoint with CORS headers, Render Static Site service in render.yaml, SKILL.md user-facing behaviour rules", "3"],
        ["Round 3 — Form Enhancement", "Conditional role title field (target clarity → show/hide); CV fallback block with toggle (JS); client type radio; current domain and languages fields; LinkedIn URL input alongside file upload; work style, travel, and management preference fields; existing portfolio textarea; back-end wiring for all new fields in submit() and build_pdf(); SKILL.md and design_process.pdf updated", "3"],
        ["Round 3b — Layout fix &amp; catch-all field", "CV fallback block moved inside CV col-md-6 (was col-12 after LinkedIn file — rendered in wrong position); internal layout converted to single-column stacked fields; optional free-form 'anything else' textarea added to Section 9; SKILL.md and design_process.pdf updated", "1"],
        ["Round 3c — Dynamic portfolio links", "Replace existing_portfolio textarea with yes/no radio + dynamic URL list; JS add/remove buttons; portfolio_links list collected via getlist(); intake PDF displays links as comma-separated list; SKILL.md and design_process.pdf updated", "1"],
        ["Round 4 — Conditional client-type logic &amp; org stage descriptions", "Client-type radio in Section 1 now drives Section 4: entrepreneurs and freelancers see a business-status question instead of employment questions; job-seekers see the employment block with a follow-up that appears only when 'Yes' is selected. Org stage checkboxes expanded with descriptive sub-labels (staff count, stage characteristics). entrepreneur_status field added to app.py data dict; _sec4_pairs() helper added to build_pdf() for conditional PDF rendering. SKILL.md and design_process.pdf updated. (Issue #16)", "2"],
        ["Round 4b — Other clarification fields", "Any question with an 'Other' radio option now reveals a free-text clarification input (d-none JS toggle). Implemented for client_type; pattern documented in SKILL.md as the standard for all future Other options. (Issue #17)", "0.5"],
        ["Round 5 — Submission metrics", "Local-only metrics system. Hidden field time_on_form_seconds added to form (JS sets value on submit); app.py logs it alongside name/email/target/uploads. Two local scripts created: extras/pull_render_logs.py (fetches Render API logs, parses Submission received/complete pairs, writes Sheet 'intake' of onboard_metrics.xlsx with date, time, name, email, target domain, uploads, time on form, server processing time, email status, attachment); extras/log_processed.py (consultant runs after generating a plan — logs start/end/duration/output to Sheet 'processed'). All files gitignored via extras/. (Issue #18)", "3"],
        ["Round 6 — Privacy statement", "Plain-print privacy statement added above the submit button, stating submitted data is used only to generate the client's plan and is not shared with any third party. SKILL.md and design_process.pdf updated. (Issue #19)", "0.5"],
        ["Round 7 — Semantic versioning", "VERSION file and CHANGELOG.md added; full commit history (53 commits) grouped into logical releases and tagged retroactively v0.1.0-v0.15.0; versioning policy documented in SKILL.md (pre-1.0, MINOR for features, PATCH for fixes/docs/hygiene); current version read live from VERSION and displayed at the bottom of the form's header. SKILL.md and design_process.pdf updated. (Issue #20)", "1.25"],
        ["Round 8 — Inference discipline", "SKILL.md updated with an explicit rule: every claim in the generated plan must trace to a client's stated answer, CV line, or JD requirement; connections between two stated facts are allowed, invented assumptions are not. design_process.pdf updated. (Issue #21)", "0.5"],
        ["Round 9 — Second security audit", "Full review of everything changed since the S-01-S-15 audit. Fixed: S-16 log-line forgery/field hijack in submission logging (sanitize + percent-encode logged fields via _log_field(), decode in extras/pull_render_logs.py); S-17 spreadsheet formula injection in onboard_metrics.xlsx (_safe_cell() guard in both extras scripts); S-18 real Render service ID hardcoded in a public tracked script (replaced with a placeholder); S-19 client slug not restricted to filename-safe characters (_client_slug() now alnum/hyphen/underscore only). Removed stale tracked loading.html. Full findings in the private extras/security.pdf. SKILL.md and design_process.pdf updated. (Issue #22)", "2"],
        ["Round 10 — Document Uploads encouragement banner", "Static, non-blocking banner added above the Section 10 upload fields, encouraging clients to fill in a CV, JD, or the CV fallback fields — framed positively, not as a warning or requirement; no validation gating added. Added after two prior intakes were submitted with neither a CV nor the fallback fields, forcing a manual gap-note follow-up. SKILL.md and design_process.pdf updated. (Issue #23)", "0.5"],
        ["Round 11 — CV/business-profile requirement", "Superseded Round 10's non-blocking banner with an actual requirement once it emerged that both prior thin-data intakes were job-seeker/freelancer types, not entrepreneurs. Section 1's client_type answer now routes Section 10's upload field (CV for job-seekers/employees/Other, Business Profile/Pitch Deck for entrepreneurs/freelancers) via a shared _is_entrepreneur_type() helper in app.py; submission requires either that upload or a CV-fallback field, enforced client-side (form.js) and server-side (app.py, HTTP 400). SKILL.md and design_process.pdf updated. (Issue #24)", "1"],
        ["Round 12 — Org-stage wording &amp; loading-page simplification", "Relabelled 'Early-stage startup (seed / Series A)' / 'Growth-stage startup (Series B+)' to 'Early-stage business' / 'Growth-stage business' to remove US venture-funding jargon not fitting a Kenya-based client base (Issue #25). Loading page (loading/index.html) simplified: countdown/progress bar and 'Application is starting up' heading replaced with a single spinner and a 'Preparing your form...' tagline in the understated style of similar branded loading screens; both the tagline and the 'Career Transition Onboarding' brand text set to 1.5rem for legibility; polling/redirect logic unchanged. SKILL.md and design_process.pdf updated. (Issue #26)", "0.5"],
        ["Round 13 — Tags, Releases &amp; client-name redaction", "Backfilled the four git tags CHANGELOG.md had already been claiming existed and published a GitHub Release for all 31 versions to date, built from each CHANGELOG.md entry rather than --generate-notes. Publishing surfaced three CHANGELOG.md entries and this design document naming real clients; all real client names were removed from every file, tracked or gitignored, with the fictitious Alex Mercer folder kept as the one safe reference example — including a new generate_gap_note.py there producing a fictitious gap.pdf for the thin-intake gap-note pattern. SKILL.md and design_process.pdf updated. (Issue #29)", "2"],
        ["Round 14 — Shared report_builder.py engine", "Extracted the ~250 lines of identical ReportLab boilerplate duplicated at the top of every client's generate_plan.py into one tracked, root-level report_builder.py (build_plan() plus a render_section_N() per fixed-shape section and a generic render_blocks() for freeform sections), with a thin generate_plan.py CLI replacing the per-client script entirely. Migrated Alex Mercer's plan to the new plan_data.py schema as the round-trip proof (17 pages, 5,252 words, identical to the original). SKILL.md and design_process.pdf updated. (Issue #31)", "3"],
        ["Round 15 — design_process.pdf &amp; security.pdf moved to extras/", "generate_design_pdf.py and generate_security_pdf.py were writing their output into Clients/, alongside actual client folders, even though both are internal project documents rather than client data — a source of real confusion when looking for the file. Both scripts' OUTPUT_PATH now target extras/, matching the convention generate_feedback_pdf.py already used; a stale extras/design_process.pdf copy from earlier in the project was overwritten with a freshly regenerated one. SKILL.md updated. (Issue #32)", "0.5"],
        ["Round 16 — generate_design_pdf.py tracked", "Verified generate_design_pdf.py holds no client data or real secrets — only project narrative, the approved Alex Mercer example, a generic placeholder, and env-var names never values — and removed it from .gitignore's private-generators block. Its output, extras/design_process.pdf, stays gitignored as a generated artefact. SKILL.md updated. (Issue #33)", "0.25"],
    ]
    col_w = [INNER_W * 0.30, INNER_W * 0.55, INNER_W * 0.15]
    story.append(phase_table(effort_rows, s, col_widths=col_w))

    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(
        "Total estimated effort: <b>80.25 hours</b>  (range: 66 – 82 hrs), comprising "
        "45 hours of product development, 12 hours of security audit and hardening, "
        "3 hours of Round 2 UX feedback, 3 hours of Round 3 form enhancements, "
        "1 hour of Round 3b layout fix, 1 hour of Round 3c dynamic portfolio links, "
        "2 hours of Round 4 conditional client-type logic and org stage descriptions, "
        "0.5 hours of Round 4b Other clarification fields, "
        "3 hours of Round 5 submission metrics, "
        "0.5 hours of Round 10 Document Uploads encouragement banner, "
        "1 hour of Round 11 CV/business-profile requirement, "
        "0.5 hours of Round 12 org-stage wording and loading-page simplification, "
        "2 hours of Round 13 tags, releases, and client-name redaction, and "
        "3 hours of Round 14 shared report_builder.py engine, and "
        "0.5 hours of Round 15 moving design_process.pdf and security.pdf to extras/, and "
        "0.25 hours of Round 16 tracking generate_design_pdf.py.",
        s["bold"],
    ))
    story.append(rule(MGRAY, 0.5))

    # ── 8b. Metrics System ────────────────────────────────────────────────────
    story.append(KeepTogether([section_header("8b. Submission Metrics System", s), Spacer(1, 0.2 * cm)]))
    story.append(Paragraph(
        "A local-only metrics system was added in Round 5 to give the consultant "
        "visibility into intake activity and plan-generation effort over time. "
        "No metrics data is committed to git — all files live in <i>extras/</i> "
        "which is permanently gitignored.",
        s["body"],
    ))
    story.append(Spacer(1, 0.2 * cm))

    metrics_rows = [
        ["Component", "Description"],
        ["time_on_form_seconds\n(index.html + form.js)",
         "Hidden form field. JavaScript records Date.now() when the page loads; "
         "on submit it computes the elapsed seconds and writes the value into the "
         "hidden field before the POST is sent."],
        ["app.py logging\n(Submission received)",
         "The existing structured log line was extended to include time_on_form=%s. "
         "Example: Submission received: name=Jane Doe email=jane@example.com "
         "target=Climate Finance uploads=2 time_on_form=843"],
        ["extras/pull_render_logs.py",
         "Fetches log entries from the Render REST API for a configurable date window. "
         "Parses 'Submission received' and 'Submission complete' log line pairs, "
         "matches them by client name within a 10-minute window, and writes one row "
         "per submission to the 'intake' sheet of onboard_metrics.xlsx. "
         "Deduplicates by (date, name) so re-runs are safe. "
         "Requires RENDER_API_KEY env var; RENDER_SERVICE_ID is optional (auto-detected)."],
        ["extras/log_processed.py",
         "Consultant runs this manually after generating a transition plan PDF. "
         "Accepts client name, start time, end time or duration (minutes), output "
         "path, and optional notes. Appends one row to the 'processed' sheet. "
         "Usage: python extras/log_processed.py \"Jane Doe\" --start \"2026-07-14 10:00\" "
         "--output \"Clients/Jane/JD_transition_plan.pdf\""],
        ["extras/onboard_metrics.xlsx",
         "Two-sheet Excel workbook. Sheet 'intake': Submission Date, Submission Time "
         "(UTC), Client Name, Client Email, Target Domain, Uploads, Time on Form (min), "
         "Server Processing (sec), Email Status, Attachment. "
         "Sheet 'processed': Client Name, Processing Start, Processing End, "
         "Duration (min), Output File, Notes. "
         "Navy header row, alternating row shading, auto-fitted column widths."],
    ]
    t = Table(metrics_rows, colWidths=[INNER_W * 0.28, INNER_W * 0.72])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 8.5),
        ("LEADING",       (0, 0), (-1, -1), 12),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.HexColor("#F4F6F9"), WHITE]),
        ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#D0D6E0")),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        "<b>Setup:</b> pip install requests openpyxl · "
        "export RENDER_API_KEY=rnd_... · "
        "then run: python extras/pull_render_logs.py",
        s["body"],
    ))
    story.append(rule(MGRAY, 0.5))

    # ── 9. Cost Analysis ──────────────────────────────────────────────────────
    story.append(KeepTogether([section_header("9. Cost Analysis", s), Spacer(1, 0.2 * cm)]))
    story.append(Paragraph(
        "The following analysis presents what a professional consultant or freelance "
        "developer would charge for this project in two market contexts. The security "
        "audit and hardening programme (12 hours, ~21% of total effort) is listed as a "
        "separate line item to make the cost of proper security practice visible and "
        "non-negotiable. All KES figures use an exchange rate of KES 130 per USD.",
        s["body"],
    ))

    # Nairobi market
    story.append(Paragraph(b("9.1  Nairobi Market"), s["h3"]))
    story.append(Paragraph(
        "The project spans three disciplines: full-stack web development, UI/UX design, "
        "and DevOps / cloud deployment. The blended rate below reflects a mid-to-senior "
        "consultant capable of delivering all three, plus a security specialist rate "
        "for the audit and hardening work.",
        s["body"],
    ))
    nbi_rows = [
        ["Discipline",                          "Nairobi Rate (KES/hr)", "Hours", "Subtotal (KES)"],
        ["Full-stack development (Flask, PDF, Email)", "2,000 – 2,500",  "28",   "56,000 – 70,000"],
        ["UI / UX design (Bootstrap dark theme)",      "1,500 – 2,000",  "6",    "9,000 – 12,000"],
        ["DevOps / deployment (Render, env vars)",     "1,800 – 2,500",  "5",    "9,000 – 12,500"],
        ["Security audit &amp; hardening",             "2,000 – 2,500",  "12",   "24,000 – 30,000"],
        ["Documentation &amp; QA",                     "1,500 – 2,000",  "6",    "9,000 – 12,000"],
    ]
    story.append(phase_table(nbi_rows, s,
        col_widths=[INNER_W*0.40, INNER_W*0.22, INNER_W*0.10, INNER_W*0.28]))
    story.append(Spacer(1, 0.1 * cm))
    story.append(Paragraph(
        "Nairobi market total:  KES 107,000 – 136,500  (~USD 823 – 1,050)",
        s["total"],
    ))
    story.append(Paragraph(
        "For reference, a fixed-price project quote in the Nairobi market for a "
        "deliverable of this scope, polish, and security posture would typically range "
        "from <b>KES 110,000 – 150,000</b>, including one round of post-launch revisions.",
        s["note"],
    ))

    # Global market
    story.append(Paragraph(b("9.2  Global Market (US / Western Europe)"), s["h3"]))
    story.append(Paragraph(
        "On international freelance platforms (Upwork, Toptal, Arc.dev), senior Python "
        "developers with full-stack, DevOps, and application security capability "
        "typically command the following rates in 2026:",
        s["body"],
    ))
    global_rows = [
        ["Discipline",                          "Global Rate (USD/hr)", "Hours", "Subtotal (USD)"],
        ["Full-stack development (Flask, PDF, Email)", "85 – 120",      "28",   "2,380 – 3,360"],
        ["UI / UX design (Bootstrap dark theme)",      "60 – 90",       "6",    "360 – 540"],
        ["DevOps / deployment (Render, env vars)",     "80 – 110",      "5",    "400 – 550"],
        ["Security audit &amp; hardening",             "90 – 130",      "12",   "1,080 – 1,560"],
        ["Documentation &amp; QA",                     "65 – 90",       "6",    "390 – 540"],
    ]
    story.append(phase_table(global_rows, s,
        col_widths=[INNER_W*0.40, INNER_W*0.22, INNER_W*0.10, INNER_W*0.28]))
    story.append(Spacer(1, 0.1 * cm))
    story.append(Paragraph(
        "Global market total:  USD 4,610 – 6,550  (~KES 599,000 – 851,000)",
        s["total"],
    ))
    story.append(Paragraph(
        "A US-based digital agency or boutique software consultancy billing at agency "
        "rates ($150 – $200/hr) would price this project at <b>USD 8,550 – 11,400</b>.",
        s["note"],
    ))

    # Summary table
    story.append(Paragraph(b("9.3  Cost Summary"), s["h3"]))
    summary_rows = [
        ["Market",                   "Rate Basis",        "Low Estimate",              "High Estimate"],
        ["Nairobi — local clients",  "KES 1,500–2,500/hr","KES 107,000\n(~USD 823)",  "KES 136,500\n(~USD 1,050)"],
        ["Nairobi — intl. clients",  "USD 25–45/hr",      "USD 1,425\n(~KES 185,000)","USD 2,565\n(~KES 334,000)"],
        ["Global freelance market",  "USD 85–130/hr",     "USD 4,610\n(~KES 599,000)","USD 6,550\n(~KES 851,000)"],
        ["US / EU agency rate",      "USD 150–200/hr",    "USD 8,550\n(~KES 1,112,000)","USD 11,400\n(~KES 1,482,000)"],
    ]
    story.append(phase_table(summary_rows, s,
        col_widths=[INNER_W*0.28, INNER_W*0.22, INNER_W*0.25, INNER_W*0.25]))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(
        "Rates based on 2025–2026 market data from Glassdoor, PayScale, Arc.dev, and "
        "lemon.io. Security audit and hardening (12 hrs) accounts for approximately 21% "
        "of total project effort, reflecting the non-negotiable cost of building a "
        "public-facing form that handles sensitive personal and career information. "
        "Ongoing hosting costs are zero on Render's free tier; Resend's free tier covers "
        "3,000 emails/month.",
        s["note"],
    ))
    story.append(rule(MGRAY, 0.5))

    # ── 10. Final Deliverable ──────────────────────────────────────────────────
    story.append(KeepTogether([section_header("10. Final Deliverable", s), Spacer(1, 0.2 * cm)]))
    story.append(Paragraph(
        "The completed system consists of the following components, all version-controlled "
        "in the GitHub repository <b>ericgitonga/career-transition-intake</b>:",
        s["body"],
    ))
    deliverables = [
        ("app.py",
         "Flask application: two routes, PDF generation, Resend email dispatch, file upload "
         "handling, and all 15 security controls implemented (_safe_suffix, _clip, _sanitize, "
         "CSRFProtect, Limiter, _security_headers, random temp filenames, finally-block cleanup, "
         "structured logging). Fully documented with detailed docstrings."),
        ("templates/index.html",
         "Dark-themed Bootstrap 5.3 form with SHA-384 SRI hashes on both CDN resources, "
         "a CSRF token hidden field, 10 accordion sections, 4 dedicated upload fields plus "
         "a multi-select additional documents field. No inline scripts. Includes: client "
         "type radio, current domain and languages fields, LinkedIn URL input, conditional "
         "role title field (revealed by target clarity), work style / travel / management "
         "preference radios, dynamic portfolio link list (yes/no radio + add/remove URL "
         "fields), free-form catch-all 'anything else' textarea, and a CV fallback block "
         "nested inside the CV column (toggle-revealed, single-column stacked layout, "
         "auto-collapsed on CV upload)."),
        ("static/form.js",
         "Form interaction JavaScript: target clarity → conditional role title reveal; "
         "CV fallback toggle (show/hide + auto-collapse on file select); hours slider "
         "value display; AJAX fetch submission; PDF blob download trigger; email status "
         "feedback. Served as a static file to satisfy the strict script-src CSP."),
        ("requirements.txt",
         "Six pinned dependencies: flask==3.1.3, flask-wtf==1.3.0, flask-limiter==4.1.1, "
         "gunicorn==26.0.0, reportlab==4.4.10, resend==2.32.2."),
        ("render.yaml",
         "Infrastructure-as-code: two services — the Flask web service (Python runtime, "
         "gunicorn start command, RESEND_API_KEY / SECRET_KEY / LOADING_SITE_ORIGIN env vars) "
         "and the companion Render Static Site (career-transition-loading, staticPublishPath: loading)."),
        ("loading/index.html",
         "Branded dark-theme loading page served by the Render Static Site. Displays a spinner "
         "and a 'Preparing your form...' tagline, no visible countdown. Polls the Flask app's "
         "/_health endpoint every 3 seconds and redirects on success. This is the canonical "
         "client-facing URL — it replaces Render's server-log cold-start screen entirely."),
        (".python-version",
         "Pins Python 3.11.9 to ensure consistent runtime across all Render deploys."),
        ("SKILL.md",
         "Consultant workflow guide including a Security First section with a controls reference "
         "table, client data handling rules, user-facing behaviour rules (plain-English errors, "
         "loading page as canonical entry point), change-management guidelines, and an expanded "
         "quality checklist with security checks as the first gate."),
        ("hosting.pdf",
         "Illustrated setup guide for deploying and operating the service, covering Render "
         "account setup, Resend API key creation, and ongoing maintenance commands."),
        ("generate_hosting_pdf.py",
         "ReportLab script that regenerates hosting.pdf when deployment instructions change. "
         "Fully documented with comprehensive docstrings."),
        ("generate_design_pdf.py",
         "ReportLab script that produces this document. Tracked in the repository; regenerate "
         "whenever the design narrative, effort breakdown, or cost figures are updated."),
    ]
    for name, desc in deliverables:
        story.append(Paragraph(f"• <b>{name}</b> — {desc}", s["bullet"]))

    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(b("Live URLs:"), s["h3"]))
    story.append(Paragraph("Client entry point (share this):  https://career-transition-loading.onrender.com", s["code"]))
    story.append(Paragraph("Flask application (internal):     https://career-transition-intake.onrender.com", s["code"]))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        "The service is production-ready and hardened. Clients are directed to the loading "
        "page URL, which handles cold-start waiting gracefully and redirects automatically "
        "to the form. On submission, their completed intake PDF is delivered to the "
        "consultant's inbox within seconds, with no manual intervention required, and "
        "the submission is logged server-side for audit and abuse detection.",
        s["body"],
    ))
    story.append(rule(GOLD, 1.5, 12, 4))

    return story


# ── Document builder ──────────────────────────────────────────────────────────

def make_doc():
    """Orchestrate the full PDF build pipeline and write the output file.

    Calls ``styles()`` to obtain the shared style dictionary, constructs a
    ``SimpleDocTemplate`` configured for A4 with standard margins, defines a
    ``footer`` callback for per-page annotation, calls ``build_story()`` to
    obtain the complete flowable list, and builds the document. Prints the
    output path to stdout on completion.

    The output is written to ``OUTPUT_PATH`` (``extras/design_process.pdf``
    relative to this script's directory). The ``extras/`` directory is
    git-ignored, keeping this internal project document out of version control.

    Raises:
        FileNotFoundError: If the ``extras/`` directory does not exist.
        PermissionError:   If the process lacks write access to ``OUTPUT_PATH``.
    """
    s = styles()
    doc = SimpleDocTemplate(
        OUTPUT_PATH, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=1.5 * cm, bottomMargin=1.8 * cm,
    )

    def footer(canvas, doc):
        """Draw a two-part footer at the bottom of each page of the PDF.

        Called by ReportLab's build pipeline via ``onFirstPage`` and
        ``onLaterPages``. Renders the document title flush-left and the
        current page number flush-right, both in 8pt grey Helvetica,
        positioned 0.7 cm from the bottom edge of the page.

        Args:
            canvas: The ReportLab canvas for the current page.
            doc:    The SimpleDocTemplate being built (provides ``doc.page``).
        """
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#888888"))
        canvas.drawString(MARGIN, 0.7 * cm,
                          "Career Transition Planning Service — Design Process Report")
        canvas.drawRightString(W - MARGIN, 0.7 * cm, f"Page {doc.page}")
        canvas.restoreState()

    doc.build(build_story(s), onFirstPage=footer, onLaterPages=footer)
    print(f"PDF written to: {OUTPUT_PATH}")


if __name__ == "__main__":
    make_doc()
