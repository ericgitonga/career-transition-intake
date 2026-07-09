import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Preformatted,
    HRFlowable, KeepTogether,
)

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "hosting.pdf")

NAVY    = colors.HexColor("#1B2A4A")
TEAL    = colors.HexColor("#0E7C7B")
GOLD    = colors.HexColor("#C9A84C")
MGRAY   = colors.HexColor("#D0D6E0")
BLACK   = colors.HexColor("#1A1A1A")
CODE_BG = colors.HexColor("#EAEEF4")

W, H = A4
MARGIN  = 1.5 * cm
INNER_W = W - 2 * MARGIN


def styles():
    return {
        "h1":   ParagraphStyle("h1",   fontName="Helvetica-Bold",   fontSize=18,
                               textColor=NAVY,  leading=24, spaceAfter=6),
        "h3":   ParagraphStyle("h3",   fontName="Helvetica-Bold",   fontSize=10.5,
                               textColor=TEAL,  leading=14, spaceBefore=10, spaceAfter=3),
        "body": ParagraphStyle("body", fontName="Helvetica",         fontSize=9.5,
                               textColor=BLACK, leading=14, spaceAfter=5, alignment=TA_JUSTIFY),
        "step": ParagraphStyle("step", fontName="Helvetica",         fontSize=9.5,
                               textColor=BLACK, leading=14, spaceAfter=4, leftIndent=14),
        "code": ParagraphStyle("code", fontName="Courier",           fontSize=8.5,
                               textColor=BLACK, leading=13, spaceAfter=0,
                               leftIndent=8, rightIndent=8),
        "note": ParagraphStyle("note", fontName="Helvetica-Oblique", fontSize=8.5,
                               textColor=colors.HexColor("#555555"), leading=12, spaceAfter=6),
        "bold": ParagraphStyle("bold", fontName="Helvetica-Bold",    fontSize=10,
                               textColor=TEAL,  leading=14, spaceAfter=8),
    }


def rule(color=GOLD, thickness=1, before=6, after=8):
    return HRFlowable(width="100%", thickness=thickness, color=color,
                      spaceBefore=before, spaceAfter=after)


def code_block(text, s):
    from reportlab.platypus import Table, TableStyle
    t = Table([[Preformatted(text.strip(), s["code"])]], colWidths=[INNER_W])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), CODE_BG),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("BOX",           (0, 0), (-1, -1), 0.5, MGRAY),
    ]))
    return t


def section_header(text, s):
    from reportlab.platypus import Table, TableStyle
    p = Paragraph(text, ParagraphStyle("sh", fontName="Helvetica-Bold", fontSize=11,
                                        textColor=colors.white, leading=14))
    t = Table([[p]], colWidths=[INNER_W])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), NAVY),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))
    return t


