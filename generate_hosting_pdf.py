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
        "h1":   ParagraphStyle("h1",   fontName="Helvetica-Bold",    fontSize=18,
                               textColor=NAVY,  leading=24, spaceAfter=6),
        "h3":   ParagraphStyle("h3",   fontName="Helvetica-Bold",    fontSize=10.5,
                               textColor=TEAL,  leading=14, spaceBefore=10, spaceAfter=3),
        "body": ParagraphStyle("body", fontName="Helvetica",          fontSize=9.5,
                               textColor=BLACK, leading=14, spaceAfter=5, alignment=TA_JUSTIFY),
        "step": ParagraphStyle("step", fontName="Helvetica",          fontSize=9.5,
                               textColor=BLACK, leading=14, spaceAfter=4, leftIndent=14),
        "code": ParagraphStyle("code", fontName="Courier",            fontSize=8.5,
                               textColor=BLACK, leading=13, spaceAfter=0,
                               leftIndent=8, rightIndent=8),
        "note": ParagraphStyle("note", fontName="Helvetica-Oblique",  fontSize=8.5,
                               textColor=colors.HexColor("#555555"), leading=12, spaceAfter=6),
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

    story.append(Paragraph("Hosting the Onboarding Form on Render", s["h1"]))
    story.append(rule(color=GOLD, thickness=1.5, before=2, after=10))
    story.append(Paragraph(
        "Render hosts the Gradio app as a Python web service on a permanent public URL. "
        "The free tier is sufficient for a low-traffic client intake form. "
        "Render watches the GitHub repo (<b>ericgitonga/career-transition-intake</b>) and "
        "redeploys automatically on every push to <b>main</b> — no CI/CD workflow required.",
        s["body"],
    ))
    story.append(Paragraph(
        "<b>After one-time setup, deploying means pushing to GitHub. That's it.</b>",
        ParagraphStyle("bold", fontName="Helvetica-Bold", fontSize=10,
                       textColor=TEAL, leading=14, spaceAfter=8),
    ))
    story.append(rule(color=MGRAY, thickness=0.5))

    # ── ONE-TIME SETUP ───────────────────────────────────────────────────────
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
        "Start Command <b>python app.py</b>",
        "Instance type: <b>Free</b>",
        "Click <b>Create Web Service</b>",
    ]:
        story.append(Paragraph(f"• {line}", s["step"]))

    story.append(Paragraph("4. Add SMTP environment variables", s["h3"]))
    story.append(Paragraph(
        "In the service dashboard, go to <b>Environment</b> and add:",
        s["body"],
    ))
    for name, desc in [
        ("SMTP_USER",     "Your Gmail address (e.g. yourname@gmail.com)"),
        ("SMTP_PASSWORD", "Your Gmail App Password — 16-character code from "
                          "https://myaccount.google.com/apppasswords"),
    ]:
        story.append(Paragraph(f"• <b>{name}</b> — {desc}", s["step"]))
    story.append(Paragraph(
        "<i>onboarding_form.py reads these from os.environ automatically. "
        "Never put credentials in the code or the repo.</i>",
        s["note"],
    ))
    story.append(Paragraph(
        "Click <b>Save Changes</b> — Render triggers a redeploy to apply the variables.",
        s["body"],
    ))

    story.append(rule(color=MGRAY, thickness=0.5))

    # ── DEPLOYING ─────────────────────────────────────────────────────────────
    story.append(KeepTogether([
        section_header("Deploying", s),
        Spacer(1, 0.25 * cm),
        Paragraph(
            "Push any change to GitHub — Render picks it up and redeploys within ~2 minutes:",
            s["body"],
        ),
        Spacer(1, 0.15 * cm),
    ]))
    story.append(code_block("git push origin main", s))

    story.append(rule(color=MGRAY, thickness=0.5))

    # ── AFTER DEPLOYMENT ──────────────────────────────────────────────────────
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
        "On the free tier, the service spins down after <b>15 minutes of inactivity</b>. "
        "The first request after a quiet period takes ~30 seconds to wake up. "
        "This is acceptable for a form shared on-demand — just warn clients that the "
        "first load after a quiet period may be briefly slow.",
        s["body"],
    ))

    story.append(Paragraph("Keeping it always on (optional)", s["h3"]))
    story.append(Paragraph(
        "Upgrade to the <b>Starter</b> plan ($7/month) to eliminate spin-down. "
        "Alternatively, use a free uptime monitor (e.g. UptimeRobot) to ping the URL "
        "every 10 minutes — this keeps the free instance warm at no cost.",
        s["body"],
    ))

    story.append(Paragraph("Updating SMTP credentials", s["h3"]))
    story.append(Paragraph(
        "Go to <b>Render dashboard → Environment</b>, update the value, and click "
        "<b>Save Changes</b>. Render redeploys automatically.",
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
