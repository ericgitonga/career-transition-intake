import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Preformatted,
    HRFlowable, KeepTogether,
)

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "hosting.pdf")

NAVY  = colors.HexColor("#1B2A4A")
TEAL  = colors.HexColor("#0E7C7B")
GOLD  = colors.HexColor("#C9A84C")
LGRAY = colors.HexColor("#F4F6F9")
MGRAY = colors.HexColor("#D0D6E0")
BLACK = colors.HexColor("#1A1A1A")
CODE_BG = colors.HexColor("#EAEEF4")

W, H = A4
MARGIN = 1.5 * cm
INNER_W = W - 2 * MARGIN


def styles():
    return {
        "h1": ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=18,
                             textColor=NAVY, leading=24, spaceAfter=6),
        "intro": ParagraphStyle("intro", fontName="Helvetica-Oblique", fontSize=10,
                                textColor=colors.HexColor("#444444"), leading=15,
                                spaceAfter=10, alignment=TA_JUSTIFY),
        "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=13,
                             textColor=NAVY, leading=17, spaceBefore=14, spaceAfter=4),
        "h3": ParagraphStyle("h3", fontName="Helvetica-Bold", fontSize=10.5,
                             textColor=TEAL, leading=14, spaceBefore=10, spaceAfter=3),
        "body": ParagraphStyle("body", fontName="Helvetica", fontSize=9.5,
                               textColor=BLACK, leading=14, spaceAfter=5,
                               alignment=TA_JUSTIFY),
        "step": ParagraphStyle("step", fontName="Helvetica", fontSize=9.5,
                               textColor=BLACK, leading=14, spaceAfter=4,
                               leftIndent=14),
        "code": ParagraphStyle("code", fontName="Courier", fontSize=8.5,
                               textColor=BLACK, leading=13, spaceAfter=0,
                               leftIndent=8, rightIndent=8),
        "note": ParagraphStyle("note", fontName="Helvetica-Oblique", fontSize=8.5,
                               textColor=colors.HexColor("#555555"), leading=12,
                               spaceAfter=6),
    }


def rule(color=GOLD, thickness=1, before=6, after=8):
    return HRFlowable(width="100%", thickness=thickness, color=color,
                      spaceBefore=before, spaceAfter=after)


def code_block(text, s):
    from reportlab.platypus import Table, TableStyle
    inner = Preformatted(text.strip(), s["code"])
    t = Table([[inner]], colWidths=[INNER_W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CODE_BG),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("BOX", (0, 0), (-1, -1), 0.5, MGRAY),
    ]))
    return t


