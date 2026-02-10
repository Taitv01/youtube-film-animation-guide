"""
Video Assembler - Combines scene images + audio into a complete video.
Uses MoviePy and FFmpeg. Includes zoom effect and lyric text overlay.
"""
import os
import glob
import numpy as np
from moviepy import (
    ImageClip, AudioFileClip, TextClip, CompositeVideoClip,
    concatenate_videoclips, vfx
)
from config import VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS, SCENE_DURATION, TRANSITION_DURATION


def create_zoom_clip(image_path, duration, zoom_direction="in",
                     width=None, height=None):
    """
    Create a clip with efficient Ken Burns zoom effect.
    Pre-loads image at higher resolution and crops per frame.
    """
    width = width or VIDEO_WIDTH
    height = height or VIDEO_HEIGHT

    # Load image and resize to slightly larger than output
    from PIL import Image as PILImage
    pil_img = PILImage.open(image_path).convert("RGB")
    # Scale to 115% of output size for zoom headroom
    scale_w = int(width * 1.15)
    scale_h = int(height * 1.15)
    pil_img = pil_img.resize((scale_w, scale_h), PILImage.LANCZOS)
    img_array = np.array(pil_img)

    if zoom_direction == "in":
        start_crop, end_crop = 0.0, 0.13  # zoom in = crop more over time
    else:
        start_crop, end_crop = 0.13, 0.0  # zoom out = crop less over time

    def make_frame(t):
        progress = t / max(duration, 0.001)
        crop_pct = start_crop + (end_crop - start_crop) * progress

        crop_x = int(scale_w * crop_pct / 2)
        crop_y = int(scale_h * crop_pct / 2)

        # Ensure we don't crop too much
        crop_x = min(crop_x, (scale_w - width) // 2)
        crop_y = min(crop_y, (scale_h - height) // 2)
        crop_x = max(crop_x, 0)
        crop_y = max(crop_y, 0)

        cropped = img_array[crop_y:crop_y+height, crop_x:crop_x+width]

        # If crop resulted in wrong size, fallback to center crop
        if cropped.shape[0] != height or cropped.shape[1] != width:
            cy = (scale_h - height) // 2
            cx = (scale_w - width) // 2
            cropped = img_array[cy:cy+height, cx:cx+width]

        return cropped

    from moviepy import VideoClip
    clip = VideoClip(make_frame, duration=duration)
    return clip


def create_lyric_overlay(lyric_text, duration, width=None, height=None):
    """Create a text overlay showing lyrics at the bottom of the screen."""
    width = width or VIDEO_WIDTH
    height = height or VIDEO_HEIGHT

    if not lyric_text or lyric_text.strip() == "":
        return None

    try:
        txt_clip = TextClip(
            text=lyric_text,
            font_size=36,
            color="white",
            stroke_color="black",
            stroke_width=2,
            size=(int(width * 0.8), None),
            method="caption",
            text_align="center",
        )
        txt_clip = (txt_clip
                    .with_duration(duration)
                    .with_position(("center", height - 120)))
        return txt_clip
    except Exception as e:
        print(f"  ⚠️ Could not create lyric overlay: {e}")
        return None


def assemble_video(scene_paths, audio_path, output_path,
                   scene_duration=None, width=None, height=None, fps=None,
                   lyrics=None):
    """
    Assemble scene images + audio into a final video.
    Includes zoom effects, crossfade transitions, and optional lyric overlay.
    """
    width = width or VIDEO_WIDTH
    height = height or VIDEO_HEIGHT
    fps = fps or VIDEO_FPS
    scene_duration = scene_duration or SCENE_DURATION

    print(f"\n🎬 Assembling video...")
    print(f"  📸 Scenes: {len(scene_paths)}")
    print(f"  🎵 Audio: {audio_path or 'None (silent)'}")

    # Load audio
    audio = None
    total_duration = len(scene_paths) * scene_duration

    if audio_path and os.path.exists(audio_path):
        audio = AudioFileClip(audio_path)
        total_duration = audio.duration
        scene_duration = total_duration / len(scene_paths)
        print(f"  ⏱️ Audio duration: {total_duration:.1f}s")
        print(f"  ⏱️ Scene duration: {scene_duration:.1f}s each")

    # Parse lyrics into per-scene lines
    lyric_lines = []
    if lyrics:
        lines = [l.strip() for l in lyrics.strip().split("\n") if l.strip()]
        # Distribute lyrics across scenes
        lines_per_scene = max(1, len(lines) // len(scene_paths))
        for i in range(len(scene_paths)):
            start = i * lines_per_scene
            end = start + lines_per_scene
            scene_lyrics = "\n".join(lines[start:end]) if start < len(lines) else ""
            lyric_lines.append(scene_lyrics)

    # Create clips with zoom effect
    clips = []
    zoom_dirs = ["in", "out"]

    for i, path in enumerate(scene_paths):
        zoom = zoom_dirs[i % 2]
        clip = create_zoom_clip(path, scene_duration, zoom, width, height)

        # Add lyric overlay if available
        if lyric_lines and i < len(lyric_lines) and lyric_lines[i]:
            lyric_clip = create_lyric_overlay(lyric_lines[i], scene_duration, width, height)
            if lyric_clip:
                clip = CompositeVideoClip([clip, lyric_clip], size=(width, height))

        clips.append(clip)
        print(f"  🎥 Clip {i+1}/{len(scene_paths)}: {os.path.basename(path)} ({scene_duration:.1f}s, zoom {zoom})")

    # Crossfade transitions
    transition = min(TRANSITION_DURATION, scene_duration * 0.2)
    if transition > 0 and len(clips) > 1:
        for i in range(1, len(clips)):
            clips[i] = clips[i].with_effects([vfx.CrossFadeIn(transition)])
            clips[i-1] = clips[i-1].with_effects([vfx.CrossFadeOut(transition)])

    # Concatenate
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


def assemble_from_clips(clip_paths, audio_path, output_path,
                        width=None, height=None, fps=None, lyrics=None):
    """
    Assemble pre-animated MP4 clips into a final video with audio.
    Used when scenes have been animated by Minimax AI.
    """
    from moviepy import VideoFileClip

    width = width or VIDEO_WIDTH
    height = height or VIDEO_HEIGHT
    fps = fps or VIDEO_FPS

    print(f"\n🎬 Assembling from {len(clip_paths)} AI-animated clips...")

    # Load audio
    audio = None
    if audio_path and os.path.exists(audio_path):
        audio = AudioFileClip(audio_path)
        print(f"  🎵 Audio: {audio.duration:.1f}s")

    # Load clips
    clips = []
    for i, path in enumerate(clip_paths):
        clip = VideoFileClip(path)
        # Resize if needed
        if clip.size != (width, height):
            clip = clip.resized((width, height))
        clips.append(clip)
        print(f"  📹 Clip {i+1}: {os.path.basename(path)} ({clip.duration:.1f}s)")

    # Add lyric overlay if available
    if lyrics:
        lines = [l.strip() for l in lyrics.strip().split("\n") if l.strip()]
        lines_per_clip = max(1, len(lines) // len(clips))
        for i, clip in enumerate(clips):
            start = i * lines_per_clip
            end = start + lines_per_clip
            lyric_text = "\n".join(lines[start:end]) if start < len(lines) else ""
            if lyric_text:
                overlay = create_lyric_overlay(lyric_text, clip.duration, width, height)
                if overlay:
                    clips[i] = CompositeVideoClip([clip, overlay], size=(width, height))

    # Crossfade transitions
    transition = 0.5
    if len(clips) > 1:
        for i in range(1, len(clips)):
            clips[i] = clips[i].with_effects([vfx.CrossFadeIn(transition)])
            clips[i-1] = clips[i-1].with_effects([vfx.CrossFadeOut(transition)])

    final = concatenate_videoclips(clips, method="compose")

    # Add audio
    if audio:
        if audio.duration > final.duration:
            audio = audio.subclipped(0, final.duration)
        elif audio.duration < final.duration:
            final = final.subclipped(0, audio.duration)
        final = final.with_audio(audio)

    # Export
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

    final.close()
    if audio:
        audio.close()

    file_size = os.path.getsize(output_path) / (1024 * 1024)
    print(f"  ✅ Video saved! Size: {file_size:.1f} MB")
    return output_path


def assemble_silent_video(scene_paths, output_path, scene_duration=None):
    """Create a video without audio."""
    return assemble_video(scene_paths, None, output_path, scene_duration)


if __name__ == "__main__":
    test_scenes = sorted(glob.glob("output/*/scenes/scene_*.png"))
    if test_scenes:
        print(f"Found {len(test_scenes)} scenes")
        assemble_silent_video(test_scenes, "test_output/test_video.mp4", 3)
    else:
        print("No test scenes found. Run image_generator.py first.")

