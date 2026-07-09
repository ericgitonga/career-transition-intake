"""
Generate Clients/design_process.pdf — a comprehensive record of the design
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
    # → Clients/design_process.pdf
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

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "Clients", "design_process.pdf")

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
        "codebase, documented in detail in a separate internal audit report (Clients/security.pdf).",
        s["body"],
    ))
    story.append(Spacer(1, 0.2 * cm))
    story.append(rule(MGRAY, 0.5))

    # ── 2. Project Brief ───────────────────────────────────────────────────────
    story.append(KeepTogether([section_header("2. Project Brief &amp; Objectives", s), Spacer(1, 0.2 * cm)]))
    story.append(Paragraph(
        "The brief was to build a structured digital intake form for a career transition "
        "coaching practice. Clients completing the form would provide information across "
        "nine thematic areas: personal information, motivation and context, target role "
        "clarity, constraints and capacity, financial expectations, learning style, "
        "network and visibility, past attempts and blockers, and deliverable preferences.",
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
        "and a phased refactor plan is stored in Clients/security.pdf "
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
    ]
    col_w = [INNER_W * 0.30, INNER_W * 0.55, INNER_W * 0.15]
    story.append(phase_table(effort_rows, s, col_widths=col_w))

    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(
        "Total estimated effort: <b>57 hours</b>  (range: 51 – 63 hrs), comprising "
        "45 hours of product development and 12 hours of security audit and hardening.",
        s["bold"],
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
         "a multi-select additional documents field. No inline scripts."),
        ("static/form.js",
         "Form interaction JavaScript: hours slider, AJAX fetch submission, PDF blob download "
         "trigger, email status feedback. Served as a static file to satisfy the strict "
         "script-src CSP with no 'unsafe-inline'."),
        ("requirements.txt",
         "Six pinned dependencies: flask==3.1.3, flask-wtf==1.3.0, flask-limiter==4.1.1, "
         "gunicorn==26.0.0, reportlab==4.4.10, resend==2.32.2."),
        ("render.yaml",
         "Infrastructure-as-code: Python runtime, build/start commands, RESEND_API_KEY and "
         "SECRET_KEY environment variable declarations (both sync: false — set in dashboard)."),
        (".python-version",
         "Pins Python 3.11.9 to ensure consistent runtime across all Render deploys."),
        ("SKILL.md",
         "Consultant workflow guide including a Security First section with a controls reference "
         "table, client data handling rules, change-management guidelines, and an expanded "
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
    story.append(Paragraph(b("Live URL:"), s["h3"]))
    story.append(Paragraph("https://career-transition-intake.onrender.com", s["code"]))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        "The service is production-ready and hardened. A client can be directed to the "
        "URL immediately. On submission, their completed intake PDF is delivered to the "
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

    The output is written to ``OUTPUT_PATH`` (``Clients/design_process.pdf``
    relative to this script's directory). The ``Clients/`` directory is
    git-ignored, keeping client-facing documents out of version control.

    Raises:
        FileNotFoundError: If the ``Clients/`` directory does not exist.
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
