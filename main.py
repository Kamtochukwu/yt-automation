"""
Runs the full daily pipeline: pick topic -> generate script -> TTS ->
fetch stock clips -> assemble video with captions -> upload to YouTube.

Triggered daily by .github/workflows/daily.yml

Commands:
  python main.py                 # one Short for this time of day
  python main.py post morning    # force the morning slot
  python main.py post 3          # all 3 Shorts in one run
  python main.py report          # write a channel progress report
"""

import os
import shutil
import sys

from config import pick_topic_for_slot, slot_for_now, VIDEOS_PER_DAY, POST_WINDOWS, WORKDIR
from src.generate_script import generate_script
from src.generate_audio import generate_audio
from src.fetch_visuals import fetch_clips
from src.assemble_video import assemble_video
from src.upload_youtube import upload_video


def run_pipeline(slot: int = 0):
    if os.path.exists(WORKDIR):
        shutil.rmtree(WORKDIR)
    os.makedirs(WORKDIR)

    topic = pick_topic_for_slot(slot)
    window = POST_WINDOWS[slot % len(POST_WINDOWS)]["name"]
    angle = topic.get("angle") or "body"
    print(f"Slot {slot + 1}/{VIDEOS_PER_DAY} ({window}) niche: {topic['niche']} / {angle}")

    print("Generating script...")
    script_data = generate_script(topic)
    print("Title:", script_data["title"])
    print("Script:", script_data["script"])

    audio_path = os.path.join(WORKDIR, "narration.mp3")
    print("Generating narration audio...")
    word_timings = generate_audio(script_data["script"], audio_path)

    clips_dir = os.path.join(WORKDIR, "clips")
    print("Fetching stock clips...")
    clip_paths = fetch_clips(script_data["keywords"], clips_dir, clips_needed=5)
    if not clip_paths:
        raise RuntimeError("No stock clips found — check PEXELS_API_KEY / keywords.")

    video_path = os.path.join(WORKDIR, "final.mp4")
    print("Assembling video...")
    assemble_video(clip_paths, audio_path, word_timings, video_path)

    description = f"{script_data['script']}\n\n{topic['hashtags']}"
    print("Uploading to YouTube...")
    upload_video(
        video_path=video_path,
        title=script_data["title"],
        description=description,
        tags=script_data["keywords"],
    )

    print("Done!")


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else "post"
    if command in ("report", "analytics"):
        from src.analytics import run_report

        run_report()
        return
    if command in ("post", "run"):
        requested = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("POST_SLOT", "auto")
        if str(requested).isdigit() and int(requested) > 1:
            count = min(VIDEOS_PER_DAY, int(requested))
            for slot in range(count):
                print(f"\n=== Posting video {slot + 1} of {count} ===")
                run_pipeline(slot)
            return
        slot = slot_for_now(None if requested in (None, "", "auto") else requested)
        print(f"\n=== Posting {POST_WINDOWS[slot]['name']} Short ===")
        run_pipeline(slot)
        return
    raise SystemExit("Usage: python main.py [post [morning|afternoon|night|count]|report]")


if __name__ == "__main__":
    main()
