#!/usr/bin/env python3
# saturday_batch.py
"""
Saturday Batch Pipeline — runs every Saturday at 6 AM ET
Generates everything Jake needs before Sunday filming:
  - Top 5 trends with confidence scores
  - 4 short-form scripts (+ intro scripts Week 1)
  - Long-form script (weekly, standard or flagship)
  - All platform captions per script
  - Exact posting schedule for the week
  - Daily Instagram Stories for 7 days
  - Platform bios (Week 1 only)
  - Collab radar (3 creator suggestions)
"""

import anthropic
import json
import random
import time
from datetime import datetime, date, timedelta
from shared.config import (
    ANTHROPIC_API_KEY, JAKE_EMAIL, MIA_EMAIL,
    DISCLAIMER, WELMIVIA_CTA, SOFT_WELMIVIA_CTA,
    CONTENT_PILLARS, POSTING_SCHEDULE, HASHTAG_SETS,
    PLATFORM_HASHTAGS, LONGFORM_SCHEDULE,
    get_plan_day, get_plan_phase, welmivia_cta_active,
    is_first_week, get_this_weeks_longform
)
from shared.prompts import (
    get_short_form_system, get_longform_system, get_caption_system,
    get_story_system, get_intro_system,
    TREND_SYSTEM, COLLAB_SYSTEM
)
from shared.email_utils import (
    send_email, email_header, email_section,
    email_table, email_wrapper
)

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Delay between Claude calls to stay within free tier rate limits
# 30,000 tokens/min limit — 90 second pause keeps us well clear
CALL_DELAY_SECONDS = 180

def wait():
    """Pause between Claude calls to respect rate limits."""
    print(f"  Waiting {CALL_DELAY_SECONDS}s to respect rate limits...")
    time.sleep(CALL_DELAY_SECONDS)

TODAY       = date.today()
PLAN_DAY    = get_plan_day()
PLAN_PHASE  = get_plan_phase()
FIRST_WEEK  = is_first_week()
CTA_ACTIVE  = welmivia_cta_active()

# Days of the week for posting schedule
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
NEXT_MONDAY = TODAY + timedelta(days=(7 - TODAY.weekday()) % 7 or 7)


def claude(system: str, prompt: str, max_tokens: int = 2000) -> str:
    """Call Claude with web search enabled."""
    msg = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=max_tokens,
        system=system,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}]
    )
    return "".join(block.text for block in msg.content if hasattr(block, "text"))


def claude_no_search(system: str, prompt: str, max_tokens: int = 2000) -> str:
    """Call Claude without web search (faster for generation tasks)."""
    msg = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": prompt}]
    )
    return "".join(block.text for block in msg.content if hasattr(block, "text"))


# ─────────────────────────────────────────────
# STEP 1 — TREND SCAN
# ─────────────────────────────────────────────

def run_trend_scan() -> str:
    print("  Running trend scan...")
    prompt = f"""
Today is {TODAY.strftime('%B %d, %Y')}. 
Search for the top trending topics this week across:
- Reddit (r/mentalhealth, r/ADHD, r/anxiety, r/depression, r/therapy)
- Recent mental health / psychiatry news
- Viral health content on TikTok and Instagram
- New research papers or studies getting media coverage
- Pop culture moments touching on mental health

Focus on Mia's pillars: {', '.join(CONTENT_PILLARS)}

Return the top 5 opportunities in the exact format specified.
Rank by confidence score (highest first).
"""
    return claude(TREND_SYSTEM, prompt, max_tokens=2500)


# ─────────────────────────────────────────────
# STEP 2 — SHORT-FORM SCRIPTS
# ─────────────────────────────────────────────

def generate_short_form_scripts(trends: str) -> str:
    print("  Generating short-form scripts...")
  
    intro_note = ""
    if FIRST_WEEK:
        intro_note = """
IMPORTANT — WEEK 1: This is the launch week. Generate:
- Script 1: CHANNEL/PROFILE INTRO — who Mia is, what this channel is, why it exists (hook them immediately)
- Scripts 2–4: Regular content from the trends below
The intro script should make people think 'finally, a psychiatrist who gets it.'
"""

    prompt = f"""
Here are this week's top trends (ranked by opportunity):

{trends}

{intro_note}

Generate 4 short-form scripts based on the top 4 trends above.
For each script, use the exact SHORT-FORM FORMAT from your instructions.

Label each script clearly:
SCRIPT 1: [trend name] | Format: [Doctor Reacts/etc] | Confidence: [score]/10
[full script]

SCRIPT 2: ...
etc.

"""
    return claude_no_search(get_short_form_system(PLAN_DAY), prompt, max_tokens=3000)


