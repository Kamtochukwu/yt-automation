"""
Central config for the daily Shorts automation.

SilentVision posts one niche only: hidden mechanisms in the viewer's body.
YouTube can then recognize the channel and keep sending it to that audience.
Animals, space, motivation, and finance are off the table.
"""

from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

CHANNEL_NICHE = "human_body"
CHANNEL_HASHTAGS = "#humanbody #bodyfacts #curiosity #education #science #shorts"

# Same niche, different body systems. Morning gets the proven skin/senses lane.
BODY_ANGLES = (
    {
        "angle": "skin_senses",
        "prompt_hint": (
            "one surprising, verifiable fact about skin, eyes, pain, touch, "
            "smell, taste, hearing, or another sense. The viewer must be able "
            "to feel or picture it happening on their own body right now."
        ),
        "visual_keywords": [
            "human skin closeup",
            "human eye closeup",
            "hands closeup",
            "person blinking",
            "fingerprint skin",
        ],
    },
    {
        "angle": "organs_blood",
        "prompt_hint": (
            "one surprising, verifiable fact about the gut, stomach, liver, "
            "heart, lungs, blood, or immune system. Something happening inside "
            "the viewer right now, not a textbook organ tour."
        ),
        "visual_keywords": [
            "heartbeat",
            "blood cells microscope",
            "human stomach",
            "person breathing",
            "medical science",
        ],
    },
    {
        "angle": "bones_nerves",
        "prompt_hint": (
            "one surprising, verifiable fact about bones, muscles, nerves, "
            "healing, or a leftover from evolution the viewer still has. "
            "Make it about their body, not a museum skeleton."
        ),
        "visual_keywords": [
            "human skeleton",
            "muscles closeup",
            "spine xray",
            "hands tendons",
            "medical science",
        ],
    },
)

# Kept so older imports and docs still resolve. Always the body niche.
TOPICS = [
    {
        "niche": CHANNEL_NICHE,
        "prompt_hint": BODY_ANGLES[0]["prompt_hint"],
        "visual_keywords": BODY_ANGLES[0]["visual_keywords"],
        "hashtags": CHANNEL_HASHTAGS,
    }
]


VIDEOS_PER_DAY = 3

# One Short per window so uploads are spaced, not dumped at once.
# Times are UTC. Nigeria is UTC+1, so these land at 8am / 3pm / 9pm.
POST_WINDOWS = (
    {"name": "morning", "utc_hour": 7},
    {"name": "afternoon", "utc_hour": 14},
    {"name": "night", "utc_hour": 20},
)
SLOT_NAMES = {window["name"]: index for index, window in enumerate(POST_WINDOWS)}


def slot_for_now(name: str | None = None) -> int:
    """
    Map a window name or the current UTC hour to slot 0, 1, or 2.
    Morning < 11:00 UTC, afternoon < 17:00 UTC, otherwise night.
    """
    if name:
        key = name.strip().lower()
        if key.isdigit():
            return max(0, min(VIDEOS_PER_DAY - 1, int(key)))
        if key in SLOT_NAMES:
            return SLOT_NAMES[key]

    from datetime import datetime, timezone

    hour = datetime.now(timezone.utc).hour
    if hour < 11:
        return 0
    if hour < 17:
        return 1
    return 2


def pick_topic_for_slot(slot: int = 0):
    """
    Every slot is the human-body niche. Slot only changes the body system
    so three daily posts stay on-topic without repeating skin three times.
    Morning = skin/senses, afternoon = organs, night = bones/nerves.
    """
    angle = BODY_ANGLES[int(slot) % len(BODY_ANGLES)]
    return {
        "niche": CHANNEL_NICHE,
        "angle": angle["angle"],
        "prompt_hint": angle["prompt_hint"],
        "visual_keywords": list(angle["visual_keywords"]),
        "hashtags": CHANNEL_HASHTAGS,
    }


def pick_topic_for_today():
    return pick_topic_for_slot(slot_for_now())


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
