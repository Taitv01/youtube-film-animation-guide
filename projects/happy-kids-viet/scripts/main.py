"""
Main Pipeline Orchestrator - Happy Kids Việt Video Production
=============================================================

Usage:
    py main.py --topic colors
    py main.py --topic counting
    py main.py --topic brush_teeth
    py main.py --topic abc
    py main.py --topic vegetables
    py main.py --list              # Show available topics
    py main.py --all               # Generate ALL topics

If you have audio: place MP3 in audio/<topic>.mp3
    e.g., audio/colors.mp3
"""
import argparse
import os
import sys
import time

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding='utf-8')

from config import get_output_dir, AUDIO_DIR
from script_generator import generate_script, save_script, get_available_topics
from image_generator import generate_all_scenes
from thumbnail_creator import create_thumbnail
from video_assembler import assemble_video, assemble_silent_video


def run_pipeline(topic, skip_video=False):
    """
    Run the complete video production pipeline for a given topic.

    Steps:
    1. Generate script (lyrics + metadata)
    2. Generate scene images
    3. Create thumbnail
    4. Assemble video (with audio if available)
    """
    start_time = time.time()

    print("=" * 60)
    print(f"🎬 HAPPY KIDS VIỆT - Video Pipeline")
    print(f"📌 Topic: {topic}")
    print("=" * 60)

    # Step 1: Generate Script
    print(f"\n📝 Step 1: Generating script...")
    try:
        script = generate_script(topic)
    except ValueError as e:
        print(f"  ❌ Error: {e}")
        return None

    output_dir = get_output_dir(topic)
    save_script(script, output_dir)
    print(f"  📁 Output directory: {output_dir}")

    # Step 2: Generate Scene Images
    print(f"\n🎨 Step 2: Generating {len(script['scene_descriptions'])} scene images...")
    scene_paths = generate_all_scenes(script["scene_descriptions"], output_dir)

    # Step 3: Create Thumbnail
    print(f"\n🖼️ Step 3: Creating thumbnail...")
    thumb_path = os.path.join(output_dir, "thumbnail.png")
    bg_colors = script["scene_descriptions"][0]["bg_colors"]
    create_thumbnail(
        title=script["raw_title"],
        emoji=script["emoji"],
        bg_colors=bg_colors,
        output_path=thumb_path,
    )

    # Step 4: Assemble Video
    if not skip_video:
        print(f"\n🎬 Step 4: Assembling video...")
        video_path = os.path.join(output_dir, "video.mp4")

        # Check for audio file
        audio_path = os.path.join(AUDIO_DIR, f"{topic.lower()}.mp3")
        if not os.path.exists(audio_path):
            # Also check wav
            audio_path_wav = os.path.join(AUDIO_DIR, f"{topic.lower()}.wav")
            if os.path.exists(audio_path_wav):
                audio_path = audio_path_wav
            else:
                print(f"  ⚠️ No audio found at: {audio_path}")
                print(f"  📌 Creating silent video (add audio later)")
                print(f"  💡 Tip: Download music from Suno AI → save as audio/{topic.lower()}.mp3")
                audio_path = None

        # Get lyrics for overlay
        lyrics_text = "\n".join(script.get("lyrics", []))

        if audio_path:
            assemble_video(scene_paths, audio_path, video_path, lyrics=lyrics_text)
        else:
            assemble_silent_video(scene_paths, video_path, scene_duration=3)
    else:
        print(f"\n⏭️ Step 4: Skipped (--skip-video flag)")
        video_path = None

    # Summary
    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print(f"✅ PIPELINE COMPLETE!")
    print(f"⏱️ Time: {elapsed:.1f} seconds")
    print(f"\n📁 Output files:")
    print(f"  📄 Lyrics:    {os.path.join(output_dir, 'lyrics.txt')}")
    print(f"  📋 Metadata:  {os.path.join(output_dir, 'metadata.json')}")
    print(f"  🎨 Scenes:    {os.path.join(output_dir, 'scenes')} ({len(scene_paths)} images)")
    print(f"  🖼️ Thumbnail: {thumb_path}")
    if video_path:
        print(f"  🎬 Video:     {video_path}")
    print("=" * 60)

    return {
        "output_dir": output_dir,
        "lyrics_path": os.path.join(output_dir, "lyrics.txt"),
        "metadata_path": os.path.join(output_dir, "metadata.json"),
        "scene_paths": scene_paths,
        "thumbnail_path": thumb_path,
        "video_path": video_path,
    }


def main():
    parser = argparse.ArgumentParser(
        description="🎵 Happy Kids Việt - Automated Video Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  py main.py --topic colors          Create "Colors" video
  py main.py --topic counting        Create "Counting" video
  py main.py --topic abc             Create "ABC" video
  py main.py --list                  Show all available topics
  py main.py --all                   Generate ALL videos
  py main.py --topic colors --skip-video  Only images + thumbnail
        """
    )
    parser.add_argument("--topic", type=str, help="Topic to generate video for")
    parser.add_argument("--list", action="store_true", help="List available topics")
    parser.add_argument("--all", action="store_true", help="Generate all topics")
    parser.add_argument("--skip-video", action="store_true", help="Skip video assembly (images + thumbnail only)")

    args = parser.parse_args()

    if args.list:
        topics = get_available_topics()
        print("📋 Available topics:")
        for t in topics:
            print(f"  • {t}")
        return

    if args.all:
        topics = get_available_topics()
        print(f"🚀 Generating ALL {len(topics)} topics...\n")
        for t in topics:
            run_pipeline(t, skip_video=args.skip_video)
            print()
        return

    if not args.topic:
        parser.print_help()
        print("\n💡 Quick start: py main.py --topic colors")
        return

    # Ensure audio directory exists
    os.makedirs(AUDIO_DIR, exist_ok=True)

    run_pipeline(args.topic, skip_video=args.skip_video)


if __name__ == "__main__":
    main()
