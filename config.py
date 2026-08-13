"""
Central config for the daily Shorts automation.
Edit TOPICS to add/remove niches. The bot rotates through them
so you get variety instead of the same niche every day.
"""

import random
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

# SilentVision traction: rare animals, human-body oddities, and space wow
# facts outperform motivation and finance by a wide margin.
TOPICS = [
    {
        "niche": "rare_animals",
        "prompt_hint": (
            "one surprising, verifiable fact about a rare, weird, or "
            "extreme animal. Pick a specific creature people have not "
            "heard of, or a known animal with a shocking survival trick. "
            "Make it feel like a nature documentary secret, not a kids show."
        ),
        "visual_keywords": [
            "wildlife closeup",
            "jungle animal",
            "ocean creature",
            "frog rainforest",
            "crocodile river",
        ],
        "hashtags": "#curiosity #education #facts #science #shorts",
    },
    {
        "niche": "human_body",
        "prompt_hint": (
            "one surprising, verifiable fact about the human body or brain. "
            "Something people feel every day but never understood, like a "
            "hidden organ trick, a sense glitch, or a survival leftover."
        ),
        "visual_keywords": [
            "human eye closeup",
            "brain scan",
            "heartbeat",
            "hands closeup",
            "medical science",
        ],
        "hashtags": "#curiosity #education #facts #science #shorts",
    },
    {
        "niche": "space_wow",
        "prompt_hint": (
            "one surprising, verifiable space fact with a concrete image "
            "people can picture: a planet, star, moon, astronaut body "
            "change, or cosmic object. Avoid vague 'space is big' lines."
        ),
        "visual_keywords": [
            "outer space stars",
            "earth from space",
            "astronaut",
            "galaxy nebula",
            "moon surface",
        ],
        "hashtags": "#curiosity #education #spacefacts #science #shorts",
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
