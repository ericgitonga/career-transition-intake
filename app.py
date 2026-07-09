import os
import tempfile
from datetime import datetime
from pathlib import Path

import resend

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
    """Shorthand constructor for a ReportLab ParagraphStyle.

    Args:
        name: Internal style name used by ReportLab (must be unique per document).
        **kw: Any keyword arguments accepted by ParagraphStyle (fontSize, textColor,
              fontName, leading, alignment, leftIndent, etc.).

    Returns:
        A configured ParagraphStyle instance.
    """
    return ParagraphStyle(name, **kw)

_h1    = _S("H1",  fontSize=16, textColor=WHITE, fontName="Helvetica-Bold", leading=20)
_label = _S("Lbl", fontSize=9.5, textColor=NAVY,  fontName="Helvetica-Bold", leading=14)
_ans   = _S("Ans", fontSize=9.5, textColor=BLACK, fontName="Helvetica",     leading=13, leftIndent=12)
_meta  = _S("Met", fontSize=8,   textColor=MGRY,  fontName="Helvetica",     leading=12, alignment=TA_CENTER)
_ct    = _S("CT",  fontSize=22,  textColor=WHITE, fontName="Helvetica-Bold", leading=28, alignment=TA_CENTER)
_cs    = _S("CS",  fontSize=14,  textColor=GOLD,  fontName="Helvetica-Bold", leading=20, alignment=TA_CENTER)
_cn    = _S("CN",  fontSize=18,  textColor=WHITE, fontName="Helvetica-Bold", leading=24, alignment=TA_CENTER)


def _banner(text):
    """Create a navy-background section-header banner for the PDF.

    Used to visually separate each of the nine intake sections in the
    generated document. The banner spans the full content width (17 cm)
    and renders the text in bold white using the _h1 paragraph style.

    Args:
        text: The section title to display (e.g. "Section 1 — Personal Information").

    Returns:
        A ReportLab Table flowable styled as a full-width navy banner.
    """
    t = Table([[Paragraph(text, _h1)]], colWidths=[17 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), NAVY),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
    ]))
    return t


def _qa(question, value):
    """Render a question/answer pair as a list of PDF flowables.

    Formats multi-select answers (lists) as a comma-separated string.
    Blank or None answers are replaced with an em-dash so the PDF never
    shows an empty field.

    Args:
        question: The field label to display in bold navy (e.g. "Full name").
        value:    The client's answer — either a plain string/None, or a list
                  of strings for checkbox fields.

    Returns:
        A list of three flowables: the question Paragraph, the answer
        Paragraph (indented), and a small vertical Spacer.
    """
    text = ", ".join(value) if isinstance(value, list) else str(value or "—").strip() or "—"
    return [Paragraph(question, _label), Paragraph(text, _ans), Spacer(1, 4)]


def build_pdf(d, path):
    """Generate the branded intake PDF from the submitted form data.

    Builds a multi-page A4 document using ReportLab's Platypus layout engine.
    The document contains:
      - A navy cover block with the client's name and submission date.
      - Nine labelled sections (Personal Information through Deliverable
        Preferences), each opened by a navy banner and closed by a divider rule.
      - A footer on every page showing the client's name and page number.

    The function defines a nested ``footer`` callback that ReportLab calls on
    each page via ``onFirstPage`` / ``onLaterPages``.

    Args:
        d:    Dictionary of form field values keyed by field name (as returned
              by the ``submit`` route). Multi-select fields are lists; all
              other fields are strings or None.
        path: Absolute filesystem path where the PDF should be written.

    Returns:
        The same ``path`` string passed in, for chaining convenience.

    Raises:
        Any ReportLab exception if layout or rendering fails (propagated to
        the caller without wrapping).
    """
    doc = SimpleDocTemplate(
        path, pagesize=A4,
        leftMargin=1.27*cm, rightMargin=1.27*cm,
        topMargin=1.5*cm,   bottomMargin=1.5*cm,
    )

    def footer(canvas, doc):
        """Draw the page footer on each page of the PDF.

        Called by ReportLab's build pipeline for every page. Renders a centred
        grey caption at the bottom of the page containing the service name,
        the client's full name, and the current page number.

        Args:
            canvas: The ReportLab canvas for the current page.
            doc:    The SimpleDocTemplate being built (provides ``doc.page``).
        """
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


