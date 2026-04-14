#!/usr/bin/env python3
# newsletter_gen.py
"""
Newsletter Generator — runs every Thursday at 9 AM ET (activates Day 30+)
Takes the week's top-performing content concept and writes a newsletter draft.
Emails to Mia for approval — she sends via ConvertKit.
"""

import anthropic
from datetime import datetime, date
from shared.config import (
    ANTHROPIC_API_KEY, MIA_EMAIL,
    get_plan_day, get_plan_phase, newsletter_active, welmivia_cta_active,
    DISCLAIMER, WELMIVIA_CTA
)
from shared.prompts import NEWSLETTER_SYSTEM
from shared.platform_apis import get_all_analytics
from shared.email_utils import (
    send_email, email_header, email_section, email_wrapper
)

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
TODAY     = date.today()
PLAN_DAY  = get_plan_day()
PLAN_PHASE = get_plan_phase()


def get_top_topic() -> str:
    """Try to get top performing topic from analytics, fall back to prompt."""
    analytics = get_all_analytics()
    top_videos = analytics.get("top_youtube_videos", [])
    top_posts  = analytics.get("top_instagram_posts", [])

    if top_videos:
        return f"Top YouTube video this week: {top_videos[0].get('title', '')}"
    if top_posts:
        return f"Top Instagram post: {top_posts[0].get('caption', '')[:100]}"
    return "No analytics data yet — generate a newsletter on a high-value psychiatric topic for the current week."


def generate_newsletter(top_topic: str) -> str:
    cta_note = f"\nInclude this Welmivia mention naturally: '{WELMIVIA_CTA}'" if welmivia_cta_active() else "\nNo Welmivia CTA yet — pure education."

    msg = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1500,
        system=NEWSLETTER_SYSTEM,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{
            "role": "user",
            "content": f"""
Today is {TODAY.strftime('%B %d, %Y')}. Plan Day {PLAN_DAY}.

Top content this week: {top_topic}

Search for any relevant recent news or research that could enrich this week's newsletter topic.
Then write the full newsletter draft.

{cta_note}

Always end with:
{DISCLAIMER}
"""
        }]
    )
    return "".join(b.text for b in msg.content if hasattr(b, "text"))


def main():
    print(f"\nNewsletter Generator")
    print(f"Date: {TODAY} | Plan Day: {PLAN_DAY}\n")

    if not newsletter_active():
        print(f"Newsletter not active until Day 30 (currently Day {PLAN_DAY}). Skipping.")
        return

    print("Getting top topic...")
    top_topic = get_top_topic()
    print(f"Topic: {top_topic[:80]}")

    print("Generating newsletter draft...")
    newsletter = generate_newsletter(top_topic)

    html_content = f"""
        {email_header(
            "Weekly Newsletter Draft",
            f"Day {PLAN_DAY} · {TODAY.strftime('%A, %B %d')} · Review and send via ConvertKit",
            "@drmiadiaz · Newsletter",
            "#2d6a4f"
        )}

        <div style="background:#d4edda;border:1px solid #28a745;border-radius:4px;
                    padding:12px 16px;font-size:13px;font-family:sans-serif;margin-bottom:24px;">
            <strong>Mia — action needed:</strong> Review this draft, make any edits,
            then send via ConvertKit. Should take under 10 minutes.
        </div>

        {email_section("Newsletter draft — copy into ConvertKit", newsletter, "#2d6a4f")}

        <div style="font-size:12px;color:#888;font-family:sans-serif;margin-top:16px;">
            Based on: {top_topic[:100]}
        </div>
    """

    send_email(
        to=[MIA_EMAIL],
        subject=f"[Newsletter Draft] Week of {TODAY.strftime('%B %d')} — ready to send",
        html_body=email_wrapper(html_content),
        plain_body=f"Newsletter draft for Day {PLAN_DAY}.\n\n{newsletter}"
    )
    print("✓ Newsletter draft sent to Mia.\n")


if __name__ == "__main__":
    main()
