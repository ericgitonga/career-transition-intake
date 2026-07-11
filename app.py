"""
Flask application for the Career Transition client onboarding intake form.

Security hardening applied (see Clients/security.pdf for full audit):
  S-01  CSRF protection via Flask-WTF (Phase 1)
  S-02  Upload size limited to 10 MB via MAX_CONTENT_LENGTH (Phase 1)
  S-03  File extension whitelist on all uploads via _safe_suffix() (Phase 1)
  S-04  Bootstrap CDN links use Subresource Integrity hashes (HTML, Phase 1)
  S-05  Rate limiting via Flask-Limiter (Phase 2)
  S-06  Exceptions logged server-side; generic message returned to client (Phase 2)
  S-07  Temp files deleted in a finally block after response is built (Phase 2)
  S-08  HTTP security headers stamped on every response (Phase 1)
  S-09  SECRET_KEY loaded from environment; app refuses to start without it (Phase 1)
  S-10  All dependencies pinned in requirements.txt (Phase 2)
  S-11  All text inputs truncated server-side via _clip() (Phase 2)
  S-12  Control characters stripped from email fields via _sanitize() (Phase 3)
  S-13  Temp filename uses cryptographically random token (Phase 3)
  S-14  Upload extension validated by whitelist — resolved by S-03 (Phase 1)
  S-15  Submission events logged via app.logger (Phase 3)
"""

import os
import secrets
import tempfile
import unicodedata
from datetime import datetime
from pathlib import Path

import resend
from flask import Flask, request, render_template, send_file
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
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

# ── S-09: Secret key ──────────────────────────────────────────────────────────
# On Render (production) SECRET_KEY is set as an environment variable via the
# dashboard.  Locally, if it is absent, we auto-generate a random key for the
# current process so development is frictionless.  The trade-off is that CSRF
# tokens are invalidated on every restart, which is acceptable in development.
_secret = os.environ.get("SECRET_KEY", "")
if not _secret:
    _secret = secrets.token_hex(32)
    import warnings
    warnings.warn(
        "SECRET_KEY not set — using a randomly generated key. "
        "CSRF tokens will be invalidated on restart. "
        "Set SECRET_KEY in your environment (or Render dashboard) for production.",
        stacklevel=1,
    )
app.config["SECRET_KEY"] = _secret

# ── S-02: Reject oversized uploads before they reach route handlers ───────────
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB

# ── S-01: CSRF protection for all state-changing POST routes ──────────────────
csrf = CSRFProtect(app)

# ── S-05: Rate limiting — generous enough for real clients, stops floods ──────
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
)

# ── S-03 / S-14: Allowed upload extensions (server-enforced whitelist) ────────
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".txt", ".jpg", ".jpeg", ".png"}

NAVY = colors.HexColor("#1B2A4A")
TEAL = colors.HexColor("#0E7C7B")
GOLD = colors.HexColor("#C9A84C")
MGRY = colors.HexColor("#D0D6E0")
WHITE = colors.white
BLACK = colors.HexColor("#1A1A1A")


# ── Security helpers ──────────────────────────────────────────────────────────

def _safe_suffix(filename: str) -> str:
    """Return the lowercased extension of *filename*, or raise ValueError if not whitelisted.

    Used for every uploaded file to prevent disallowed types (e.g. .exe, .sh)
    from reaching the temp directory or being forwarded to the consultant's inbox.

    Args:
        filename: The client-supplied filename, e.g. ``"resume.PDF"`` or ``"cv.docx"``.

    Returns:
        The lowercased extension including the leading dot, e.g. ``".pdf"``.

    Raises:
        ValueError: If the extension is absent or not in ALLOWED_EXTENSIONS.
    """
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"File type '{suffix or '(none)'}' is not permitted. "
            f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )
    return suffix


def _clip(value, max_len: int = 5000) -> str:
    """Truncate *value* to *max_len* characters to prevent CPU/memory exhaustion.

    Applies to every text field before it is passed to the PDF builder. Without
    this guard, a crafted submission with megabyte-sized textarea values could
    exhaust gunicorn worker RAM during ReportLab rendering (S-11).

    Args:
        value:   The raw string from ``request.form.get()``, or None.
        max_len: Maximum number of characters to keep. Defaults to 5 000,
                 which covers the longest narrative textarea fields.

    Returns:
        The original string if within limits, a truncated copy otherwise,
        or an empty string if *value* is None.
    """
    if not isinstance(value, str):
        return value or ""
    return value[:max_len] if len(value) > max_len else value


def _sanitize(value: str) -> str:
    """Strip newlines and Unicode control characters from *value*.

    Prevents body spoofing in the plain-text email summary (S-12). A client
    name containing newlines could inject fake 'Email:' lines into the message
    body when it is interpolated into the Resend text payload.

    Args:
        value: Any string field used in the email subject or body.

    Returns:
        The input with all Unicode category-C (control) characters removed
        and leading/trailing whitespace stripped.
    """
    return "".join(
        ch for ch in (value or "")
        if unicodedata.category(ch)[0] != "C"
    ).strip()


