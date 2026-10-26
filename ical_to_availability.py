#!/usr/bin/env python3
"""Turns the calendar exported from the Booking.com extranet (iCal / .ics) into src/availability.json.

usage: ical_to_availability.py FILE.ics [--out src/availability.json] [--months 16] [--generated 2026-10-07T20:00:00Z] [--closed-from 2027-02-01]

Only the booked / closed nights are kept, as [first night, check-out day) pairs of ISO dates, merged and
clipped to the next N months. Guest details (summaries, descriptions, UIDs) are never copied.
The export link itself is secret: this script reads a file and never stores or prints a URL.

--closed-from DATE: Booking.com's iCal only lists nights it has explicitly closed or booked. Nights it has never put on
sale (no rates or availability opened) are missing from it, yet the public page cannot sell them either. When the public
page shows nothing for sale from some day on, pass that day here: every night from DATE on is then shown as unavailable.
"""
import argparse
import datetime as dt
import json
import pathlib
import re
import sys

try:
    from zoneinfo import ZoneInfo
    LOCAL = ZoneInfo("Europe/Madrid")
except Exception:  # pragma: no cover
    LOCAL = None

ROOT = pathlib.Path(__file__).resolve().parent.parent


def unfold(text):
    out = []
    for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if line[:1] in (" ", "\t") and out:
            out[-1] += line[1:]
        else:
            out.append(line)
    return out


def parse_value(name_params, value):
    """Returns a date (all-day) or a date after converting a timestamp to Madrid time."""
    params = name_params.upper()
    v = value.strip()
    if "VALUE=DATE" in params and "T" not in v.upper() or re.fullmatch(r"\d{8}", v):
        return dt.datetime.strptime(v[:8], "%Y%m%d").date(), True
    m = re.fullmatch(r"(\d{8}T\d{6})(Z?)", v)
    if not m:
        raise ValueError("unsupported date value: %r" % v)
    t = dt.datetime.strptime(m.group(1), "%Y%m%dT%H%M%S")
    if m.group(2) == "Z" and LOCAL is not None:
        t = t.replace(tzinfo=dt.timezone.utc).astimezone(LOCAL)
    return t.date(), False


def events(lines):
    cur = None
    for line in lines:
        if line == "BEGIN:VEVENT":
            cur = {}
        elif line == "END:VEVENT":
            if cur is not None:
                yield cur
            cur = None
        elif cur is not None and ":" in line:
            head, value = line.split(":", 1)
            name = head.split(";", 1)[0].upper()
            if name in ("DTSTART", "DTEND", "STATUS", "RRULE"):
                cur[name] = (head, value)


def build(ics_text, today, months):
    ranges, skipped = [], 0
    for ev in events(unfold(ics_text)):
        if "DTSTART" not in ev:
            skipped += 1
            continue
        if "STATUS" in ev and ev["STATUS"][1].strip().upper() == "CANCELLED":
            skipped += 1
            continue
        if "RRULE" in ev:
            print("warning: recurring event ignored (not expected in a Booking.com export)", file=sys.stderr)
            skipped += 1
            continue
        start, _ = parse_value(*ev["DTSTART"])
        if "DTEND" in ev:
            end, _ = parse_value(*ev["DTEND"])
        else:
            end = start + dt.timedelta(days=1)
        if end <= start:
            end = start + dt.timedelta(days=1)
        ranges.append((start, end))

    horizon = (today.replace(day=1) + dt.timedelta(days=32 * months)).replace(day=1)
    clipped = []
    for a, b in ranges:
        a = max(a, today)
        b = min(b, horizon)
        if a < b:
            clipped.append((a, b))
    clipped.sort()
    merged = []
    for a, b in clipped:
        if merged and a <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], b))
        else:
            merged.append((a, b))
    return merged, len(ranges), skipped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ics")
    ap.add_argument("--out", default=str(ROOT / "src" / "availability.json"))
    ap.add_argument("--months", type=int, default=16)
    ap.add_argument("--generated", default=None)
    ap.add_argument("--today", default=None, help="override today's date (tests)")
    ap.add_argument("--closed-from", default=None, help="first day Booking.com has nothing on sale (YYYY-MM-DD)")
    args = ap.parse_args()

    text = sys.stdin.read() if args.ics == "-" else pathlib.Path(args.ics).read_text(encoding="utf-8", errors="replace")
    if "BEGIN:VCALENDAR" not in text:
        raise SystemExit("that file is not an iCal calendar (no BEGIN:VCALENDAR)")
    today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()
    merged, total, skipped = build(text, today, args.months)
    generated = args.generated or dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    data = {"generated": generated, "source": "booking-ical", "busy": [[a.isoformat(), b.isoformat()] for a, b in merged]}
    if args.closed_from:
        dt.date.fromisoformat(args.closed_from)  # validates the format
        data["closedFrom"] = args.closed_from
    pathlib.Path(args.out).write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    nights = sum((b - a).days for a, b in merged)
    print("events read: %d (skipped %d) -> %d blocks, %d booked nights" % (total, skipped, len(merged), nights))
    if merged:
        print("first block %s -> %s, last block %s -> %s" % (merged[0][0], merged[0][1], merged[-1][0], merged[-1][1]))


if __name__ == "__main__":
    main()
