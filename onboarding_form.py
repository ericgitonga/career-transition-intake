#!/usr/bin/env python3
"""
Career Transition Client Onboarding Form
Gradio web form → ReportLab PDF → Gmail (smtp.gmail.com)

Setup: set SMTP_USER and SMTP_PASSWORD env vars before running, e.g.
  export SMTP_USER="you@gmail.com"
  export SMTP_PASSWORD="your-app-password"   # Gmail App Password, not login password

Run:
  conda run -n ds python onboarding_form.py
"""

import os
import smtplib
import tempfile
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import gradio as gr
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable, KeepTogether, Paragraph,
    SimpleDocTemplate, Spacer, Table, TableStyle,
)

RECIPIENT = "gitonga@gmail.com"

NAVY  = colors.HexColor("#1B2A4A")
TEAL  = colors.HexColor("#0E7C7B")
GOLD  = colors.HexColor("#C9A84C")
LGRAY = colors.HexColor("#F4F6F9")
MGRY  = colors.HexColor("#D0D6E0")
WHITE = colors.white
BLACK = colors.HexColor("#1A1A1A")


# ── ReportLab helpers ─────────────────────────────────────────────────────────

def _S(name, **kw):
    return ParagraphStyle(name, **kw)


_h1     = _S("H1",  fontSize=16, textColor=WHITE, fontName="Helvetica-Bold", leading=20)
_label  = _S("Lbl", fontSize=9.5, textColor=NAVY,  fontName="Helvetica-Bold", leading=14)
_ans    = _S("Ans", fontSize=9.5, textColor=BLACK, fontName="Helvetica",     leading=13, leftIndent=12)
_meta   = _S("Met", fontSize=8,  textColor=MGRY,  fontName="Helvetica",     leading=12, alignment=TA_CENTER)
_ct     = _S("CT",  fontSize=22, textColor=WHITE, fontName="Helvetica-Bold", leading=28, alignment=TA_CENTER)
_cs     = _S("CS",  fontSize=14, textColor=GOLD,  fontName="Helvetica-Bold", leading=20, alignment=TA_CENTER)
_cn     = _S("CN",  fontSize=18, textColor=WHITE, fontName="Helvetica-Bold", leading=24, alignment=TA_CENTER)


def _banner(text):
    t = Table([[Paragraph(text, _h1)]], colWidths=[17 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), NAVY),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
    ]))
    return t


def _qa(question, value):
    text = ", ".join(value) if isinstance(value, list) else str(value or "—").strip() or "—"
    return [Paragraph(question, _label), Paragraph(text, _ans), Spacer(1, 4)]