def send_email(pdf_path, data, upload_paths):
    """Send the intake PDF and any uploaded documents to the consultant via Resend.

    Uses the Resend HTTP API (not SMTP) so the call succeeds on hosting
    providers that block outbound port 587. The API key is read from the
    ``RESEND_API_KEY`` environment variable at call time. The sender address
    defaults to ``onboarding@resend.dev`` (Resend's shared domain, no DNS
    setup required) and can be overridden by setting a ``FROM_EMAIL``
    environment variable to a verified custom-domain address.

    Each file — the generated PDF plus every uploaded document — is read into
    memory and passed to Resend as a list of byte integers, which is the format
    the Resend Python SDK expects for attachments.

    Args:
        pdf_path:     Absolute path to the generated intake PDF.
        data:         Dictionary of form field values (used to populate the
                      plain-text email body and subject line).
        upload_paths: List of absolute paths to client-uploaded documents.
                      May be empty if the client did not attach any files.

    Raises:
        KeyError:  If ``RESEND_API_KEY`` is not set in the environment.
        Exception: Any network or API error raised by the Resend SDK
                   (propagated to the caller, which sets email_status="failed").
    """
    resend.api_key = os.environ["RESEND_API_KEY"]
    n_docs = len(upload_paths)
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
    attachments = []
    for fpath in [pdf_path] + upload_paths:
        if not fpath or not os.path.exists(str(fpath)):
            continue
        with open(fpath, "rb") as f:
            attachments.append({"filename": Path(fpath).name, "content": list(f.read())})
    resend.Emails.send({
        "from":        os.environ.get("FROM_EMAIL", "onboarding@resend.dev"),
        "to":          [RECIPIENT],
        "subject":     (f"Career Transition Intake — {data.get('full_name', 'New Client')} — "
                        f"{datetime.now().strftime('%d %b %Y')}"),
        "text":        body,
        "attachments": attachments,
    })


@app.route("/")
def index():
    """Serve the onboarding intake form.

    Renders ``templates/index.html`` with the consultant's recipient address
    injected so the template can display it in the UI.

    Returns:
        A Flask Response containing the rendered HTML form (HTTP 200).
    """
    return render_template("index.html", recipient=RECIPIENT)


@app.route("/submit", methods=["POST"])
def submit():
    """Process a submitted intake form: generate a PDF, email it, and return it for download.

    Workflow:
      1. Validate that ``full_name`` is present; return HTTP 400 otherwise.
      2. Collect all form fields into a flat dictionary.
      3. Build the branded intake PDF and write it to the system temp directory.
         The filename uses the client's initials and a timestamp
         (e.g. ``JWM_intake_20260710_1430.pdf``).
      4. Save any uploaded files (CV, LinkedIn export, job description, learning
         plan, and additional documents) to temp files.
      5. If ``RESEND_API_KEY`` is present in the environment, attempt to email
         the PDF and all uploads to the consultant. The outcome is recorded as
         ``sent``, ``failed``, or ``skipped`` and returned in the
         ``X-Email-Status`` response header so the browser can surface a
         meaningful status message without blocking the download.
      6. Stream the PDF back to the client as a file download attachment.

    Returns:
        A Flask Response that streams the PDF for download (HTTP 200) with an
        ``X-Email-Status`` header set to one of:
          - ``"sent"``    — email delivered successfully.
          - ``"failed"``  — email attempted but an exception was raised.
          - ``"skipped"`` — ``RESEND_API_KEY`` not configured; email not attempted.

    Returns HTTP 400 if ``full_name`` is missing.
    Returns HTTP 500 if PDF generation raises an exception.
    """
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
    for field in ["cv_file", "linkedin_file", "jd_file", "learning_plan_file"]:
        f = request.files.get(field)
        if f and f.filename:
            suffix = Path(f.filename).suffix or ".bin"
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            f.save(tmp.name)
            uploads.append(tmp.name)
    for f in request.files.getlist("additional_files"):
        if f and f.filename:
            suffix = Path(f.filename).suffix or ".bin"
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            f.save(tmp.name)
            uploads.append(tmp.name)

    email_status = "skipped"
    if os.environ.get("RESEND_API_KEY"):
        try:
            send_email(pdf_path, data, uploads)
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