# ─────────────────────────────────────────────
# STEP 3 — LONG-FORM SCRIPT
# ─────────────────────────────────────────────

def generate_longform_script() -> str:
    print("  Generating long-form script...")

    scheduled = get_this_weeks_longform()
    if scheduled:
        topic = scheduled["title"]
        video_type = scheduled["type"]
        length_note = "20–30 minutes (flagship deep dive)" if video_type == "flagship" else "8–12 minutes (standard)"
    else:
        # Generate a relevant topic if none scheduled
        topic = f"A clinically important topic in {random.choice(CONTENT_PILLARS)}"
        video_type = "standard"
        length_note = "8–12 minutes"

    intro_note = "WEEK 1 NOTE: This is the launch week YouTube video. Open with Mia's full channel intro before the main content." if FIRST_WEEK else ""

    prompt = f"""
Write a {length_note} YouTube script on this topic:

TITLE: {topic}
TYPE: {video_type}
{intro_note}

Follow the LONG-FORM YOUTUBE SCRIPT FORMAT exactly.
Include:
- Thumbnail concept (3 options)
- Chapter timestamps
- B-roll suggestions per chapter  
- YouTube end card suggestion
- Full spoken script

"""
    return claude_no_search(LONGFORM_SYSTEM, prompt, max_tokens=4000)


# ─────────────────────────────────────────────
# STEP 4 — CAPTIONS
# ─────────────────────────────────────────────

def generate_captions(scripts: str) -> str:
    print("  Generating platform captions...")

    hashtags_info = json.dumps(HASHTAG_SETS, indent=2)
    welmivia_note = f"Include this Welmivia CTA in appropriate captions: '{WELMIVIA_CTA}'" if CTA_ACTIVE else "No Welmivia CTA in captions yet."

    prompt = f"""
Based on these 4 scripts:

{scripts[:2000]}... [scripts continue]

Generate platform-specific captions for each script.

Available hashtags:
{hashtags_info}

TikTok: use sets A + B + 1-2 from C. Max 7 tags.
Instagram: use sets A + B + C. Max 15 tags.
YouTube: use sets B + C. Max 5 tags.
LinkedIn: use set C only. Max 3 tags.

For each script, label clearly:
CAPTIONS FOR SCRIPT [N]:

TIKTOK:
[caption + hashtags + disclaimer]

INSTAGRAM:
[caption + hashtags + disclaimer]

YOUTUBE SHORTS:
[caption + hashtags + disclaimer]

LINKEDIN:
[caption + hashtags + disclaimer]

---

{welmivia_note}
Always append the full disclaimer at the end of every caption.
Disclaimer: {DISCLAIMER}
"""
    return claude_no_search(get_caption_system(PLAN_DAY), prompt, max_tokens=3000)


# ─────────────────────────────────────────────
# STEP 5 — POSTING SCHEDULE
# ─────────────────────────────────────────────

def generate_posting_schedule() -> list:
    """Generate exact posting times for the week as table rows."""
    schedule_rows = []
    current_day = NEXT_MONDAY

    post_map = {
        0: ("6:30 PM ET", "TikTok + Instagram + YouTube Shorts", "Short #1 — strongest hook"),
        1: ("7:00 AM ET", "LinkedIn",                            "LinkedIn post (auto-pipeline)"),
        2: ("6:30 PM ET", "TikTok + Instagram + YouTube Shorts", "Short #2 — framework deep-dive"),
        3: ("12:00 PM ET","TikTok + Instagram + YouTube Shorts + LinkedIn", "Short #3 + LinkedIn post"),
        4: ("7:00 PM ET", "TikTok + Instagram + YouTube Shorts", "Short #4 — trend react"),
        5: ("11:00 AM ET","TikTok + Instagram + YouTube Shorts", "Optional Short #5"),
        6: ("10:00 AM ET","YouTube Long-form",                   "Long-form YouTube"),
    }

    for i in range(7):
        day = current_day + timedelta(days=i)
        time_et, platforms, content = post_map[i]
        schedule_rows.append([
            day.strftime("%A %b %d"),
            time_et,
            platforms,
            content
        ])

    return schedule_rows


# ─────────────────────────────────────────────
# STEP 6 — INSTAGRAM STORIES
# ─────────────────────────────────────────────

