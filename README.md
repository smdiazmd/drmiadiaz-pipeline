# @drmiadiaz Content Pipeline

Fully automated content operations for Dr. Mia Diaz across TikTok, Instagram, YouTube, and LinkedIn.

One GitHub repository. Runs automatically. Zero manual input once configured.

---

## What this does

| When | What runs | Who gets it |
|---|---|---|
| Every Saturday 6 AM ET | Trend scan + 4 short-form scripts + long-form script + all captions + posting schedule + Instagram stories + collab radar | Jake + Mia |
| Every Monday 7 AM ET | Analytics report from all platforms | Jake + Mia |
| Every Monday 8 AM ET | Welmivia intake CTA report (activates Day 60) | Mia only |
| Every Thursday 9 AM ET | Weekly newsletter draft (activates Day 30) | Mia only |
| Every day 9 AM ET | Comment analysis + crisis detection | Jake (+ Mia for crisis) |
| Immediately when triggered | Crisis comment alert | Jake + Mia |
| Week 1 only | Platform bios + intro scripts for all platforms | Jake + Mia |

---

## Layer 1 vs Layer 2

This pipeline is built in two layers so you can run it today without waiting for API approvals.

**Layer 1 — runs today (no platform APIs needed):**
- Saturday batch (scripts, captions, schedule, stories, collabs)
- Newsletter generator
- Placeholder analytics report

**Layer 2 — activates as APIs are approved:**
- Real analytics from YouTube, Instagram, TikTok
- Automatic comment pulling and analysis
- Bio link click tracking via Later

Each platform module activates automatically when you add its credentials as a GitHub secret. No code changes needed.

---

## Step 1 — Create a new private GitHub repo

