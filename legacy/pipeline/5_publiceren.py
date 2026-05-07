#!/usr/bin/env python3
"""
5_publiceren.py — Briefing versturen via Telegram (OpenClaw channel)
"""

import subprocess
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent.parent
OUTPUT = BASE / "data" / "briefing_latest.md"

def send_telegram(message):
    """Verstuurt via OpenClaw message tool"""
    result = subprocess.run(
        ["openclaw", "message", "send", "--channel", "telegram", "--message", message],
        capture_output=True, text=True
    )
    return result.returncode == 0

def main():
    if not OUTPUT.exists():
        print("Geen briefing gevonden om te publiceren")
        return

    content = OUTPUT.read_text()
    date = datetime.utcnow().strftime("%d %b %Y")

    # Telegram-friendly versie (geen markdown tables)
    lines = content.split("\n")
    telegram_lines = []
    for line in lines:
        if line.startswith("|"):  # skip tabel-rijen
            continue
        telegram_lines.append(line)

    message = "\n".join(telegram_lines[:60])  # cap op 60 regels

    success = send_telegram(f"🧬 *Biotech Radar — {date}*\n\n{message}")
    if success:
        print("✅ Briefing verstuurd via Telegram")
    else:
        print("❌ Telegram versturen mislukt — check openclaw config")

if __name__ == "__main__":
    main()
