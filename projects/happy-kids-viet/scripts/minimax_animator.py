"""
Minimax (Hailuo) AI Video Animator
Converts static scene images into animated video clips using Minimax API.
Requires MINIMAX_API_KEY environment variable or .env file.
"""
import os
import sys
import time
import base64
import requests

# Try to load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

API_BASE = "https://api.minimax.io/v1"
MODEL = "MiniMax-Hailuo-2.3"
DEFAULT_DURATION = 6  # seconds per clip
DEFAULT_RESOLUTION = "1080P"
POLL_INTERVAL = 10  # seconds between status checks
MAX_POLL_TIME = 600  # 10 minutes max wait per clip


def get_api_key():
    """Get Minimax API key from environment."""
    key = os.environ.get("MINIMAX_API_KEY", "")
    if not key:
        env_file = os.path.join(os.path.dirname(__file__), ".env")
        if os.path.exists(env_file):
            with open(env_file) as f:
                for line in f:
                    if line.startswith("MINIMAX_API_KEY="):
                        key = line.strip().split("=", 1)[1].strip().strip('"\'')
    if not key:
        raise ValueError(
            "MINIMAX_API_KEY not found!\n"
            "  1. Register at https://platform.minimax.io\n"
            "  2. Get API key from Account > API Keys\n"
            "  3. Set: MINIMAX_API_KEY=your_key in .env file"
        )
    return key


def _get_headers():
    """Get auth headers."""
    return {"Authorization": f"Bearer {get_api_key()}"}


def _image_to_url(image_path):
    """
    Convert local image to a base64 data URI for the API.
    Minimax accepts URLs, so we need to either:
    1. Upload to a hosting service, or
    2. Use base64 data URI
    For simplicity, we upload the file first.
    """
    # Read image and encode as base64
    with open(image_path, "rb") as f:
        img_data = f.read()

    ext = os.path.splitext(image_path)[1].lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}.get(ext.lstrip("."), "image/png")

    # Try to upload to Minimax file API first
    try:
        url = f"{API_BASE}/files/upload"
        files = {"file": (os.path.basename(image_path), img_data, mime)}
        data = {"purpose": "file-extract"}
        response = requests.post(url, headers=_get_headers(), files=files, data=data)
        response.raise_for_status()
        result = response.json()
        if "file" in result and "download_url" in result["file"]:
            return result["file"]["download_url"]
    except Exception:
        pass

    # Fallback: use base64 data URI
    b64 = base64.b64encode(img_data).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def submit_image_to_video(image_path, prompt, duration=None, resolution=None):
    """
    Submit an image-to-video generation task.

    Args:
        image_path: Path to the source image
        prompt: Text describing the desired animation/motion
        duration: Video duration in seconds (default: 6)
        resolution: "1080P" or "720P"

    Returns:
        task_id (str)
    """
    duration = duration or DEFAULT_DURATION
    resolution = resolution or DEFAULT_RESOLUTION

    # Get image URL
    image_url = _image_to_url(image_path)

    url = f"{API_BASE}/video_generation"
    payload = {
        "prompt": prompt,
        "first_frame_image": image_url,
        "model": MODEL,
        "duration": duration,
        "resolution": resolution,
    }

    response = requests.post(url, headers=_get_headers(), json=payload)
    response.raise_for_status()
    result = response.json()

    if "task_id" not in result:
        raise Exception(f"No task_id in response: {result}")

    return result["task_id"]


def poll_task_status(task_id):
    """
    Poll task status until completion.

    Returns:
        file_id (str) on success
    """
    url = f"{API_BASE}/query/video_generation"
    params = {"task_id": task_id}
    elapsed = 0

    while elapsed < MAX_POLL_TIME:
        time.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL

        response = requests.get(url, headers=_get_headers(), params=params)
        response.raise_for_status()
        result = response.json()

        status = result.get("status", "unknown")
        print(f"    ⏳ Status: {status} ({elapsed}s)")

        if status == "Success":
            return result["file_id"]
        elif status == "Fail":
            error = result.get("error_message", "Unknown error")
            raise Exception(f"Video generation failed: {error}")

    raise TimeoutError(f"Task {task_id} timed out after {MAX_POLL_TIME}s")


