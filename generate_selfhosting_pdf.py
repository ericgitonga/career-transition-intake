"""
Generate Clients/self-hosting.pdf — a step-by-step guide to hosting the
Career Transition intake form on a custom domain, covering two paths:
  Path A — Custom domain on Render (quick, retains existing auto-deploy)
  Path B — Full VPS self-hosting with GitHub Actions auto-deploy pipeline
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

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "Clients", "self-hosting.pdf")

NAVY    = colors.HexColor("#1B2A4A")
TEAL    = colors.HexColor("#0E7C7B")
GOLD    = colors.HexColor("#C9A84C")
MGRAY   = colors.HexColor("#D0D6E0")
BLACK   = colors.HexColor("#1A1A1A")
WHITE   = colors.white
CODE_BG = colors.HexColor("#1E2533")
CODE_FG = colors.HexColor("#E6EDF3")
LIGHT   = colors.HexColor("#F7F9FC")
WARN_BG = colors.HexColor("#FFF8E6")
WARN_BD = colors.HexColor("#C9A84C")
TIP_BG  = colors.HexColor("#E8F5F0")
TIP_BD  = colors.HexColor("#0E7C7B")

W, H    = A4
MARGIN  = 1.5 * cm
INNER_W = W - 2 * MARGIN


# ── Styles ────────────────────────────────────────────────────────────────────

def styles():
    """Return the paragraph style dictionary."""
    def S(name, **kw):
        return ParagraphStyle(name, **kw)
    return {
        "title":  S("title",  fontName="Helvetica-Bold",   fontSize=20, textColor=WHITE,
                    leading=26, alignment=TA_CENTER),
        "sub":    S("sub",    fontName="Helvetica-Bold",   fontSize=12, textColor=GOLD,
                    leading=18, alignment=TA_CENTER),
        "meta":   S("meta",   fontName="Helvetica",         fontSize=9,  textColor=MGRAY,
                    leading=13, alignment=TA_CENTER),
        "h3":     S("h3",     fontName="Helvetica-Bold",   fontSize=10.5, textColor=TEAL,
                    leading=14, spaceBefore=8, spaceAfter=3),
        "body":   S("body",   fontName="Helvetica",         fontSize=9.5, textColor=BLACK,
                    leading=14, spaceAfter=5, alignment=TA_JUSTIFY),
        "bullet": S("bullet", fontName="Helvetica",         fontSize=9.5, textColor=BLACK,
                    leading=14, spaceAfter=3, leftIndent=14),
        "code":   S("code",   fontName="Courier",           fontSize=8,   textColor=CODE_FG,
                    leading=12, leftIndent=8, rightIndent=8),
        "note":   S("note",   fontName="Helvetica-Oblique", fontSize=8.5,
                    textColor=colors.HexColor("#555555"), leading=12, spaceAfter=5),
        "step":   S("step",   fontName="Helvetica-Bold",   fontSize=10,  textColor=NAVY,
                    leading=14, spaceBefore=6, spaceAfter=2),
        "th":     S("th",     fontName="Helvetica-Bold",   fontSize=8.5, textColor=WHITE,
                    leading=12),
        "td":     S("td",     fontName="Courier",           fontSize=8,   textColor=BLACK,
                    leading=12),
        "td2":    S("td2",    fontName="Helvetica",         fontSize=8.5, textColor=BLACK,
                    leading=12),
        "warn":   S("warn",   fontName="Helvetica",         fontSize=9,   textColor=BLACK,
                    leading=13),
        "tip":    S("tip",    fontName="Helvetica",         fontSize=9,   textColor=BLACK,
                    leading=13),
        "path":   S("path",   fontName="Courier-Bold",      fontSize=9,   textColor=TEAL,
                    leading=13),
    }


# ── Helpers ───────────────────────────────────────────────────────────────────

def rule(color=GOLD, thickness=1, before=6, after=8):
    return HRFlowable(width="100%", thickness=thickness, color=color,
                      spaceBefore=before, spaceAfter=after)


def section_header(text):
    """Full-width navy section banner."""
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


def path_header(letter, title, subtitle):
    """Coloured path-choice banner (Path A / Path B)."""
    bg = TEAL if letter == "A" else NAVY
    p1 = Paragraph(f"PATH {letter} — {title}", ParagraphStyle(
        "ph1", fontName="Helvetica-Bold", fontSize=12, textColor=WHITE, leading=16))
    p2 = Paragraph(subtitle, ParagraphStyle(
        "ph2", fontName="Helvetica", fontSize=9, textColor=GOLD, leading=13))
    t = Table([[p1], [p2]], colWidths=[INNER_W])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), bg),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
    ]))
    return t


def step_block(n, title, s):
    """Numbered step header."""
    num = Paragraph(str(n), ParagraphStyle(
        "sn", fontName="Helvetica-Bold", fontSize=10, textColor=WHITE, leading=13,
        alignment=TA_CENTER))
    lbl = Paragraph(title, ParagraphStyle(
        "sl", fontName="Helvetica-Bold", fontSize=10, textColor=NAVY, leading=13))
    t = Table([[num, lbl]], colWidths=[0.65 * cm, INNER_W - 0.65 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (0, 0), TEAL),
        ("BACKGROUND",    (1, 0), (1, 0), LIGHT),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (0, 0), 4),
        ("LEFTPADDING",   (1, 0), (1, 0), 8),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def code_block(text):
    """Dark-background monospaced code block."""
    lines = text.strip().split("\n")
    rows = [[Preformatted(line, ParagraphStyle(
        "cl", fontName="Courier", fontSize=8, textColor=CODE_FG, leading=12))]
        for line in lines]
    t = Table(rows, colWidths=[INNER_W])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), CODE_BG),
        ("TOPPADDING",    (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("TOPPADDING",    (0, 0), (0, 0), 8),
        ("BOTTOMPADDING", (0, -1), (0, -1), 8),
    ]))
    return t


def dns_table(rows, s):
    """DNS record table."""
    header, *data = rows
    tdata = [[Paragraph(c, s["th"]) for c in header]] + \
            [[Paragraph(c, s["td"] if i < 3 else s["td2"]) for i, c in enumerate(row)]
             for row in data]
    t = Table(tdata, colWidths=[INNER_W * 0.12, INNER_W * 0.20, INNER_W * 0.12, INNER_W * 0.56],
              repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  NAVY),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [LIGHT, colors.HexColor("#EDF0F5")]),
        ("GRID",          (0, 0), (-1, -1), 0.4, MGRAY),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def callout(text, style, bg, border_color):
    """Coloured callout box (warning or tip)."""
    p = Paragraph(text, style)
    t = Table([[p]], colWidths=[INNER_W])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), bg),
        ("LINEBEFORE",    (0, 0), (0, -1), 3, border_color),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))
    return t


def warn(text, s):
    return callout(f"⚠  {text}", s["warn"], WARN_BG, WARN_BD)


def tip(text, s):
    return callout(f"✓  {text}", s["tip"], TIP_BG, TIP_BD)


def b(t):
    return f"<b>{t}</b>"


def bullet(text, s):
    return Paragraph(f"• {text}", s["bullet"])


# ── Story ─────────────────────────────────────────────────────────────────────

def build_story(s):
    """Assemble all flowables for the self-hosting guide."""
    story = []

    # Cover
    cover = Table([
        [Paragraph("CAREER TRANSITION INTAKE FORM", s["title"])],
        [Spacer(1, 0.2 * cm)],
        [Paragraph("Self-Hosting Guide", s["sub"])],
        [Paragraph("Custom Domain · VPS Deployment · GitHub Auto-Deploy", s["sub"])],
        [Spacer(1, 0.3 * cm)],
        [Paragraph("Internal Reference — July 2026", s["meta"])],
    ], colWidths=[INNER_W])
    cover.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), NAVY),
        ("TOPPADDING",    (0, 0), (-1, -1), 18),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 18),
        ("LEFTPADDING",   (0, 0), (-1, -1), 20),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 20),
    ]))
    story += [cover, Spacer(1, 0.4 * cm), rule(GOLD, 2, 2, 10)]

    # Overview
    story.append(KeepTogether([section_header("Overview"), Spacer(1, 0.2 * cm)]))
    story.append(Paragraph(
        "This guide covers everything needed to serve the Career Transition intake form "
        "from your own domain name (e.g. <b>intake.yourdomain.com</b>) rather than the "
        "default Render subdomain. Two paths are presented:",
        s["body"],
    ))
    for item in [
        "<b>Path A — Custom domain on Render</b> (recommended): point your domain at the "
        "existing Render service. Render handles SSL, uptime, and auto-deploy from GitHub. "
        "Done in under 15 minutes.",
        "<b>Path B — Full VPS self-hosting</b>: run the app on your own server "
        "(DigitalOcean, Hetzner, Linode, etc.) behind Nginx with Let's Encrypt SSL and "
        "a GitHub Actions pipeline that redeploys automatically on every push to main.",
    ]:
        story.append(bullet(item, s))
    story.append(Paragraph(
        "Both paths end with the same result: the form is reachable at your domain, "
        "email is sent via Resend, and a git push to main triggers an automatic redeploy.",
        s["body"],
    ))
    story.append(rule(MGRAY, 0.5))

    # ── Part 0: Register a domain ─────────────────────────────────────────────
    story.append(KeepTogether([section_header("Step 0 — Register a Domain"), Spacer(1, 0.2 * cm)]))
    story.append(Paragraph(
        "Both paths require a domain name you control. If you already have one, skip to "
        "Path A or B. If not, register one with any of the following registrars — "
        "Cloudflare Registrar is recommended because it sells domains at cost (no markup) "
        "and its DNS dashboard is the fastest to configure.",
        s["body"],
    ))
    reg_rows = [
        ["Registrar", "URL", "Notes"],
        ["Cloudflare", "cloudflare.com/products/registrar", "At-cost pricing, excellent DNS UI"],
        ["Namecheap",  "namecheap.com",                    "Competitive pricing, good for .com"],
        ["Porkbun",    "porkbun.com",                      "Often cheapest for .com renewals"],
        ["Google / Squarespace", "domains.squarespace.com","Simple UI; Google Domains migrated here"],
    ]
    t = Table(
        [[Paragraph(c, s["th"]) for c in reg_rows[0]]] +
        [[Paragraph(c, s["td2"]) for c in row] for row in reg_rows[1:]],
        colWidths=[INNER_W * 0.22, INNER_W * 0.42, INNER_W * 0.36],
    )
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  NAVY),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [LIGHT, colors.HexColor("#EDF0F5")]),
        ("GRID",          (0, 0), (-1, -1), 0.4, MGRAY),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 7),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 7),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.15 * cm))
    story.append(tip(
        "For a coaching practice, a subdomain of an existing domain works well and costs "
        "nothing extra — e.g. intake.yourname.com or onboarding.yourpractice.com.",
        s,
    ))
    story.append(rule(MGRAY, 0.5))

    # ════════════════════════════════════════════════════════════════════════
    # PATH A
    # ════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(path_header("A", "Custom Domain on Render",
                              "Keep Render hosting — just point your domain at it. "
                              "GitHub auto-deploy already works. Done in ~15 minutes."))
    story.append(Spacer(1, 0.3 * cm))

    # A-1
    story.append(step_block(1, "Add your custom domain in Render", s))
    story.append(Spacer(1, 0.15 * cm))
    for item in [
        "Open the Render dashboard and select the <b>career-transition-intake</b> service.",
        "Click <b>Settings → Custom Domains → Add Custom Domain</b>.",
        "Type your domain or subdomain (e.g. <b>intake.yourdomain.com</b>) and click <b>Save</b>.",
        "Render displays the DNS record you need to create — copy it before moving on.",
    ]:
        story.append(bullet(item, s))

    # A-2
    story.append(Spacer(1, 0.2 * cm))
    story.append(step_block(2, "Create the DNS record at your registrar", s))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(
        "Log into your domain registrar's DNS settings and add one of the following, "
        "depending on whether you are using a subdomain or the root domain:",
        s["body"],
    ))
    story.append(dns_table([
        ["Type", "Name", "TTL", "Value"],
        ["CNAME", "intake", "Auto", "career-transition-intake.onrender.com"],
        ["ALIAS / ANAME", "@", "Auto", "career-transition-intake.onrender.com  (root domain only)"],
    ], s))
    story.append(Spacer(1, 0.1 * cm))
    story.append(warn(
        "Do not use an A record pointing to an IP address — Render's IPs can change. "
        "Always use a CNAME (or ALIAS for root domains).",
        s,
    ))

    # A-3
    story.append(Spacer(1, 0.2 * cm))
    story.append(step_block(3, "Wait for DNS propagation and SSL", s))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(
        "DNS changes typically propagate within 1–10 minutes on Cloudflare and up to "
        "48 hours on some registrars (usually much faster). Once Render detects the "
        "record, it automatically provisions a Let's Encrypt SSL certificate. "
        "The domain status in the Render dashboard will show <b>Active</b> when ready.",
        s["body"],
    ))
    story.append(tip(
        "You can check propagation progress at whatsmydns.net — search for your domain "
        "and select CNAME to see which regions have picked up the new record.",
        s,
    ))

    # A-4
    story.append(Spacer(1, 0.2 * cm))
    story.append(step_block(4, "Verify", s))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(
        "Open a browser and navigate to your domain. The intake form should load over "
        "HTTPS with a valid certificate. GitHub auto-deploy remains active — every push "
        "to main redeploys the service and the custom domain continues to work.",
        s["body"],
    ))
    story.append(tip(
        "Path A is complete. Skip to the Resend Custom Domain section if you want "
        "email to be sent from your own domain address rather than onboarding@resend.dev.",
        s,
    ))
    story.append(rule(MGRAY, 0.5))

    # ════════════════════════════════════════════════════════════════════════
    # PATH B
    # ════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(path_header("B", "Full VPS Self-Hosting",
                              "Run the app on your own server with Nginx, gunicorn, "
                              "Let's Encrypt SSL, and GitHub Actions auto-deploy."))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "This path gives you complete control: your own server, your own domain, "
        "no dependency on Render. The reference server is an Ubuntu 22.04 LTS VPS. "
        "Any provider works — DigitalOcean ($6/mo Droplet), Hetzner (€4/mo CX11), "
        "or Linode/Akamai ($5/mo Nanode) are all sufficient for this workload.",
        s["body"],
    ))

    # B-1
    story.append(step_block(1, "Provision a server", s))
    story.append(Spacer(1, 0.15 * cm))
    for item in [
        "Create an account at your chosen VPS provider.",
        "Create a new server: <b>Ubuntu 22.04 LTS</b>, smallest plan (1 vCPU / 1 GB RAM).",
        "Add your SSH public key during setup so you can log in without a password.",
        "Note the server's public IP address.",
    ]:
        story.append(bullet(item, s))

    # B-2
    story.append(Spacer(1, 0.2 * cm))
    story.append(step_block(2, "Point your domain at the server", s))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(
        "In your registrar's DNS settings, create an A record pointing your subdomain "
        "to the server's IP:",
        s["body"],
    ))
    story.append(dns_table([
        ["Type", "Name", "TTL", "Value"],
        ["A", "intake", "Auto / 300", "YOUR_SERVER_IP"],
    ], s))

    # B-3
    story.append(Spacer(1, 0.2 * cm))
    story.append(step_block(3, "Initial server setup", s))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph("SSH into the server and run the following:", s["body"]))
    story.append(code_block("""\
