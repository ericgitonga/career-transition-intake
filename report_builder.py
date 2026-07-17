"""
Shared Career Transition Plan PDF engine.

One engine for every client: all ReportLab styling, layout helpers, and
per-SKILL.md-section rendering logic lives here. A client's own file
(Clients/<Name>/plan_data.py) holds only content — a PLAN dict — never
ReportLab code. See generate_plan.py for the CLI that ties the two together.

Two kinds of section in this document:
  - Fixed-shape sections (2, 3, 5, 8, 9, 11) have real layout logic of their
    own (priority-coloured cells, semester cards, a bold-first-column
    tracker) and get a dedicated render_section_N(data, story) function.
  - Freeform sections (1, 4, 6, 7, 10, 12) are a heading plus a mix of
    paragraphs, shaded boxes, two-column bullet lists, and tables — these
    are driven by a generic `blocks` list so no section-specific code is
    needed for them at all.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    HRFlowable, KeepTogether, Table, TableStyle,
)

# ── Palette ───────────────────────────────────────────────────────────────────
NAVY  = colors.HexColor("#1B2A4A")
TEAL  = colors.HexColor("#0E7C7B")
GOLD  = colors.HexColor("#C9A84C")
LGRAY = colors.HexColor("#F4F6F9")
MGRAY = colors.HexColor("#D0D6E0")
WHITE = colors.white
BLACK = colors.HexColor("#1A1A1A")
RED   = colors.HexColor("#C0392B")
AMBER = colors.HexColor("#D4860A")
GREEN = colors.HexColor("#1A7A4A")

BORDER_COLORS = {"gold": GOLD, "teal": TEAL}
PRIORITY_STYLES = {
    # priority key -> (badge background, badge text, badge foreground)
    "HIGH": (RED,   "HIGH", WHITE),
    "MED":  (AMBER, "MED",  WHITE),
    "LOW":  (GREEN, "LOW",  WHITE),
    "NONE": (LGRAY, "—",    BLACK),
}

W, H    = A4
MARGIN  = 1.27 * cm
INNER_W = W - 2 * MARGIN


# ── Paragraph styles ──────────────────────────────────────────────────────────
def S(name, **kw):
    return ParagraphStyle(name, **kw)


ST = {
    "cover_name":    S("cn",  fontName="Helvetica-Bold",    fontSize=28,
                       textColor=WHITE,  leading=36, alignment=TA_CENTER),
    "cover_sub":     S("cs",  fontName="Helvetica-Bold",    fontSize=14,
                       textColor=GOLD,   leading=20, alignment=TA_CENTER),
    "cover_tag":     S("ct",  fontName="Helvetica-Oblique", fontSize=11,
                       textColor=colors.HexColor("#B0C4D8"), leading=16, alignment=TA_CENTER),
    "cover_meta":    S("cm",  fontName="Helvetica",         fontSize=9,
                       textColor=colors.HexColor("#8899AA"), leading=13, alignment=TA_CENTER),
    "cover_conf":    S("cc",  fontName="Helvetica-Oblique", fontSize=8,
                       textColor=colors.HexColor("#667788"), leading=11, alignment=TA_CENTER),
    "tagline":       S("tl",  fontName="Helvetica",         fontSize=10,
                       textColor=BLACK,  leading=15, alignment=TA_JUSTIFY),
    "h2":            S("h2",  fontName="Helvetica-Bold",    fontSize=11,
                       textColor=TEAL,   leading=15, spaceBefore=10, spaceAfter=3),
    "h3":            S("h3",  fontName="Helvetica-Bold",    fontSize=10,
                       textColor=NAVY,   leading=13, spaceBefore=6, spaceAfter=2),
    "body":          S("bo",  fontName="Helvetica",         fontSize=9.5,
                       textColor=BLACK,  leading=14, spaceAfter=4, alignment=TA_JUSTIFY),
    "bullet":        S("bu",  fontName="Helvetica",         fontSize=9.5,
                       textColor=BLACK,  leading=14, spaceAfter=3, leftIndent=12),
    "cell":          S("ce",  fontName="Helvetica",         fontSize=8.5,
                       textColor=BLACK,  leading=12),
    "cell_b":        S("cb",  fontName="Helvetica-Bold",    fontSize=8.5,
                       textColor=BLACK,  leading=12),
    "th":            S("th",  fontName="Helvetica-Bold",    fontSize=8.5,
                       textColor=WHITE,  leading=12),
    "sem_title":     S("st",  fontName="Helvetica-Bold",    fontSize=11,
                       textColor=WHITE,  leading=15),
    "sem_dates":     S("sd",  fontName="Helvetica-Oblique", fontSize=9,
                       textColor=GOLD,   leading=12),
    "sem_label":     S("sl",  fontName="Helvetica-Bold",    fontSize=8.5,
                       textColor=TEAL,   leading=12),
    "sem_body":      S("sb",  fontName="Helvetica",         fontSize=9,
                       textColor=BLACK,  leading=13, alignment=TA_JUSTIFY),
    "tracker_focus": S("tf",  fontName="Helvetica-Bold",    fontSize=8,
                       textColor=NAVY,   leading=11),
    "tracker_item":  S("ti",  fontName="Helvetica",         fontSize=7.5,
                       textColor=BLACK,  leading=11),
    "pitch":         S("pi",  fontName="Helvetica-Oblique", fontSize=9.5,
                       textColor=BLACK,  leading=14, alignment=TA_JUSTIFY,
                       leftIndent=10, rightIndent=10),
    "pri_badge":     S("pc",  fontName="Helvetica-Bold",    fontSize=8,
                       leading=11),
}


# ── Generic layout helpers ────────────────────────────────────────────────────
def rule(color=GOLD, thick=0.75, before=5, after=7):
    return HRFlowable(width="100%", thickness=thick, color=color,
                       spaceBefore=before, spaceAfter=after)


def section_header(text):
    p = Paragraph(text, ParagraphStyle(
        "sh", fontName="Helvetica-Bold", fontSize=11,
        textColor=WHITE, leading=14))
    t = Table([[p]], colWidths=[INNER_W])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), NAVY),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))
    return t


def shaded_box(paragraphs, bg=LGRAY, border=TEAL):
    t = Table([[paragraphs]], colWidths=[INNER_W - 4])
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


def two_col(left_items, right_items):
    col = (INNER_W - 6) / 2
    left_cells  = [[Paragraph(f"• {x}", ST["bullet"])] for x in left_items]
    right_cells = [[Paragraph(f"• {x}", ST["bullet"])] for x in right_items]
    max_rows = max(len(left_cells), len(right_cells))
    while len(left_cells)  < max_rows: left_cells.append([""])
    while len(right_cells) < max_rows: right_cells.append([""])
    data = [[Table(left_cells, colWidths=[col]), Table(right_cells, colWidths=[col])]]
    t = Table(data, colWidths=[col + 3, col + 3])
    t.setStyle(TableStyle([
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))
    return t


def data_table(headers, rows, col_ratios=None):
    """Styled data table. rows is a list of lists of strings or Flowables.
    col_ratios (fractions of INNER_W, need not sum to 1) defaults to even columns."""
    if col_ratios is None:
        col_ratios = [1 / len(headers)] * len(headers)
    col_widths = [INNER_W * r for r in col_ratios]
    h_row = [Paragraph(h, ST["th"]) for h in headers]
    data = [h_row]
    for row in rows:
        data.append([
            Paragraph(c, ST["cell"]) if isinstance(c, str) else c
            for c in row
        ])
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0), (-1, 0),  NAVY),
        ("TOPPADDING",     (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 4),
        ("LEFTPADDING",    (0, 0), (-1, -1), 5),
        ("RIGHTPADDING",   (0, 0), (-1, -1), 5),
        ("VALIGN",         (0, 0), (-1, -1), "TOP"),
        ("GRID",           (0, 0), (-1, -1), 0.4, MGRAY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LGRAY]),
    ]))
    return t


def pri_cell(priority, width=None):
    """Colour-coded priority badge used by the skills-gap table. priority is
    one of the PRIORITY_STYLES keys (HIGH/MED/LOW/NONE)."""
    bg, label, fg = PRIORITY_STYLES[priority]
    p = Paragraph(label, ParagraphStyle("pc", parent=ST["pri_badge"], textColor=fg))
    t = Table([[p]], colWidths=[width] if width else None)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), bg),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
    ]))
    return t


def semester_card(client_first_name, num, title, dates, objective, topics, deliverables, connects):
    hdr_p  = Paragraph(f"Semester {num} — {title}", ST["sem_title"])
    date_p = Paragraph(dates, ST["sem_dates"])
    header = Table([[hdr_p, date_p]], colWidths=[INNER_W * 0.70, INNER_W * 0.30])
    header.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), NAVY),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",         (1, 0), (1, 0),   "RIGHT"),
    ]))

    def label(txt):
        return Paragraph(txt, ST["sem_label"])

    def body(txt):
        return Paragraph(txt, ST["sem_body"])

    def bullets(items):
        return [Paragraph(f"• {i}", ST["sem_body"]) for i in items]

    content = [
        header,
        Spacer(1, 5),
        label("Objective"),
        body(objective),
        Spacer(1, 4),
        label("Core Topics  (books & self-study / in-person workshops)"),
        *bullets(topics),
        Spacer(1, 4),
        label("Deliverables / Milestones"),
        *bullets(deliverables),
        Spacer(1, 4),
        label(f"Connects to {client_first_name}'s Background"),
        body(connects),
        Spacer(1, 4),
        rule(color=MGRAY, thick=0.5, before=2, after=2),
    ]
    return KeepTogether(content)


def footer_canvas_factory(doc_title):
    def footer_canvas(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(colors.HexColor("#888888"))
        canvas.drawCentredString(W / 2, 0.65 * cm, f"{doc_title}  ·  Page {doc.page}")
        canvas.restoreState()
    return footer_canvas


# ── Generic freeform-section content renderer ─────────────────────────────────
def render_blocks(blocks, story):
    """Render a list of content blocks for a freeform section (1, 4, 6, 7, 10, 12).

    Each block is a dict with an optional "heading" (rendered in ST['h2']) and
    exactly one content key:
      - "paragraph": str, rendered in ST['body']
      - "shaded_box": {"paragraphs": [...], "border": "gold"|"teal" (default teal)}
        where each item in "paragraphs" is either a plain string (ST['body'])
        or a {"text": str, "style": "body"|"h3"|"pitch" (default body),
        "space_after": int (optional gap before the next paragraph in the box)}
      - "two_col": {"left": [...], "right": [...]}
      - "table": {"headers": [...], "rows": [[...]], "col_ratios": [...] (optional)}
    "space_after" at the block level overrides the default 8pt spacer appended
    after the whole block.
    """
    for block in blocks:
        if "heading" in block:
            story.append(Paragraph(block["heading"], ST["h2"]))

        if "paragraph" in block:
            story.append(Paragraph(block["paragraph"], ST["body"]))
        elif "shaded_box" in block:
            sb = block["shaded_box"]
            content = []
            for p in sb["paragraphs"]:
                if isinstance(p, str):
                    p = {"text": p}
                content.append(Paragraph(p["text"], ST[p.get("style", "body")]))
                if p.get("space_after"):
                    content.append(Spacer(1, p["space_after"]))
            story.append(shaded_box(content, border=BORDER_COLORS.get(sb.get("border", "teal"), TEAL)))
        elif "two_col" in block:
            tc = block["two_col"]
            story.append(two_col(tc["left"], tc["right"]))
        elif "table" in block:
            tb = block["table"]
            story.append(data_table(tb["headers"], tb["rows"], tb.get("col_ratios")))

        story.append(Spacer(1, block.get("space_after", 8)))


# ── Cover page & opening tagline ───────────────────────────────────────────────
def render_cover(client, story):
    cover = Table(
        [
            [Paragraph(client["name"], ST["cover_name"])],
            [Spacer(1, 8)],
            [Paragraph("Career Transition Plan", ST["cover_sub"])],
            [Spacer(1, 6)],
            [Paragraph(f"From {client['from_domain']}  →  {client['to_domain']}", ST["cover_tag"])],
            [Spacer(1, 20)],
            [Paragraph(f"{client['location']}  ·  {client['date']}", ST["cover_meta"])],
            [Spacer(1, 10)],
            [Paragraph(client["confidentiality"], ST["cover_conf"])],
        ],
        colWidths=[INNER_W],
    )
    cover.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), NAVY),
        ("TOPPADDING",    (0, 0), (0, 0),   60),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 60),
        ("LEFTPADDING",   (0, 0), (-1, -1), 20),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 20),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(cover)
    story.append(PageBreak())


def render_opening_tagline(text, story):
    story.append(shaded_box([Paragraph(text, ST["tagline"])], border=GOLD))
    story.append(Spacer(1, 12))


# ── Section 2 — Where You Are Heading ─────────────────────────────────────────
def render_section_2(data, first_name, story):
    s2 = data["section_2"]
    story.append(section_header("Section 2 — Where You Are Heading"))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Target Role Archetype", ST["h2"]))
    story.append(data_table(
        ["Role Archetype", "Sector", f"Why {first_name} Fits"],
        [[a["role"], a["sector"], a["fit"]] for a in s2["archetypes"]],
        col_ratios=[0.32, 0.22, 0.46],
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph(s2["orgs_heading"], ST["h2"]))
    story.append(two_col(s2["orgs_left"], s2["orgs_right"]))
    story.append(Spacer(1, 12))
    story.append(PageBreak())


# ── Section 3 — Skills Gap Analysis ───────────────────────────────────────────
def render_section_3(data, story):
    rows = data["section_3"]["skills_gap"]
    story.append(section_header("Section 3 — Skills Gap Analysis"))
    story.append(Spacer(1, 6))

    col_ratios = [0.30, 0.10, 0.10, 0.10, 0.18, 0.22]
    table_rows = [
        [r["area"], r["current"], r["required"], r["gap"], r["when"], pri_cell(r["priority"])]
        for r in rows
    ]
    story.append(data_table(
        ["Skill / Knowledge Area", "Current", "Required", "Gap", "When to Close", "Priority"],
        table_rows, col_ratios,
    ))
    story.append(Spacer(1, 12))
    story.append(PageBreak())


# ── Section 5 — Detailed Semester Plans ───────────────────────────────────────
def render_section_5(data, first_name, story):
    story.append(section_header("Section 5 — Detailed Semester Plans"))
    story.append(Spacer(1, 8))
    for sem in data["semesters"]:
        story.append(semester_card(
            first_name, sem["num"], sem["title"], sem["dates"], sem["objective"],
            sem["topics"], sem["deliverables"], sem["connects"],
        ))
    story.append(Spacer(1, 6))
    story.append(PageBreak())


# ── Section 8 — Portfolio Building ────────────────────────────────────────────
def render_section_8(data, story):
    s8 = data["section_8"]
    story.append(section_header("Section 8 — Portfolio Building"))
    story.append(Spacer(1, 6))
    story.append(data_table(
        ["#", "Portfolio Piece", "Created In", "What It Demonstrates"],
        [[str(i + 1), p["piece"], p["created_in"], p["demonstrates"]]
         for i, p in enumerate(s8["pieces"])],
        col_ratios=[0.05, 0.32, 0.13, 0.50],
    ))
    story.append(Spacer(1, 6))
    story.append(shaded_box([Paragraph(s8["tip"], ST["body"])]))
    story.append(Spacer(1, 12))
    story.append(PageBreak())


# ── Section 9 — Monthly Action Tracker ────────────────────────────────────────
def render_section_9(data, story):
    rows = data["section_9"]["tracker"]
    story.append(section_header("Section 9 — Monthly Action Tracker"))
    story.append(Spacer(1, 6))

    def tc(text):
        return Paragraph(text, ST["tracker_item"])

    def tb(text):
        return Paragraph(f"<b>{text}</b>", ST["tracker_focus"])

    table_rows = [
        [tb(r["month"]), tc(r["learning"]), tc(r["networking"]), tc(r["portfolio"])]
        for r in rows
    ]
    story.append(data_table(
        ["Month", "Learning Focus", "Networking Action", "Portfolio / Visibility"],
        table_rows, col_ratios=[0.09, 0.30, 0.30, 0.31],
    ))
    story.append(Spacer(1, 12))
    story.append(PageBreak())


# ── Section 10 — Positioning & Narrative ──────────────────────────────────────
def render_section_10(data, story):
    s10 = data["section_10"]
    story.append(section_header("Section 10 — Positioning & Narrative"))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Elevator Pitch  (spoken aloud: ~60 seconds)", ST["h2"]))
    story.append(shaded_box([Paragraph(s10["pitch"], ST["pitch"])], border=GOLD))
    story.append(Spacer(1, 10))

    story.append(Paragraph(s10["reframe_heading"], ST["h2"]))
    story.append(data_table(
        ["Current CV Language", s10["reframe_col_2_heading"]],
        [[r["old"], r["new"]] for r in s10["reframing"]],
        col_ratios=[0.36, 0.64],
    ))
    story.append(Spacer(1, 12))
    story.append(PageBreak())


# ── Section 11 — Success Metrics ──────────────────────────────────────────────
def render_section_11(data, story):
    rows = data["section_11"]["metrics"]
    story.append(section_header("Section 11 — Success Metrics"))
    story.append(Spacer(1, 6))
    story.append(data_table(
        ["Milestone", "Target Date", "Status"],
        [[m["milestone"], m["target_date"], ""] for m in rows],
        col_ratios=[0.55, 0.20, 0.25],
    ))
    story.append(Spacer(1, 12))
    story.append(PageBreak())


# ── Build ──────────────────────────────────────────────────────────────────────
def build_plan(data, output_path):
    client = data["client"]
    first_name = client["name"].split()[0]
    doc_title = f"{client['initials']} Career Transition Plan"

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=1.2 * cm,
        title=doc_title,
    )
    story = []

    render_cover(client, story)
    render_opening_tagline(data["opening_tagline"], story)

    story.append(section_header("Section 1 — Your Starting Point"))
    story.append(Spacer(1, 6))
    render_blocks(data["section_1"]["blocks"], story)

    render_section_2(data, first_name, story)
    render_section_3(data, story)

    story.append(section_header("Section 4 — The Transition Roadmap (Overview)"))
    story.append(Spacer(1, 6))
    render_blocks(data["section_4"]["blocks"], story)
    story.append(PageBreak())

    render_section_5(data, first_name, story)

    story.append(section_header("Section 6 — Certifications Roadmap"))
    story.append(Spacer(1, 6))
    render_blocks(data["section_6"]["blocks"], story)
    story.append(PageBreak())

    story.append(section_header("Section 7 — Networking & Visibility Strategy"))
    story.append(Spacer(1, 6))
    render_blocks(data["section_7"]["blocks"], story)
    story.append(PageBreak())

    render_section_8(data, story)
    render_section_9(data, story)
    render_section_10(data, story)
    render_section_11(data, story)

    story.append(section_header("Section 12 — A Final Word"))
    story.append(Spacer(1, 8))
    render_blocks(data["section_12"]["blocks"], story)

    doc.build(story, onFirstPage=footer_canvas_factory(doc_title), onLaterPages=footer_canvas_factory(doc_title))
    print(f"Saved -> {output_path}")
