#!/usr/bin/env python3
# analytics_report.py
"""
Monday Analytics Report — runs every Monday at 7 AM ET
Pulls data from all configured platforms automatically.
Gracefully skips unconfigured platforms.
Emails formatted report to Mia + Jake.
"""

import anthropic
from datetime import datetime, date, timedelta
from shared.config import (
    ANTHROPIC_API_KEY, JAKE_EMAIL, MIA_EMAIL,
    get_plan_day, get_plan_phase, analytics_available,
    LAUNCH_DATE
)
from shared.prompts import ANALYTICS_SYSTEM
from shared.platform_apis import get_all_analytics, analytics_available
from shared.email_utils import (
    send_email, email_header, email_section,
    email_table, email_wrapper
)

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
TODAY     = date.today()
PLAN_DAY  = get_plan_day()
PLAN_PHASE = get_plan_phase()

# Follower gates from 90-day plan
GATES = {30: 1000, 60: 5000, 90: 20000}


def analyze_with_claude(analytics_data: dict) -> str:
    """Send analytics to Claude for interpretation and recommendations."""
    msg = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2000,
        system=ANALYTICS_SYSTEM,
        messages=[{
            "role": "user",
            "content": f"""
Plan Day: {PLAN_DAY} | Phase: {PLAN_PHASE}
Week ending: {TODAY.strftime('%B %d, %Y')}

Analytics data:
{str(analytics_data)}

Follower gates: Day 30 = 1,000 | Day 60 = 5,000 | Day 90 = 20,000

Generate the full Monday report in the format specified.
Be direct. No filler. Mia and Jake need actionable insights.
"""
        }]
    )
    return "".join(b.text for b in msg.content if hasattr(b, "text"))


def build_scorecard(analytics: dict) -> list:
    """Build follower scorecard table rows."""
    yt  = analytics.get("youtube", {})
    ig  = analytics.get("instagram", {})
    tt  = analytics.get("tiktok", {})

    # Determine next gate
    next_gate_day = min((d for d in GATES if d >= PLAN_DAY), default=90)
    next_gate_followers = GATES[next_gate_day]
    days_remaining = next_gate_day - PLAN_DAY

    rows = []
    if yt:  rows.append(["YouTube",   str(yt.get("subscribers", "—")),  "—", "—"])
    if ig:  rows.append(["Instagram", str(ig.get("followers", "—")),    "—", "—"])
    if tt:  rows.append(["TikTok",    str(tt.get("followers", "—")),    "—", "—"])
    if not rows:
        rows = [["All platforms", "APIs not yet configured", "—", f"Day {next_gate_day}: {next_gate_followers:,} followers in {days_remaining} days"]]
    return rows


def no_api_placeholder() -> str:
    return f"""No platform APIs configured yet.

Once YouTube API is active (same-day approval), analytics will auto-populate here.
Instagram: 1–3 days after first posts.
TikTok: apply after 2 weeks of posting.

Plan Day: {PLAN_DAY} | Phase: {PLAN_PHASE.upper()}
Next gate: {next(v for k,v in GATES.items() if k >= PLAN_DAY):,} followers by Day {next(k for k in GATES if k >= PLAN_DAY)}

Action this week: Focus on posting consistency. Analytics become meaningful after Week 2.
"""


def main():
    print(f"\nMonday Analytics Report")
    print(f"Date: {TODAY} | Plan Day: {PLAN_DAY}\n")

    analytics = get_all_analytics()
    has_data  = any(analytics.get(p) for p in ["youtube", "instagram", "tiktok"])

    if has_data:
        print("Analytics data retrieved. Analyzing with Claude...")
        analysis = analyze_with_claude(analytics)
        scorecard_rows = build_scorecard(analytics)
    else:
        print("No APIs configured yet — generating placeholder report.")
        analysis = no_api_placeholder()
        scorecard_rows = [["APIs pending", "—", "—", "See setup guide"]]

    # Top performers section
    top_yt = analytics.get("top_youtube_videos", [])
    top_ig = analytics.get("top_instagram_posts", [])

    top_content_rows = []
    for v in top_yt[:3]:
        top_content_rows.append([
            "YouTube", v.get("title","")[:50],
            str(v.get("views","—")), str(v.get("likes","—"))
        ])
    for p in top_ig[:3]:
        top_content_rows.append([
            "Instagram", p.get("caption","")[:50],
            str(p.get("likes","—")), str(p.get("comments","—"))
        ])

    # Build email
    week_start = (TODAY - timedelta(days=7)).strftime("%b %d")
    week_end   = TODAY.strftime("%b %d")

    scorecard_table = email_table(
        ["Platform", "Followers/Subscribers", "Week Change", "Notes"],
        scorecard_rows
    )

    top_table = email_table(
        ["Platform", "Content", "Views/Likes", "Engagement"],
        top_content_rows
    ) if top_content_rows else "<p style='font-family:sans-serif;font-size:13px;color:#888;'>No content data yet — APIs pending.</p>"

    html_content = f"""
        {email_header(
            f"Weekly Analytics — {week_start}–{week_end}",
            f"Day {PLAN_DAY} · {PLAN_PHASE.upper()} phase · Monday morning report",
            "@drmiadiaz · Analytics",
            "#1a4a8a"
        )}

        <div style="font-size:10px;letter-spacing:0.14em;text-transform:uppercase;
                    color:#1a4a8a;font-family:sans-serif;margin-bottom:12px;font-weight:600;">
            Follower scorecard
        </div>
        {scorecard_table}

        <div style="font-size:10px;letter-spacing:0.14em;text-transform:uppercase;
                    color:#1a4a8a;font-family:sans-serif;margin-bottom:12px;font-weight:600;">
            Top performing content this week
        </div>
        {top_table}

        {email_section("Analysis + recommendations", analysis, "#1a4a8a")}
    """

    send_email(
        to=[JAKE_EMAIL, MIA_EMAIL],
        subject=f"[Analytics] Week of {week_start}–{week_end} · Day {PLAN_DAY}",
        html_body=email_wrapper(html_content),
        plain_body=f"Weekly analytics report. Plan Day {PLAN_DAY}.\n\n{analysis}"
    )
    print("✓ Analytics report sent.\n")


if __name__ == "__main__":
    main()
