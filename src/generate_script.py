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

from config import END_CTA, TARGET_DURATION_SECONDS

USED_TOPICS_PATH = Path(__file__).resolve().parent.parent / "reports" / "used_topics.json"

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODELS = (
    "llama-3.3-70b-versatile",
    "openai/gpt-oss-20b",
    "llama-3.1-8b-instant",
)
# Counted after the follow CTA is attached. ~2.7 words/sec on GuyNeural
# lands 122-140 words near 45 seconds.
MIN_SCRIPT_WORDS = 122
MAX_SCRIPT_WORDS = 148
SCRIPT_ATTEMPTS = 6

# Reject drafts that would split the channel away from body facts.
OFF_NICHE_WORDS = (
    "squid",
    "frog",
    "shark",
    "mole",
    "giraffe",
    "axolotl",
    "crocodile",
    "aardvark",
    "okapi",
    "jellyfish",
    "planet",
    "moon",
    "galaxy",
    "astronaut",
    "supernova",
    "neutron",
    "motivation",
    "rise up",
    "invest",
    "crypto",
    "millionaire",
)


def _on_niche(candidate: dict) -> str | None:
    """Return a reject reason, or None if the draft stays on the body niche."""
    title = (candidate.get("title") or "").strip()
    title_l = title.lower()
    if "you" not in title_l and "your" not in title_l:
        return "title missing You/Your"
    for word in OFF_NICHE_WORDS:
        if word in title_l:
            return f"off-niche title word: {word}"
    return None


def _with_cta(script: str) -> str:
    """Make sure the spoken follow line is at the end, once."""
    text = (script or "").strip()
    lowered = text.lower()
    if "follow this channel" in lowered or "subscribe" in lowered:
        return text
    if text and text[-1] not in ".!?":
        text += "."
    return f"{text} {END_CTA}".strip()


def record_used_topic(topic_key: str) -> None:
    """Remember a fact only after the Short is long enough to upload."""
    key = (topic_key or "").strip().lower()
    if not key:
        return
    used = []
    if USED_TOPICS_PATH.exists():
        try:
            used = json.loads(USED_TOPICS_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            used = []
    if key in [str(item).lower() for item in used]:
        return
    used.append(key)
    USED_TOPICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    USED_TOPICS_PATH.write_text(json.dumps(used, indent=2), encoding="utf-8")


def generate_script(topic: dict, length_hint: str = "") -> dict:
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
        "You write YouTube Shorts for SilentVision. "
        "This channel is ONLY about hidden mechanisms inside the viewer's body. "
        "Every video must be about their skin, senses, organs, blood, bones, "
        "muscles, nerves, healing, or a leftover from human evolution. "
        "Never write about animals, space, planets, stars, the moon, "
        "motivation, finance, self-help, or generic trivia. "
        "Never write vague brain philosophy like 'your brain is lying' "
        "or 'the brain is so cool'. Pick one body part and one mechanism. "
        "Structure the narration in this order: "
        "1) HOOK: first sentence, 8-12 words, a stop-the-scroll claim. "
        "Open with a contradiction or a fact that sounds impossible. "
        "Never start with Did you know, Imagine, What if, Hey, or Welcome. "
        "2) PAYOFF: one widely reported scientific fact with a concrete "
        "image the viewer can feel on their own body. "
        "3) TWIST: the weirder detail that makes the fact land. "
        "4) CLOSE: one short fact payoff. Do not ask people to follow, "
        "subscribe, like, or comment. A follow line is added after you write. "
        f"Spoken length must land near {TARGET_DURATION_SECONDS} seconds: "
        "write 115-135 words, punchy, out loud, no filler. "
        "Only use a widely reported scientific fact. Do not invent numbers, "
        "percentages, or fake mechanisms. If you are not sure, pick a simpler fact. "
        "No stage directions, no emojis in the script. "
        "Title MUST contain You or Your. Under 70 characters. No hashtags. "
        "No emojis. Name the body part and the hidden mechanism. "
        "Title style examples that worked: "
        "'Your Skin is a Supercomputer', "
        "'You Are Born with 300 Pain Sensors in Your Eyes', "
        "'Why Your Brain Can't Feel Pain', "
        "'Your Gut Controls Your Mood', "
        "'Why You Can't Tickle Yourself', "
        "'Bones Remember Your Life'. "
        "keywords must be concrete stock-footage search terms for that "
        "body part (human eye closeup, skin texture, heartbeat, hands, "
        "blood vessels), not abstract words. "
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
        f"Title must use You or Your, like 'Your Skin is a Supercomputer'. "
        f"Make the hook the strongest line in the script. "
        f"Target about {TARGET_DURATION_SECONDS} seconds spoken. "
        f"Write enough for a {TARGET_DURATION_SECONDS} second read-aloud: "
        f"{MIN_SCRIPT_WORDS - 12}-{MAX_SCRIPT_WORDS - 12} words before the follow line. "
        f"Do not reuse any of these already-posted facts: {avoid}"
    )
    if length_hint:
        user_prompt += f"\n{length_hint}"

    last_error = None
    data = None
    for attempt in range(SCRIPT_ATTEMPTS):
        model = GROQ_MODELS[attempt % len(GROQ_MODELS)]
        extra = ""
        if attempt > 0:
            extra = (
                f" Previous draft was the wrong length. Rewrite it to "
                f"{MIN_SCRIPT_WORDS}-{MAX_SCRIPT_WORDS} spoken words including "
                f"a natural ending. Expand the payoff and twist with concrete "
                f"body detail. Do not pad with filler."
            )
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt + extra},
            ],
            "temperature": 0.7,
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
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")[:400]
            last_error = f"{exc.code} {exc.reason}: {body}"
            print(f"Groq model {model} failed: {last_error}")
            continue

        content = result["choices"][0]["message"]["content"]
        try:
            candidate = json.loads(content)
        except json.JSONDecodeError as exc:
            last_error = f"invalid JSON from {model}: {exc}"
            print(last_error)
            continue

        candidate["script"] = _with_cta(candidate.get("script") or "")
        script = candidate["script"]
        word_count = len(script.split())
        print(f"Groq model used: {model} ({word_count} words with CTA)")
        niche_fail = _on_niche(candidate)
        if niche_fail:
            last_error = f"{model} off-niche: {niche_fail}"
            print(last_error)
            continue
        if word_count < MIN_SCRIPT_WORDS or word_count > MAX_SCRIPT_WORDS:
            last_error = (
                f"{model} wrote {word_count} words, "
                f"need {MIN_SCRIPT_WORDS}-{MAX_SCRIPT_WORDS}"
            )
            print(last_error)
            continue

        data = candidate
        break

    if data is None:
        raise RuntimeError(
            f"Groq script generation failed (no {MIN_SCRIPT_WORDS}-"
            f"{MAX_SCRIPT_WORDS} word draft): {last_error}"
        )

    print("CTA:", END_CTA)

    if not data.get("keywords"):
        data["keywords"] = topic["visual_keywords"]

    return data


if __name__ == "__main__":
    from config import pick_topic_for_today

    t = pick_topic_for_today()
    out = generate_script(t)
    print(json.dumps(out, indent=2))
