"""
Thumbnail Creator - Generates YouTube thumbnails using Pillow.
Creates eye-catching 1280x720 thumbnails with bright colors and large text.
"""
import os
import math
from PIL import Image, ImageDraw, ImageFont
from config import THUMB_WIDTH, THUMB_HEIGHT, get_font_path


def create_thumbnail(title, emoji, bg_colors, output_path):
    """
    Create a YouTube thumbnail (1280x720).

    Args:
        title: Short title text (e.g., "LEARN COLORS!")
        emoji: Emoji for visual pop (e.g., "🌈")
        bg_colors: Tuple of two RGB colors for gradient
        output_path: Where to save the thumbnail
    """
    width, height = THUMB_WIDTH, THUMB_HEIGHT

    # Create gradient background
    img = Image.new("RGB", (width, height))
    pixels = img.load()
    for y in range(height):
        for x in range(width):
            # Diagonal gradient
            ratio = (x + y) / (width + height)
            r = int(bg_colors[0][0] * (1 - ratio) + bg_colors[1][0] * ratio)
            g = int(bg_colors[0][1] * (1 - ratio) + bg_colors[1][1] * ratio)
            b = int(bg_colors[0][2] * (1 - ratio) + bg_colors[1][2] * ratio)
            pixels[x, y] = (r, g, b)

    draw = ImageDraw.Draw(img)
    font_path = get_font_path()

    # Draw decorative stars
    star_positions = [
        (80, 80, 25), (width - 90, 70, 30),
        (100, height - 90, 20), (width - 80, height - 80, 25),
        (width // 2 - 200, 60, 15), (width // 2 + 200, height - 60, 18),
    ]
    for sx, sy, sr in star_positions:
        _draw_star(draw, sx, sy, sr, (255, 255, 255))

    # Draw large circles decoration
    for cx, cy, cr in [(160, height//2, 120), (width-160, height//2, 100)]:
        draw.ellipse(
            [cx-cr, cy-cr, cx+cr, cy+cr],
            outline=(255, 255, 255, 80), width=3
        )

    # === Main Title Text ===
    try:
        title_font = ImageFont.truetype(font_path, 120) if font_path else ImageFont.load_default()
    except Exception:
        title_font = ImageFont.load_default()

    # Clean title for display (remove emoji from title text)
    display_title = title.upper()

    # Calculate position
    bbox = draw.textbbox((0, 0), display_title, font=title_font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (width - tw) // 2
    ty = (height - th) // 2 - 20

    # Draw text shadow
    for offset in [(3, 3), (-1, -1), (3, -1), (-1, 3)]:
        draw.text((tx + offset[0], ty + offset[1]),
                  display_title, font=title_font, fill=(0, 0, 0))

    # Draw main text
    draw.text((tx, ty), display_title, font=title_font, fill=(255, 255, 255))

    # === Subtitle: Channel Name ===
    try:
        sub_font = ImageFont.truetype(font_path, 42) if font_path else ImageFont.load_default()
    except Exception:
        sub_font = ImageFont.load_default()

    sub_text = "Happy Kids Việt"
    sub_bbox = draw.textbbox((0, 0), sub_text, font=sub_font)
    sub_w = sub_bbox[2] - sub_bbox[0]
    sub_x = (width - sub_w) // 2
    sub_y = ty + th + 40

    # Pill background
    pill_pad = 15
    _draw_rounded_rect(draw, (
        sub_x - pill_pad * 2, sub_y - pill_pad,
        sub_x + sub_w + pill_pad * 2, sub_y + (sub_bbox[3] - sub_bbox[1]) + pill_pad
    ), 12, fill=(0, 0, 0))
    draw.text((sub_x, sub_y), sub_text, font=sub_font, fill=(255, 255, 255))

    # === "For Kids" badge (top-right) ===
    try:
        badge_font = ImageFont.truetype(font_path, 28) if font_path else ImageFont.load_default()
    except Exception:
        badge_font = ImageFont.load_default()

    badge_text = "FOR KIDS"
    badge_bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
    badge_w = badge_bbox[2] - badge_bbox[0]
    badge_h = badge_bbox[3] - badge_bbox[1]
    badge_x = width - badge_w - 40
    badge_y = 25

    _draw_rounded_rect(draw, (
        badge_x - 15, badge_y - 8,
        badge_x + badge_w + 15, badge_y + badge_h + 8
    ), 10, fill=(255, 224, 102))
    draw.text((badge_x, badge_y), badge_text, font=badge_font, fill=(44, 62, 80))

    # Save
    img.save(output_path, "PNG", quality=95)
    print(f"  ✅ Thumbnail saved: {output_path}")
    return output_path


def _draw_star(draw, cx, cy, r, fill):
    """Draw a star shape."""
    points = []
    for i in range(10):
        angle = math.pi / 2 + i * math.pi / 5
        radius = r if i % 2 == 0 else r * 0.4
        x = cx + radius * math.cos(angle)
        y = cy - radius * math.sin(angle)
        points.append((x, y))
    draw.polygon(points, fill=fill)


def _draw_rounded_rect(draw, xy, radius, fill):
    """Draw a rounded rectangle."""
    x1, y1, x2, y2 = xy
    draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
    draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
    draw.pieslice([x1, y1, x1 + 2*radius, y1 + 2*radius], 180, 270, fill=fill)
    draw.pieslice([x2 - 2*radius, y1, x2, y1 + 2*radius], 270, 360, fill=fill)
    draw.pieslice([x1, y2 - 2*radius, x1 + 2*radius, y2], 90, 180, fill=fill)
    draw.pieslice([x2 - 2*radius, y2 - 2*radius, x2, y2], 0, 90, fill=fill)


if __name__ == "__main__":
    os.makedirs("test_output", exist_ok=True)
    create_thumbnail(
        title="LEARN COLORS!",
        emoji="🌈",
        bg_colors=[(77, 171, 247), (218, 119, 242)],
        output_path="test_output/test_thumbnail.png"
    )
    print("Test thumbnail created!")
