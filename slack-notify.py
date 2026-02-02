#!/usr/bin/env python3
"""Post the current summit notification bar message to Slack."""

import json
import os
import re
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

ATHENS = ZoneInfo("Europe/Athens")

SCHEDULE = [
    # Pre-event
    {"start": "2026-01-01T00:00", "end": "2026-02-02T00:00", "text": "Athens Edition 2026 is coming!", "type": "info"},

    # Arrival Day - Feb 2
    {"start": "2026-02-02T00:00", "end": "2026-02-02T07:30", "text": "Arrival Day — 6 already in Athens, 23 more joining today!", "type": "info"},
    {"start": "2026-02-02T07:30", "end": "2026-02-02T12:00", "text": "Welcome to Athens, Jennifer! ☀️ — 22 more arriving today", "type": "live"},
    {"start": "2026-02-02T12:00", "end": "2026-02-02T13:00", "text": "Welcome Emilios, Andreas, Nikos, Rami, Pavlos & Vasilis! — 16 more to come", "type": "live"},
    {"start": "2026-02-02T13:00", "end": "2026-02-02T13:50", "text": "Welcome Emma! — 15 more arriving today", "type": "live"},
    {"start": "2026-02-02T13:50", "end": "2026-02-02T14:30", "text": "Welcome Deborah & Claire! — 13 more to come", "type": "live"},
    {"start": "2026-02-02T14:30", "end": "2026-02-02T17:15", "text": "Welcome Panagiotis! — Next group landing at 17:30", "type": "live"},
    {"start": "2026-02-02T17:15", "end": "2026-02-02T17:30", "text": "Welcome Aris, Evripides, Panagiotis & Anna! — 8 more to come", "type": "live"},
    {"start": "2026-02-02T17:30", "end": "2026-02-02T18:00", "text": "Welcome Walk through Athens — Meet at hotel reception", "time": "17:30", "type": "live"},
    {"start": "2026-02-02T18:00", "end": "2026-02-02T19:00", "text": "Welcome Drinks at Couleur Local Bar — Rooftop views of the Acropolis", "time": "From 18:00", "type": "live"},
    {"start": "2026-02-02T19:00", "end": "2026-02-02T20:00", "text": "Welcome Jonathan, Ben, Ellie, Sue, Joe, Naomi & Lara! 🎉", "type": "live"},
    {"start": "2026-02-02T20:00", "end": "2026-02-02T20:30", "text": "Welcome Demis! Everyone's here — see you at dinner 🇬🇷", "type": "live"},
    {"start": "2026-02-02T20:30", "end": "2026-02-02T23:59", "text": "Dinner at Kalamaki Bar — Traditional Greek taverna", "time": "From 20:30", "type": "live"},

    # Day 1 - Feb 3
    {"start": "2026-02-03T09:00", "end": "2026-02-03T09:30", "text": "Welcome to the Summit", "time": "09:00 – 09:30", "type": "live"},
    {"start": "2026-02-03T09:30", "end": "2026-02-03T10:30", "text": "Locum's Nest in Numbers", "time": "09:30 – 10:30", "type": "live"},
    {"start": "2026-02-03T10:30", "end": "2026-02-03T10:45", "text": "Break — Grab a coffee!", "time": "10:30 – 10:45", "type": "info"},
    {"start": "2026-02-03T10:45", "end": "2026-02-03T11:30", "text": "Product Direction and Growth Opportunities in 2026", "time": "10:45 – 11:30", "type": "live"},
    {"start": "2026-02-03T11:30", "end": "2026-02-03T13:30", "text": "Breakout Sessions — Track A: Platform Walkthrough | Track B: 2025 Releases | Track C: Data & Reporting", "time": "11:30 – 13:30", "type": "live"},
    {"start": "2026-02-03T13:30", "end": "2026-02-03T14:30", "text": "Lunch", "time": "13:30 – 14:30", "type": "info"},
    {"start": "2026-02-03T14:30", "end": "2026-02-03T16:30", "text": "Afternoon Breakouts — Track A: Ideation to Iteration | Track B: The Asset Challenge", "time": "14:30 – 16:30", "type": "live"},
    {"start": "2026-02-03T16:30", "end": "2026-02-03T17:30", "text": "Whole Company Debrief", "time": "16:30 – 17:30", "type": "live"},
    {"start": "2026-02-03T17:30", "end": "2026-02-03T20:00", "text": "Optional Acropolis Sunset Drinks or Coffee — Meet at hotel reception", "time": "17:30", "type": "info"},
    {"start": "2026-02-03T20:00", "end": "2026-02-03T22:00", "text": "Dinner at Onos Taverna — Sharing plates & Greek flavours", "time": "From 20:00", "type": "live"},
    {"start": "2026-02-03T22:00", "end": "2026-02-03T23:59", "text": "Optional After Dinner Drinks — 360, A for Athens, City Zen or Ciel", "time": "From 22:00", "type": "info"},

    # Day 2 - Feb 4
    {"start": "2026-02-04T00:00", "end": "2026-02-04T09:00", "text": "Day 2 starts at 09:00 — Good morning Athens!", "type": "upcoming"},
    {"start": "2026-02-04T09:00", "end": "2026-02-04T09:30", "text": "Welcome to Day 2", "time": "09:00 – 09:30", "type": "live"},
    {"start": "2026-02-04T09:30", "end": "2026-02-04T10:30", "text": "Product Discovery: Rates and Demand Control", "time": "09:30 – 10:30", "type": "live"},
    {"start": "2026-02-04T10:30", "end": "2026-02-04T13:00", "text": "Morning Breakouts — Track A: Rates & Demand Control | Track B: National Staff Bank Strategy", "time": "10:30 – 13:00", "type": "live"},
    {"start": "2026-02-04T13:00", "end": "2026-02-04T14:00", "text": "Lunch", "time": "13:00 – 14:00", "type": "info"},
    {"start": "2026-02-04T14:00", "end": "2026-02-04T17:00", "text": "Afternoon Sessions — Track A: Timesheet Self Service | Track B: National Staff Bank Strategy Pt 2", "time": "14:00 – 17:00", "type": "live"},
    {"start": "2026-02-04T17:00", "end": "2026-02-04T17:30", "text": "Whole Company Debrief", "time": "17:00 – 17:30", "type": "live"},
    {"start": "2026-02-04T17:30", "end": "2026-02-04T18:00", "text": "Free time — Freshen up before drinks", "type": "info"},
    {"start": "2026-02-04T18:00", "end": "2026-02-04T20:30", "text": "Pre-Dinner Drinks at Dóor — Creative cocktails in a refined setting", "time": "From 18:00", "type": "live"},
    {"start": "2026-02-04T20:30", "end": "2026-02-04T23:59", "text": "Dinner at To Paradosiako — Authentic neighbourhood taverna", "time": "From 20:30", "type": "live"},

    # Day 3 - Feb 5
    {"start": "2026-02-05T00:00", "end": "2026-02-05T10:00", "text": "Free morning — Optional Walking Tour at 10:00", "type": "upcoming"},
    {"start": "2026-02-05T10:00", "end": "2026-02-05T13:00", "text": "Optional Walking Tour of Athens", "time": "From 10:00", "type": "live"},
    {"start": "2026-02-05T13:00", "end": "2026-02-05T14:00", "text": "Free afternoon — Explore, museums, or relax", "type": "info"},
    {"start": "2026-02-05T14:00", "end": "2026-02-05T16:00", "text": "Exec Team Meeting", "time": "14:00 – 16:00", "type": "live"},
    {"start": "2026-02-05T16:00", "end": "2026-02-05T23:59", "text": "Free evening — Use your dinner allowance at a restaurant of your choice!", "type": "info"},

    # Day 4 - Feb 6
    {"start": "2026-02-06T00:00", "end": "2026-02-06T10:00", "text": "Free day — Explore Athens at your leisure", "type": "info"},
    {"start": "2026-02-06T10:00", "end": "2026-02-06T12:00", "text": "Exec Team Meeting", "time": "10:00 – 12:00", "type": "live"},
    {"start": "2026-02-06T12:00", "end": "2026-02-06T19:00", "text": "Free afternoon — Departures begin. Safe travels!", "type": "info"},
    {"start": "2026-02-06T19:00", "end": "2026-02-06T23:59", "text": "Free evening — Use your dinner allowance at a restaurant of your choice!", "type": "info"},

    # Post-event departures
    {"start": "2026-02-07T00:00", "end": "2026-02-10T23:59", "text": "Departures continue — Safe travels home!", "type": "info"},

    # Post-event
    {"start": "2026-02-11T00:00", "end": "2026-12-31T23:59", "text": "Thanks for an amazing Athens Edition 2026!", "type": "info"},
]