def build_pdf(d: dict, path: str) -> str:
    doc = SimpleDocTemplate(
        path, pagesize=A4,
        leftMargin=1.27*cm, rightMargin=1.27*cm,
        topMargin=1.5*cm,   bottomMargin=1.5*cm,
    )

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(MGRY)
        canvas.drawCentredString(
            A4[0] / 2, 0.6 * cm,
            f"Career Transition Onboarding · {d.get('full_name', '')} · Page {doc.page}",
        )
        canvas.restoreState()

    W, story = 17 * cm, []

    # Cover
    story.append(Spacer(1, 1.5 * cm))
    cover = Table([
        [Paragraph("CAREER TRANSITION", _ct)],
        [Paragraph("Client Onboarding Intake", _cs)],
        [Paragraph(d.get("full_name", ""), _cn)],
        [Paragraph(datetime.now().strftime("Submitted: %d %B %Y"), _meta)],
    ], colWidths=[W])
    cover.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), NAVY),
        ("TOPPADDING",    (0, 0), (-1, -1), 16),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 16),
        ("LEFTPADDING",   (0, 0), (-1, -1), 20),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 20),
    ]))
    story += [cover, Spacer(1, 0.4*cm),
              HRFlowable(width=W, thickness=2, color=GOLD),
              Spacer(1, 0.8*cm)]

    sections = [
        ("Section 1 — Personal Information", [
            ("Full name",                              d.get("full_name")),
            ("City & Country",                         d.get("city_country")),
            ("Email address",                          d.get("client_email")),
            ("Preferred currency",                     d.get("currency")),
            ("Transition timeline preference",         d.get("timeline")),
        ]),
        ("Section 2 — Motivation & Context", [
            ("What is driving this transition?",                       d.get("motivation_type")),
            ("How long have you been thinking about this move?",       d.get("thinking_duration")),
            ("Concrete steps already taken",                           d.get("steps_taken")),
            ("What specifically attracts you to the target domain?",   d.get("attraction")),
        ]),
        ("Section 3 — Target Role Clarity", [
            ("How clear are you on the role you want?",                d.get("target_clarity")),
            ("Preferred organisation types",                           d.get("org_types")),
            ("Roles / sectors explicitly ruled out",                   d.get("ruled_out")),
            ("People or organisations you admire in the target field", d.get("admired")),
            ("Target domain / field",                                  d.get("target_domain")),
        ]),
        ("Section 4 — Constraints & Capacity", [
            ("Currently employed?",                                    d.get("employed")),
            ("If employed — transitioning while working or leaving?",  d.get("employed_status")),
            ("Hours per week available for transition work",           d.get("hours_per_week")),
            ("Financial runway",                                       d.get("financial_runway")),
            ("Geographic constraints",                                 d.get("geography")),
            ("Personal / family commitments affecting schedule",       d.get("personal_commitments")),
        ]),
        ("Section 5 — Financial Expectations", [
            ("Type of move targeted",                                  d.get("move_type")),
            ("Minimum income level to protect",                        d.get("income_floor")),
        ]),
        ("Section 6 — Learning Style & Pace", [
            ("Preferred learning format",                              d.get("learning_format")),
            ("Breadth-first or depth-first?",                          d.get("learning_preference")),
            ("Learning formats to avoid",                              d.get("learning_avoid")),
        ]),
        ("Section 7 — Network & Visibility", [
            ("Existing contacts in the target domain",                 d.get("network_warmth")),
            ("Is the transition confidential?",                        d.get("transition_confidential")),
            ("Comfort with public visibility",                         d.get("visibility_comfort")),
            ("Mentor status",                                          d.get("mentor_status")),
        ]),
        ("Section 8 — Past Attempts & Blockers", [
            ("Previous attempts to make this move",                    d.get("past_attempts")),
            ("Biggest uncertainties or fears",                         d.get("biggest_fears")),
        ]),
        ("Section 9 — Deliverable Preferences", [
            ("Who will see this plan?",                                d.get("plan_audience")),
            ("Sections to emphasise",                                  d.get("emphasise")),
            ("Background notes / anything to handle with care",        d.get("background_notes")),
        ]),
    ]

    for title, pairs in sections:
        story.append(KeepTogether([_banner(title), Spacer(1, 8)]))
        for q, a in pairs:
            story += _qa(q, a)
        story += [Spacer(1, 6), HRFlowable(width=W, thickness=0.5, color=MGRY), Spacer(1, 6)]

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return path


# ── Email ─────────────────────────────────────────────────────────────────────

def send_email(pdf_path: str, data: dict, attachments: list, smtp_user: str, smtp_password: str):
    msg = MIMEMultipart()
    msg["From"]    = smtp_user
    msg["To"]      = RECIPIENT
    msg["Subject"] = (
        f"Career Transition Intake — {data.get('full_name', 'New Client')} — "
        f"{datetime.now().strftime('%d %b %Y')}"
    )
    n_docs = len([a for a in attachments if a])
    body = (
        f"New career transition onboarding submission received.\n\n"
        f"Client:   {data.get('full_name', '—')}\n"
        f"Email:    {data.get('client_email', '—')}\n"
        f"Location: {data.get('city_country', '—')}\n"
        f"Timeline: {data.get('timeline', '—')}\n"
        f"Target:   {data.get('target_domain', '—')}\n\n"
        f"Full intake responses are in the attached PDF."
        + (f"\n{n_docs} supporting document(s) also attached." if n_docs else "")
    )
    msg.attach(MIMEText(body, "plain"))

    for fpath in [pdf_path] + attachments:
        if not fpath or not os.path.exists(str(fpath)):
            continue
        with open(fpath, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f'attachment; filename="{Path(fpath).name}"')
        msg.attach(part)

    with smtplib.SMTP("smtp.gmail.com", 587) as srv:
        srv.ehlo()
        srv.starttls()
        srv.login(smtp_user, smtp_password)
        srv.sendmail(smtp_user, RECIPIENT, msg.as_string())


# ── Submit handler ────────────────────────────────────────────────────────────

def _file_path(f):
    """Normalise a Gradio file value to a path string or None."""
    if f is None:
        return None
    if isinstance(f, str):
        return f if os.path.exists(f) else None
    if hasattr(f, "name"):
        return f.name if os.path.exists(f.name) else None
    return None


