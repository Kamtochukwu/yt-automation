"""
Generates a short video script using Groq's free-tier LLM API
(OpenAI-compatible endpoint, no cost, generous free rate limits).

Get a free key at https://console.groq.com -> API Keys.
Set it as the GROQ_API_KEY environment variable / GitHub secret.
"""

import os
import json
import urllib.request

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"  # fast + free tier friendly


def generate_script(topic: dict) -> dict:
    """
    Returns a dict: {"title": ..., "script": ..., "keywords": [...]}
    'script' is the exact narration text (what the TTS voice will read).
    """
    api_key = os.environ["GROQ_API_KEY"]

    system_prompt = (
        "You write scripts for viral YouTube Shorts (30-45 seconds spoken). "
        "Output ONLY valid JSON, no markdown fences, no commentary. "
        "JSON schema: "
        '{"title": "<catchy <=60 char title>", '
        '"script": "<narration text only, no stage directions, '
        'no emojis, natural spoken sentences, 80-110 words>", '
        '"keywords": ["<3-5 short visual search keywords for stock footage>"]}'
    )

    user_prompt = f"Write {topic['prompt_hint']}"

    payload = {
        "model": GROQ_MODEL,
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
        },
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    content = result["choices"][0]["message"]["content"]
    data = json.loads(content)

    # basic safety net in case keywords missing
    if not data.get("keywords"):
        data["keywords"] = topic["visual_keywords"]

    return data


if __name__ == "__main__":
    from config import pick_topic_for_today

    t = pick_topic_for_today()
    out = generate_script(t)
    print(json.dumps(out, indent=2))