def generate_stories() -> str:
    print("  Generating Instagram Stories...")
    prompt = f"""
Generate daily Instagram Story concepts for the week of {NEXT_MONDAY.strftime('%B %d')}.
Plan Day: {PLAN_DAY} | Phase: {PLAN_PHASE}

Create 7 days of stories (Monday–Sunday).
Rotate through all story types: Poll / Q&A Box / Quote Card / Behind-scenes / Engagement Question / Countdown / Myth or Fact

{'Include a story about the launch/channel intro this week — Day 1 energy.' if FIRST_WEEK else ''}
{'Include at least one story mentioning Welmivia and the intake link.' if CTA_ACTIVE else ''}

Use the exact format:
DAY 1 — Monday [date] — [Type]
Visual: ...
Text overlay: ...
Interactive element: ...

DAY 2 — Tuesday [date] — [Type]
...etc
"""
    return claude_no_search(get_story_system(PLAN_DAY), prompt, max_tokens=2000)


# ─────────────────────────────────────────────
# STEP 7 — COLLAB RADAR
# ─────────────────────────────────────────────

def generate_collab_radar() -> str:
    print("  Running collab radar...")
    prompt = f"""
Today is {TODAY.strftime('%B %d, %Y')}.
Search for 3 mental health / psychiatry creators active this week who would be good 
collaboration targets for Dr. Mia Diaz as she builds her audience from zero.

Focus on creators who:
- Post evidence-based content (not pseudoscience)
- Are in the 50K–500K range (accessible)
- Have posted in the last 2 weeks
- Cover anxiety, ADHD, trauma, burnout, or psychiatry

Return results in the exact format from your instructions.
"""
    return claude(COLLAB_SYSTEM, prompt, max_tokens=1500)


# ─────────────────────────────────────────────
# WEEK 1 ONLY — INTRO CONTENT + BIOS
# ─────────────────────────────────────────────

def generate_intro_content() -> str:
    print("  Generating Week 1 intro content...")
    prompt = """
Generate launch week intro content for Dr. Mia Diaz across all platforms.

Include:
1. YOUTUBE CHANNEL INTRO SCRIPT (60–90 seconds) — who she is, what the channel is, why it exists
2. TIKTOK/INSTAGRAM REELS INTRO SCRIPT (30–45 seconds) — punchier, faster version
3. LINKEDIN INTRO POST (200–250 words written post, not video)
4. FIRST TWEET/X POST (optional — 280 chars)

These are the very first things her audience will see. Make them unforgettable.
Lead with value and POV, not biography.
"""
    return claude_no_search(get_intro_system(PLAN_DAY), prompt, max_tokens=2000)


def generate_bios() -> str:
    print("  Generating platform bios...")
    prompt = """
Generate optimized bios for all of Dr. Mia Diaz's platforms:

1. TikTok bio (80 chars max)
2. Instagram bio (150 chars max) — can use line breaks
3. YouTube About section (write ~300 words)
4. LinkedIn Headline (220 chars max)
5. LinkedIn About section (write ~500 words)
6. Beacons.ai bio (160 chars)
7. Google Business Profile description (write ~200 words)

For each, provide 2 variants (A and B) so Mia can choose.
"""
    return claude_no_search(BIO_SYSTEM, prompt, max_tokens=2500)


# ─────────────────────────────────────────────
# BUILD + SEND EMAIL
# ─────────────────────────────────────────────