def download_video(file_id, output_path):
    """
    Download generated video using file_id.
    """
    url = f"{API_BASE}/files/retrieve"
    params = {"file_id": file_id}

    response = requests.get(url, headers=_get_headers(), params=params)
    response.raise_for_status()
    download_url = response.json()["file"]["download_url"]

    # Download the video file
    video_response = requests.get(download_url)
    video_response.raise_for_status()

    with open(output_path, "wb") as f:
        f.write(video_response.content)

    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"    ✅ Clip saved: {output_path} ({size_mb:.1f}MB)")
    return output_path


def animate_scene(image_path, prompt, output_path, duration=None):
    """
    Full workflow: image → submit → poll → download clip.
    """
    print(f"  🎬 Animating: {os.path.basename(image_path)}")
    print(f"    📝 Prompt: {prompt[:60]}...")

    task_id = submit_image_to_video(image_path, prompt, duration)
    print(f"    📤 Task submitted: {task_id}")

    file_id = poll_task_status(task_id)
    print(f"    📥 File ready: {file_id}")

    return download_video(file_id, output_path)


def animate_all_scenes(scene_paths, scene_descriptions, output_dir, duration=None):
    """
    Animate all scenes with rate limiting.

    Args:
        scene_paths: List of image file paths
        scene_descriptions: List of dicts with 'text' and 'subtext'
        output_dir: Where to save animated clips
        duration: Duration per clip (default: 6s)

    Returns:
        List of clip paths (animated MP4 files)
    """
    clips_dir = os.path.join(output_dir, "clips")
    os.makedirs(clips_dir, exist_ok=True)

    clip_paths = []
    for i, (img_path, desc) in enumerate(zip(scene_paths, scene_descriptions)):
        clip_name = f"clip_{i+1:02d}.mp4"
        clip_path = os.path.join(clips_dir, clip_name)

        # Skip if already generated
        if os.path.exists(clip_path) and os.path.getsize(clip_path) > 1000:
            print(f"  ⏭️ Clip {i+1}/{len(scene_paths)}: Already exists, skipping")
            clip_paths.append(clip_path)
            continue

        # Build animation prompt
        text = desc.get("text", "")
        subtext = desc.get("subtext", "")
        prompt = (
            f"Cute 3D Pixar-style animation for kids. "
            f"The scene shows {text} - {subtext}. "
            f"Colorful, playful motion, sparkles and stars floating around. "
            f"Smooth gentle camera movement. Kid-friendly and fun."
        )

        try:
            animate_scene(img_path, prompt, clip_path, duration)
            clip_paths.append(clip_path)
        except Exception as e:
            print(f"  ❌ Clip {i+1} failed: {e}")
            clip_paths.append(None)

        # Rate limiting: small delay between requests
        if i < len(scene_paths) - 1:
            print(f"  ⏰ Waiting 5s before next clip...")
            time.sleep(5)

    return clip_paths


if __name__ == "__main__":
    # Quick test
    print("🎬 Minimax Video Animator Test")
    print(f"  API Base: {API_BASE}")
    print(f"  Model: {MODEL}")

    try:
        key = get_api_key()
        print(f"  API Key: {key[:8]}...{key[-4:]}")
        print("  ✅ API key found!")
    except ValueError as e:
        print(f"  ❌ {e}")
        sys.exit(1)

    # Test with first available scene
    import glob
    scenes = sorted(glob.glob("output/*/scenes/scene_01.png"))
    if scenes:
        print(f"\n  Testing with: {scenes[0]}")
        os.makedirs("test_output", exist_ok=True)
        try:
            animate_scene(
                scenes[0],
                "Cute colorful cartoon animation, sparkles floating, kid-friendly",
                "test_output/test_clip.mp4"
            )
            print("  ✅ Test clip generated!")
        except Exception as e:
            print(f"  ❌ Test failed: {e}")
    else:
        print("  No scenes found. Run main.py --topic colors --skip-video first")
