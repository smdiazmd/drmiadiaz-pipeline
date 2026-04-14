#!/usr/bin/env python3
# comment_analyzer.py
"""
Comment Analyzer — runs daily at 9 AM ET
Pulls comments from all configured platforms.
Analyzes for: repeated questions, crisis language, content opportunities, referral signals.
Emails Jake a prioritized action list.
Crisis comments trigger immediate separate alert.
"""

import anthropic
from datetime import datetime, date
from shared.config import (
    ANTHROPIC_API_KEY, JAKE_EMAIL, MIA_EMAIL,
    CRISIS_ALERT_EMAIL, CRISIS_KEYWORDS,
    get_plan_day, get_plan_phase
)
from shared.platform_apis import get_all_comments
from shared.email_utils import (
    send_email, email_header, email_section,
    email_table, email_wrapper
)

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
TODAY     = date.today()
PLAN_DAY  = get_plan_day()


def check_for_crisis(comments: list) -> list:
    """Flag comments containing crisis language."""
    flagged = []
    for comment in comments:
        text = comment.get("text", "").lower()
        for keyword in CRISIS_KEYWORDS:
            if keyword in text:
                flagged.append(comment)
                break
    return flagged


def send_crisis_alert(flagged_comments: list):
    """Send immediate crisis alert email."""
    comment_list = "\n\n".join([
        f"Platform: {c.get('platform', 'Unknown')}\n"
        f"Comment: {c.get('text', '')}\n"
        f"Video: {c.get('video', 'Unknown')}"
        for c in flagged_comments
    ])

    html = email_wrapper(f"""
        {email_header(
            "⚠ Crisis Comment Alert",
            f"{len(flagged_comments)} comment(s) flagged — immediate response needed",
            "CRISIS ALERT",
            "#8a1a1a"
        )}
        <div style="background:#f8d7da;border:1px solid #f5c6cb;border-radius:4px;
                    padding:16px;font-family:sans-serif;font-size:14px;margin-bottom:24px;">
            <strong>Action required:</strong> Review these comments immediately.
            Reply with the ;;crisis shortcut: <em>"If you're in crisis, please call or text 988 — 
            trained counselors are available 24/7."</em>
            <br><br>
            Do NOT engage further. Screenshot and notify Mia same day.
        </div>
        {email_section("Flagged comments", comment_list, "#8a1a1a", "#fff5f5")}
    """)

    send_email(
        to=[CRISIS_ALERT_EMAIL, MIA_EMAIL],
        subject=f"⚠ CRISIS COMMENT ALERT — {len(flagged_comments)} flagged — immediate action needed",
        html_body=html,
        plain_body=f"CRISIS ALERT: {len(flagged_comments)} comments flagged.\n\n{comment_list}"
    )
    print(f"⚠ Crisis alert sent — {len(flagged_comments)} comments flagged")


def analyze_comments_with_claude(comments: list) -> str:
    """Use Claude to analyze comments for patterns and opportunities."""
    if not comments:
        return "No comments retrieved yet — platform APIs pending or no content posted."

    comment_text = "\n".join([
        f"[{c.get('platform','?')}] {c.get('text','')} (likes: {c.get('likes',0)})"
        for c in comments[:50]  # limit to top 50
    ])

    msg = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1500,
        messages=[{
            "role": "user",
            "content": f"""
Analyze these comments from Dr. Mia Diaz's social media (psychiatry/mental health content):

{comment_text}

Provide:

1. REPEATED QUESTIONS (asked 3+ times — these become videos):
List each question with frequency and a suggested video hook.

2. CONTENT OPPORTUNITIES:
Topics the audience is clearly hungry for based on comment patterns.

3. REFERRAL SIGNALS:
Comments that suggest the person might benefit from Welmivia (Virginia residents asking about care, etc.)
List these with suggested reply using the ;;welm shortcut.

4. ENGAGEMENT PATTERNS:
What topics are generating the most comments and why.

5. THIS WEEK'S VIDEO IDEA:
One specific video to make based purely on what the comments are asking for.

Be direct. Jake reads this Monday morning before batch prep.
"""
        }]
    )
    return "".join(b.text for b in msg.content if hasattr(b, "text"))


def main():
    print(f"\nComment Analyzer")
    print(f"Date: {TODAY} | Plan Day: {PLAN_DAY}\n")

    print("Fetching comments from platforms...")
    comments = get_all_comments()
    print(f"Retrieved {len(comments)} comments")

    # Crisis check first — always
    crisis_comments = check_for_crisis(comments)
    if crisis_comments:
        print(f"⚠ {len(crisis_comments)} crisis comments detected — sending alert")
        send_crisis_alert(crisis_comments)

    # Skip regular report if no comments
    if not comments:
        print("No comments to analyze. Skipping regular report.")
        return

    print("Analyzing with Claude...")
    analysis = analyze_comments_with_claude(comments)

    # Build top comments table
    top_rows = []
    for c in comments[:10]:
        top_rows.append([
            c.get("platform", "?"),
            c.get("text", "")[:70] + "..." if len(c.get("text","")) > 70 else c.get("text",""),
            str(c.get("likes", 0)),
            c.get("video", "")[:40]
        ])

    html_content = f"""
        {email_header(
            "Comment Intelligence Report",
            f"Day {PLAN_DAY} · {TODAY.strftime('%A, %B %d')} · {len(comments)} comments analyzed",
            "@drmiadiaz · Comments",
            "#555"
        )}

        {'<div style="background:#f8d7da;border:1px solid #f5c6cb;border-radius:4px;padding:12px 16px;font-size:13px;font-family:sans-serif;margin-bottom:24px;">⚠ <strong>' + str(len(crisis_comments)) + ' crisis comments flagged</strong> — separate alert sent. Check that email first.</div>' if crisis_comments else ''}

        <div style="font-size:10px;letter-spacing:0.14em;text-transform:uppercase;
                    color:#555;font-family:sans-serif;margin-bottom:12px;font-weight:600;">
            Top comments by engagement
        </div>
        {email_table(["Platform", "Comment", "Likes", "Video"], top_rows)}

        {email_section("Analysis + content opportunities", analysis, "#555")}
    """

    send_email(
        to=[JAKE_EMAIL],
        cc=MIA_EMAIL,
        subject=f"[Comments] {len(comments)} analyzed · {len(crisis_comments)} flagged · Day {PLAN_DAY}",
        html_body=email_wrapper(html_content),
        plain_body=f"Comment report. {len(comments)} analyzed, {len(crisis_comments)} crisis flags.\n\n{analysis}"
    )
    print("✓ Comment report sent.\n")


if __name__ == "__main__":
    main()
