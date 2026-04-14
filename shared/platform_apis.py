# shared/platform_apis.py
"""
Platform API integrations — YouTube, Instagram, TikTok.
Each function fails gracefully if credentials aren't set yet.
Layer 1 (no APIs): returns empty data, pipeline continues.
Layer 2 (APIs active): returns real data.
"""

import json
import urllib.request
import urllib.parse
from shared.config import (
    YOUTUBE_API_KEY, YOUTUBE_CHANNEL_ID,
    INSTAGRAM_ACCESS_TOKEN, INSTAGRAM_ACCOUNT_ID,
    TIKTOK_ACCESS_TOKEN
)


def api_available(key: str) -> bool:
    return bool(key and key != "")


# ─────────────────────────────────────────────
# YOUTUBE
# ─────────────────────────────────────────────

def get_youtube_analytics() -> dict:
    """
    Fetch YouTube channel analytics.
    Returns empty dict if API key not set.
    """
    if not api_available(YOUTUBE_API_KEY) or not api_available(YOUTUBE_CHANNEL_ID):
        print("⚠ YouTube API not configured — skipping analytics")
        return {}

    try:
        url = (
            f"https://www.googleapis.com/youtube/v3/channels"
            f"?part=statistics&id={YOUTUBE_CHANNEL_ID}&key={YOUTUBE_API_KEY}"
        )
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read())

        stats = data["items"][0]["statistics"]
        return {
            "subscribers":   int(stats.get("subscriberCount", 0)),
            "total_views":   int(stats.get("viewCount", 0)),
            "video_count":   int(stats.get("videoCount", 0)),
        }
    except Exception as e:
        print(f"⚠ YouTube analytics error: {e}")
        return {}


def get_youtube_top_videos(max_results: int = 5) -> list:
    """Fetch recent video performance."""
    if not api_available(YOUTUBE_API_KEY) or not api_available(YOUTUBE_CHANNEL_ID):
        return []

    try:
        # Get recent videos
        search_url = (
            f"https://www.googleapis.com/youtube/v3/search"
            f"?part=snippet&channelId={YOUTUBE_CHANNEL_ID}"
            f"&maxResults={max_results}&order=date&type=video&key={YOUTUBE_API_KEY}"
        )
        with urllib.request.urlopen(search_url) as r:
            search_data = json.loads(r.read())

        video_ids = [item["id"]["videoId"] for item in search_data.get("items", [])]
        if not video_ids:
            return []

        # Get stats for those videos
        stats_url = (
            f"https://www.googleapis.com/youtube/v3/videos"
            f"?part=statistics,snippet&id={','.join(video_ids)}&key={YOUTUBE_API_KEY}"
        )
        with urllib.request.urlopen(stats_url) as r:
            stats_data = json.loads(r.read())

        videos = []
        for item in stats_data.get("items", []):
            videos.append({
                "title":     item["snippet"]["title"],
                "views":     int(item["statistics"].get("viewCount", 0)),
                "likes":     int(item["statistics"].get("likeCount", 0)),
                "comments":  int(item["statistics"].get("commentCount", 0)),
                "published": item["snippet"]["publishedAt"][:10],
            })
        return sorted(videos, key=lambda x: x["views"], reverse=True)

    except Exception as e:
        print(f"⚠ YouTube video fetch error: {e}")
        return []


def get_youtube_comments(max_results: int = 100) -> list:
    """Fetch recent comments across channel videos."""
    if not api_available(YOUTUBE_API_KEY) or not api_available(YOUTUBE_CHANNEL_ID):
        return []

    try:
        videos = get_youtube_top_videos(max_results=10)
        all_comments = []

        for video in videos[:5]:  # limit to top 5 videos
            video_id = video.get("id", "")
            if not video_id:
                continue

            url = (
                f"https://www.googleapis.com/youtube/v3/commentThreads"
                f"?part=snippet&videoId={video_id}"
                f"&maxResults=20&order=relevance&key={YOUTUBE_API_KEY}"
            )
            with urllib.request.urlopen(url) as r:
                data = json.loads(r.read())

            for item in data.get("items", []):
                comment = item["snippet"]["topLevelComment"]["snippet"]
                all_comments.append({
                    "text":   comment["textDisplay"],
                    "likes":  comment["likeCount"],
                    "video":  video.get("title", ""),
                })

        return sorted(all_comments, key=lambda x: x["likes"], reverse=True)

    except Exception as e:
        print(f"⚠ YouTube comments error: {e}")
        return []


