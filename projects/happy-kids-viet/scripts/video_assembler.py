"""
Video Assembler - Combines scene images + audio into a complete video.
Uses MoviePy and FFmpeg. Optimized for fast encoding.
"""
import os
import glob
from moviepy import (
    ImageClip, AudioFileClip,
    concatenate_videoclips, vfx
)
from config import VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS, SCENE_DURATION, TRANSITION_DURATION


def assemble_video(scene_paths, audio_path, output_path,
                   scene_duration=None, width=None, height=None, fps=None):
    """
    Assemble scene images + audio into a final video.
    Optimized: uses static images (no per-frame Ken Burns) for fast encoding.
    """
    width = width or VIDEO_WIDTH
    height = height or VIDEO_HEIGHT
    fps = fps or VIDEO_FPS
    scene_duration = scene_duration or SCENE_DURATION

    print(f"\n🎬 Assembling video...")
    print(f"  📸 Scenes: {len(scene_paths)}")
    print(f"  🎵 Audio: {audio_path or 'None (silent)'}")

    # Load audio to determine total duration
    audio = None
    total_duration = len(scene_paths) * scene_duration

    if audio_path and os.path.exists(audio_path):
        audio = AudioFileClip(audio_path)
        total_duration = audio.duration
        scene_duration = total_duration / len(scene_paths)
        print(f"  ⏱️ Audio duration: {total_duration:.1f}s")
        print(f"  ⏱️ Scene duration: {scene_duration:.1f}s each")

    # Create simple image clips (no Ken Burns = 10x faster)
    clips = []
    for i, path in enumerate(scene_paths):
        clip = (ImageClip(path)
                .with_duration(scene_duration)
                .resized((width, height)))
        clips.append(clip)
        print(f"  🎥 Clip {i+1}/{len(scene_paths)}: {os.path.basename(path)} ({scene_duration:.1f}s)")

    # Add crossfade transitions
    transition = min(TRANSITION_DURATION, scene_duration * 0.3)
    if transition > 0 and len(clips) > 1:
        for i in range(1, len(clips)):
            clips[i] = clips[i].with_effects([vfx.CrossFadeIn(transition)])
            clips[i-1] = clips[i-1].with_effects([vfx.CrossFadeOut(transition)])

    # Concatenate all clips
    final = concatenate_videoclips(clips, method="compose")

    # Add audio
    if audio:
        if audio.duration > final.duration:
            audio = audio.subclipped(0, final.duration)
        final = final.with_audio(audio)

    # Export with optimized settings
    print(f"\n  💾 Exporting to: {output_path}")
    final.write_videofile(
        output_path,
        fps=fps,
        codec="libx264",
        audio_codec="aac",
        preset="ultrafast",
        threads=4,
        logger="bar",
    )

    # Cleanup
    final.close()
    if audio:
        audio.close()

    file_size = os.path.getsize(output_path) / (1024 * 1024)
    print(f"  ✅ Video saved! Size: {file_size:.1f} MB")
    return output_path


def assemble_silent_video(scene_paths, output_path, scene_duration=None):
    """Create a video without audio (for preview/testing)."""
    return assemble_video(scene_paths, None, output_path, scene_duration)


if __name__ == "__main__":
    test_scenes = sorted(glob.glob("output/*/scenes/scene_*.png"))
    if test_scenes:
        print(f"Found {len(test_scenes)} scenes")
        assemble_silent_video(test_scenes, "test_output/test_video.mp4", 3)
    else:
        print("No test scenes found. Run image_generator.py first.")
