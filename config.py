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


VIDEOS_PER_DAY = 3


def pick_topic_for_slot(slot: int = 0):
    """
    Each daily run posts one video per niche. Slot 0, 1, 2 rotate
    through TOPICS, shifted by day-of-year so the order changes.
    """
    import datetime
    day_index = datetime.date.today().timetuple().tm_yday
    return TOPICS[(day_index + int(slot)) % len(TOPICS)]


def pick_topic_for_today():
    return pick_topic_for_slot(0)


# ---- Video settings ----
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920  # vertical, for Shorts
TARGET_DURATION_SECONDS = 45
FONT_SIZE = 70
CAPTION_COLOR = "white"
CAPTION_HIGHLIGHT_COLOR = "#FFD700"

# TTS voice (edge-tts). Full list: `edge-tts --list-voices`
TTS_VOICE = "en-US-GuyNeural"

# Output paths
WORKDIR = "workdir"