1. Go to [github.com](https://github.com) → click **+** → **New repository**
2. Name it: `drmiadiaz-pipeline`
3. Set to **Private**
4. Check **Add a README file**
5. Click **Create repository**

---

## Step 2 — Upload files

Your repo needs this exact structure:

```
drmiadiaz-pipeline/
├── saturday_batch.py
├── analytics_report.py
├── comment_analyzer.py
├── newsletter_gen.py
├── intake_tracker.py
├── requirements.txt
├── shared/
│   ├── config.py
│   ├── prompts.py
│   ├── email_utils.py
│   └── platform_apis.py
└── .github/
    └── workflows/
        ├── saturday_batch.yml
        ├── monday_report.yml
        ├── comment_analyzer.yml
        ├── newsletter.yml
        └── intake_tracker.yml
```

**Easiest way — use GitHub Desktop:**
1. Download [GitHub Desktop](https://desktop.github.com) — free app
2. Click **Clone a repository** → find your new repo → choose a folder on your computer
3. Open that folder. Copy ALL files from the zip into it (maintaining the folder structure)
4. In GitHub Desktop you'll see all the files listed as changes
5. Type "Initial upload" in the Summary box → click **Commit to main** → click **Push origin**

Done. All files are now in GitHub.

---

## Step 3 — Add GitHub Secrets

Go to your repo → **Settings → Secrets and variables → Actions → New repository secret**

### Layer 1 secrets (add these today — required to run):

| Secret Name | Value | Notes |
|---|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic API key | From console.anthropic.com → API Keys |
| `GMAIL_ADDRESS` | your@gmail.com | The Gmail that sends the emails |
| `GMAIL_APP_PASSWORD` | 16-char app password | See Gmail App Password setup below |
| `MIA_EMAIL` | mia's inbox email | Where Mia receives reports |
| `JAKE_EMAIL` | jake's inbox email | Where Jake receives batch briefs |
| `CRISIS_ALERT_EMAIL` | jake's email or phone-email | For immediate crisis alerts — can be same as JAKE_EMAIL |

### Layer 2 secrets (add when APIs are approved):

| Secret Name | Platform | When to add |
|---|---|---|
| `YOUTUBE_API_KEY` | YouTube | Same day (see YouTube API setup below) |
| `YOUTUBE_CHANNEL_ID` | YouTube | Same day |
| `INSTAGRAM_ACCESS_TOKEN` | Instagram | After 1–3 days of posting |
| `INSTAGRAM_ACCOUNT_ID` | Instagram | Same time as access token |
| `TIKTOK_ACCESS_TOKEN` | TikTok | After 2 weeks of posting |
| `LATER_API_KEY` | Later | When Welmivia CTA goes live (Day 60) |

---

## Gmail App Password setup

1. Go to [myaccount.google.com/security](https://myaccount.google.com/security)
2. Enable **2-Step Verification** if not already on
3. Search for **"App passwords"**
4. Create one → label it `Content Pipeline`
5. Copy the 16-character password (shown once only)
6. Paste into `GMAIL_APP_PASSWORD` secret — no spaces

---

## YouTube API setup (do this today — same-day approval)

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Click **Select a project** → **New Project** → name it `drmiadiaz` → **Create**
3. In the search bar, search **"YouTube Data API v3"** → click it → click **Enable**
4. Click **Create Credentials** → **API Key**
5. Copy the key → add as `YOUTUBE_API_KEY` secret in GitHub
6. To find your Channel ID: go to [youtube.com](https://youtube.com) → your channel → the URL will contain your channel ID (starts with `UC...`) → add as `YOUTUBE_CHANNEL_ID`

---

## Instagram API setup (do after first week of posting)

1. Go to [developers.facebook.com](https://developers.facebook.com)
2. Click **My Apps** → **Create App** → choose **Business** type
3. Add **Instagram Graph API** product
4. Connect your Instagram account (must be a Professional/Creator account)
5. Generate a long-lived access token
6. Add as `INSTAGRAM_ACCESS_TOKEN` and `INSTAGRAM_ACCOUNT_ID` secrets

**Note:** Instagram requires a business/creator account. Switch in Instagram Settings → Account → Switch to Professional Account if not already done.

---

## TikTok API setup (do after 2 weeks of posting)

1. Go to [developers.tiktok.com](https://developers.tiktok.com)
2. Apply for **Content Posting API** and **Research API**
3. Wait for approval (3–7 days)
4. Generate access token
5. Add as `TIKTOK_ACCESS_TOKEN` secret

**Why wait:** TikTok's API review looks at account history. Applying on a brand new account often gets delayed. After 2 weeks of posting you'll have a much smoother approval.

---

## Later API setup (Day 60 — when Welmivia CTA goes live)

1. Log into [later.com](https://later.com)
2. Go to **Settings → API**
3. Generate API key
4. Add as `LATER_API_KEY` secret

---

## Step 4 — Test it

1. Go to your repo → **Actions** tab
2. Click **Saturday Batch Brief** in the left list
3. Click **Run workflow** → **Run workflow**
4. Wait ~3–5 minutes (this one is longer — it generates a lot)
5. Check both Jake and Mia's inboxes

---

## How the 90-day plan auto-tracking works

The pipeline knows what day of the plan it is based on the `LAUNCH_DATE` in `shared/config.py`. 

It automatically:
- Adds soft Welmivia mentions starting Day 45
- Activates full Welmivia CTAs on Day 60
- Starts the newsletter on Day 30
- Starts the intake tracker on Day 60
- Generates intro content in Week 1 only

**If your launch date changed from April 10:** Open `shared/config.py` and update line:
```python
LAUNCH_DATE = date(2026, 4, 10)
```

---

## Customizing content

**Add topics to the short-form rotation:**
Edit `CONTENT_PILLARS` in `shared/config.py`

**Update long-form YouTube schedule:**
Edit `LONGFORM_SCHEDULE` in `shared/config.py`

**Change system prompts / voice:**
Edit `shared/prompts.py` — all Claude instructions live here

**Change posting times:**
Edit `POSTING_SCHEDULE` in `shared/config.py`

---

## What Jake's week looks like

| Day | What arrives | Jake's action |
|---|---|---|
| Saturday AM | Batch brief email | Reviews scripts, loads teleprompter, preps Sunday |
| Sunday | Films per batch brief | Uploads to Vizard, edits in CapCut, schedules in Later |
| Monday AM | Analytics report | Reviews with Mia, notes priorities |
| Daily 9 AM | Comment report | Reviews flags, sends replies |
| Thursday AM | Newsletter draft (Day 30+) | Forwards to Mia for approval |
| Any time | Crisis alert | Responds immediately with ;;crisis |

---

## Cost estimate

| Service | Cost |
|---|---|
| GitHub Actions | Free (each run uses 2–5 min of free tier's 2,000/month) |
| Anthropic API | ~$0.10–0.20 per Saturday batch · ~$0.02 per other run |
| Gmail SMTP | Free |
| YouTube API | Free (10,000 units/day free tier) |
| Instagram API | Free |
| TikTok API | Free |

**Estimated monthly total: $3–8/month** (almost entirely Anthropic API)

---

## Troubleshooting

**"Module not found: shared"**
→ Make sure the `shared/` folder uploaded correctly with all 4 files inside it.

**Saturday batch runs but email doesn't arrive**
→ Check Gmail App Password. Check spam folder. Confirm MIA_EMAIL and JAKE_EMAIL secrets are set.

**Analytics report shows "APIs not configured"**
→ Normal until you add platform API keys. Layer 1 still works fully.

**Crisis alert not working**
→ Confirm CRISIS_ALERT_EMAIL secret is set. Can be same as JAKE_EMAIL.

**Wrong plan day**
→ Update LAUNCH_DATE in shared/config.py to match your actual Day 1.