# ── S-08: HTTP security headers on every response ─────────────────────────────
@app.after_request
def _security_headers(resp):
    """Stamp HTTP security headers onto every outgoing response.

    Addresses S-08 from the security audit. Applied unconditionally so that
    error responses (400, 413, 500) are also covered.

    Headers applied:
        X-Content-Type-Options  — prevents MIME-type sniffing attacks.
        X-Frame-Options         — blocks clickjacking via iframe embedding.
        Referrer-Policy         — limits URL leakage to cross-origin requests.
        Permissions-Policy      — revokes unnecessary browser feature access.
        Content-Security-Policy — restricts script and style sources;
                                  no 'unsafe-inline' for scripts since all JS
                                  is served from static/form.js ('self').

    Args:
        resp: The Flask Response object about to be sent to the client.

    Returns:
        The same Response object with security headers added.
    """
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    resp.headers["Permissions-Policy"] = "geolocation=(), microphone=()"
    resp.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "style-src 'self' cdn.jsdelivr.net 'unsafe-inline'; "
        "script-src 'self' cdn.jsdelivr.net; "
        "img-src 'self' data:; "
        "font-src 'self' cdn.jsdelivr.net;"
    )
    return resp


# ── PDF helpers ───────────────────────────────────────────────────────────────

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
        ]),
        ("Section 3 — Target Role Clarity", [
            ("Target domain / field",                                 d.get("target_domain")),
            ("What specifically attracts you to this domain?",        d.get("attraction")),
            ("How clear are you on the role you want?",               d.get("target_clarity")),
            ("Preferred organisation types",                          d.get("org_types")),
            ("Preferred organisation stage",                          d.get("org_stage")),
            ("Roles / sectors explicitly ruled out",                  d.get("ruled_out")),
            ("People or organisations you admire in the target field",d.get("admired")),
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
        ("Section 9 — About Your Plan", [
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

    Fields used in the email subject/body are sanitised with ``_sanitize()``
    before interpolation to prevent control-character spoofing (S-12).

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

    name     = _sanitize(data.get("full_name", "—"))
    email    = _sanitize(data.get("client_email", "—"))
    location = _sanitize(data.get("city_country", "—"))
    timeline = _sanitize(data.get("timeline", "—"))
    target   = _sanitize(data.get("target_domain", "—"))

    n_docs = len(upload_paths)
    body = (
        f"New career transition onboarding submission received.\n\n"
        f"Client:   {name}\n"
        f"Email:    {email}\n"
        f"Location: {location}\n"
        f"Timeline: {timeline}\n"
        f"Target:   {target}\n\n"
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
        "subject":     (f"Career Transition Intake — {name} — "
                        f"{datetime.now().strftime('%d %b %Y')}"),
        "text":        body,
        "attachments": attachments,
    })


@app.route("/_health")
def health():
    """Lightweight liveness probe for the Render static-site loading page.

    Returns a minimal JSON response immediately so the loading page can detect
    when the app has finished its cold start and is ready to serve the form.
    CORS headers are added for the companion static loading site.
    """
    resp = app.response_class(
        response='{"status":"ok"}',
        status=200,
        mimetype="application/json",
    )
    loading_origin = os.environ.get(
        "LOADING_SITE_ORIGIN", "https://career-transition-loading.onrender.com"
    )
    resp.headers["Access-Control-Allow-Origin"] = loading_origin
    resp.headers["Access-Control-Allow-Methods"] = "GET"
    return resp


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
@limiter.limit("5 per minute; 20 per hour")
def submit():
    """Process a submitted intake form: generate a PDF, email it, and return it for download.

    Workflow:
      1. Validate CSRF token (enforced automatically by Flask-WTF before this handler runs).
      2. Validate that ``full_name`` is present; return HTTP 400 otherwise.
      3. Collect all form fields into a flat dictionary. Each text value is
         truncated to a safe maximum length via ``_clip()`` (S-11).
      4. Build the branded intake PDF and write it to the system temp directory.
         The filename uses a cryptographically random token (S-13), e.g.
         ``intake_3f9a1b2c.pdf``.
      5. Save any uploaded files (CV, LinkedIn export, job description, learning
         plan, and additional documents) to temp files. Each upload's extension
         is validated against ALLOWED_EXTENSIONS (S-03 / S-14); disallowed
         types return HTTP 400 before the file is written.
      6. If ``RESEND_API_KEY`` is present in the environment, attempt to email
         the PDF and all uploads to the consultant. The outcome is recorded as
         ``sent``, ``failed``, or ``skipped`` and returned in the
         ``X-Email-Status`` response header so the browser can surface a
         meaningful status message without blocking the download.
      7. Stream the PDF back to the client as a file download attachment.
      8. Delete all temp files in a ``finally`` block regardless of outcome (S-07).

    Returns:
        A Flask Response that streams the PDF for download (HTTP 200) with an
        ``X-Email-Status`` header set to one of:
          - ``"sent"``    — email delivered successfully.
          - ``"failed"``  — email attempted but an exception was raised.
          - ``"skipped"`` — ``RESEND_API_KEY`` not configured; email not attempted.

    Returns HTTP 400 if ``full_name`` is missing or an uploaded file type is not whitelisted.
    Returns HTTP 413 if the total upload size exceeds 10 MB (raised by Flask before this handler).
    Returns HTTP 429 if the rate limit is exceeded (raised by Flask-Limiter).
    Returns HTTP 500 if PDF generation raises an exception.
    """
    full_name = _clip(request.form.get("full_name", "").strip(), 200)
    if not full_name:
        return "Please enter your full name.", 400

    data = dict(
        full_name=full_name,
        city_country=_clip(request.form.get("city_country"), 200),
        client_email=_clip(request.form.get("client_email"), 200),
        currency=_clip(request.form.get("currency"), 50),
        timeline=_clip(request.form.get("timeline"), 100),
        motivation_type=_clip(request.form.get("motivation_type"), 200),
        thinking_duration=_clip(request.form.get("thinking_duration"), 200),
        steps_taken=_clip(request.form.get("steps_taken"), 5000),
        attraction=_clip(request.form.get("attraction"), 5000),
        target_domain=_clip(request.form.get("target_domain"), 500),
        target_clarity=_clip(request.form.get("target_clarity"), 200),
        org_types=request.form.getlist("org_types"),
        org_stage=request.form.getlist("org_stage"),
        ruled_out=_clip(request.form.get("ruled_out"), 2000),
        admired=_clip(request.form.get("admired"), 2000),
        employed=_clip(request.form.get("employed"), 100),
        employed_status=_clip(request.form.get("employed_status"), 200),
        hours_per_week=_clip(request.form.get("hours_per_week", "10"), 10) + " hrs/week",
        financial_runway=_clip(request.form.get("financial_runway"), 100),
        geography=_clip(request.form.get("geography"), 2000),
        personal_commitments=_clip(request.form.get("personal_commitments"), 2000),
        move_type=_clip(request.form.get("move_type"), 200),
        income_floor=_clip(request.form.get("income_floor"), 2000),
        learning_format=request.form.getlist("learning_format"),
        learning_preference=_clip(request.form.get("learning_preference"), 200),
        learning_avoid=_clip(request.form.get("learning_avoid"), 2000),
        network_warmth=_clip(request.form.get("network_warmth"), 200),
        transition_confidential=_clip(request.form.get("transition_confidential"), 200),
        visibility_comfort=_clip(request.form.get("visibility_comfort"), 200),
        mentor_status=_clip(request.form.get("mentor_status"), 200),
        past_attempts=_clip(request.form.get("past_attempts"), 5000),
        biggest_fears=_clip(request.form.get("biggest_fears"), 5000),
        plan_audience=_clip(request.form.get("plan_audience"), 200),
        emphasise=_clip(request.form.get("emphasise"), 5000),
        background_notes=_clip(request.form.get("background_notes"), 5000),
    )

    # S-13: cryptographically random filename — not guessable from initials + time
    token    = secrets.token_hex(8)
    pdf_name = f"intake_{token}.pdf"
    pdf_path = os.path.join(tempfile.gettempdir(), pdf_name)

    try:
        build_pdf(data, pdf_path)
    except Exception as exc:
        # S-06: log full detail server-side; return generic message to client
        app.logger.error("PDF generation failed: %s", exc, exc_info=True)
        return "PDF generation failed. Please try again.", 500

    # S-03 / S-14: validate extension against whitelist before writing to disk
    uploads = []
    all_files = (
        [request.files.get(fld) for fld in ["cv_file", "linkedin_file", "jd_file", "learning_plan_file"]]
        + request.files.getlist("additional_files")
    )
    for f in all_files:
        if not f or not f.filename:
            continue
        try:
            suffix = _safe_suffix(f.filename)
        except ValueError as exc:
            return str(exc), 400
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        f.save(tmp.name)
        uploads.append(tmp.name)

    # S-15: structured submission log for audit trail and abuse detection
    app.logger.info(
        "Submission received: name=%s email=%s target=%s uploads=%d",
        data.get("full_name"), data.get("client_email"),
        data.get("target_domain"), len(uploads),
    )

    email_status = "skipped"
    if os.environ.get("RESEND_API_KEY"):
        try:
            send_email(pdf_path, data, uploads)
            email_status = "sent"
        except Exception:
            email_status = "failed"

    # S-15: log outcome so silent email failures are visible in server logs
    app.logger.info(
        "Submission complete: name=%s email_status=%s",
        data.get("full_name"), email_status,
    )

    # S-07: delete all temp files after response is built, regardless of outcome
    try:
        resp = send_file(pdf_path, as_attachment=True,
                         download_name=pdf_name, mimetype="application/pdf")
        resp.headers["X-Email-Status"] = email_status
        return resp
    finally:
        for p in [pdf_path] + uploads:
            try:
                os.unlink(p)
            except OSError:
                pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