def submit(
    # Section 1
    full_name, city_country, client_email, currency, timeline,
    # Section 2
    motivation_type, thinking_duration, steps_taken, attraction,
    # Section 3
    target_domain, target_clarity, org_types, ruled_out, admired,
    # Section 4
    employed, employed_status, hours_per_week, financial_runway,
    geography, personal_commitments,
    # Section 5
    move_type, income_floor,
    # Section 6
    learning_format, learning_preference, learning_avoid,
    # Section 7
    network_warmth, transition_confidential, visibility_comfort, mentor_status,
    # Section 8
    past_attempts, biggest_fears,
    # Section 9
    plan_audience, emphasise, background_notes,
    # Documents
    cv_file, linkedin_file, jd_file, learning_plan_file, headshot_file,
    # Email
    send_email_flag, smtp_user, smtp_password,
):
    if not full_name or not full_name.strip():
        return "Please enter your full name before submitting.", None

    data = dict(
        full_name=full_name.strip(),
        city_country=city_country, client_email=client_email,
        currency=currency, timeline=timeline,
        motivation_type=motivation_type, thinking_duration=thinking_duration,
        steps_taken=steps_taken, attraction=attraction,
        target_domain=target_domain, target_clarity=target_clarity,
        org_types=org_types, ruled_out=ruled_out, admired=admired,
        employed=employed, employed_status=employed_status,
        hours_per_week=str(hours_per_week) + " hrs/week",
        financial_runway=financial_runway, geography=geography,
        personal_commitments=personal_commitments,
        move_type=move_type, income_floor=income_floor,
        learning_format=learning_format, learning_preference=learning_preference,
        learning_avoid=learning_avoid,
        network_warmth=network_warmth, transition_confidential=transition_confidential,
        visibility_comfort=visibility_comfort, mentor_status=mentor_status,
        past_attempts=past_attempts, biggest_fears=biggest_fears,
        plan_audience=plan_audience, emphasise=emphasise, background_notes=background_notes,
    )

    initials = "".join(w[0].upper() for w in full_name.split() if w)
    pdf_name = f"{initials}_intake_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    pdf_path = os.path.join(tempfile.gettempdir(), pdf_name)

    try:
        build_pdf(data, pdf_path)
    except Exception as exc:
        return f"PDF generation failed: {exc}", None

    uploads = [_file_path(f) for f in [cv_file, linkedin_file, jd_file, learning_plan_file, headshot_file]]
    uploads = [p for p in uploads if p]

    log = [f"Intake PDF ready: {pdf_name}"]

    if send_email_flag:
        u = (smtp_user or os.environ.get("SMTP_USER", "")).strip()
        p = (smtp_password or os.environ.get("SMTP_PASSWORD", "")).strip()
        if not u or not p:
            log.append("Email skipped — SMTP credentials not provided.")
        else:
            try:
                send_email(pdf_path, data, uploads, u, p)
                suffix = f" + {len(uploads)} document(s)" if uploads else ""
                log.append(f"Email sent to {RECIPIENT} (PDF{suffix} attached).")
            except Exception as exc:
                log.append(f"Email failed: {exc}")
    else:
        log.append("Email not requested.")

    return "\n".join(log), pdf_path


# ── Gradio UI ─────────────────────────────────────────────────────────────────

ENV_SMTP_USER = os.environ.get("SMTP_USER", "")
ENV_SMTP_PASS = os.environ.get("SMTP_PASSWORD", "")

TIMELINE_CHOICES = [
    "6 months (urgent)",
    "12 months",
    "18 months (default)",
    "24 months",
    "24+ months (patient/part-time)",
]
RUNWAY_CHOICES = [
    "Less than 3 months",
    "3–6 months",
    "6–12 months",
    "12–18 months",
    "18+ months",
    "Currently employed — no runway needed",
]
ORG_TYPES = [
    "NGO / Non-profit",
    "Multilateral / UN agency",
    "Development finance institution",
    "Corporate / Multinational",
    "Tech company",
    "Government / Public sector",
    "Think tank / Research institute",
    "Consultancy",
    "Startup",
    "Academic institution",
]
LEARNING_FORMATS = [
    "Self-paced online (Coursera, edX, LinkedIn Learning)",
    "Cohort / community-based program",
    "Intensive bootcamp",
    "University / postgrad program",
    "Mentorship / apprenticeship",
    "Books & self-study",
    "In-person workshops / conferences",
]
VISIBILITY_LEVELS = [
    "Very comfortable — already active publicly",
    "Comfortable — willing to start posting",
    "Neutral — open but not enthusiastic",
    "Uncomfortable — prefer to stay low-profile",
    "Not comfortable at all",
]

