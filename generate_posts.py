#!/usr/bin/env python3
"""
SarvamNee — Auto Post Generator
================================
Step 1: Run yt-dlp to extract playlist data:
    pip install yt-dlp
    yt-dlp --flat-playlist --print "%(title)s|%(id)s|%(upload_date)s" \
        "https://www.youtube.com/playlist?list=PLhKUGqdBdKFu93TWt0RzMvV81RiezduVX" \
        > playlist.txt

Step 2: Run this script:
    python generate_posts.py

It will create one .md file in _posts/ for each video.
"""

import os
import re
from datetime import datetime

# ── CONFIG ────────────────────────────────────────────────────────────
PLAYLIST_FILE = "playlist.txt"     # output from yt-dlp
POSTS_DIR     = "_posts"
DEFAULT_CAT   = "murugan"          # default category for this playlist

# Keyword → category mapping (edit freely)
CATEGORY_RULES = {
    "murugan":     ["முருகன்", "murugan", "potri", "போற்றி", "thirupugal", "thiruppugazh",
                    "kandha", "skandha", "subramanya", "vel", "வேல்"],
    "shiva":       ["சிவன்", "shiva", "thevaram", "தேவாரம்", "pradosham", "பிரதோஷம்",
                    "thiruvasagam", "lingam", "nataraja"],
    "vishnu":      ["விஷ்ணு", "vishnu", "narayana", "perumal", "thiruppavai", "azhwar"],
    "narayaniyam": ["நாராயணீயம்", "narayaniyam", "dasaka", "தசகம்"],
    "amman":       ["அம்மன்", "amman", "devi", "lakshmi", "saraswathi", "durga", "parvathi"],
    "thevaram":    ["தேவாரம்", "thevaram", "thirumurai"],
    "viratham":    ["விரதம்", "viratham", "ekadasi", "ஏகாதசி", "kanda sashti", "karthigai"],
}

EMOJI = {
    "murugan": "🦚", "shiva": "🌙", "vishnu": "🪷",
    "amman": "🔱", "narayaniyam": "📿", "thevaram": "🎵",
    "viratham": "🪔",
}

# ── HELPERS ───────────────────────────────────────────────────────────

def detect_category(title: str) -> str:
    title_lower = title.lower()
    for cat, keywords in CATEGORY_RULES.items():
        for kw in keywords:
            if kw.lower() in title_lower:
                return cat
    return DEFAULT_CAT


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:60]


def parse_date(raw: str) -> str:
    """Convert yt-dlp date YYYYMMDD → YYYY-MM-DD. Fallback to today."""
    try:
        return datetime.strptime(raw.strip(), "%Y%m%d").strftime("%Y-%m-%d")
    except Exception:
        return datetime.today().strftime("%Y-%m-%d")


def make_post(title: str, video_id: str, date_str: str) -> str:
    category = detect_category(title)
    tags = [category, "tamil devotional", "sarvamnee"]
    tags_yaml = "[" + ", ".join(tags) + "]"

    return f"""---
layout: post
title: "{title}"
date: {date_str}
category: {category}
youtube_id: "{video_id}"
tags: {tags_yaml}
description: "{title} — SarvamNee YouTube Channel"
---

## வீடியோ குறிப்புகள் | Video Notes

- **வகை:** {category.capitalize()}
- **சேனல்:** SarvamNee
- **YouTube:** [காண்க](https://www.youtube.com/watch?v={video_id})

> 🙏 மேலும் வீடியோக்களுக்கு எங்கள் [YouTube சேனலை](https://www.youtube.com/@SarvamNee) பின்தொடருங்கள்.
"""


# ── MAIN ──────────────────────────────────────────────────────────────

def main():
    os.makedirs(POSTS_DIR, exist_ok=True)

    if not os.path.exists(PLAYLIST_FILE):
        print(f"ERROR: '{PLAYLIST_FILE}' not found.")
        print()
        print("Run this first:")
        print("  yt-dlp --flat-playlist --print '%(title)s|%(id)s|%(upload_date)s' \\")
        print("    'https://www.youtube.com/playlist?list=PLhKUGqdBdKFu93TWt0RzMvV81RiezduVX' \\")
        print("    > playlist.txt")
        return

    created = 0
    skipped = 0

    with open(PLAYLIST_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split("|")
            if len(parts) < 2:
                print(f"  SKIP (bad format): {line}")
                skipped += 1
                continue

            title    = parts[0].strip()
            video_id = parts[1].strip()
            date_raw = parts[2].strip() if len(parts) > 2 else ""
            date_str = parse_date(date_raw)

            slug     = slugify(title) or video_id
            filename = f"{date_str}-{slug}.md"
            filepath = os.path.join(POSTS_DIR, filename)

            if os.path.exists(filepath):
                print(f"  EXISTS: {filename}")
                skipped += 1
                continue

            content = make_post(title, video_id, date_str)
            with open(filepath, "w", encoding="utf-8") as out:
                out.write(content)

            print(f"  CREATED: {filename}")
            created += 1

    print()
    print(f"Done! {created} posts created, {skipped} skipped.")
    print(f"Now run: bundle exec jekyll serve")


if __name__ == "__main__":
    main()
