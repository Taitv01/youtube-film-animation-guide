"""
Video Assembler - Combines scene images + audio into a complete video.
Uses MoviePy and FFmpeg.
"""
import os
import glob
from moviepy import (
    ImageClip, AudioFileClip, CompositeVideoClip,
    TextClip, concatenate_videoclips, vfx
)
from config import VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS, SCENE_DURATION, TRANSITION_DURATION


def create_ken_burns_clip(image_path, duration, zoom_direction="in"):
    """
    Create a clip with Ken Burns (zoom) effect.
    zoom_direction: "in" = zoom in, "out" = zoom out
    """
    clip = ImageClip(image_path).with_duration(duration)

    if zoom_direction == "in":
        start_scale, end_scale = 1.0, 1.15
    else:
        start_scale, end_scale = 1.15, 1.0

    def resize_func(t):
        progress = t / duration
        scale = start_scale + (end_scale - start_scale) * progress
        return scale

    clip = clip.resized(resize_func)
    clip = clip.with_position("center")

    return clip


def assemble_video(scene_paths, audio_path, output_path,
                   scene_duration=None, width=None, height=None, fps=None):
    """
    Assemble scene images + audio into a final video.

    Args:
        scene_paths: List of image file paths
        audio_path: Path to audio file (MP3/WAV) or None for silent video
        output_path: Where to save the video
        scene_duration: Seconds per scene (auto-calculated if audio provided)
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
        # Recalculate scene duration to fit audio
        scene_duration = total_duration / len(scene_paths)
        print(f"  ⏱️ Audio duration: {total_duration:.1f}s")
        print(f"  ⏱️ Scene duration: {scene_duration:.1f}s each")

    # Create clips with Ken Burns effect
    clips = []
    zoom_directions = ["in", "out"]

    for i, path in enumerate(scene_paths):
        zoom = zoom_directions[i % 2]
        clip = create_ken_burns_clip(path, scene_duration, zoom)
        clip = clip.resized((width, height))
        clips.append(clip)
        print(f"  🎥 Clip {i+1}/{len(scene_paths)}: {os.path.basename(path)} ({scene_duration:.1f}s, zoom {zoom})")

    # Add crossfade transitions
    if TRANSITION_DURATION > 0 and len(clips) > 1:
        for i in range(1, len(clips)):
            clips[i] = clips[i].with_effects([
                vfx.CrossFadeIn(TRANSITION_DURATION)
            ])
            clips[i-1] = clips[i-1].with_effects([
                vfx.CrossFadeOut(TRANSITION_DURATION)
            ])

    # Concatenate all clips
    final = concatenate_videoclips(clips, method="compose")

    # Add audio if available
    if audio:
        # Trim or loop audio to match video
        if audio.duration > final.duration:
            audio = audio.subclipped(0, final.duration)
        final = final.with_audio(audio)

    # Export
    print(f"\n  💾 Exporting to: {output_path}")
    final.write_videofile(
        output_path,
        fps=fps,
        codec="libx264",
        audio_codec="aac",
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
    # Test with existing scenes
    test_scenes = sorted(glob.glob("output/*/scenes/scene_*.png"))
    if test_scenes:
        print(f"Found {len(test_scenes)} scenes")
        assemble_silent_video(test_scenes, "test_output/test_video.mp4", 3)
    else:
        print("No test scenes found. Run image_generator.py first.")
