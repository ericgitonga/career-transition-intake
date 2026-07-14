"""
Pull submission logs from Render and populate extras/onboard_metrics.xlsx (Sheet: intake).

Setup:
    pip install requests openpyxl
    export RENDER_API_KEY=rnd_...            # Render dashboard → Account → API Keys
    export RENDER_SERVICE_ID=srv_...         # optional — taken from Render dashboard URL
                                             # if omitted, script searches by service name

Usage:
    python extras/pull_render_logs.py              # last 30 days
    python extras/pull_render_logs.py --days 7     # last 7 days
    python extras/pull_render_logs.py --since 2026-07-01   # from a specific date
"""

import argparse
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("Missing dependency — run: pip install requests openpyxl")

try:
    import openpyxl
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
except ImportError:
    sys.exit("Missing dependency — run: pip install requests openpyxl")

XLSX        = Path(__file__).parent / "onboard_metrics.xlsx"
API_BASE    = "https://api.render.com/v1"
INTAKE_SHEET    = "intake"
PROCESSED_SHEET = "processed"

HEADER_FILL = PatternFill("solid", fgColor="1B2A4A")
HEADER_FONT = Font(bold=True, color="FFFFFF")
ALT_FILL    = PatternFill("solid", fgColor="F4F6F9")

INTAKE_COLS = [
    "Submission Date",
    "Submission Time (UTC)",
    "Client Name",
    "Client Email",
    "Target Domain",
    "Uploads",
    "Time on Form (min)",
    "Server Processing (sec)",
    "Email Status",
    "Attachment",
]

PROCESSED_COLS = [
    "Client Name",
    "Processing Start",
    "Processing End",
    "Duration (min)",
    "Output File",
    "Notes",
]


# ── Render API helpers ────────────────────────────────────────────────────────

def _auth_headers():
    key = os.environ.get("RENDER_API_KEY", "").strip()
    if not key:
        sys.exit(
            "RENDER_API_KEY not set.\n"
            "Get one at: Render dashboard → Account Settings → API Keys\n"
            "Then: export RENDER_API_KEY=rnd_..."
        )
    return {"Authorization": f"Bearer {key}", "Accept": "application/json"}


def _find_service_id(headers):
    sid = os.environ.get("RENDER_SERVICE_ID", "").strip()
    if sid:
        return sid
    print("RENDER_SERVICE_ID not set — searching services for 'career-transition' …")
    r = requests.get(f"{API_BASE}/services?limit=100", headers=headers, timeout=15)
    r.raise_for_status()
    payload = r.json()
    # Render wraps each item: [{"service": {...}}, ...]  or returns flat list
    items = payload if isinstance(payload, list) else payload.get("services", [])
    for item in items:
        svc = item.get("service", item)
        name = svc.get("name", "") or svc.get("slug", "")
        if "career-transition" in name.lower():
            found_id = svc.get("id", "")
            print(f"  Found service: {name!r} → {found_id}")
            return found_id
    sys.exit(
        "Could not find a service matching 'career-transition'.\n"
        "Set RENDER_SERVICE_ID=srv_... (visible in Render dashboard URL) and retry."
    )


def _fetch_logs(service_id, since_dt, until_dt, headers):
    """Fetch log entries; tries both known Render log API shapes."""
    params = {
        "startTime": since_dt.isoformat(),
        "endTime":   until_dt.isoformat(),
        "limit":     1000,
    }
    # Shape 1: /v1/logs?resource[id]=...&resource[type]=service  (newer API)
    p1 = {**params, "resource[id]": service_id, "resource[type]": "service"}
    r = requests.get(f"{API_BASE}/logs", headers=headers, params=p1, timeout=30)
    if r.ok:
        data = r.json()
        entries = data.get("logs", data.get("items", data if isinstance(data, list) else []))
        if entries:
            return entries

    # Shape 2: /v1/services/{id}/logs  (older API)
    p2 = {**params, "serviceId": service_id}
    r = requests.get(f"{API_BASE}/services/{service_id}/logs", headers=headers, params=p2, timeout=30)
    r.raise_for_status()
    data = r.json()
    return data.get("logs", data.get("items", data if isinstance(data, list) else []))


# ── Log parsing ───────────────────────────────────────────────────────────────

RE_RECEIVED = re.compile(
    r"Submission received: "
    r"name=(?P<name>.+?) "
    r"email=(?P<email>\S+) "
    r"target=(?P<target>.+?) "
    r"uploads=(?P<uploads>\d+)"
    r"(?:\s+time_on_form=(?P<time_on_form>\d+))?"
)
RE_COMPLETE = re.compile(
    r"Submission complete: "
    r"name=(?P<name>.+?) "
    r"email_status=(?P<email_status>\S+) "
    r"attachment=(?P<attachment>\S+)"
)


def _parse_ts(entry):
    for key in ("timestamp", "time", "createdAt", "logged_at", "date"):
        raw = entry.get(key)
        if raw:
            try:
                return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
            except ValueError:
                pass
    return None


