"""
Generates a short video script using Groq's free-tier LLM API
(OpenAI-compatible endpoint, no cost, generous free rate limits).

Get a free key at https://console.groq.com -> API Keys.
Set it as the GROQ_API_KEY environment variable / GitHub secret.
"""

import os
import json
import urllib.error
import urllib.request
from pathlib import Path

USED_TOPICS_PATH = Path(__file__).resolve().parent.parent / "reports" / "used_topics.json"

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODELS = (
    "llama-3.1-8b-instant",
    "openai/gpt-oss-20b",
    "llama-3.3-70b-versatile",
)


def generate_script(topic: dict) -> dict:
    """
    Returns a dict: {"title": ..., "script": ..., "keywords": [...]}
    'script' is the exact narration text (what the TTS voice will read).
    """
    api_key = os.environ["GROQ_API_KEY"]
    used = []
    if USED_TOPICS_PATH.exists():
        try:
            used = json.loads(USED_TOPICS_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            used = []

    system_prompt = (
        "You write YouTube Shorts for SilentVision, a curiosity channel. "
        "The videos that get traction are specific rare-animal secrets, "
        "weird human-body facts, and concrete space wow facts. "
        "Do not write motivation, finance, self-help, or generic trivia. "
        "Hook in the first sentence. One fact only. Spoken, punchy, 80-110 words. "
        "Only use a widely reported scientific fact. Do not invent numbers, "
        "percentages, or fake mechanisms. If you are not sure, pick a simpler fact. "
        "No stage directions, no emojis in the script. "
        "Title style examples that worked: "
        "'The SHOCKING Truth About Crocodiles Survival Secrets', "
        "'Why You Never See Baby Birds', "
        "'The Teaspoon That Weighs 4 Billion Tons'. "
        "Title must be under 70 characters, no hashtags in the title. "
        "keywords must be concrete stock-footage search terms for that subject "
        "(animal name, habitat, planet, body part), not abstract words. "
        "Output ONLY valid JSON, no markdown fences. "
        "JSON schema: "
        '{"title": "<catchy title>", '
        '"script": "<narration text>", '
        '"keywords": ["<3-5 visual search keywords>"], '
        '"topic_key": "<short lowercase phrase naming the exact fact>"}'
    )

    avoid = "; ".join(used[:40]) if used else "none yet"
    user_prompt = (
        f"Write {topic['prompt_hint']}\n"
        f"Do not reuse any of these already-posted facts: {avoid}"
    )

    last_error = None
    result = None
    for model in GROQ_MODELS:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.9,
            "response_format": {"type": "json_object"},
        }
        req = urllib.request.Request(
            GROQ_API_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "yt-automation/1.0",
                "Accept": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode("utf-8"))
            print(f"Groq model used: {model}")
            break
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")[:400]
            last_error = f"{exc.code} {exc.reason}: {body}"
            print(f"Groq model {model} failed: {last_error}")

    if result is None:
        raise RuntimeError(f"Groq script generation failed: {last_error}")

    content = result["choices"][0]["message"]["content"]
    data = json.loads(content)

    if not data.get("keywords"):
        data["keywords"] = topic["visual_keywords"]

    topic_key = (data.get("topic_key") or data.get("title") or "").strip().lower()
    if topic_key:
        if topic_key not in [str(item).lower() for item in used]:
            used.append(topic_key)
            USED_TOPICS_PATH.parent.mkdir(parents=True, exist_ok=True)
            USED_TOPICS_PATH.write_text(
                json.dumps(used, indent=2),
                encoding="utf-8",
            )

    return data


if __name__ == "__main__":
    from config import pick_topic_for_today

    t = pick_topic_for_today()
    out = generate_script(t)
    print(json.dumps(out, indent=2))
