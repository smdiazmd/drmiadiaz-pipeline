## .github/workflows/ — all workflow files

# ─────────────────────────────────────────────
# FILE 1: saturday_batch.yml
# ─────────────────────────────────────────────

name: Saturday Batch Brief

on:
  schedule:
    - cron: '0 10 * * 6'   # Saturday 6:00 AM ET (10:00 UTC)
  workflow_dispatch:

jobs:
  saturday-batch:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install anthropic
      - run: python saturday_batch.py
        env:
          ANTHROPIC_API_KEY:  ${{ secrets.ANTHROPIC_API_KEY }}
          GMAIL_ADDRESS:      ${{ secrets.GMAIL_ADDRESS }}
          GMAIL_APP_PASSWORD: ${{ secrets.GMAIL_APP_PASSWORD }}
          MIA_EMAIL:          ${{ secrets.MIA_EMAIL }}
          JAKE_EMAIL:         ${{ secrets.JAKE_EMAIL }}
          YOUTUBE_API_KEY:    ${{ secrets.YOUTUBE_API_KEY }}
          YOUTUBE_CHANNEL_ID: ${{ secrets.YOUTUBE_CHANNEL_ID }}
          INSTAGRAM_ACCESS_TOKEN: ${{ secrets.INSTAGRAM_ACCESS_TOKEN }}
          INSTAGRAM_ACCOUNT_ID:   ${{ secrets.INSTAGRAM_ACCOUNT_ID }}
          TIKTOK_ACCESS_TOKEN:    ${{ secrets.TIKTOK_ACCESS_TOKEN }}

---

# ─────────────────────────────────────────────
# FILE 2: monday_report.yml
# ─────────────────────────────────────────────

name: Monday Analytics Report

on:
  schedule:
    - cron: '0 12 * * 1'   # Monday 7:00 AM ET (12:00 UTC)
  workflow_dispatch:

jobs:
  monday-report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install anthropic
      - run: python analytics_report.py
        env:
          ANTHROPIC_API_KEY:  ${{ secrets.ANTHROPIC_API_KEY }}
          GMAIL_ADDRESS:      ${{ secrets.GMAIL_ADDRESS }}
          GMAIL_APP_PASSWORD: ${{ secrets.GMAIL_APP_PASSWORD }}
          MIA_EMAIL:          ${{ secrets.MIA_EMAIL }}
          JAKE_EMAIL:         ${{ secrets.JAKE_EMAIL }}
          YOUTUBE_API_KEY:    ${{ secrets.YOUTUBE_API_KEY }}
          YOUTUBE_CHANNEL_ID: ${{ secrets.YOUTUBE_CHANNEL_ID }}
          INSTAGRAM_ACCESS_TOKEN: ${{ secrets.INSTAGRAM_ACCESS_TOKEN }}
          INSTAGRAM_ACCOUNT_ID:   ${{ secrets.INSTAGRAM_ACCOUNT_ID }}
          TIKTOK_ACCESS_TOKEN:    ${{ secrets.TIKTOK_ACCESS_TOKEN }}

---

# ─────────────────────────────────────────────
# FILE 3: comment_analyzer.yml
# ─────────────────────────────────────────────

name: Comment Analyzer

on:
  schedule:
    - cron: '0 14 * * *'   # Daily 9:00 AM ET (14:00 UTC)
  workflow_dispatch:

jobs:
  comment-analyzer:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install anthropic
      - run: python comment_analyzer.py
        env:
          ANTHROPIC_API_KEY:   ${{ secrets.ANTHROPIC_API_KEY }}
          GMAIL_ADDRESS:       ${{ secrets.GMAIL_ADDRESS }}
          GMAIL_APP_PASSWORD:  ${{ secrets.GMAIL_APP_PASSWORD }}
          MIA_EMAIL:           ${{ secrets.MIA_EMAIL }}
          JAKE_EMAIL:          ${{ secrets.JAKE_EMAIL }}
          CRISIS_ALERT_EMAIL:  ${{ secrets.CRISIS_ALERT_EMAIL }}
          YOUTUBE_API_KEY:     ${{ secrets.YOUTUBE_API_KEY }}
          YOUTUBE_CHANNEL_ID:  ${{ secrets.YOUTUBE_CHANNEL_ID }}
          INSTAGRAM_ACCESS_TOKEN: ${{ secrets.INSTAGRAM_ACCESS_TOKEN }}
          INSTAGRAM_ACCOUNT_ID:   ${{ secrets.INSTAGRAM_ACCOUNT_ID }}
          TIKTOK_ACCESS_TOKEN:    ${{ secrets.TIKTOK_ACCESS_TOKEN }}

---

# ─────────────────────────────────────────────
# FILE 4: newsletter.yml
# ─────────────────────────────────────────────

name: Newsletter Generator

on:
  schedule:
    - cron: '0 14 * * 4'   # Thursday 9:00 AM ET (14:00 UTC)
  workflow_dispatch:

jobs:
  newsletter:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install anthropic
      - run: python newsletter_gen.py
        env:
          ANTHROPIC_API_KEY:  ${{ secrets.ANTHROPIC_API_KEY }}
          GMAIL_ADDRESS:      ${{ secrets.GMAIL_ADDRESS }}
          GMAIL_APP_PASSWORD: ${{ secrets.GMAIL_APP_PASSWORD }}
          MIA_EMAIL:          ${{ secrets.MIA_EMAIL }}
          YOUTUBE_API_KEY:    ${{ secrets.YOUTUBE_API_KEY }}
          YOUTUBE_CHANNEL_ID: ${{ secrets.YOUTUBE_CHANNEL_ID }}
          INSTAGRAM_ACCESS_TOKEN: ${{ secrets.INSTAGRAM_ACCESS_TOKEN }}
          INSTAGRAM_ACCOUNT_ID:   ${{ secrets.INSTAGRAM_ACCOUNT_ID }}

---

# ─────────────────────────────────────────────
# FILE 5: intake_tracker.yml
# ─────────────────────────────────────────────

name: Intake CTA Tracker

on:
  schedule:
    - cron: '0 13 * * 1'   # Monday 8:00 AM ET (13:00 UTC) — runs after analytics
  workflow_dispatch:

jobs:
  intake-tracker:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install anthropic
      - run: python intake_tracker.py
        env:
          ANTHROPIC_API_KEY:  ${{ secrets.ANTHROPIC_API_KEY }}
          GMAIL_ADDRESS:      ${{ secrets.GMAIL_ADDRESS }}
          GMAIL_APP_PASSWORD: ${{ secrets.GMAIL_APP_PASSWORD }}
          MIA_EMAIL:          ${{ secrets.MIA_EMAIL }}
          LATER_API_KEY:      ${{ secrets.LATER_API_KEY }}
