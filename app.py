import os
import smtplib
import tempfile
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from flask import Flask, request, render_template, send_file
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable, KeepTogether, Paragraph,
    SimpleDocTemplate, Spacer, Table, TableStyle,
)

app = Flask(__name__)
RECIPIENT = "gitonga@gmail.com"

NAVY = colors.HexColor("#1B2A4A")
TEAL = colors.HexColor("#0E7C7B")
GOLD = colors.HexColor("#C9A84C")
MGRY = colors.HexColor("#D0D6E0")
WHITE = colors.white
BLACK = colors.HexColor("#1A1A1A")

def _S(name, **kw):
    return ParagraphStyle(name, **kw)

_h1    = _S("H1",  fontSize=16, textColor=WHITE, fontName="Helvetica-Bold", leading=20)
_label = _S("Lbl", fontSize=9.5, textColor=NAVY,  fontName="Helvetica-Bold", leading=14)
_ans   = _S("Ans", fontSize=9.5, textColor=BLACK, fontName="Helvetica",     leading=13, leftIndent=12)
_meta  = _S("Met", fontSize=8,   textColor=MGRY,  fontName="Helvetica",     leading=12, alignment=TA_CENTER)
_ct    = _S("CT",  fontSize=22,  textColor=WHITE, fontName="Helvetica-Bold", leading=28, alignment=TA_CENTER)
_cs    = _S("CS",  fontSize=14,  textColor=GOLD,  fontName="Helvetica-Bold", leading=20, alignment=TA_CENTER)
_cn    = _S("CN",  fontSize=18,  textColor=WHITE, fontName="Helvetica-Bold", leading=24, alignment=TA_CENTER)


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


def build_pdf(d, path):
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
            ("Full name",                             d.get("full_name")),
            ("City & Country",                        d.get("city_country")),
            ("Email address",                         d.get("client_email")),
            ("Preferred currency",                    d.get("currency")),
            ("Transition timeline preference",        d.get("timeline")),
        ]),
        ("Section 2 — Motivation & Context", [
            ("What is driving this transition?",                      d.get("motivation_type")),
            ("How long have you been thinking about this move?",      d.get("thinking_duration")),
            ("Concrete steps already taken",                          d.get("steps_taken")),
            ("What specifically attracts you to the target domain?",  d.get("attraction")),
        ]),
        ("Section 3 — Target Role Clarity", [
            ("How clear are you on the role you want?",               d.get("target_clarity")),
            ("Preferred organisation types",                          d.get("org_types")),
            ("Roles / sectors explicitly ruled out",                  d.get("ruled_out")),
            ("People or organisations you admire in the target field",d.get("admired")),
            ("Target domain / field",                                 d.get("target_domain")),
        ]),
        ("Section 4 — Constraints & Capacity", [
            ("Currently employed?",                                   d.get("employed")),
            ("If employed — transitioning while working or leaving?", d.get("employed_status")),
            ("Hours per week available for transition work",          d.get("hours_per_week")),
            ("Financial runway",                                      d.get("financial_runway")),
            ("Geographic constraints",                                d.get("geography")),
            ("Personal / family commitments affecting schedule",      d.get("personal_commitments")),
        ]),
        ("Section 5 — Financial Expectations", [
            ("Type of move targeted",                                 d.get("move_type")),
            ("Minimum income level to protect",                       d.get("income_floor")),
        ]),
        ("Section 6 — Learning Style & Pace", [
            ("Preferred learning format",                             d.get("learning_format")),
            ("Breadth-first or depth-first?",                         d.get("learning_preference")),
            ("Learning formats to avoid",                             d.get("learning_avoid")),
        ]),
        ("Section 7 — Network & Visibility", [
            ("Existing contacts in the target domain",                d.get("network_warmth")),
            ("Is the transition confidential?",                       d.get("transition_confidential")),
            ("Comfort with public visibility",                        d.get("visibility_comfort")),
            ("Mentor status",                                         d.get("mentor_status")),
        ]),
        ("Section 8 — Past Attempts & Blockers", [
            ("Previous attempts to make this move",                   d.get("past_attempts")),
            ("Biggest uncertainties or fears",                        d.get("biggest_fears")),
        ]),
        ("Section 9 — Deliverable Preferences", [
            ("Who will see this plan?",                               d.get("plan_audience")),
            ("Sections to emphasise",                                 d.get("emphasise")),
            ("Background notes / anything to handle with care",       d.get("background_notes")),
        ]),
    ]

    for title, pairs in sections:
        story.append(KeepTogether([_banner(title), Spacer(1, 8)]))
        for q, a in pairs:
            story += _qa(q, a)
        story += [Spacer(1, 6), HRFlowable(width=W, thickness=0.5, color=MGRY), Spacer(1, 6)]

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return path


