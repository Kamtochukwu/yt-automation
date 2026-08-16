"""
Converts the script text to speech using edge-tts (free, no API key,
uses Microsoft Edge's online neural voices).

Also captures word-boundary timing so we can render karaoke-style
captions synced to the audio.

Install: pip install edge-tts
"""

import asyncio
import edge_tts

from config import TTS_VOICE


async def _synthesize(text: str, out_mp3: str):
    communicate = edge_tts.Communicate(text, TTS_VOICE)
    word_timings = []

    with open(out_mp3, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                word_timings.append(
                    {
                        "word": chunk["text"],
                        "start": chunk["offset"] / 10_000_000,  # 100ns -> s
                        "duration": chunk["duration"] / 10_000_000,
                    }
                )
    return word_timings


def generate_audio(text: str, out_mp3: str) -> tuple[list, float]:
    """
    Writes narration audio to out_mp3.
    Returns (word_timings, spoken_duration_seconds).
    """
    timings = asyncio.run(_synthesize(text, out_mp3))
    if timings:
        last = timings[-1]
        duration = last["start"] + last["duration"]
    else:
        duration = 0.0
    print(f"Narration duration: {duration:.1f}s")
    return timings, duration


if __name__ == "__main__":
    import json

    sample = "This is a quick test of the free text to speech engine."
    timings, duration = generate_audio(sample, "test.mp3")
    print("duration", duration)
    print(json.dumps(timings, indent=2))
