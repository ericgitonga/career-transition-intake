"""
Generate Clients/design_process.pdf — a comprehensive record of the design
process, technical decisions, and cost analysis for the Career Transition
client onboarding form.
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

W, H    = A4
MARGIN  = 1.5 * cm
INNER_W = W - 2 * MARGIN


# ── Styles ────────────────────────────────────────────────────────────────────

def styles():
    """Return the paragraph style dictionary for the document."""
    def S(name, **kw):
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
    """Return a styled horizontal rule flowable."""
    return HRFlowable(width="100%", thickness=thickness, color=color,
                      spaceBefore=before, spaceAfter=after)


def section_header(text, s):
    """Return a full-width navy banner for major document sections."""
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
    """Return a teal-left-border sub-section label."""
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
    """Return a styled data table for the platform decision or cost sections."""
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
    """Wrap text in bold HTML tags for inline use in Paragraph strings."""
    return f"<b>{text}</b>"


def bullet(text, s):
    """Return a single indented bullet-point Paragraph."""
    return Paragraph(f"• {text}", s["bullet"])


# ── Document body ─────────────────────────────────────────────────────────────

def build_story(s):
    """Assemble all flowables for the design process document."""
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

    # Phase 1
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

    # Phase 2
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

    # Phase 3
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
        "Gradio's post-startup self-ping to 127.0.0.1 always failed with 'localhost not "
        "accessible'. Patched by replacing url_ok with a lambda that always returns True.",
    ]:
        story.append(bullet(item, s))
    story.append(Paragraph(
        "Even after all patches, the accumulation of monkey-patches against an ageing "
        "framework represented unacceptable technical debt. The client requested a "
        "framework change.",
        s["body"],
    ))
    story.append(Paragraph(
        "<i>Decision: Replace Gradio entirely. Rewrite the application in Flask.</i>",
        s["note"],
    ))

    # Phase 4
    story.append(KeepTogether([sub_header("Phase 4 — Flask on Render (Final)", s), Spacer(1, 0.15 * cm)]))
    story.append(Paragraph(
        "The application was rewritten from scratch in Flask. The form UI was rebuilt in "
        "Bootstrap 5 with a full dark theme, all Gradio dependencies were removed, and "
        "the PDF generation logic (ReportLab) was retained and refined. The Flask app "
        "deployed cleanly on the first attempt.",
        s["body"],
    ))
    story.append(Paragraph(
        "One remaining issue surfaced: Render's free tier blocks outbound SMTP (port 587), "
        "causing gunicorn worker timeouts when the app attempted to send email via Gmail. "
        "This was resolved by replacing the smtplib / SMTP approach with the Resend "
        "transactional email API, which sends over HTTPS and is never blocked by hosting "
        "providers.",
        s["body"],
    ))
    story.append(Spacer(1, 0.1 * cm))

    # Comparison table
    story.append(Paragraph(b("Platform comparison summary:"), s["h3"]))
    story.append(phase_table(
        [
            ["Platform", "Outcome", "Blocking Issue"],
            ["Hugging Face Spaces", "✗ Abandoned", "Paid plan required; ZeroGPU lock"],
            ["Google Cloud Run", "✗ Aborted", "Excessive operational complexity"],
            ["Render + Gradio", "✗ Abandoned", "Cascade of framework compatibility bugs"],
            ["Render + Flask", "✓ Deployed", "None — production-stable"],
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
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        "The application has two routes: GET / serves the intake form; POST /submit "
        "processes the submission, generates the PDF, attempts email delivery, and "
        "returns the PDF as a file download. The email outcome (sent / failed / skipped) "
        "is communicated back to the browser via an X-Email-Status response header, "
        "allowing the JavaScript layer to display an accurate status message without "
        "blocking the download.",
        s["body"],
    ))

    story.append(sub_header("PDF Generation — ReportLab Platypus", s))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(
        "The PDF is generated programmatically using ReportLab's Platypus layout engine. "
        "Each submission produces a multi-page A4 document featuring a navy cover block "
        "with the client's name and submission date, nine labelled intake sections each "
        "opened by a navy banner, question/answer pairs formatted with bold navy labels "
        "and indented answers, and a per-page footer showing the client name and page "
        "number. Multi-select fields (checkboxes) are joined as comma-separated strings; "
        "blank fields render as an em-dash to prevent empty space in the output.",
        s["body"],
    ))

    story.append(sub_header("Email Delivery — Resend", s))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(
        "Email is sent via the Resend transactional API using the resend Python SDK. "
        "Resend operates over HTTPS (port 443) rather than SMTP (port 587), making it "
        "immune to the port-blocking policies common on cloud hosting platforms. "
        "The API key is stored as a Render environment variable (RESEND_API_KEY) and "
        "is never exposed in the codebase or repository. Clients see no email-related "
        "configuration — submission is a single button click.",
        s["body"],
    ))
    story.append(Paragraph(
        "All uploaded documents (CV, LinkedIn export, job description, learning plan, "
        "and any additional files) are read into memory and attached to the email "
        "alongside the generated PDF. The email body contains a plain-text summary "
        "of the client's key details for at-a-glance review.",
        s["body"],
    ))

    story.append(sub_header("Hosting — Render", s))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(
        "Render's Python web service provides a permanent public URL, automatic TLS, "
        "and GitHub-triggered continuous deployment at no cost on the free tier. "
        "A render.yaml file checked into the repository codifies the service "
        "configuration (build command, start command, environment variable keys) so "
        "the hosting setup is reproducible and version-controlled. Deployment of any "
        "change requires only a git push to the main branch.",
        s["body"],
    ))
    story.append(Spacer(1, 0.1 * cm))
    story.append(rule(MGRAY, 0.5))

    # ── 5. UI/UX Design ───────────────────────────────────────────────────────
    story.append(KeepTogether([section_header("5. UI / UX Design", s), Spacer(1, 0.2 * cm)]))
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
        "(Personal Information) expanded by default so clients immediately see progress. "
        "Sections 2 through 10 (Document Uploads) are collapsed and opened on demand, "
        "reducing visual overwhelm for what is a substantial intake questionnaire.",
        s["body"],
    ))
    story.append(Paragraph(
        "Field types were chosen to match the nature of each question: radio buttons "
        "for mutually exclusive choices, checkboxes for multi-select options (organisation "
        "types, learning formats), a range slider for hours per week, and textareas for "
        "open-ended narrative responses. The document upload section includes dedicated "
        "fields for common file types plus a multi-select 'Additional documents' field "
        "that accepts multiple files in a single selection.",
        s["body"],
    ))

    story.append(Paragraph(b("Submission flow:"), s["h3"]))
    story.append(Paragraph(
        "Form submission is handled entirely via the browser's Fetch API — the page "
        "never reloads. The submit button is disabled and relabelled 'Processing…' during "
        "the server round-trip. On success, the PDF blob is captured from the response, "
        "a temporary object URL is created, and the download is triggered programmatically. "
        "A persistent download link is also shown on the page. The status banner reports "
        "whether email delivery succeeded, failed, or was not configured, based on the "
        "X-Email-Status response header.",
        s["body"],
    ))
    story.append(Spacer(1, 0.1 * cm))
    story.append(rule(MGRAY, 0.5))

    # ── 6. Key Design Decisions ────────────────────────────────────────────────
    story.append(KeepTogether([section_header("6. Key Design Decisions", s), Spacer(1, 0.2 * cm)]))

    decisions = [
        ("No client credentials", "Removing the email settings section from the client-facing form "
         "and moving all credentials to Render environment variables eliminates a significant "
         "friction point and prevents clients from encountering technical setup requirements "
         "that are irrelevant to their task."),
        ("Resend over SMTP", "Gmail SMTP on port 587 is blocked by most cloud hosting providers "
         "to prevent spam. Resend's HTTPS API bypasses this entirely and requires only a single "
         "API key environment variable rather than an email address + App Password pair."),
        ("ReportLab over a template engine", "Generating the PDF programmatically with ReportLab "
         "gives precise control over typography, colour, spacing, and layout. PDF-from-HTML "
         "approaches (WeasyPrint, pdfkit) introduce browser rendering dependencies and are "
         "heavier to host; ReportLab is a pure-Python library with no system dependencies."),
        ("Flask over Gradio / FastAPI", "Flask is the thinnest viable option: one file, two routes, "
         "no framework magic. It eliminates the compatibility fragility that plagued the Gradio "
         "implementation while keeping the codebase easy to maintain and extend."),
        ("Bootstrap 5 dark theme", "Using data-bs-theme='dark' on the root HTML element gives "
         "Bootstrap's component library an appropriate baseline in dark mode, reducing the amount "
         "of custom CSS needed to achieve the dark aesthetic while keeping all interactive states "
         "(focus, hover, validation) consistent."),
        ("X-Email-Status response header", "Returning email outcome in a response header rather "
         "than the response body allows the PDF to be streamed as the primary response payload "
         "while still communicating delivery status to the JavaScript layer — avoiding the "
         "complexity of a two-request pattern or a JSON envelope around the binary PDF."),
    ]
    for title, body in decisions:
        story.append(Paragraph(b(title), s["h3"]))
        story.append(Paragraph(body, s["body"]))

    story.append(rule(MGRAY, 0.5))

    # ── 7. Development Phases & Effort ─────────────────────────────────────────
    story.append(PageBreak())
    story.append(KeepTogether([section_header("7. Development Phases &amp; Effort Breakdown", s), Spacer(1, 0.2 * cm)]))
    story.append(Paragraph(
        "The following breakdown reflects the actual work performed across the full "
        "lifecycle of the project, including all platform iterations and their associated "
        "debugging. Hours are estimates based on typical task durations for work of this "
        "nature and complexity.",
        s["body"],
    ))
    story.append(Spacer(1, 0.1 * cm))

    effort_rows = [
        ["Phase", "Description", "Est. Hours"],
        ["Discovery & Scoping", "Requirements capture, field design, section planning", "2"],
        ["Form Architecture", "10-section field map, input type selection, validation rules", "3"],
        ["HF Spaces Setup", "Initial Gradio form build, README configuration, first deploy", "3"],
        ["HF Spaces Debugging", "colorTo, HfFolder, ZeroGPU, css/theme API fixes", "3"],
        ["Cloud Run Spike", "Dockerfile, GitHub Actions workflow (aborted)", "2"],
        ["Render / Gradio Setup", "render.yaml, Python pin, initial Gradio deploy", "2"],
        ["Render / Gradio Debugging", "Blank page, audioop, boolean schema, starlette, localhost", "5"],
        ["Flask Rewrite", "app.py routes, form handling, Jinja2 template", "4"],
        ["ReportLab PDF Engine", "Cover block, 9 sections, Q&A formatting, footer", "3"],
        ["Email Integration", "SMTP attempt, timeout fix, migration to Resend API", "3"],
        ["UI / Dark Theme", "Bootstrap 5 dark mode, custom CSS, accordion, JS fetch", "4"],
        ["UI Refinement", "Section removal, heading copy, multi-file upload, headshot removal", "2"],
        ["Deployment & DevOps", "render.yaml, env vars, gunicorn config, .python-version", "2"],
        ["Documentation", "hosting.pdf, README, docstrings (app.py + generate_hosting_pdf.py)", "4"],
        ["Testing & QA", "End-to-end submission, email delivery, PDF review, edge cases", "3"],
    ]
    col_w = [INNER_W * 0.30, INNER_W * 0.55, INNER_W * 0.15]
    story.append(phase_table(effort_rows, s, col_widths=col_w))

    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(
        "Total estimated effort: <b>45 hours</b>  (range: 40 – 50 hrs depending on "
        "scope interpretation and experience level of developer).",
        s["bold"],
    ))
    story.append(rule(MGRAY, 0.5))

    # ── 8. Cost Analysis ──────────────────────────────────────────────────────
    story.append(KeepTogether([section_header("8. Cost Analysis", s), Spacer(1, 0.2 * cm)]))
    story.append(Paragraph(
        "The following analysis presents what a professional consultant or freelance "
        "developer would charge for this project in two market contexts: the Nairobi "
        "local market, and the global (US / Western Europe) freelance market. "
        "All KES figures use an exchange rate of KES 130 per USD.",
        s["body"],
    ))

    # Nairobi market
    story.append(Paragraph(b("8.1  Nairobi Market"), s["h3"]))
    story.append(Paragraph(
        "The project spans three disciplines: full-stack web development (Flask, "
        "ReportLab, Resend), UI/UX design (Bootstrap 5, dark theme, accordion layout), "
        "and DevOps / cloud deployment (Render, environment management, CI/CD). "
        "The blended rate below reflects a mid-to-senior consultant capable of "
        "delivering all three.",
        s["body"],
    ))
    nbi_rows = [
        ["Discipline", "Nairobi Rate (KES/hr)", "Hours", "Subtotal (KES)"],
        ["Full-stack development (Flask, PDF, Email)", "2,000 – 2,500", "28", "56,000 – 70,000"],
        ["UI / UX design (Bootstrap dark theme)", "1,500 – 2,000", "6",  "9,000 – 12,000"],
        ["DevOps / deployment (Render, env vars)", "1,800 – 2,500", "5",  "9,000 – 12,500"],
        ["Documentation & QA", "1,500 – 2,000", "6",  "9,000 – 12,000"],
    ]
    story.append(phase_table(nbi_rows, s,
        col_widths=[INNER_W*0.40, INNER_W*0.22, INNER_W*0.10, INNER_W*0.28]))
    story.append(Spacer(1, 0.1 * cm))
    story.append(Paragraph(
        "Nairobi market total:  KES 83,000 – 106,500  (~USD 640 – 820)",
        s["total"],
    ))
    story.append(Paragraph(
        "For reference, a fixed-price project quote in the Nairobi market for a "
        "deliverable of this scope and polish would typically range from "
        "<b>KES 85,000 – 120,000</b>, including one round of post-launch revisions.",
        s["note"],
    ))

    # Global market
    story.append(Paragraph(b("8.2  Global Market (US / Western Europe)"), s["h3"]))
    story.append(Paragraph(
        "On international freelance platforms (Upwork, Toptal, Arc.dev), senior Python "
        "developers with full-stack and DevOps capability typically command the following "
        "rates in 2026:",
        s["body"],
    ))
    global_rows = [
        ["Discipline", "Global Rate (USD/hr)", "Hours", "Subtotal (USD)"],
        ["Full-stack development (Flask, PDF, Email)", "85 – 120", "28", "2,380 – 3,360"],
        ["UI / UX design (Bootstrap dark theme)", "60 – 90",  "6",  "360 – 540"],
        ["DevOps / deployment (Render, env vars)", "80 – 110", "5",  "400 – 550"],
        ["Documentation & QA", "65 – 90",  "6",  "390 – 540"],
    ]
    story.append(phase_table(global_rows, s,
        col_widths=[INNER_W*0.40, INNER_W*0.22, INNER_W*0.10, INNER_W*0.28]))
    story.append(Spacer(1, 0.1 * cm))
    story.append(Paragraph(
        "Global market total:  USD 3,530 – 4,990  (~KES 459,000 – 649,000)",
        s["total"],
    ))
    story.append(Paragraph(
        "A US-based digital agency or boutique software consultancy billing at agency "
        "rates ($150 – $200/hr) would price this project at <b>USD 6,750 – 9,000</b>.",
        s["note"],
    ))

    # Summary table
    story.append(Paragraph(b("8.3  Cost Summary"), s["h3"]))
    summary_rows = [
        ["Market", "Rate Basis", "Low Estimate", "High Estimate"],
        ["Nairobi — local clients", "KES 1,500–2,500/hr", "KES 83,000\n(~USD 640)", "KES 106,500\n(~USD 820)"],
        ["Nairobi — intl. clients", "USD 25–40/hr", "USD 1,125\n(~KES 146,000)", "USD 1,800\n(~KES 234,000)"],
        ["Global freelance market", "USD 75–120/hr", "USD 3,530\n(~KES 459,000)", "USD 4,990\n(~KES 649,000)"],
        ["US / EU agency rate", "USD 150–200/hr", "USD 6,750\n(~KES 878,000)", "USD 9,000\n(~KES 1,170,000)"],
    ]
    story.append(phase_table(summary_rows, s,
        col_widths=[INNER_W*0.28, INNER_W*0.22, INNER_W*0.25, INNER_W*0.25]))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(
        "Note: Rates are based on 2025–2026 market data from Glassdoor, PayScale, "
        "Arc.dev, and lemon.io. All figures assume a single mid-to-senior freelance "
        "consultant delivering the full scope. Ongoing hosting costs are zero on "
        "Render's free tier; Resend's free tier covers 3,000 emails/month.",
        s["note"],
    ))
    story.append(rule(MGRAY, 0.5))

    # ── 9. Final Deliverable ───────────────────────────────────────────────────
    story.append(KeepTogether([section_header("9. Final Deliverable", s), Spacer(1, 0.2 * cm)]))
    story.append(Paragraph(
        "The completed system consists of the following components, all version-controlled "
        "in the GitHub repository <b>ericgitonga/career-transition-intake</b>:",
        s["body"],
    ))
    deliverables = [
        ("app.py", "Flask application: two routes, PDF generation, Resend email dispatch, "
         "file upload handling, X-Email-Status header. Fully documented with detailed docstrings."),
        ("templates/index.html", "Dark-themed Bootstrap 5 form: 10 accordion sections, "
         "4 dedicated file upload fields plus a multi-select additional documents field, "
         "AJAX submission with PDF blob download and email status feedback."),
        ("requirements.txt", "Minimal dependency set: flask, gunicorn, reportlab, resend."),
        ("render.yaml", "Infrastructure-as-code for Render: Python runtime, build/start "
         "commands, RESEND_API_KEY environment variable declaration."),
        (".python-version", "Pins Python 3.11.9 to ensure consistent runtime across deploys."),
        ("hosting.pdf", "Illustrated setup guide for deploying and operating the service, "
         "covering Render account setup, Resend API key creation, and ongoing maintenance."),
        ("generate_hosting_pdf.py", "ReportLab script that regenerates hosting.pdf when the "
         "deployment instructions change. Fully documented with docstrings."),
        ("generate_design_pdf.py", "ReportLab script that produces this document."),
    ]
    for name, desc in deliverables:
        story.append(Paragraph(f"• <b>{name}</b> — {desc}", s["bullet"]))

    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(b("Live URL:"), s["h3"]))
    story.append(Paragraph(
        "https://career-transition-intake.onrender.com", s["code"]))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        "The service is production-ready. A client can be directed to the URL "
        "immediately. On submission their completed intake PDF is delivered to "
        "the consultant's inbox within seconds, with no manual intervention required.",
        s["body"],
    ))
    story.append(rule(GOLD, 1.5, 12, 4))

    return story


# ── Document builder ──────────────────────────────────────────────────────────

def make_doc():
    """Build and write the design process PDF to Clients/design_process.pdf."""
    s = styles()
    doc = SimpleDocTemplate(
        OUTPUT_PATH, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=1.5 * cm, bottomMargin=1.8 * cm,
    )

    def footer(canvas, doc):
        """Draw page number and document title at the bottom of every page."""
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#888888"))
        canvas.drawString(MARGIN, 0.7 * cm, "Career Transition Planning Service — Design Process Report")
        canvas.drawRightString(W - MARGIN, 0.7 * cm, f"Page {doc.page}")
        canvas.restoreState()

    doc.build(build_story(s), onFirstPage=footer, onLaterPages=footer)
    print(f"PDF written to: {OUTPUT_PATH}")


if __name__ == "__main__":
    make_doc()