def send_email(pdf_path, data, attachments, smtp_user, smtp_password):
    msg = MIMEMultipart()
    msg["From"]    = smtp_user
    msg["To"]      = RECIPIENT
    msg["Subject"] = (
        f"Career Transition Intake — {data.get('full_name', 'New Client')} — "
        f"{datetime.now().strftime('%d %b %Y')}"
    )
    n_docs = len(attachments)
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
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as srv:
        srv.ehlo()
        srv.starttls()
        srv.login(smtp_user, smtp_password)
        srv.sendmail(smtp_user, RECIPIENT, msg.as_string())


@app.route("/")
def index():
    return render_template("index.html",
                           smtp_user=os.environ.get("SMTP_USER", ""),
                           recipient=RECIPIENT)


@app.route("/submit", methods=["POST"])
def submit():
    full_name = request.form.get("full_name", "").strip()
    if not full_name:
        return "Please enter your full name.", 400

    data = dict(
        full_name=full_name,
        city_country=request.form.get("city_country"),
        client_email=request.form.get("client_email"),
        currency=request.form.get("currency"),
        timeline=request.form.get("timeline"),
        motivation_type=request.form.get("motivation_type"),
        thinking_duration=request.form.get("thinking_duration"),
        steps_taken=request.form.get("steps_taken"),
        attraction=request.form.get("attraction"),
        target_domain=request.form.get("target_domain"),
        target_clarity=request.form.get("target_clarity"),
        org_types=request.form.getlist("org_types"),
        ruled_out=request.form.get("ruled_out"),
        admired=request.form.get("admired"),
        employed=request.form.get("employed"),
        employed_status=request.form.get("employed_status"),
        hours_per_week=request.form.get("hours_per_week", "10") + " hrs/week",
        financial_runway=request.form.get("financial_runway"),
        geography=request.form.get("geography"),
        personal_commitments=request.form.get("personal_commitments"),
        move_type=request.form.get("move_type"),
        income_floor=request.form.get("income_floor"),
        learning_format=request.form.getlist("learning_format"),
        learning_preference=request.form.get("learning_preference"),
        learning_avoid=request.form.get("learning_avoid"),
        network_warmth=request.form.get("network_warmth"),
        transition_confidential=request.form.get("transition_confidential"),
        visibility_comfort=request.form.get("visibility_comfort"),
        mentor_status=request.form.get("mentor_status"),
        past_attempts=request.form.get("past_attempts"),
        biggest_fears=request.form.get("biggest_fears"),
        plan_audience=request.form.get("plan_audience"),
        emphasise=request.form.get("emphasise"),
        background_notes=request.form.get("background_notes"),
    )

    initials = "".join(w[0].upper() for w in full_name.split() if w)
    pdf_name = f"{initials}_intake_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    pdf_path = os.path.join(tempfile.gettempdir(), pdf_name)

    try:
        build_pdf(data, pdf_path)
    except Exception as exc:
        return f"PDF generation failed: {exc}", 500

    uploads = []
    for field in ["cv_file", "linkedin_file", "jd_file", "learning_plan_file", "headshot_file"]:
        f = request.files.get(field)
        if f and f.filename:
            suffix = Path(f.filename).suffix or ".bin"
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            f.save(tmp.name)
            uploads.append(tmp.name)

    email_status = "skipped"
    if request.form.get("send_email_flag") == "on":
        smtp_user = (request.form.get("smtp_user") or os.environ.get("SMTP_USER", "")).strip()
        smtp_pw   = (request.form.get("smtp_password") or os.environ.get("SMTP_PASSWORD", "")).strip()
        if smtp_user and smtp_pw:
            try:
                send_email(pdf_path, data, uploads, smtp_user, smtp_pw)
                email_status = "sent"
            except Exception:
                email_status = "failed"

    resp = send_file(pdf_path, as_attachment=True,
                     download_name=pdf_name, mimetype="application/pdf")
    resp.headers["X-Email-Status"] = email_status
    return resp


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