# ─────────────────────────────────────────────
# INSTAGRAM
# ─────────────────────────────────────────────

def get_instagram_analytics() -> dict:
    """Fetch Instagram account insights."""
    if not api_available(INSTAGRAM_ACCESS_TOKEN) or not api_available(INSTAGRAM_ACCOUNT_ID):
        print("⚠ Instagram API not configured — skipping analytics")
        return {}

    try:
        url = (
            f"https://graph.instagram.com/{INSTAGRAM_ACCOUNT_ID}"
            f"?fields=followers_count,media_count&access_token={INSTAGRAM_ACCESS_TOKEN}"
        )
        with urllib.request.urlopen(url) as r:
            data = json.loads(r.read())

        return {
            "followers":    data.get("followers_count", 0),
            "media_count":  data.get("media_count", 0),
        }
    except Exception as e:
        print(f"⚠ Instagram analytics error: {e}")
        return {}


def get_instagram_top_posts(limit: int = 5) -> list:
    """Fetch recent Instagram post performance."""
    if not api_available(INSTAGRAM_ACCESS_TOKEN) or not api_available(INSTAGRAM_ACCOUNT_ID):
        return []

    try:
        url = (
            f"https://graph.instagram.com/{INSTAGRAM_ACCOUNT_ID}/media"
            f"?fields=id,caption,like_count,comments_count,timestamp,media_type"
            f"&limit={limit}&access_token={INSTAGRAM_ACCESS_TOKEN}"
        )
        with urllib.request.urlopen(url) as r:
            data = json.loads(r.read())

        posts = []
        for item in data.get("data", []):
            posts.append({
                "caption":   (item.get("caption", "")[:80] + "...") if item.get("caption") else "",
                "likes":     item.get("like_count", 0),
                "comments":  item.get("comments_count", 0),
                "type":      item.get("media_type", ""),
                "date":      item.get("timestamp", "")[:10],
            })
        return posts

    except Exception as e:
        print(f"⚠ Instagram posts error: {e}")
        return []


# ─────────────────────────────────────────────
# TIKTOK
# ─────────────────────────────────────────────

def get_tiktok_analytics() -> dict:
    """
    Fetch TikTok account analytics.
    NOTE: Apply for TikTok API after 2 weeks of posting.
    """
    if not api_available(TIKTOK_ACCESS_TOKEN):
        print("⚠ TikTok API not configured — skipping analytics")
        return {}

    try:
        url = "https://open.tiktokapis.com/v2/user/info/?fields=follower_count,following_count,video_count"
        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {TIKTOK_ACCESS_TOKEN}"}
        )
        with urllib.request.urlopen(req) as r:
            data = json.loads(r.read())

        user = data.get("data", {}).get("user", {})
        return {
            "followers":    user.get("follower_count", 0),
            "following":    user.get("following_count", 0),
            "video_count":  user.get("video_count", 0),
        }
    except Exception as e:
        print(f"⚠ TikTok analytics error: {e}")
        return {}


# ─────────────────────────────────────────────
# AGGREGATED ANALYTICS
# ─────────────────────────────────────────────

def get_all_analytics() -> dict:
    """
    Pull analytics from all platforms.
    Returns whatever is available — gracefully skips unconfigured platforms.
    """
    return {
        "youtube":   get_youtube_analytics(),
        "instagram": get_instagram_analytics(),
        "tiktok":    get_tiktok_analytics(),
        "top_youtube_videos": get_youtube_top_videos(),
        "top_instagram_posts": get_instagram_top_posts(),
    }


def get_all_comments() -> list:
    """Pull comments from all available platforms."""
    comments = []
    comments.extend(get_youtube_comments())
    # TikTok and Instagram comment APIs added here when access approved
    return comments


def analytics_available() -> bool:
    """Check if any platform analytics are configured."""
    return any([
        api_available(YOUTUBE_API_KEY),
        api_available(INSTAGRAM_ACCESS_TOKEN),
        api_available(TIKTOK_ACCESS_TOKEN),
    ])
