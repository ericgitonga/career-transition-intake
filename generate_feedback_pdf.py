"""
Generate extras/feedback_01.pdf — Round 1 feedback synthesis report for the
Career Transition intake form, based on testing sessions with Jean Onyango and
Aida (July 2026).

Covers:
  1  Overview
  2  Critical Bug: CSRF Token Invalidation
  3  Form Flow Issues
  4  New Question Suggestions
  5  Section Title Clarity
  6  Scope & Audience
  7  Error Display
  8  Summary Change Table

Usage:
    python generate_feedback_pdf.py
    # → extras/feedback_01.pdf
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    HRFlowable, KeepTogether, Table, TableStyle, PageBreak,
)

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "extras", "feedback_01.pdf")

NAVY  = colors.HexColor("#1B2A4A")
TEAL  = colors.HexColor("#0E7C7B")
GOLD  = colors.HexColor("#C9A84C")
MGRAY = colors.HexColor("#D0D6E0")
LGRAY = colors.HexColor("#F4F6F9")
BLACK = colors.HexColor("#1A1A1A")
WHITE = colors.white
RED   = colors.HexColor("#C0392B")
GREEN = colors.HexColor("#1A7A4A")
AMBER = colors.HexColor("#E67E22")

W, H     = A4
MARGIN   = 1.5 * cm
INNER_W  = W - 2 * MARGIN


# ── Styles ────────────────────────────────────────────────────────────────────

def styles():
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
        "note":     S("note",   fontName="Helvetica-Oblique", fontSize=8.5,
                      textColor=colors.HexColor("#555555"), leading=12, spaceAfter=5),
        "cell":     S("cell",   fontName="Helvetica",         fontSize=9,   textColor=BLACK,
                      leading=12),
        "cell_bold":S("cb",     fontName="Helvetica-Bold",    fontSize=9,   textColor=BLACK,
                      leading=12),
        "th":       S("th",     fontName="Helvetica-Bold",    fontSize=9,   textColor=WHITE,
                      leading=12),
        "critical": S("crit",   fontName="Helvetica-Bold",    fontSize=9,   textColor=RED,
                      leading=12),
        "high":     S("high",   fontName="Helvetica-Bold",    fontSize=9,   textColor=AMBER,
                      leading=12),
        "low":      S("low",    fontName="Helvetica-Bold",    fontSize=9,   textColor=GREEN,
                      leading=12),
        "quote":    S("quote",  fontName="Helvetica-Oblique", fontSize=9,
                      textColor=colors.HexColor("#333355"), leading=13,
                      leftIndent=16, rightIndent=8, spaceAfter=4),
    }


# ── Helpers ───────────────────────────────────────────────────────────────────

def rule(color=GOLD, thickness=1, before=6, after=8):
    return HRFlowable(width="100%", thickness=thickness, color=color,
                      spaceBefore=before, spaceAfter=after)


def section_header(text, _s):
    p = Paragraph(text, ParagraphStyle(
        "sh_fb", fontName="Helvetica-Bold", fontSize=11,
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


def callout(label, text, s, bg=LGRAY, border=TEAL):
    """Shaded callout box with a coloured left border."""
    inner = ParagraphStyle("co_inner", fontName="Helvetica", fontSize=9.5,
                           textColor=BLACK, leading=14)
    label_style = ParagraphStyle("co_label", fontName="Helvetica-Bold",
                                 fontSize=9.5, textColor=border, leading=14)
    content = [Paragraph(f"<b>{label}</b>", label_style),
               Paragraph(text, inner)]
    t = Table([[content]], colWidths=[INNER_W - 4])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), bg),
        ("LINEBEFORE",    (0, 0), (0, -1),  3, border),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))
    return t


# ── Cover ─────────────────────────────────────────────────────────────────────

def cover(s):
    cover_bg = Table(
        [[Paragraph("Career Transition Intake Form", s["title"])],
         [Paragraph("Round 1 Feedback Report", s["subtitle"])],
         [Spacer(1, 6)],
         [Paragraph("Testers: Jean Onyango · Aida", s["meta"])],
         [Paragraph("Date: 10 July 2026 &nbsp;|&nbsp; Prepared by: Eric Gitonga", s["meta"])]],
        colWidths=[INNER_W],
    )
    cover_bg.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), NAVY),
        ("TOPPADDING",    (0, 0), (-1, -1), 28),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 28),
        ("LEFTPADDING",   (0, 0), (-1, -1), 18),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 18),
    ]))
    return [cover_bg, rule(GOLD, 2, 0, 16)]


# ── Section 1: Overview ───────────────────────────────────────────────────────

def section_overview(s):
    out = [
        section_header("1.  Overview", s), Spacer(1, 8),
        Paragraph(
            "This report synthesises feedback from two testers who reviewed and attempted to "
            "complete the Career Transition intake form at "
            "<i>career-transition-intake.onrender.com</i> on 10 July 2026. "
            "Jean Onyango completed a full walkthrough and documented her responses and "
            "observations inline (printed to PDF after the form failed to submit). "
            "Aida reviewed the form and provided a written UX summary.",
            s["body"]),
        Paragraph(
            "The findings are grouped into five categories: a critical technical bug that "
            "prevented submission entirely; form flow issues where question sequencing confused "
            "testers; a missing question identified by Jean; a section title that needs "
            "rewording; and a scope/audience gap flagged by Aida. Each finding includes "
            "a recommended fix and a priority rating.",
            s["body"]),
        Spacer(1, 4),
        rule(MGRAY, 0.5),
    ]
    return out


# ── Section 2: Critical Bug ───────────────────────────────────────────────────

def section_csrf(s):
    out = [
        section_header("2.  Critical Bug — CSRF Token Invalidation on Server Restart", s),
        Spacer(1, 8),
    ]

    out += [
        Paragraph("Source", s["h3"]),
        Paragraph(
            "Jean's feedback and server log from the Render deployment.",
            s["body"]),

        Paragraph("What happened", s["h3"]),
        Paragraph(
            "Jean opened the form at 11:31 UTC and spent approximately 15 minutes filling it in. "
            "At 11:46 UTC the Render instance was spun down (free-tier idle timeout). "
            "When Jean clicked Submit at 11:49 UTC the server had already restarted with a "
            "newly generated <b>SECRET_KEY</b>, invalidating her CSRF token. "
            "Every POST attempt returned HTTP 400. She tried ten times before giving up and "
            "printing the page to PDF instead.",
            s["body"]),
    ]

    out.append(callout(
        "Jean's exact words:",
        "\"The PDF generation did not happen. Gave the error: Error: &lt;!doctype html&gt; "
        "&lt;html lang=en&gt; &lt;title&gt;400 Bad Request&lt;/title&gt; &lt;h1&gt;Bad "
        "Request&lt;/h1&gt; &lt;p&gt;The CSRF session token is missing.&lt;/p&gt; — "
        "The form refused to submit.\"",
        s))
    out.append(Spacer(1, 8))

    out += [
        Paragraph("Root cause", s["h3"]),
        Paragraph(
            "The <b>SECRET_KEY</b> environment variable is not set in the Render dashboard. "
            "The app falls back to <i>secrets.token_hex(32)</i> on each startup, so every "
            "restart generates a new key and invalidates all outstanding CSRF tokens. "
            "On Render's free tier, instances spin down after 15 minutes of inactivity and "
            "restart on the next request — exactly the pattern that hit Jean.",
            s["body"]),

        Paragraph("Fix", s["h3"]),
    ]

    fix_rows = [
        [Paragraph("Step", s["th"]), Paragraph("Action", s["th"])],
        [Paragraph("1", s["cell"]),
         Paragraph(
             "Go to Render dashboard → <i>career-transition-intake</i> service → "
             "Environment → Add environment variable.",
             s["cell"])],
        [Paragraph("2", s["cell"]),
         Paragraph(
             "Set <b>SECRET_KEY</b> to a strong random value, e.g. output of "
             "<i>python -c \"import secrets; print(secrets.token_hex(32))\"</i>.",
             s["cell"])],
        [Paragraph("3", s["cell"]),
         Paragraph(
             "Trigger a manual redeploy so the new variable takes effect.",
             s["cell"])],
        [Paragraph("4", s["cell"]),
         Paragraph(
             "Verify: load the form, wait 20 minutes (to force a spin-down), reload, "
             "fill in and submit — should succeed.",
             s["cell"])],
    ]
    col_w = [1.2 * cm, INNER_W - 1.2 * cm]
    t = Table(fix_rows, colWidths=col_w)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  NAVY),
        ("BACKGROUND",    (0, 1), (-1, -1), LGRAY),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, LGRAY]),
        ("GRID",          (0, 0), (-1, -1), 0.4, MGRAY),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))
    out += [t, Spacer(1, 6)]

    out.append(callout(
        "Priority: CRITICAL",
        "Blocked a real user from submitting entirely. No workaround exists for non-technical "
        "users. Must be resolved before the next tester session.",
        s, bg=colors.HexColor("#FEF0F0"), border=RED))
    out.append(Spacer(1, 4))
    out.append(rule(MGRAY, 0.5))
    return out


# ── Section 3: Form Flow ──────────────────────────────────────────────────────

def section_flow(s):
    out = [
        section_header("3.  Form Flow Issue — Question Appears Before Its Subject", s),
        Spacer(1, 8),
    ]

    out += [
        Paragraph("Source", s["h3"]),
        Paragraph("Jean Onyango — inline feedback written into the form during her session.", s["body"]),

        Paragraph("What happened", s["h3"]),
        Paragraph(
            "In Section 2 (Motivation &amp; Context), the form asks: "
            "<i>\"What specifically attracts you to the target domain?\"</i> "
            "This question appears <b>before</b> the user has been asked what their target "
            "domain is. The target domain field lives in Section 3 (Target Role Clarity). "
            "Jean could not answer meaningfully because no domain had been established yet.",
            s["body"]),
    ]

    out.append(callout(
        "Jean's exact words (written into the field):",
        "\"Here, you need to ask what the target domain is first, before asking what attracts "
        "me to it. This question should move to the target clarity role section.\"",
        s))
    out.append(Spacer(1, 8))

    out += [
        Paragraph("Fix", s["h3"]),
        Paragraph(
            "Move <i>\"What specifically attracts you to the target domain?\"</i> from "
            "Section 2 to Section 3, placing it immediately <b>after</b> the "
            "<i>\"Target domain / field\"</i> input. The question becomes logical once the "
            "domain is established and the answer will be richer because the respondent has "
            "just named what they are targeting.",
            s["body"]),
    ]

    out.append(callout(
        "Priority: HIGH",
        "Caused confusion for a first-time user and produced an unusable answer. "
        "The fix is a simple reorder — no new fields needed.",
        s, bg=colors.HexColor("#FFF8EE"), border=AMBER))
    out.append(Spacer(1, 4))
    out.append(rule(MGRAY, 0.5))
    return out


# ── Section 4: New Question ───────────────────────────────────────────────────

def section_lifecycle(s):
    out = [
        section_header("4.  New Question — Target Organisation Lifecycle Stage", s),
        Spacer(1, 8),
    ]

    out += [
        Paragraph("Source", s["h3"]),
        Paragraph(
            "Jean Onyango — written into the 'Roles / sectors explicitly ruled out' field "
            "in Section 3.",
            s["body"]),

        Paragraph("What was suggested", s["h3"]),
    ]

    out.append(callout(
        "Jean's exact words (in the ruled-out field):",
        "\"Also ask a question around the life cycle stage of the target organization: "
        "Start-up, mid-[stage]...\"",
        s))
    out.append(Spacer(1, 8))

    out += [
        Paragraph("Why this matters", s["h3"]),
        Paragraph(
            "An applicant targeting a seed-stage startup needs a very different plan "
            "(equity literacy, tolerance for ambiguity, generalist skills) than one targeting "
            "a mature multilateral (compliance expertise, formal procurement, hierarchy "
            "navigation). Knowing the preferred lifecycle stage lets the plan tailor "
            "organisation targets in Section 2 and the skills gap analysis in Section 3 "
            "of the deliverable more precisely.",
            s["body"]),

        Paragraph("Proposed addition", s["h3"]),
        Paragraph(
            "Add a new multi-select field to Section 3 (Target Role Clarity), positioned "
            "after 'Preferred organisation types':",
            s["body"]),
    ]

    options = [
        ("Preferred organisation stage (select all that apply)",
         "Early-stage startup (seed / Series A)\n"
         "Growth-stage startup (Series B+)\n"
         "Established / mid-size organisation\n"
         "Large / mature organisation (1000+ staff)\n"
         "No preference"),
    ]
    q_rows = [
        [Paragraph("Proposed field label", s["th"]), Paragraph("Options", s["th"])],
        [Paragraph(options[0][0], s["cell_bold"]),
         Paragraph(options[0][1].replace("\n", "<br/>"), s["cell"])],
    ]
    col_w = [INNER_W * 0.4, INNER_W * 0.6]
    t = Table(q_rows, colWidths=col_w)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  NAVY),
        ("BACKGROUND",    (0, 1), (-1, -1), LGRAY),
        ("GRID",          (0, 0), (-1, -1), 0.4, MGRAY),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))
    out += [t, Spacer(1, 8)]

    out.append(callout(
        "Priority: MEDIUM",
        "Adds genuine value to the plan output and was requested by a tester organically. "
        "No form logic changes needed — it is a standalone multi-select.",
        s, bg=colors.HexColor("#FFF8EE"), border=AMBER))
    out.append(Spacer(1, 4))
    out.append(rule(MGRAY, 0.5))
    return out


# ── Section 5: Section Title ──────────────────────────────────────────────────

def section_title_clarity(s):
    out = [
        section_header("5.  Section Title Clarity — 'Deliverable Preferences'", s),
        Spacer(1, 8),
    ]

    out += [
        Paragraph("Source", s["h3"]),
        Paragraph("Jean Onyango — written into the 'Sections to emphasise' field.", s["body"]),
    ]

    out.append(callout(
        "Jean's exact words:",
        "\"This section on Deliverable Preferences is not clear to me, when I look at the "
        "title and the questions. Maybe re-word the title?\"",
        s))
    out.append(Spacer(1, 8))

    out += [
        Paragraph("Why the current title fails", s["h3"]),
        Paragraph(
            "The word 'deliverable' is consultant jargon that the client has not been "
            "introduced to at this point in the form. The questions in the section — "
            "who will see the plan, what to emphasise, background notes — are actually "
            "about how the plan should be framed and personalised, which is a more "
            "intuitive framing.",
            s["body"]),

        Paragraph("Recommended rename", s["h3"]),
    ]

    rename_rows = [
        [Paragraph("Current title", s["th"]), Paragraph("Proposed title", s["th"]),
         Paragraph("Rationale", s["th"])],
        [Paragraph("9  Deliverable Preferences", s["cell"]),
         Paragraph("9  About Your Plan", s["cell_bold"]),
         Paragraph(
             "Plain language; directly describes the questions that follow "
             "(who sees it, what to highlight, what to handle with care).",
             s["cell"])],
    ]
    col_w = [INNER_W * 0.28, INNER_W * 0.28, INNER_W * 0.44]
    t = Table(rename_rows, colWidths=col_w)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  NAVY),
        ("BACKGROUND",    (0, 1), (-1, -1), LGRAY),
        ("GRID",          (0, 0), (-1, -1), 0.4, MGRAY),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))
    out += [t, Spacer(1, 8)]

    out.append(callout(
        "Priority: LOW",
        "One-word change to index.html with no backend or logic impact. "
        "Worth doing alongside the other UX fixes.",
        s, bg=colors.HexColor("#F0FBF4"), border=GREEN))
    out.append(Spacer(1, 4))
    out.append(rule(MGRAY, 0.5))
    return out


# ── Section 6: Scope & Audience ───────────────────────────────────────────────

def section_scope(s):
    out = [
        section_header("6.  Scope & Audience — Form Appears Corporate-Only", s),
        Spacer(1, 8),
    ]

    out += [
        Paragraph("Source", s["h3"]),
        Paragraph("Aida — written feedback summary.", s["body"]),
    ]

    out.append(callout(
        "Aida's exact words:",
        "\"So at first I thought it was only for those who are, who've been or who wish to "
        "join the job market but I can see you've included startup somewhere there as well "
        "so making it also open to those who are entrepreneurs or willing to get into that… "
        "Make sure to let those who wish to fill it know that it captures both those in the "
        "job market and those out of it. Because at first glance it looks like its only for "
        "the corporate world. For those who are in business and maybe wish to venture into a "
        "different one or expand, maybe keep the CV option open. Is that doable?\"",
        s))
    out.append(Spacer(1, 8))

    out += [
        Paragraph("Why this matters", s["h3"]),
        Paragraph(
            "The form's subtitle, framing copy, and section labels all use language that "
            "implies a job-seeker model (CV upload, 'target job description', 'employed / "
            "made redundant'). An entrepreneur considering a pivot into a new sector, or "
            "expanding into an adjacent business domain, would feel the form is not for them "
            "and may disengage. Yet the plan output is equally applicable to business pivots.",
            s["body"]),

        Paragraph("Recommended changes", s["h3"]),
    ]

    changes = [
        ["Where", "Current", "Proposed change"],
        ["Form subtitle",
         "\"Complete all sections below. Your responses will be compiled and emailed to your "
         "consultant.\"",
         "Add a one-line scope note: \"This form is for career changers, sector pivots, and "
         "entrepreneurs exploring a new domain.\""],
        ["CV upload label",
         "\"CV / Résumé (PDF recommended) *\" (marked required)",
         "Make optional and rename: \"CV / Résumé or company profile (optional for "
         "entrepreneurs)\" — with a helper note explaining the alternatives."],
        ["Section 3 org types",
         "List ends at 'Startup'",
         "No change needed — startup is already there. The issue is upstream framing, "
         "not the option list."],
        ["Target domain field",
         "No helper text",
         "Add placeholder hint: e.g. 'Fintech, Climate-focused NGOs, EdTech startup, "
         "Agribusiness pivot…' — signals that business pivots are valid entries."],
    ]
    col_w = [INNER_W * 0.2, INNER_W * 0.35, INNER_W * 0.45]
    rows = [[Paragraph(c, s["th"] if i == 0 else (s["cell_bold"] if j == 0 else s["cell"]))
             for j, c in enumerate(row)]
            for i, row in enumerate(changes)]
    t = Table(rows, colWidths=col_w)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  NAVY),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, LGRAY]),
        ("GRID",          (0, 0), (-1, -1), 0.4, MGRAY),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))
    out += [t, Spacer(1, 8)]

    out.append(callout(
        "Priority: MEDIUM",
        "Affects the perceived target audience before a user even starts filling in the form. "
        "Copy changes only — no backend or logic impact.",
        s, bg=colors.HexColor("#FFF8EE"), border=AMBER))
    out.append(Spacer(1, 4))
    out.append(rule(MGRAY, 0.5))
    return out


# ── Section 7: Error Display ──────────────────────────────────────────────────

def section_error_display(s):
    out = [
        section_header("7.  Error Display — Raw HTML Shown to User on Submit Failure", s),
        Spacer(1, 8),
    ]

    out += [
        Paragraph("Source", s["h3"]),
        Paragraph("Jean's printed PDF — the final page shows the error message exactly as displayed.", s["body"]),

        Paragraph("What the user saw", s["h3"]),
        Paragraph(
            "When submission failed due to the CSRF issue, the form displayed the raw Flask "
            "HTTP error response directly inside the form's error box:",
            s["body"]),
    ]

    out.append(callout(
        "Displayed verbatim to the user:",
        "Error: &lt;!doctype html&gt; &lt;html lang=en&gt; &lt;title&gt;400 Bad "
        "Request&lt;/title&gt; &lt;h1&gt;Bad Request&lt;/h1&gt; &lt;p&gt;The CSRF session "
        "token is missing.&lt;/p&gt;",
        s, bg=colors.HexColor("#FEF0F0"), border=RED))
    out.append(Spacer(1, 8))

    out += [
        Paragraph("Fix", s["h3"]),
        Paragraph(
            "In <b>static/form.js</b>, the fetch error handler displays the raw server "
            "response text. It should instead check the HTTP status code and show a "
            "human-readable message. For a 400/403 CSRF error specifically, the message "
            "should instruct the user to refresh and try again:",
            s["body"]),
        Paragraph(
            "Suggested user-facing message for a 400 response: "
            "<i>\"Your session has expired. Please refresh the page and resubmit — "
            "your answers will still be visible.\"</i>",
            s["note"]),
        Paragraph(
            "The fix lives entirely in <b>static/form.js</b> — no backend changes needed. "
            "The fetch response handler should branch on <i>response.ok</i> and "
            "<i>response.status</i> rather than passing raw text to the DOM.",
            s["body"]),
    ]

    out.append(callout(
        "Priority: HIGH",
        "Technical error messages surfaced to end users are a UX failure and can cause "
        "distrust. This fix also makes session-expiry recoverable — users are told to "
        "refresh rather than abandoning.",
        s, bg=colors.HexColor("#FFF8EE"), border=AMBER))
    out.append(Spacer(1, 4))
    out.append(rule(MGRAY, 0.5))
    return out


# ── Section 8: Summary Table ──────────────────────────────────────────────────

def section_summary(s):
    out = [
        PageBreak(),
        section_header("8.  Summary Change Table", s),
        Spacer(1, 8),
        Paragraph(
            "All findings from Round 1, ordered by priority. Each item includes the source "
            "tester, the affected component, and the recommended action.",
            s["body"]),
        Spacer(1, 6),
    ]

    header = ["#", "Finding", "Source", "Component", "Action", "Priority"]
    rows = [
        ["1",
         "SECRET_KEY not set on Render — CSRF tokens invalidated on every restart",
         "Jean", "Render env / app.py",
         "Set SECRET_KEY in Render dashboard; redeploy",
         "CRITICAL"],
        ["2",
         "'What attracts you to target domain?' precedes the target domain question",
         "Jean", "index.html — Section 2 & 3",
         "Move question to Section 3, after 'Target domain / field'",
         "HIGH"],
        ["3",
         "Raw HTML error shown on submit failure",
         "Jean", "static/form.js",
         "Parse HTTP status; show user-friendly session-expiry message",
         "HIGH"],
        ["4",
         "No question about preferred org lifecycle stage",
         "Jean", "index.html — Section 3",
         "Add multi-select: Early startup / Growth startup / Established / Large / No preference",
         "MEDIUM"],
        ["5",
         "Form appears corporate/job-market only — entrepreneurs feel excluded",
         "Aida", "index.html — framing copy",
         "Add scope note to subtitle; make CV optional for entrepreneurs; add domain field hints",
         "MEDIUM"],
        ["6",
         "Section 9 title 'Deliverable Preferences' is unclear",
         "Jean", "index.html — Section 9 header",
         "Rename to 'About Your Plan'",
         "LOW"],
    ]

    priority_styles = {
        "CRITICAL": s["critical"],
        "HIGH":     s["high"],
        "LOW":      s["low"],
        "MEDIUM":   ParagraphStyle("med", fontName="Helvetica-Bold", fontSize=9,
                                   textColor=AMBER, leading=12),
    }

    def cell(text, style=None):
        return Paragraph(text, style or s["cell"])

    table_rows = [[Paragraph(h, s["th"]) for h in header]]
    for row in rows:
        pri = row[5]
        table_rows.append([
            cell(row[0]),
            cell(row[1]),
            cell(row[2]),
            cell(row[3]),
            cell(row[4]),
            Paragraph(pri, priority_styles.get(pri, s["cell"])),
        ])

    col_w = [0.5*cm, INNER_W*0.27, 1.0*cm, INNER_W*0.18, INNER_W*0.28, 1.5*cm]
    t = Table(table_rows, colWidths=col_w)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  NAVY),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, LGRAY]),
        ("GRID",          (0, 0), (-1, -1), 0.4, MGRAY),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))
    out += [t, Spacer(1, 12)]

    out += [
        Paragraph("Also noted (positive)", s["h3"]),
        Paragraph(
            "Jean specifically called out that answer-pointer hints beside each question "
            "(the helper text explaining why the question is asked) were useful: "
            "<i>\"I like that pointers to answers are given. It helps the respondent keep "
            "on the right track and give relevant answers.\"</i> "
            "Retain this pattern in all future form iterations.",
            s["body"]),
    ]

    out.append(Spacer(1, 4))
    out.append(rule(MGRAY, 0.5))
    return out


# ── Build ─────────────────────────────────────────────────────────────────────

def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MGRAY)
    canvas.drawCentredString(W / 2, 0.8 * cm,
                             f"Career Transition Intake Form — Round 1 Feedback Report  |  Page {doc.page}")
    canvas.restoreState()


def build():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=1.8 * cm,
    )
    s = styles()
    story = []
    story += cover(s)
    story += section_overview(s)
    story += section_csrf(s)
    story += section_flow(s)
    story += section_lifecycle(s)
    story += section_title_clarity(s)
    story += section_scope(s)
    story += section_error_display(s)
    story += section_summary(s)
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"Written → {OUTPUT_PATH}")


if __name__ == "__main__":
    build()
