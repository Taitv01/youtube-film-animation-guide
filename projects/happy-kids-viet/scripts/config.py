"""
Config module for Happy Kids Việt video pipeline.
"""
import os

# === Channel Info ===
CHANNEL_NAME = "Happy Kids Việt"
CHANNEL_TAGLINE = "Nursery Rhymes • Educational Songs"

# === Video Settings ===
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
VIDEO_FPS = 24
SCENE_DURATION = 3  # seconds per scene
TRANSITION_DURATION = 0.5  # crossfade seconds

# === Thumbnail Settings ===
THUMB_WIDTH = 1280
THUMB_HEIGHT = 720

# === Color Palette (Kid-friendly, bright) ===
COLORS = {
    "red":      (255, 107, 107),
    "orange":   (255, 169, 77),
    "yellow":   (255, 224, 102),
    "green":    (105, 219, 124),
    "blue":     (77, 171, 247),
    "purple":   (218, 119, 242),
    "pink":     (247, 131, 172),
    "white":    (255, 255, 255),
    "dark":     (44, 62, 80),
}

# Color cycle for scenes
SCENE_BACKGROUNDS = [
    [(77, 171, 247), (105, 219, 124)],    # blue → green
    [(255, 169, 77), (255, 224, 102)],     # orange → yellow
    [(218, 119, 242), (247, 131, 172)],    # purple → pink
    [(255, 107, 107), (255, 169, 77)],     # red → orange
    [(105, 219, 124), (77, 171, 247)],     # green → blue
    [(247, 131, 172), (218, 119, 242)],    # pink → purple
    [(255, 224, 102), (105, 219, 124)],    # yellow → green
    [(77, 171, 247), (218, 119, 242)],     # blue → purple
]

# === Fonts ===
# Using system fonts - will fallback gracefully
FONT_PATHS = [
    "C:/Windows/Fonts/arialbd.ttf",   # Arial Bold
    "C:/Windows/Fonts/arial.ttf",      # Arial
    "C:/Windows/Fonts/segoeui.ttf",    # Segoe UI
]

def get_font_path():
    """Return first available font path."""
    for fp in FONT_PATHS:
        if os.path.exists(fp):
            return fp
    return None

# === Directories ===
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")
AUDIO_DIR = os.path.join(PROJECT_DIR, "audio")

def get_output_dir(topic):
    """Get/create output directory for a topic."""
    d = os.path.join(OUTPUT_DIR, topic.lower().replace(" ", "_"))
    os.makedirs(d, exist_ok=True)
    os.makedirs(os.path.join(d, "scenes"), exist_ok=True)
    return d

# === Default SEO Tags ===
DEFAULT_TAGS = [
    "nursery rhymes", "kids songs", "children songs",
    "educational videos for kids", "baby songs",
    "toddler videos", "preschool songs",
    "Happy Kids Viet", "learn for kids",
]