def build_story(s):
    story = []

    story.append(Paragraph("Hosting the Career Transition Intake Form on Render", s["h1"]))
    story.append(rule(color=GOLD, thickness=1.5, before=2, after=10))
    story.append(Paragraph(
        "The intake form is a Flask web application hosted on Render as a Python web service. "
        "It collects structured client responses across 10 sections, generates PDF, "
        "and emails it automatically to the consultant via Resend — no SMTP configuration "
        "or credentials are shown to clients. "
        "Render watches the GitHub repo (<b>ericgitonga/career-transition-intake</b>) and "
        "redeploys automatically on every push to <b>main</b>.",
        s["body"],
    ))
    story.append(Paragraph(
        "<b>After one-time setup, deploying a change means pushing to GitHub. That's it.</b>",
        s["bold"],
    ))
    story.append(rule(color=MGRAY, thickness=0.5))

    # ── ONE-TIME SETUP ────────────────────────────────────────────────────────
    story.append(KeepTogether([
        section_header("One-Time Setup", s),
        Spacer(1, 0.25 * cm),
        Paragraph("These steps are required once before the first deployment.", s["note"]),
    ]))

    story.append(Paragraph("1. Create a Render account", s["h3"]))
    story.append(Paragraph(
        "Go to <b>https://render.com</b> and sign up — the free tier requires no credit card.",
        s["body"],
    ))

    story.append(Paragraph("2. Connect your GitHub account", s["h3"]))
    story.append(Paragraph(
        "In the Render dashboard, click your avatar → <b>Account Settings → Git Provider → "
        "Connect GitHub</b>. Authorise Render to access the "
        "<b>ericgitonga/career-transition-intake</b> repo.",
        s["body"],
    ))

    story.append(Paragraph("3. Create a new Web Service", s["h3"]))
    for line in [
        "Click <b>New → Web Service</b>",
        "Select the <b>career-transition-intake</b> repository",
        "Render detects <b>render.yaml</b> automatically and fills in the settings",
        "Confirm: Runtime <b>Python</b>, Build Command <b>pip install -r requirements.txt</b>, "
        "Start Command <b>gunicorn app:app --bind 0.0.0.0:$PORT</b>",
        "Instance type: <b>Free</b>",
        "Click <b>Create Web Service</b>",
    ]:
        story.append(Paragraph(f"• {line}", s["step"]))

    story.append(Paragraph("4. Sign up for Resend (email delivery)", s["h3"]))
    story.append(Paragraph(
        "Resend is a transactional email service that sends over HTTPS — it is never blocked "
        "by hosting providers the way SMTP is. The free tier allows 3,000 emails per month.",
        s["body"],
    ))
    for line in [
        "Go to <b>https://resend.com</b> and sign up using the consultant's email address "
        "(e.g. example@gmail.com) — this becomes the verified recipient address",
        "In the Resend dashboard, go to <b>API Keys → Create API Key</b>",
        "Give it a name (e.g. <i>career-transition-form</i>) and copy the key — it is shown only once",
    ]:
        story.append(Paragraph(f"• {line}", s["step"]))

    story.append(Paragraph("5. Add the Resend API key to Render", s["h3"]))
    story.append(Paragraph(
        "In the Render service dashboard, go to <b>Environment</b> and add one variable:",
        s["body"],
    ))
    story.append(Paragraph(
        "• <b>RESEND_API_KEY</b> — the API key copied from step 4",
        s["step"],
    ))
    story.append(Paragraph(
        "<i>The app reads this from the environment automatically. "
        "Never put the key in the code or the repository.</i>",
        s["note"],
    ))
    story.append(Paragraph(
        "Click <b>Save Changes</b> — Render triggers a redeploy to apply the variable.",
        s["body"],
    ))

    story.append(rule(color=MGRAY, thickness=0.5))

    # ── HOW IT WORKS ─────────────────────────────────────────────────────────
    story.append(KeepTogether([
        section_header("How It Works", s),
        Spacer(1, 0.25 * cm),
    ]))

    story.append(Paragraph("Client experience", s["h3"]))
    story.append(Paragraph(
        "Clients open the URL, complete the 10-section dark-themed accordion form, "
        "optionally upload documents (CV, LinkedIn export, job description, learning plan, "
        "and additional files), then click <b>Submit Onboarding Form</b>. "
        "The server generates a PDF, emails it to the consultant automatically, "
        "and triggers a download in the client's browser. "
        "No credentials, no email settings, and no configuration are shown to clients.",
        s["body"],
    ))

    story.append(Paragraph("Email sender address", s["h3"]))
    story.append(Paragraph(
        "By default the form sends from <b>onboarding@resend.dev</b> (Resend's shared address). "
        "To send from a custom domain (e.g. <i>noreply@yourdomain.com</i>), verify the domain "
        "in the Resend dashboard and set a <b>FROM_EMAIL</b> environment variable in Render "
        "with the desired address.",
        s["body"],
    ))

    story.append(rule(color=MGRAY, thickness=0.5))

    # ── DEPLOYING ────────────────────────────────────────────────────────────
    story.append(KeepTogether([
        section_header("Deploying Updates", s),
        Spacer(1, 0.25 * cm),
        Paragraph(
            "Push any change to the main branch — Render picks it up and redeploys "
            "within ~2 minutes:",
            s["body"],
        ),
        Spacer(1, 0.15 * cm),
    ]))
    story.append(code_block("git push origin main", s))

    story.append(rule(color=MGRAY, thickness=0.5))

    # ── AFTER DEPLOYMENT ─────────────────────────────────────────────────────
    story.append(KeepTogether([
        section_header("After Deployment", s),
        Spacer(1, 0.25 * cm),
    ]))

    story.append(Paragraph("Your URL", s["h3"]))
    story.append(Paragraph(
        "Render assigns a permanent URL shown at the top of the service dashboard:",
        s["body"],
    ))
    story.append(code_block("https://career-transition-intake.onrender.com", s))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(
        "This URL does not change between deploys.",
        s["note"],
    ))

    story.append(Paragraph("Free tier spin-down", s["h3"]))
    story.append(Paragraph(
        "On the free tier the service spins down after <b>15 minutes of inactivity</b>. "
        "The first request after a quiet period takes ~30 seconds to wake up. "
        "For a form shared on-demand this is acceptable — just warn clients that the "
        "first load may be briefly slow. To eliminate spin-down, upgrade to the "
        "<b>Starter</b> plan ($7/month) or use a free uptime monitor such as "
        "UptimeRobot to ping the URL every 10 minutes.",
        s["body"],
    ))

    story.append(Paragraph("Rotating the Resend API key", s["h3"]))
    story.append(Paragraph(
        "Go to the Resend dashboard, revoke the old key and create a new one. "
        "Then go to <b>Render → Environment</b>, update <b>RESEND_API_KEY</b>, "
        "and click <b>Save Changes</b>. Render redeploys automatically.",
        s["body"],
    ))

    return story


def make_doc():
    s = styles()
    doc = SimpleDocTemplate(
        OUTPUT_PATH, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=1.5 * cm, bottomMargin=1.8 * cm,
    )

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#888888"))
        canvas.drawCentredString(W / 2, 0.7 * cm,
                                 f"Career Transition Planning Service  ·  Page {doc.page}")
        canvas.restoreState()

    doc.build(build_story(s), onFirstPage=footer, onLaterPages=footer)
    print(f"PDF written to: {OUTPUT_PATH}")


if __name__ == "__main__":
    make_doc()