def section_header(text, s):
    from reportlab.platypus import Table, TableStyle
    p = Paragraph(text, ParagraphStyle("sh", fontName="Helvetica-Bold", fontSize=11,
                                        textColor=colors.white, leading=14))
    t = Table([[p]], colWidths=[INNER_W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    return t


def build_story(s):
    story = []

    # Title
    story.append(Paragraph("Hosting the Onboarding Form on Hugging Face Spaces", s["h1"]))
    story.append(rule(color=GOLD, thickness=1.5, before=2, after=10))

    story.append(Paragraph(
        "Hugging Face Spaces runs Gradio apps for free on a persistent public URL — no 72-hour expiry. "
        "The GitHub repo (<b>ericgitonga/career-transition-intake</b>) is already set up with a CI/CD "
        "workflow that syncs to HF Spaces automatically on every push to <b>main</b>. All required "
        "files — <b>app.py</b>, <b>requirements.txt</b>, and <b>README.md</b> with the HF Space card "
        "frontmatter — are already in the repo.",
        s["body"],
    ))
    story.append(Paragraph(
        "<b>Deploying means pushing to GitHub. That's it.</b>",
        ParagraphStyle("bold_center", fontName="Helvetica-Bold", fontSize=10,
                       textColor=TEAL, leading=14, spaceAfter=8),
    ))

    story.append(rule(color=MGRAY, thickness=0.5))

    # ── ONE-TIME SETUP ───────────────────────────────────────────────────────
    story.append(KeepTogether([
        section_header("One-Time Setup", s),
        Spacer(1, 0.25 * cm),
        Paragraph(
            "These steps are required once before the first deployment.",
            s["note"],
        ),
    ]))

    # Step 1
    story.append(Paragraph("1. Create a Hugging Face account", s["h3"]))
    story.append(Paragraph(
        "Go to <b>https://huggingface.co</b> and sign up. The free tier is sufficient.",
        s["body"],
    ))

    # Step 2
    story.append(Paragraph("2. Create a new Space", s["h3"]))
    for line in [
        "Click your profile avatar → <b>New Space</b>",
        "Space name: <b>career-transition-intake</b> (must match exactly)",
        "License: MIT (or leave blank)",
        "SDK: <b>Gradio</b>",
        "Hardware: <b>CPU Basic</b> (free)",
        "Click <b>Create Space</b> — this creates the HF repo at:<br/>"
        "<i>https://huggingface.co/spaces/&lt;your-hf-username&gt;/career-transition-intake</i>",
    ]:
        story.append(Paragraph(f"• {line}", s["step"]))

    # Step 3
    story.append(Paragraph("3. Create a Hugging Face token", s["h3"]))
    for line in [
        "Go to <b>https://huggingface.co/settings/tokens</b>",
        "Click <b>New token</b> → name it e.g. <i>github-deploy</i> → Role: <b>Write</b>",
        "Copy the token — you will not see it again",
    ]:
        story.append(Paragraph(f"• {line}", s["step"]))

    # Step 4
    story.append(Paragraph("4. Add secrets to the GitHub repo", s["h3"]))
    story.append(Paragraph(
        "The deploy workflow reads two secrets. Open "
        "<b>github.com/ericgitonga/career-transition-intake → Settings → Secrets → Actions</b> "
        "and add:",
        s["body"],
    ))
    for line in [
        "<b>HF_TOKEN</b> → the Hugging Face token you just created",
        "<b>HF_USERNAME</b> → your Hugging Face username",
    ]:
        story.append(Paragraph(f"• {line}", s["step"]))

    # Step 5
    story.append(Paragraph("5. Add SMTP credentials to the HF Space", s["h3"]))
    story.append(Paragraph(
        "The form sends emails via Gmail. Credentials must be stored as HF Secrets — never "
        "in code. Open your Space → <b>Settings</b> tab → <b>Repository secrets</b> and add:",
        s["body"],
    ))
    for line in [
        "<b>SMTP_USER</b> → your Gmail address (e.g. <i>yourname@gmail.com</i>)",
        "<b>SMTP_PASSWORD</b> → your Gmail App Password (16-character code from "
        "https://myaccount.google.com/apppasswords)",
    ]:
        story.append(Paragraph(f"• {line}", s["step"]))
    story.append(Paragraph(
        "<i>onboarding_form.py already reads these from os.environ — no code change needed.</i>",
        s["note"],
    ))

    story.append(rule(color=MGRAY, thickness=0.5))

    # ── DEPLOYING ─────────────────────────────────────────────────────────────
    story.append(KeepTogether([
        section_header("Deploying", s),
        Spacer(1, 0.25 * cm),
        Paragraph(
            "Once the one-time setup is complete, deployment is fully automated. "
            "Push any changes to the GitHub repo:",
            s["body"],
        ),
        Spacer(1, 0.15 * cm),
    ]))
    story.append(code_block("git push origin main", s))
    story.append(Spacer(1, 0.25 * cm))
    story.append(Paragraph(
        "The GitHub Actions workflow (<b>.github/workflows/deploy.yml</b>) clones the HF Space repo, "
        "syncs all files from GitHub, and pushes. The Space rebuilds automatically — roughly 2 minutes.",
        s["body"],
    ))

    story.append(rule(color=MGRAY, thickness=0.5))

    # ── AFTER DEPLOYMENT ──────────────────────────────────────────────────────
    story.append(KeepTogether([
        section_header("After Deployment", s),
        Spacer(1, 0.25 * cm),
    ]))

    story.append(Paragraph(
        "Your permanent public URL will be:",
        s["body"],
    ))
    story.append(code_block(
        "https://<your-hf-username>-career-transition-intake.hf.space", s
    ))
    story.append(Spacer(1, 0.2 * cm))

    for line in [
        "Every push to <b>main</b> on GitHub triggers a redeploy automatically.",
        "The free tier sleeps after ~48 hours of inactivity. The Space wakes on the next visit "
        "(~30 seconds). Warn clients that the first load after a quiet period may be slow.",
    ]:
        story.append(Paragraph(f"• {line}", s["step"]))

    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("<b>To prevent sleep (optional)</b>", s["h3"]))
    story.append(Paragraph(
        "Upgrade the Space hardware to <b>CPU Upgrade</b> ($0.03/hr) — paid Spaces never sleep. "
        "Or keep the free tier and note that the first load after inactivity takes ~30 seconds.",
        s["body"],
    ))

    return story


def make_doc():
    s = styles()
    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=A4,
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

    story = build_story(s)
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"PDF written to: {OUTPUT_PATH}")


if __name__ == "__main__":
    make_doc()