def _parse_entries(entries):
    received_list = []
    complete_list = []

    for e in entries:
        msg = e.get("message") or e.get("text") or e.get("log") or ""
        dt  = _parse_ts(e)

        m = RE_RECEIVED.search(msg)
        if m:
            d = m.groupdict()
            d["_dt"] = dt
            received_list.append(d)
            continue

        m = RE_COMPLETE.search(msg)
        if m:
            d = m.groupdict()
            d["_dt"] = dt
            complete_list.append(d)

    rows = []
    used = set()
    for recv in received_list:
        name    = recv["name"]
        dt_recv = recv["_dt"]
        proc_secs  = ""
        email_status = ""
        attachment   = ""

        for i, comp in enumerate(complete_list):
            if i in used:
                continue
            if comp["name"] != name:
                continue
            dt_comp = comp.get("_dt")
            if dt_recv and dt_comp and abs((dt_comp - dt_recv).total_seconds()) < 600:
                used.add(i)
                proc_secs    = round((dt_comp - dt_recv).total_seconds(), 1)
                email_status = comp.get("email_status", "")
                attachment   = comp.get("attachment", "")
                break

        tof_raw = recv.get("time_on_form")
        tof_min = round(int(tof_raw) / 60, 1) if tof_raw else ""

        rows.append({
            "Submission Date":       dt_recv.strftime("%Y-%m-%d") if dt_recv else "",
            "Submission Time (UTC)": dt_recv.strftime("%H:%M:%S") if dt_recv else "",
            "Client Name":           name,
            "Client Email":          recv.get("email", ""),
            "Target Domain":         recv.get("target", ""),
            "Uploads":               int(recv.get("uploads", 0)),
            "Time on Form (min)":    tof_min,
            "Server Processing (sec)": proc_secs,
            "Email Status":          email_status,
            "Attachment":            attachment,
        })
    return rows


# ── Excel helpers ─────────────────────────────────────────────────────────────

def _load_or_create():
    if XLSX.exists():
        return openpyxl.load_workbook(XLSX)
    wb = openpyxl.Workbook()
    if "Sheet" in wb.sheetnames:
        del wb["Sheet"]
    return wb


def _ensure_sheet(wb, name, cols):
    if name not in wb.sheetnames:
        ws = wb.create_sheet(name)
        for ci, col in enumerate(cols, 1):
            c = ws.cell(1, ci, col)
            c.font  = HEADER_FONT
            c.fill  = HEADER_FILL
            c.alignment = Alignment(horizontal="center", wrap_text=True)
        ws.freeze_panes = "A2"
        ws.row_dimensions[1].height = 30
    return wb[name]


def _existing_keys(ws):
    """Return set of (date, name) already in the sheet to avoid duplicate rows."""
    keys = set()
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0] and row[2]:
            keys.add((str(row[0]), str(row[2])))
    return keys


def _append_rows(ws, rows, cols, existing_keys):
    added = 0
    for row_data in rows:
        key = (row_data.get("Submission Date", ""), row_data.get("Client Name", ""))
        if key in existing_keys:
            print(f"  Skipping duplicate: {key[1]} on {key[0]}")
            continue
        r = ws.max_row + 1
        for ci, col in enumerate(cols, 1):
            c = ws.cell(r, ci, row_data.get(col, ""))
            if r % 2 == 0:
                c.fill = ALT_FILL
        existing_keys.add(key)
        added += 1
    return added


def _autofit(ws):
    for col in ws.columns:
        width = max((len(str(c.value or "")) for c in col), default=8)
        ws.column_dimensions[get_column_letter(col[0].column)].width = min(width + 4, 45)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Pull Render submission logs → onboard_metrics.xlsx")
    parser.add_argument("--days",  type=int, default=30, help="How many days back to fetch (default: 30)")
    parser.add_argument("--since", help="Fetch from this date, e.g. 2026-07-01 (overrides --days)")
    args = parser.parse_args()

    until = datetime.now(timezone.utc)
    since = (
        datetime.fromisoformat(args.since).replace(tzinfo=timezone.utc)
        if args.since
        else until - timedelta(days=args.days)
    )

    print(f"Fetching Render logs from {since.date()} to {until.date()} …")
    headers    = _auth_headers()
    service_id = _find_service_id(headers)
    entries    = _fetch_logs(service_id, since, until, headers)
    print(f"  {len(entries)} log line(s) retrieved")

    rows = _parse_entries(entries)
    print(f"  {len(rows)} submission event(s) parsed")

    wb = _load_or_create()
    ws_intake    = _ensure_sheet(wb, INTAKE_SHEET,    INTAKE_COLS)
    _ensure_sheet(wb, PROCESSED_SHEET, PROCESSED_COLS)

    existing = _existing_keys(ws_intake)
    added    = _append_rows(ws_intake, rows, INTAKE_COLS, existing)

    _autofit(ws_intake)
    _autofit(wb[PROCESSED_SHEET])
    wb.save(XLSX)
    print(f"  {added} new row(s) written → {XLSX}")


if __name__ == "__main__":
    main()