# Log in
ssh root@YOUR_SERVER_IP

# Update packages
apt update && apt upgrade -y

# Install dependencies
apt install -y python3 python3-pip python3-venv git nginx certbot python3-certbot-nginx

# Create a non-root user to run the app
adduser --disabled-password --gecos "" appuser
usermod -aG sudo appuser"""))

    # B-4
    story.append(Spacer(1, 0.2 * cm))
    story.append(step_block(4, "Clone the repository and install dependencies", s))
    story.append(Spacer(1, 0.15 * cm))
    story.append(code_block("""\
# Switch to appuser
su - appuser

# Clone the repo
git clone https://github.com/ericgitonga/career-transition-intake.git
cd career-transition-intake

# Create virtual environment and install packages
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt"""))

    # B-5
    story.append(Spacer(1, 0.2 * cm))
    story.append(step_block(5, "Set environment variables", s))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(
        "Create a file to hold the app's secrets. It will be sourced by the systemd "
        "service — never commit this file to git.",
        s["body"],
    ))
    story.append(code_block("""\
# Still as appuser, from the repo directory
cat > /home/appuser/career-transition-intake/.env << 'EOF'
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
FROM_EMAIL=intake@yourdomain.com
EOF

chmod 600 /home/appuser/career-transition-intake/.env"""))

    # B-6
    story.append(Spacer(1, 0.2 * cm))
    story.append(step_block(6, "Create a systemd service for gunicorn", s))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(
        "A systemd service keeps gunicorn running, restarts it on failure, and starts "
        "it automatically on server reboot. Run the following as root:",
        s["body"],
    ))
    story.append(code_block("""\
