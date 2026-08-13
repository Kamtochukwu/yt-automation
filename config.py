"""
Central config for the daily Shorts automation.
Edit TOPICS to add/remove niches. The bot rotates through them
so you get variety instead of the same niche every day.
"""

import random
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

TOPICS = [
    {
        "niche": "motivation",
        "prompt_hint": "a short, punchy motivational message about discipline, "
                        "resilience, or personal growth. Make it feel like a "
                        "wake-up call, not a generic quote.",
        "visual_keywords": ["sunrise", "running", "mountain climb", "city hustle"],
        "hashtags": "#motivation #mindset #discipline #shorts",
    },
    {
        "niche": "news_facts_trivia",
        "prompt_hint": "one surprising, verifiable, and interesting fact about "
                        "science, history, or the world that most people don't know.",
        "visual_keywords": ["space", "nature timelapse", "technology", "abstract"],
        "hashtags": "#didyouknow #facts #trivia #shorts",
    },
    {
        "niche": "finance_tech_tips",
        "prompt_hint": "one practical, beginner-friendly tip about personal finance, "
                        "saving money, or a useful tech/productivity trick.",
        "visual_keywords": ["laptop coding", "money", "office work", "smartphone app"],
        "hashtags": "#finance #moneytips #tech #shorts",
    },
]


def pick_topic_for_today():
    """
    Deterministic-ish rotation: pick topic based on day-of-year so it's
    different every day but reproducible if the workflow re-runs.
    Falls back to random if you'd rather have full randomness.
    """
    import datetime
    day_index = datetime.date.today().timetuple().tm_yday
    return TOPICS[day_index % len(TOPICS)]


# ---- Video settings ----
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920  # vertical, for Shorts
TARGET_DURATION_SECONDS = 40  # keep it short-form friendly (under 60s)
FONT_SIZE = 70
CAPTION_COLOR = "white"
CAPTION_HIGHLIGHT_COLOR = "#FFD700"

# TTS voice (edge-tts). Full list: `edge-tts --list-voices`
TTS_VOICE = "en-US-GuyNeural"

# Output paths
WORKDIR = "workdir"