def build_and_send(
    trends, scripts, longform, captions,
    schedule_rows, stories, collabs,
    intro=None, bios=None
):
    print("  Building email...")

    week_of = NEXT_MONDAY.strftime("%B %d")
    longform_info = get_this_weeks_longform()
    longform_title = longform_info["title"] if longform_info else "Weekly long-form"
    longform_type  = longform_info["type"].upper() if longform_info else "STANDARD"

    schedule_table = email_table(
        ["Day", "Post Time ET", "Platforms", "Content"],
        schedule_rows
    )

    phase_badge_colors = {
        "establish": "#1a1a1a",
        "scale":     "#1a4a8a",
        "launch":    "#8a1a1a",
        "monetize":  "#2d6a4f",
    }
    badge_color = phase_badge_colors.get(PLAN_PHASE, "#1a1a1a")

    week1_banner = ""
    if FIRST_WEEK:
        week1_banner = f"""
        <div style="background:#fff3cd;border:1px solid #ffc107;border-radius:4px;
                    padding:12px 16px;font-size:13px;font-family:sans-serif;margin-bottom:24px;">
            🚀 <strong>LAUNCH WEEK</strong> — Intro scripts and platform bios included below.
            Post the channel intro first before any other content.
        </div>
        """

    cta_banner = ""
    if CTA_ACTIVE:
        cta_banner = f"""
        <div style="background:#d4edda;border:1px solid #28a745;border-radius:4px;
                    padding:12px 16px;font-size:13px;font-family:sans-serif;margin-bottom:24px;">
            ✅ <strong>DAY {PLAN_DAY} — WELMIVIA CTA ACTIVE</strong> — 
            Intake link is live. CTAs included in scripts and captions.
        </div>
        """

    intro_sections = ""
    if FIRST_WEEK and intro and bios:
        intro_sections = f"""
        <div style="border-top:2px solid #ffc107;margin:32px 0 24px;"></div>
        <div style="font-size:11px;letter-spacing:0.12em;text-transform:uppercase;
                    color:#999;font-family:sans-serif;margin-bottom:20px;">
            🚀 Week 1 launch content
        </div>
        {email_section("Platform bios — choose your favorites", bios, "#b8860b")}
        {email_section("Intro scripts — post these first", intro, "#b8860b")}
        """

    html_content = f"""
        {email_header(
            f"Batch Brief — Week of {week_of}",
            f"Day {PLAN_DAY} · {PLAN_PHASE.upper()} phase · {TODAY.strftime('%A, %B %d')}",
            f"@drmiadiaz · Saturday Batch",
            badge_color
        )}

        {week1_banner}
        {cta_banner}

        <!-- SCHEDULE -->
        <div style="font-size:10px;letter-spacing:0.14em;text-transform:uppercase;
                    color:#1a1a1a;font-family:sans-serif;margin-bottom:12px;font-weight:600;">
            Posting schedule — week of {week_of}
        </div>
        {schedule_table}

        <!-- TRENDS -->
        {email_section("Trend scan — top 5 opportunities this week", trends, "#1a4a8a")}

        <!-- SCRIPTS -->
        {email_section("Short-form scripts (4) — film Sunday", scripts, "#1a1a1a")}

        <!-- LONG-FORM -->
        {email_section(f"Long-form script — {longform_title} [{longform_type}]", longform, "#2d6a4f")}

        <!-- CAPTIONS -->
        {email_section("Platform captions — all 4 scripts × 4 platforms", captions, "#555")}

        <!-- STORIES -->
        {email_section("Instagram stories — 7 days (Mon–Sun)", stories, "#833ab4")}

        <!-- COLLABS -->
        {email_section("Collab radar — 3 creator opportunities this week", collabs, "#c0392b")}

        {intro_sections}

        <div style="background:#f0f0f0;border-radius:4px;padding:12px 16px;
                    font-size:12px;font-family:sans-serif;color:#555;margin-top:24px;">
            📋 <strong>Jake's Sunday checklist:</strong>
            Studio setup on floor tape marks (7:45 AM) ·
            Teleprompter loaded with today's scripts ·
            Elgato + Lume Cube on · practicals on 15 min early ·
            Film in order: Short 1 → 2 → 3 → 4 → Long-form ·
            Upload to Vizard.ai after each outfit change ·
            Schedule all posts in Later before 1:30 PM
        </div>
    """

    send_email(
        to=[JAKE_EMAIL, MIA_EMAIL],
        subject=f"[Batch Brief] Week of {week_of} — {PLAN_PHASE.upper()} Day {PLAN_DAY}",
        html_body=email_wrapper(html_content),
        plain_body=f"Saturday batch brief for week of {week_of}. Open HTML version for full formatted content."
    )


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    print(f"\nSaturday Batch Pipeline")
    print(f"Date: {TODAY} | Plan Day: {PLAN_DAY} | Phase: {PLAN_PHASE}")
    print(f"First week: {FIRST_WEEK} | Welmivia CTA: {CTA_ACTIVE}\n")

    print("Step 1/7 — Trend scan")
    trends = run_trend_scan()
    wait()

    print("Step 2/7 — Short-form scripts")
    scripts = generate_short_form_scripts(trends)
    wait()

    print("Step 3/7 — Long-form script")
    longform = generate_longform_script()
    wait()

    print("Step 4/7 — Platform captions")
    captions = generate_captions(scripts)
    wait()

    print("Step 5/7 — Posting schedule")
    schedule_rows = generate_posting_schedule()

    print("Step 6/7 — Instagram stories")
    stories = generate_stories()
    wait()

    print("Step 7/7 — Collab radar")
    collabs = generate_collab_radar()

    intro, bios = None, None
    if FIRST_WEEK:
        wait()
        print("Week 1 — Generating intro content + bios")
        intro = generate_intro_content()
        wait()
        bios  = generate_bios()

    print("Sending email...")
    build_and_send(trends, scripts, longform, captions,
                   schedule_rows, stories, collabs, intro, bios)
    print("✓ Saturday batch complete.\n")


if __name__ == "__main__":
    main()
