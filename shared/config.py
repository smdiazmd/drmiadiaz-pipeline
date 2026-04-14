# shared/config.py
"""
Central configuration for the Dr. Mia Diaz content pipeline.
All settings, constants, and platform configs live here.
"""

import os
from datetime import datetime, date

# ─────────────────────────────────────────────
# CREDENTIALS — all set as GitHub Secrets
# ─────────────────────────────────────────────

ANTHROPIC_API_KEY   = os.environ.get("ANTHROPIC_API_KEY", "")
GMAIL_ADDRESS       = os.environ.get("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD  = os.environ.get("GMAIL_APP_PASSWORD", "")
MIA_EMAIL           = os.environ.get("MIA_EMAIL", "")       # Mia's inbox
JAKE_EMAIL          = os.environ.get("JAKE_EMAIL", "")      # Jake's inbox
CRISIS_ALERT_EMAIL  = os.environ.get("CRISIS_ALERT_EMAIL", JAKE_EMAIL)  # immediate alerts

# Platform API credentials (add as secrets when approved)
YOUTUBE_API_KEY         = os.environ.get("YOUTUBE_API_KEY", "")
YOUTUBE_CHANNEL_ID      = os.environ.get("YOUTUBE_CHANNEL_ID", "")
INSTAGRAM_ACCESS_TOKEN  = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
INSTAGRAM_ACCOUNT_ID    = os.environ.get("INSTAGRAM_ACCOUNT_ID", "")
TIKTOK_ACCESS_TOKEN     = os.environ.get("TIKTOK_ACCESS_TOKEN", "")
LATER_API_KEY           = os.environ.get("LATER_API_KEY", "")

# ─────────────────────────────────────────────
# 90-DAY PLAN TRACKING
# ─────────────────────────────────────────────

LAUNCH_DATE = date(2026, 5, 1)  # Day 1

def get_plan_day() -> int:
    """Returns current day of the 90-day plan."""
    delta = date.today() - LAUNCH_DATE
    return max(1, delta.days + 1)

def get_plan_phase() -> str:
    day = get_plan_day()
    if day <= 30:   return "establish"
    if day <= 59:   return "scale"
    if day == 60:   return "launch"
    if day <= 90:   return "monetize"
    return "post_90"

def welmivia_cta_active() -> bool:
    """Welmivia CTA goes live on Day 60."""
    return get_plan_day() >= 60

def newsletter_active() -> bool:
    """Newsletter starts Day 30."""
    return get_plan_day() >= 30

def is_first_week() -> bool:
    return get_plan_day() <= 7

# ─────────────────────────────────────────────
# CONTENT PILLARS
# ─────────────────────────────────────────────

CONTENT_PILLARS = [
    "anxiety",
    "ADHD",
    "burnout",
    "trauma",
    "medications and psychiatry",
    "AI and mental health",
    "precision psychiatry and metabolic health",
]

# ─────────────────────────────────────────────
# PLATFORM POSTING SCHEDULE
# ─────────────────────────────────────────────

# Best posting times ET for each day
POSTING_SCHEDULE = {
    "Monday":    {"time": "6:30 PM ET", "platforms": ["TikTok", "Instagram Reels", "YouTube Shorts"], "content": "Short #1 — strongest hook of week"},
    "Tuesday":   {"time": "7:00 AM ET", "platforms": ["LinkedIn"],                                    "content": "LinkedIn post (auto-pipeline)"},
    "Wednesday": {"time": "6:30 PM ET", "platforms": ["TikTok", "Instagram Reels", "YouTube Shorts"], "content": "Short #2 — framework deep-dive"},
    "Thursday":  {"time": "12:00 PM ET","platforms": ["TikTok", "Instagram Reels", "YouTube Shorts", "LinkedIn"], "content": "Short #3 — quick tip or myth bust + LinkedIn post"},
    "Friday":    {"time": "7:00 PM ET", "platforms": ["TikTok", "Instagram Reels", "YouTube Shorts"], "content": "Short #4 — trend react or Reddit breakdown"},
    "Saturday":  {"time": "11:00 AM ET","platforms": ["TikTok", "Instagram Reels", "YouTube Shorts"], "content": "Short #5 — personal angle or comment reply (if 5th filmed)"},
    "Sunday":    {"time": "10:00 AM ET","platforms": ["YouTube Long-form", "LinkedIn"],               "content": "Long-form YouTube + LinkedIn post (auto-pipeline)"},
}

YOUTUBE_LONGFORM_TIME = "10:00 AM ET Saturday"  # schedule ahead for Sunday publish

# ─────────────────────────────────────────────
# HASHTAG SETS
# ─────────────────────────────────────────────

HASHTAG_SETS = {
    "A_large":   ["#mentalhealth", "#anxiety", "#depression", "#therapy", "#wellness"],
    "B_medium":  ["#psychiatry", "#mentalwellness", "#adhd", "#burnout", "#traumahealing"],
    "C_niche":   ["#telepsychiatry", "#drmiadiaz", "#welmivia", "#virginiapsychiatry", "#psychiatrist"],
    "D_trending": [],  # populated dynamically by trend scan
}

PLATFORM_HASHTAGS = {
    "tiktok":    {"sets": ["A_large", "B_medium", "C_niche"], "max": 7},
    "instagram": {"sets": ["A_large", "B_medium", "C_niche"], "max": 15},
    "youtube":   {"sets": ["B_medium", "C_niche"],             "max": 5},
    "linkedin":  {"sets": ["C_niche"],                         "max": 3},
}

# ─────────────────────────────────────────────
# DISCLAIMER + CTA TEMPLATES
# ─────────────────────────────────────────────

DISCLAIMER = """This content is for educational purposes only and does not constitute medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider regarding any medical condition. If you are in crisis, call or text 988.
— Dr. Mia Diaz, MD | Welmivia Medical | welmivia.com"""

WELMIVIA_CTA = "If you're in Virginia and ready to take the next step — Welmivia Medical is in my bio. Direct pay. Telehealth. Psychiatry that actually listens."

SOFT_WELMIVIA_CTA = "At my practice I see this often — the patterns are real and they're treatable."

# ─────────────────────────────────────────────
# CRISIS KEYWORDS
# ─────────────────────────────────────────────

CRISIS_KEYWORDS = [
    "want to die", "kill myself", "end my life", "suicide", "suicidal",
    "don't want to be here", "can't go on", "no reason to live",
    "self harm", "cutting", "hurting myself", "overdose",
    "goodbye forever", "final note", "last message"
]

# ─────────────────────────────────────────────
# LONG-FORM YOUTUBE TOPIC SCHEDULE
# ─────────────────────────────────────────────

LONGFORM_SCHEDULE = [
    {"week": 2,  "date": "Apr 20", "title": "Why Your Antidepressant Might Be Wrong for Your DNA",          "type": "standard"},
    {"week": 4,  "date": "May 4",  "title": "ADHD in Women: The 10-Year Diagnosis Gap",                     "type": "standard"},
    {"week": 6,  "date": "May 18", "title": "Burnout vs. Depression: A Psychiatrist's Distinction",         "type": "flagship"},
    {"week": 8,  "date": "Jun 1",  "title": "GLP-1 Drugs and Your Brain: What the Data Actually Shows",     "type": "standard"},
    {"week": 10, "date": "Jun 15", "title": "Attachment Styles: The Neuroscience of Who You Choose",        "type": "standard"},
    {"week": 12, "date": "Jun 29", "title": "AI Psychosis: A Psychiatrist Reads the Actual Research",       "type": "flagship"},
    {"week": 13, "date": "Jul 6",  "title": "Precision Psychiatry: DNA + Gut + Sleep = Your Brain",         "type": "flagship"},
]

def get_this_weeks_longform() -> dict | None:
    """Returns the long-form topic scheduled for this week, if any."""
    today = date.today()
    for item in LONGFORM_SCHEDULE:
        scheduled = datetime.strptime(f"{item['date']} 2026", "%b %d %Y").date()
        days_diff = abs((today - scheduled).days)
        if days_diff <= 3:
            return item
    return None