TYPE_INDICATORS = {
    "live": ("\U0001f7e2", "Now"),
    "upcoming": ("\U0001f7e1", "Next"),
    "info": ("\u2139\ufe0f", "Notice"),
}

STATE_FILE = ".last-notification"


def parse_dt(s):
    return datetime.fromisoformat(s).replace(tzinfo=ATHENS)


def find_active_event(now):
    for event in SCHEDULE:
        if parse_dt(event["start"]) <= now <= parse_dt(event["end"]):
            return event
    return None


def build_message(event):
    indicator, label = TYPE_INDICATORS.get(event["type"], ("\u2139\ufe0f", "Notice"))
    text = re.sub(r"<[^>]+>", "", event["text"])
    msg = f"{indicator} *{label}* — {text}"
    if event.get("time"):
        msg += f"  ·  {event['time']}"
    return msg


def main():
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook_url:
        print("SLACK_WEBHOOK_URL not set, exiting.")
        return

    now = datetime.now(ATHENS)
    print(f"Current time in Athens: {now.isoformat()}")

    event = find_active_event(now)
    if event is None:
        print("No active event right now.")
        return

    print(f"Active event: {event['text']} (starts {event['start']})")

    # Check if we already posted this event
    last_start = None
    try:
        with open(STATE_FILE) as f:
            last_start = f.read().strip()
    except FileNotFoundError:
        pass

    if last_start == event["start"]:
        print("Already posted this event, skipping.")
        return

    # Build and send message
    message = build_message(event)
    print(f"Posting: {message}")

    payload = json.dumps({"text": message}).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        print(f"Slack response: {resp.status} {resp.read().decode()}")

    # Save state
    with open(STATE_FILE, "w") as f:
        f.write(event["start"])
    print("State saved.")


if __name__ == "__main__":
    main()