css = """
.form-title { font-size: 1.6rem; font-weight: 700; color: #1B2A4A; margin-bottom: 0; }
.form-sub   { color: #0E7C7B; font-size: 1rem; margin-top: 0; }
.status-box textarea { font-family: monospace; font-size: 0.88rem; }
"""

with gr.Blocks(title="Career Transition Onboarding") as app:

    gr.Markdown("# Career Transition Onboarding", elem_classes="form-title")
    gr.Markdown(
        "Complete all sections below. Your responses will be compiled into a "
        "professionally formatted PDF and, if enabled, emailed to your consultant.",
        elem_classes="form-sub",
    )

    # ── Section 1: Personal Information ───────────────────────────────────────
    with gr.Accordion("1 — Personal Information", open=True):
        with gr.Row():
            full_name      = gr.Textbox(label="Full name *", placeholder="e.g. Jane Wanjiru Mwangi")
            client_email   = gr.Textbox(label="Your email address", placeholder="jane@example.com")
        with gr.Row():
            city_country   = gr.Textbox(label="City & Country", placeholder="e.g. Nairobi, Kenya")
            currency       = gr.Textbox(label="Preferred currency", placeholder="e.g. KES / USD")
        timeline = gr.Radio(
            label="Transition timeline preference",
            choices=TIMELINE_CHOICES,
            value="18 months (default)",
        )

    # ── Section 2: Motivation & Context ───────────────────────────────────────
    with gr.Accordion("2 — Motivation & Context", open=False):
        motivation_type = gr.Radio(
            label="What is driving this transition?",
            choices=[
                "Proactive — a new opportunity genuinely excites me",
                "Reactive — layoff, redundancy, or job loss",
                "Reactive — burnout or values misalignment",
                "Reactive — life event (relocation, family, health)",
                "Mixed — both push and pull factors",
            ],
        )
        thinking_duration = gr.Radio(
            label="How long have you been seriously thinking about this move?",
            choices=[
                "Less than 3 months — early stage",
                "3–6 months",
                "6–12 months",
                "More than a year",
                "Several years — this has been on hold",
            ],
        )
        steps_taken = gr.Textbox(
            label="Concrete steps already taken (courses enrolled, conversations had, applications submitted)",
            placeholder="e.g. Completed Coursera AI for Everyone; attended two industry events; spoke with two people already in the field",
            lines=3,
        )
        attraction = gr.Textbox(
            label="What specifically attracts you to the target domain? (Values, income, lifestyle, impact, intellectual interest — be honest)",
            placeholder="e.g. I want work that aligns with my environmental values and I believe sustainability skills will be in demand...",
            lines=4,
        )

    # ── Section 3: Target Role Clarity ────────────────────────────────────────
    with gr.Accordion("3 — Target Role Clarity", open=False):
        target_domain = gr.Textbox(
            label="Target domain / field *",
            placeholder="e.g. Climate Finance, ESG Advisory, Digital Health, Data Governance",
        )
        target_clarity = gr.Radio(
            label="How clear are you on the role you want?",
            choices=[
                "Very clear — I know the exact title and sector",
                "Clear — I know the general direction and function",
                "Partially clear — I have 2–3 options I'm weighing",
                "Exploring — I know what I'm leaving, not where I'm going",
            ],
        )
        org_types = gr.CheckboxGroup(
            label="Preferred organisation types (select all that apply)",
            choices=ORG_TYPES,
        )
        ruled_out = gr.Textbox(
            label="Roles, sectors, or organisation types explicitly ruled out",
            placeholder="e.g. No pure sales roles; not interested in extractive industries",
            lines=2,
        )
        admired = gr.Textbox(
            label="People or organisations you admire in the target field",
            placeholder="e.g. Ellen MacArthur Foundation; Dr. Akinwumi Adesina; IFC's climate team",
            lines=2,
        )

    # ── Section 4: Constraints & Capacity ─────────────────────────────────────
    with gr.Accordion("4 — Constraints & Capacity", open=False):
        employed = gr.Radio(
            label="Are you currently employed?",
            choices=["Yes", "No — I have left / been made redundant", "No — about to leave"],
        )
        employed_status = gr.Radio(
            label="If employed — which best describes your situation?",
            choices=[
                "Transitioning while employed (evenings / weekends only)",
                "Planning to leave soon to focus full-time on the transition",
                "Not applicable",
            ],
            value="Not applicable",
        )
        hours_per_week = gr.Slider(
            label="Hours per week realistically available for study, networking, and portfolio work",
            minimum=2, maximum=60, step=1, value=10,
        )
        financial_runway = gr.Radio(
            label="Financial runway — how long can you invest in this transition before needing income from the new field?",
            choices=RUNWAY_CHOICES,
        )
        geography = gr.Textbox(
            label="Geographic constraints",
            placeholder="e.g. Must stay in Nairobi; open to East Africa; remote-only preferred; willing to relocate globally",
            lines=2,
        )
        personal_commitments = gr.Textbox(
            label="Personal or family commitments that affect your study schedule (optional)",
            placeholder="e.g. Primary caregiver for young children — evenings only; managing a health condition",
            lines=2,
        )

    # ── Section 5: Financial Expectations ─────────────────────────────────────
    with gr.Accordion("5 — Financial Expectations", open=False):
        move_type = gr.Radio(
            label="Type of move you are targeting",
            choices=[
                "Step up — I expect to earn more in the new field",
                "Lateral — roughly the same level and pay",
                "Step back in seniority / pay to break in — acceptable short-term",
                "Unsure — open to guidance",
            ],
        )
        income_floor = gr.Textbox(
            label="Is there a minimum income level you need to protect? (optional — approximate figure and currency)",
            placeholder="e.g. USD 60,000 / year — below this I cannot cover my obligations",
            lines=2,
        )

    # ── Section 6: Learning Style ──────────────────────────────────────────────
    with gr.Accordion("6 — Learning Style & Pace", open=False):
        learning_format = gr.CheckboxGroup(
            label="Preferred learning formats (select all that apply)",
            choices=LEARNING_FORMATS,
        )
        learning_preference = gr.Radio(
            label="How do you prefer to build knowledge?",
            choices=[
                "Breadth-first — explore widely across the domain, then specialise",
                "Depth-first — go deep on one thing before moving to the next",
                "No preference / depends on the topic",
            ],
        )
        learning_avoid = gr.Textbox(
            label="Learning formats you dislike or have tried without success (optional)",
            placeholder="e.g. I've abandoned 3 MOOCs — I need a cohort for accountability",
            lines=2,
        )

    # ── Section 7: Network & Visibility ───────────────────────────────────────
    with gr.Accordion("7 — Network & Visibility", open=False):
        network_warmth = gr.Radio(
            label="Existing contacts already working in the target domain",
            choices=[
                "None — starting from scratch",
                "1–3 contacts — a thin warm network",
                "4–10 contacts — moderate network",
                "10+ contacts — strong existing network",
            ],
        )
        transition_confidential = gr.Radio(
            label="Is your transition confidential? (affects LinkedIn and visibility tactics)",
            choices=[
                "Yes — my employer and colleagues must not know yet",
                "Partially — close contacts know but not my employer",
                "No — the transition is open; I can post and share publicly",
            ],
        )
        visibility_comfort = gr.Radio(
            label="Comfort with public visibility (LinkedIn posts, articles, speaking, events)",
            choices=VISIBILITY_LEVELS,
        )
        mentor_status = gr.Radio(
            label="Mentor / coach status",
            choices=[
                "I already have a mentor in the target field",
                "I have a general career coach but not a domain mentor",
                "No mentor — I'd like one built into the plan",
                "No mentor and not interested in one",
            ],
        )

    # ── Section 8: Past Attempts & Blockers ───────────────────────────────────
    with gr.Accordion("8 — Past Attempts & Blockers", open=False):
        past_attempts = gr.Textbox(
            label="Have you tried to make this move before? What got in the way?",
            placeholder="e.g. Started a sustainability cert 2 years ago but stopped when work got busy; applied for 3 roles and got no callbacks",
            lines=4,
        )
        biggest_fears = gr.Textbox(
            label="What aspects of the transition feel most uncertain or daunting?",
            placeholder="e.g. I worry my age is a disadvantage; I'm not sure my CV will be taken seriously without a formal qualification; I don't know anyone in this world",
            lines=4,
        )

    # ── Section 9: Deliverable Preferences ────────────────────────────────────
    with gr.Accordion("9 — Deliverable Preferences", open=False):
        plan_audience = gr.Radio(
            label="Who will see this plan?",
            choices=[
                "Just me — personal accountability tool",
                "Me and my family / partner",
                "Me and my employer or sponsor (they are funding the transition)",
                "I may share it with potential employers or networks",
            ],
        )
        emphasise = gr.Textbox(
            label="Are there sections or topics you'd like to emphasise in the plan?",
            placeholder="e.g. I want detailed networking scripts; please go deep on certifications; I need the portfolio section to be very practical",
            lines=3,
        )
        background_notes = gr.Textbox(
            label="Is there anything about your background you are particularly proud of, or anything to handle carefully?",
            placeholder="e.g. I'm proud of my work in conflict-affected settings — please use that. Prefer not to highlight the two-year gap in 2019–2020.",
            lines=3,
        )

    # ── Section 10: Document Uploads ──────────────────────────────────────────
    with gr.Accordion("10 — Document Uploads", open=False):
        gr.Markdown(
            "Upload supporting documents. These will be attached to the email sent to your consultant "
            "and used to generate your Career Transition Plan."
        )
        with gr.Row():
            cv_file           = gr.File(label="CV / Résumé (PDF recommended) *", file_types=[".pdf", ".doc", ".docx"])
            linkedin_file     = gr.File(label="LinkedIn export or profile summary (optional)", file_types=[".pdf", ".txt"])
        with gr.Row():
            jd_file           = gr.File(label="Target job description (TXT or PDF)", file_types=[".pdf", ".txt"])
            learning_plan_file = gr.File(label="Existing learning plan (optional)", file_types=[".pdf", ".txt", ".docx"])
        headshot_file = gr.File(label="Professional headshot (optional — JPG/PNG)", file_types=[".jpg", ".jpeg", ".png"])

    # ── Section 11: Email Settings ────────────────────────────────────────────
    with gr.Accordion("11 — Email Settings", open=not bool(ENV_SMTP_USER)):
        if ENV_SMTP_USER:
            gr.Markdown(
                f"SMTP credentials loaded from environment (`SMTP_USER` / `SMTP_PASSWORD`). "
                f"Sending from **{ENV_SMTP_USER}** → **{RECIPIENT}**. "
                "Override below only if needed."
            )
        else:
            gr.Markdown(
                f"Enter your Gmail SMTP credentials to email the intake PDF to **{RECIPIENT}**. "
                "Use a [Gmail App Password](https://myaccount.google.com/apppasswords), not your login password. "
                "Leave blank to skip email and download the PDF manually instead."
            )
        send_email_flag = gr.Checkbox(
            label=f"Send intake PDF (and uploaded documents) to {RECIPIENT}",
            value=bool(ENV_SMTP_USER),
        )
        with gr.Row():
            smtp_user     = gr.Textbox(
                label="Gmail address (sender)",
                value=ENV_SMTP_USER,
                placeholder="you@gmail.com",
            )
            smtp_password = gr.Textbox(
                label="Gmail App Password",
                value=ENV_SMTP_PASS,
                placeholder="xxxx xxxx xxxx xxxx",
                type="password",
            )

    # ── Submit ─────────────────────────────────────────────────────────────────
    gr.Markdown("---")
    submit_btn  = gr.Button("Submit Onboarding Form", variant="primary", size="lg")
    status_out  = gr.Textbox(label="Status", interactive=False, lines=4, elem_classes="status-box")
    pdf_out     = gr.File(label="Download your intake PDF", visible=True)

    submit_btn.click(
        fn=submit,
        inputs=[
            full_name, city_country, client_email, currency, timeline,
            motivation_type, thinking_duration, steps_taken, attraction,
            target_domain, target_clarity, org_types, ruled_out, admired,
            employed, employed_status, hours_per_week, financial_runway,
            geography, personal_commitments,
            move_type, income_floor,
            learning_format, learning_preference, learning_avoid,
            network_warmth, transition_confidential, visibility_comfort, mentor_status,
            past_attempts, biggest_fears,
            plan_audience, emphasise, background_notes,
            cv_file, linkedin_file, jd_file, learning_plan_file, headshot_file,
            send_email_flag, smtp_user, smtp_password,
        ],
        outputs=[status_out, pdf_out],
    )

if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0", server_port=7860, share=True,
        inbrowser=True, css=css, theme=gr.themes.Soft(),
    )