# Switch back to root
exit   # exits appuser shell

cat > /etc/systemd/system/career-transition.service << 'EOF'
[Unit]
Description=Career Transition Intake — gunicorn
After=network.target

[Service]
User=appuser
WorkingDirectory=/home/appuser/career-transition-intake
EnvironmentFile=/home/appuser/career-transition-intake/.env
ExecStart=/home/appuser/career-transition-intake/.venv/bin/gunicorn \\
          app:app --bind 127.0.0.1:8000 --workers 2 --timeout 60
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable career-transition
systemctl start career-transition
systemctl status career-transition   # should show: active (running)"""))

    # B-7
    story.append(Spacer(1, 0.2 * cm))
    story.append(step_block(7, "Configure Nginx as a reverse proxy", s))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(
        "Nginx sits in front of gunicorn, handles HTTPS, and serves the app publicly. "
        "Replace <b>intake.yourdomain.com</b> with your actual subdomain throughout:",
        s["body"],
    ))
    story.append(code_block("""\
cat > /etc/nginx/sites-available/career-transition << 'EOF'
server {
    listen 80;
    server_name intake.yourdomain.com;

    client_max_body_size 20M;

    location / {
        proxy_pass         http://127.0.0.1:8000;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }
}
EOF

ln -s /etc/nginx/sites-available/career-transition \\
      /etc/nginx/sites-enabled/career-transition

nginx -t          # confirm config is valid
systemctl reload nginx"""))

    # B-8
    story.append(Spacer(1, 0.2 * cm))
    story.append(step_block(8, "Provision SSL with Let's Encrypt", s))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(
        "Certbot obtains a free SSL certificate and automatically updates the Nginx "
        "config to redirect HTTP to HTTPS. DNS must have propagated before this step.",
        s["body"],
    ))
    story.append(code_block("""\
certbot --nginx -d intake.yourdomain.com

# Follow the prompts:
#   Enter your email address (for renewal notices)
#   Agree to the terms of service
#   Choose to redirect HTTP to HTTPS (option 2)

# Certbot auto-renews via a systemd timer — verify it is active:
systemctl status certbot.timer"""))
    story.append(Spacer(1, 0.1 * cm))
    story.append(tip(
        "Certbot certificates last 90 days and renew automatically. "
        "You never need to touch this again unless you change the domain.",
        s,
    ))

    # B-9
    story.append(Spacer(1, 0.2 * cm))
    story.append(step_block(9, "Verify the live site", s))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(
        "Open a browser and navigate to https://intake.yourdomain.com. "
        "The dark-themed intake form should load over HTTPS with a valid certificate. "
        "Submit a test entry to confirm PDF generation and email delivery.",
        s["body"],
    ))
    story.append(rule(MGRAY, 0.5))

    # ── GitHub Actions Auto-Deploy ─────────────────────────────────────────────
    story.append(PageBreak())
    story.append(KeepTogether([
        section_header("GitHub Actions Auto-Deploy Pipeline (Path B)"),
        Spacer(1, 0.2 * cm),
    ]))
    story.append(Paragraph(
        "With this pipeline in place, every push to the main branch on GitHub "
        "automatically SSHes into your server, pulls the latest code, reinstalls "
        "any new dependencies, and restarts gunicorn — matching the seamless deploy "
        "experience of Render, but on your own server.",
        s["body"],
    ))

    # Step A: deploy user SSH key
    story.append(Paragraph(b("Step A — Create a deploy SSH key on the server"), s["h3"]))
    story.append(code_block("""\
# Run as appuser on the server
ssh-keygen -t ed25519 -C "github-deploy" -f ~/.ssh/deploy_key -N ""

# Add the PUBLIC key to authorized_keys
cat ~/.ssh/deploy_key.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# Print the PRIVATE key — you will paste this into GitHub
cat ~/.ssh/deploy_key"""))
    story.append(Spacer(1, 0.1 * cm))
    story.append(warn(
        "The private key (deploy_key) must never be committed to the repository. "
        "Copy it to GitHub Secrets only.",
        s,
    ))

    # Step B: GitHub secrets
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(b("Step B — Add secrets to GitHub"), s["h3"]))
    story.append(Paragraph(
        "In the GitHub repository, go to <b>Settings → Secrets and variables → "
        "Actions → New repository secret</b> and add three secrets:",
        s["body"],
    ))
    sec_rows = [
        ["Secret name", "Value"],
        ["SERVER_HOST", "Your server's public IP address"],
        ["SERVER_USER", "appuser"],
        ["SERVER_SSH_KEY", "The full contents of ~/.ssh/deploy_key (private key)"],
    ]
    t2 = Table(
        [[Paragraph(c, s["th"]) for c in sec_rows[0]]] +
        [[Paragraph(c, s["td"] if i == 0 else s["td2"]) for i, c in enumerate(row)]
         for row in sec_rows[1:]],
        colWidths=[INNER_W * 0.35, INNER_W * 0.65],
    )
    t2.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  NAVY),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [LIGHT, colors.HexColor("#EDF0F5")]),
        ("GRID",          (0, 0), (-1, -1), 0.4, MGRAY),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 7),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 7),
    ]))
    story.append(t2)

    # Step C: workflow file
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(b("Step C — Create the GitHub Actions workflow file"), s["h3"]))
    story.append(Paragraph(
        "In the repository on your local machine, create the following file and push it:",
        s["body"],
    ))
    story.append(Paragraph(".github/workflows/deploy.yml", s["path"]))
    story.append(Spacer(1, 0.1 * cm))
    story.append(code_block("""\
name: Deploy to VPS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy via SSH
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SERVER_SSH_KEY }}
          script: |
            cd /home/appuser/career-transition-intake
            git pull origin main
            source .venv/bin/activate
            pip install -r requirements.txt --quiet
            sudo systemctl restart career-transition"""))
    story.append(Spacer(1, 0.1 * cm))
    story.append(warn(
        "The workflow uses sudo systemctl restart. Grant appuser passwordless sudo "
        "for this one command by running visudo on the server and adding:\n"
        "appuser ALL=(ALL) NOPASSWD: /bin/systemctl restart career-transition",
        s,
    ))

    # Step D: push and verify
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(b("Step D — Push the workflow and verify"), s["h3"]))
    story.append(code_block("""\
# On your local machine
git add .github/workflows/deploy.yml
git commit -m "Add GitHub Actions auto-deploy workflow"
git push origin main"""))
    story.append(Spacer(1, 0.1 * cm))
    story.append(Paragraph(
        "Open the repository on GitHub → <b>Actions</b> tab. The Deploy to VPS workflow "
        "will appear and run immediately. A green tick means the deploy succeeded. "
        "From this point on, every push to main automatically redeploys the server.",
        s["body"],
    ))
    story.append(tip(
        "Check the Actions tab after every push to confirm deploys are succeeding. "
        "If a deploy fails, the previous version continues running — the server is "
        "never left in a broken state.",
        s,
    ))
    story.append(rule(MGRAY, 0.5))

    # ── Resend custom domain ───────────────────────────────────────────────────
    story.append(KeepTogether([
        section_header("Custom Sender Email via Resend (Both Paths)"),
        Spacer(1, 0.2 * cm),
    ]))
    story.append(Paragraph(
        "By default the form sends email from <b>onboarding@resend.dev</b>. "
        "To send from your own address (e.g. <b>intake@yourdomain.com</b>), "
        "verify your domain in Resend and set one additional environment variable.",
        s["body"],
    ))

    story.append(Paragraph(b("1. Verify your domain in Resend"), s["h3"]))
    for item in [
        "Log into resend.com → <b>Domains → Add Domain</b>.",
        "Enter your domain (e.g. <b>yourdomain.com</b>) and select your DNS provider.",
        "Resend displays a set of DNS records to add — typically three TXT records "
        "and one MX record.",
    ]:
        story.append(bullet(item, s))

    story.append(Spacer(1, 0.1 * cm))
    story.append(Paragraph(b("2. Add the DNS records at your registrar"), s["h3"]))
    story.append(dns_table([
        ["Type", "Name", "TTL", "Value"],
        ["TXT", "resend._domainkey", "Auto", "p=MIGfMA0GCSqG... (from Resend dashboard)"],
        ["TXT", "@", "Auto", "v=spf1 include:amazonses.com ~all"],
        ["MX",  "bounces", "Auto", "feedback-smtp.us-east-1.amazonses.com"],
    ], s))
    story.append(Spacer(1, 0.1 * cm))
    story.append(Paragraph(
        "After saving the records, click <b>Verify</b> in the Resend dashboard. "
        "Propagation typically takes 1–10 minutes. The domain status will change to "
        "<b>Verified</b> when ready.",
        s["body"],
    ))

    story.append(Paragraph(b("3. Set the FROM_EMAIL environment variable"), s["h3"]))
    story.append(Paragraph(
        "Once the domain is verified, set a FROM_EMAIL variable to the address you "
        "want to send from:", s["body"]))
    story.append(Paragraph(b("Path A (Render):"), s["note"]))
    story.append(Paragraph(
        "Render dashboard → Environment → Add variable: "
        "<b>FROM_EMAIL</b> = intake@yourdomain.com → Save Changes.",
        s["body"],
    ))
    story.append(Paragraph(b("Path B (VPS):"), s["note"]))
    story.append(code_block("""\
# Edit the .env file on the server
nano /home/appuser/career-transition-intake/.env

# Add or update:
FROM_EMAIL=intake@yourdomain.com

# Restart the service
sudo systemctl restart career-transition"""))
    story.append(Spacer(1, 0.1 * cm))
    story.append(tip(
        "The sender name shown in email clients (e.g. 'Career Transition Intake') "
        "can be set in app.py by changing the 'from' field to: "
        "Career Transition <intake@yourdomain.com>",
        s,
    ))
    story.append(rule(MGRAY, 0.5))

    # ── Maintenance ───────────────────────────────────────────────────────────
    story.append(KeepTogether([
        section_header("Ongoing Maintenance (Path B)"),
        Spacer(1, 0.2 * cm),
    ]))
    story.append(Paragraph(
        "Once deployed, the server requires minimal attention. "
        "Below are the commands you will reach for most often:",
        s["body"],
    ))
    maint = [
        ("Check app status",      "sudo systemctl status career-transition"),
        ("View live logs",        "sudo journalctl -u career-transition -f"),
        ("Restart the app",       "sudo systemctl restart career-transition"),
        ("Reload Nginx",          "sudo systemctl reload nginx"),
        ("Check SSL certificate", "sudo certbot certificates"),
        ("Manual server update",  "sudo apt update && sudo apt upgrade -y"),
    ]
    rows = [[Paragraph(a, s["td2"]), Paragraph(b, s["td"])] for a, b in maint]
    mt = Table(rows, colWidths=[INNER_W * 0.35, INNER_W * 0.65])
    mt.setStyle(TableStyle([
        ("ROWBACKGROUNDS",(0, 0), (-1, -1), [LIGHT, colors.HexColor("#EDF0F5")]),
        ("GRID",          (0, 0), (-1, -1), 0.4, MGRAY),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 7),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 7),
    ]))
    story.append(mt)
    story.append(Spacer(1, 0.15 * cm))
    story.append(warn(
        "SSL certificates renew automatically via the certbot.timer systemd service. "
        "If you ever change the server or domain, run: certbot --nginx -d newdomain.com",
        s,
    ))
    story.append(rule(GOLD, 1.5, 10, 4))

    return story


# ── Document builder ──────────────────────────────────────────────────────────

def make_doc():
    """Build and write the self-hosting guide to Clients/self-hosting.pdf."""
    s = styles()
    doc = SimpleDocTemplate(
        OUTPUT_PATH, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=1.5 * cm, bottomMargin=1.8 * cm,
    )

    def footer(canvas, doc):
        """Page footer with document title and page number."""
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#888888"))
        canvas.drawString(MARGIN, 0.7 * cm,
                          "Career Transition Intake — Self-Hosting Guide")
        canvas.drawRightString(W - MARGIN, 0.7 * cm, f"Page {doc.page}")
        canvas.restoreState()

    doc.build(build_story(s), onFirstPage=footer, onLaterPages=footer)
    print(f"PDF written to: {OUTPUT_PATH}")


if __name__ == "__main__":
    make_doc()
