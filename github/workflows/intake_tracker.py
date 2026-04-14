#!/usr/bin/env python3
# intake_tracker.py
"""
Intake CTA Tracker — runs every Monday at 8 AM ET (activates Day 60+)
Pulls bio link click data from Later API.
Correlates with top-performing content to identify which posts drive conversions.
Emails weekly conversion report to Mia.
"""

import anthropic
import urllib.request
import json
from datetime import datetime, date, timedelta
from shared.config import (
    ANTHROPIC_API_KEY, MIA_EMAIL, LATER_API_KEY,
    get_plan_day, get_plan_phase, welmivia_cta_active
)
from shared.email_utils import (
    send_email, email_header, email_section,
    email_table, email_wrapper
)

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
TODAY     = date.today()
PLAN_DAY  = get_plan_day()


def get_later_analytics() -> dict:
    """Fetch bio link clicks from Later API."""
    if not LATER_API_KEY:
        return {}
    try:
        url = "https://api.later.com/v2/analytics/linkinbio"
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {LATER_API_KEY}",
                "Content-Type": "application/json"
            }
        )
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"⚠ Later API error: {e}")
        return {}


def analyze_conversion_data(later_data: dict, plan_day: int) -> str:
    msg = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": f"""
Dr. Mia Diaz runs Welmivia Medical, a direct-pay telehealth psychiatry practice in Virginia.
Welmivia CTA went live on Day 60 of her content plan. Currently Day {plan_day}.

Bio link click data from Later:
{json.dumps(later_data, indent=2) if later_data else "Later API not configured yet."}

Analyze and provide:
1. Total bio link clicks this week
2. Which days had the highest click-through
3. Correlation with posting schedule (which posts likely drove traffic)
4. Estimated conversion funnel (clicks → likely intake form views)
5. ONE specific recommendation to increase intake conversions this week

Be direct. Mia is a founder reviewing her patient acquisition metrics.
"""
        }]
    )
    return "".join(b.text for b in msg.content if hasattr(b, "text"))


def main():
    print(f"\nIntake CTA Tracker")
    print(f"Date: {TODAY} | Plan Day: {PLAN_DAY}\n")

    if not welmivia_cta_active():
        print(f"Intake tracker not active until Day 60 (currently Day {PLAN_DAY}). Skipping.")
        return

    print("Fetching Later analytics...")
    later_data = get_later_analytics()

    print("Analyzing conversion data...")
    analysis = analyze_conversion_data(later_data, PLAN_DAY)

    days_since_launch = PLAN_DAY - 60
    week_start = (TODAY - timedelta(days=7)).strftime("%b %d")

    html_content = f"""
        {email_header(
            "Welmivia Intake CTA Report",
            f"Day {PLAN_DAY} · {days_since_launch} days since CTA launch · Week of {week_start}",
            "Welmivia · Conversion",
            "#2d6a4f"
        )}

        {email_section("Conversion analysis", analysis, "#2d6a4f")}

        {'<div style="background:#fff3cd;border:1px solid #ffc107;border-radius:4px;padding:12px 16px;font-size:13px;font-family:sans-serif;margin-top:16px;">⚠ <strong>Later API not configured</strong> — add LATER_API_KEY to GitHub secrets to enable automatic click tracking.</div>' if not later_data else ''}
    """

    send_email(
        to=[MIA_EMAIL],
        subject=f"[Intake CTA] Conversion report · Day {PLAN_DAY} · {days_since_launch}d since launch",
        html_body=email_wrapper(html_content),
        plain_body=f"Intake CTA report. Day {PLAN_DAY}.\n\n{analysis}"
    )
    print("✓ Intake tracker report sent.\n")


if __name__ == "__main__":
    main()
