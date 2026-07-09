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
    story.append(Paragraph("Hosting the Onboarding Form on Google Cloud Run", s["h1"]))
    story.append(rule(color=GOLD, thickness=1.5, before=2, after=10))

    story.append(Paragraph(
        "Google Cloud Run hosts the Gradio app as a Docker container on a permanent public URL. "
        "The free tier covers 2 million requests and 360,000 GB-seconds of compute per month — "
        "more than sufficient for a low-traffic client intake form. "
        "The GitHub repo (<b>ericgitonga/career-transition-intake</b>) is set up with a CI/CD "
        "workflow that builds and deploys automatically on every push to <b>main</b>.",
        s["body"],
    ))
    story.append(Paragraph(
        "<b>Deploying means pushing to GitHub. That's it.</b>",
        ParagraphStyle("bold_center", fontName="Helvetica-Bold", fontSize=10,
                       textColor=TEAL, leading=14, spaceAfter=8),
    ))

    story.append(rule(color=MGRAY, thickness=0.5))

    # ── ONE-TIME GCP SETUP ───────────────────────────────────────────────────
    story.append(KeepTogether([
        section_header("One-Time GCP Setup", s),
        Spacer(1, 0.25 * cm),
        Paragraph("These steps are required once before the first deployment.", s["note"]),
    ]))

    story.append(Paragraph("1. Create or select a Google Cloud project", s["h3"]))
    story.append(Paragraph(
        "Go to <b>https://console.cloud.google.com</b>. Create a new project or select an "
        "existing one. Note the <b>Project ID</b> (not the project name).",
        s["body"],
    ))

    story.append(Paragraph("2. Enable required APIs", s["h3"]))
    story.append(Paragraph(
        "In the Google Cloud Console, go to <b>APIs &amp; Services → Library</b> and enable:",
        s["body"],
    ))
    for api in [
        "Cloud Run API",
        "Container Registry API",
        "Cloud Build API",
    ]:
        story.append(Paragraph(f"• {api}", s["step"]))

    story.append(Paragraph("3. Create a service account", s["h3"]))
    story.append(Paragraph(
        "Go to <b>IAM &amp; Admin → Service Accounts → Create Service Account</b>. "
        "Name it e.g. <i>github-deployer</i>. Grant it these roles:",
        s["body"],
    ))
    for role in [
        "Cloud Run Admin",
        "Storage Admin  (required to push to Container Registry)",
        "Service Account User",
    ]:
        story.append(Paragraph(f"• {role}", s["step"]))
    story.append(Paragraph(
        "After creating, open the service account → <b>Keys → Add Key → Create new key → JSON</b>. "
        "Download the JSON file — you will paste its contents into a GitHub secret.",
        s["body"],
    ))

    story.append(rule(color=MGRAY, thickness=0.5))

    # ── ONE-TIME GITHUB SETUP ────────────────────────────────────────────────
    story.append(KeepTogether([
        section_header("One-Time GitHub Setup", s),
        Spacer(1, 0.25 * cm),
        Paragraph(
            "Open <b>github.com/ericgitonga/career-transition-intake → "
            "Settings → Secrets and variables → Actions</b> and add these secrets:",
            s["body"],
        ),
    ]))

    secrets = [
        ("GCP_PROJECT_ID", "Your Google Cloud project ID (e.g. my-project-123456)"),
        ("GCP_SA_KEY", "The full contents of the service account JSON key file"),
        ("SMTP_USER", "Your Gmail address (e.g. yourname@gmail.com)"),
        ("SMTP_PASSWORD",
         "Your Gmail App Password — 16-character code from "
         "https://myaccount.google.com/apppasswords"),
    ]
    for name, desc in secrets:
        story.append(Paragraph(f"• <b>{name}</b> — {desc}", s["step"]))

    story.append(Paragraph(
        "<i>SMTP_USER and SMTP_PASSWORD are injected as environment variables into the Cloud Run "
        "service at deploy time. onboarding_form.py reads them from os.environ automatically.</i>",
        s["note"],
    ))

    story.append(rule(color=MGRAY, thickness=0.5))

    # ── DEPLOYING ─────────────────────────────────────────────────────────────
    story.append(KeepTogether([
        section_header("Deploying", s),
        Spacer(1, 0.25 * cm),
        Paragraph(
            "Once setup is complete, deployment is fully automated. Push any change to GitHub:",
            s["body"],
        ),
        Spacer(1, 0.15 * cm),
    ]))
    story.append(code_block("git push origin main", s))
    story.append(Spacer(1, 0.25 * cm))
    story.append(Paragraph(
        "The GitHub Actions workflow (<b>.github/workflows/deploy.yml</b>) will:",
        s["body"],
    ))
    for step in [
        "Authenticate to Google Cloud using the service account key",
        "Build the Docker image from the repo's <b>Dockerfile</b>",
        "Push the image to Google Container Registry (<i>gcr.io/PROJECT_ID/career-transition-intake</i>)",
        "Deploy the new image to Cloud Run in <b>us-central1</b>",
    ]:
        story.append(Paragraph(f"• {step}", s["step"]))
    story.append(Paragraph(
        "First deploy takes 3–5 minutes (image build). Subsequent deploys are faster (~2 min).",
        s["note"],
    ))

    story.append(rule(color=MGRAY, thickness=0.5))

    # ── AFTER DEPLOYMENT ──────────────────────────────────────────────────────
    story.append(KeepTogether([
        section_header("After Deployment", s),
        Spacer(1, 0.25 * cm),
    ]))

    story.append(Paragraph("Finding your URL", s["h3"]))
    story.append(Paragraph(
        "After the first deploy, go to <b>Google Cloud Console → Cloud Run → "
        "career-transition-intake</b>. The public URL is shown at the top of the service page. "
        "It looks like:",
        s["body"],
    ))
    story.append(code_block(
        "https://career-transition-intake-<hash>-uc.a.run.app", s
    ))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        "This URL is permanent — it does not change between deploys.",
        s["note"],
    ))

    story.append(Paragraph("Cold starts", s["h3"]))
    story.append(Paragraph(
        "Cloud Run scales to zero when idle. The first request after a quiet period "
        "takes ~5–10 seconds while the container starts. Subsequent requests are instant. "
        "For a client intake form this is acceptable — warn clients that the first load "
        "may be briefly slow.",
        s["body"],
    ))

    story.append(Paragraph("Keeping it warm (optional)", s["h3"]))
    story.append(Paragraph(
        "To eliminate cold starts, set a minimum instance count of 1 in the Cloud Run service settings "
        "(<b>Edit &amp; Deploy → Capacity → Minimum number of instances → 1</b>). "
        "This incurs a small charge (~$3–5/month on the free-tier compute allocation).",
        s["body"],
    ))

    story.append(Paragraph("Updating SMTP credentials", s["h3"]))
    story.append(Paragraph(
        "Update the <b>SMTP_USER</b> or <b>SMTP_PASSWORD</b> GitHub secrets, then push an empty "
        "commit to trigger a redeploy:",
        s["body"],
    ))
    story.append(code_block(
        'git commit --allow-empty -m "Redeploy to pick up new secrets"\ngit push origin main', s
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
