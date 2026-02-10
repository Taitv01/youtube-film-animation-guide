"""
Image Generator - Creates colorful scene images using Pillow.
No external API needed - pure Python graphics.
"""
import os
import math
from PIL import Image, ImageDraw, ImageFont
from config import VIDEO_WIDTH, VIDEO_HEIGHT, get_font_path, get_output_dir


def create_gradient(width, height, color1, color2, direction="vertical"):
    """Create a gradient background image."""
    img = Image.new("RGB", (width, height))
    pixels = img.load()

    for y in range(height):
        for x in range(width):
            if direction == "vertical":
                ratio = y / height
            elif direction == "horizontal":
                ratio = x / width
            else:  # diagonal
                ratio = (x + y) / (width + height)

            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pixels[x, y] = (r, g, b)

    return img


def draw_rounded_rect(draw, xy, radius, fill):
    """Draw a rounded rectangle."""
    x1, y1, x2, y2 = xy
    draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
    draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
    draw.pieslice([x1, y1, x1 + 2*radius, y1 + 2*radius], 180, 270, fill=fill)
    draw.pieslice([x2 - 2*radius, y1, x2, y1 + 2*radius], 270, 360, fill=fill)
    draw.pieslice([x1, y2 - 2*radius, x1 + 2*radius, y2], 90, 180, fill=fill)
    draw.pieslice([x2 - 2*radius, y2 - 2*radius, x2, y2], 0, 90, fill=fill)


def draw_decorative_circles(draw, width, height, color1, color2):
    """Add decorative circles/bubbles to the background."""
    import random
    random.seed(42)  # Consistent decoration
    for _ in range(15):
        x = random.randint(0, width)
        y = random.randint(0, height)
        r = random.randint(20, 80)
        opacity_color = (
            min(255, color1[0] + 40),
            min(255, color1[1] + 40),
            min(255, color1[2] + 40),
        )
        draw.ellipse([x-r, y-r, x+r, y+r], fill=None, outline=opacity_color, width=3)


def draw_star(draw, cx, cy, r, fill):
    """Draw a simple star shape."""
    points = []
    for i in range(10):
        angle = math.pi / 2 + i * math.pi / 5
        radius = r if i % 2 == 0 else r * 0.4
        x = cx + radius * math.cos(angle)
        y = cy - radius * math.sin(angle)
        points.append((x, y))
    draw.polygon(points, fill=fill)


def create_scene_image(scene_desc, scene_index, output_path,
                       width=None, height=None):
    """
    Create a single scene image with:
    - Gradient background
    - Large emoji/text
    - Subtitle text
    - Decorative elements
    """
    width = width or VIDEO_WIDTH
    height = height or VIDEO_HEIGHT

    bg_colors = scene_desc.get("bg_colors", [(77,171,247), (41,128,185)])
    main_text = scene_desc["text"]
    sub_text = scene_desc.get("sub", "")

    # Create gradient background
    directions = ["vertical", "horizontal", "diagonal"]
    direction = directions[scene_index % len(directions)]
    img = create_gradient(width, height, bg_colors[0], bg_colors[1], direction)
    draw = ImageDraw.Draw(img)

    # Add decorative elements
    draw_decorative_circles(draw, width, height, bg_colors[0], bg_colors[1])

    # Add star decorations
    star_color = (255, 255, 255)
    draw_star(draw, 100, 100, 30, star_color)
    draw_star(draw, width - 100, 150, 25, star_color)
    draw_star(draw, 150, height - 120, 20, star_color)
    draw_star(draw, width - 150, height - 100, 35, star_color)

    # Load font
    font_path = get_font_path()

    # Draw main text (large)
    try:
        main_font = ImageFont.truetype(font_path, 160) if font_path else ImageFont.load_default()
    except Exception:
        main_font = ImageFont.load_default()

    # Calculate text position (centered)
    bbox = draw.textbbox((0, 0), main_text, font=main_font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    text_x = (width - text_w) // 2
    text_y = (height - text_h) // 2 - 60

    # Draw text shadow
    shadow_offset = 4
    draw.text((text_x + shadow_offset, text_y + shadow_offset),
              main_text, font=main_font, fill=(0, 0, 0, 80))

    # Draw main text (white)
    draw.text((text_x, text_y), main_text, font=main_font, fill=(255, 255, 255))

    # Draw subtitle
    if sub_text:
        try:
            sub_font = ImageFont.truetype(font_path, 64) if font_path else ImageFont.load_default()
        except Exception:
            sub_font = ImageFont.load_default()

        # Subtitle background pill
        sub_bbox = draw.textbbox((0, 0), sub_text, font=sub_font)
        sub_w = sub_bbox[2] - sub_bbox[0]
        sub_h = sub_bbox[3] - sub_bbox[1]
        sub_x = (width - sub_w) // 2
        sub_y = text_y + text_h + 60

        pill_padding = 20
        pill_rect = (
            sub_x - pill_padding,
            sub_y - pill_padding // 2,
            sub_x + sub_w + pill_padding,
            sub_y + sub_h + pill_padding // 2,
        )
        draw_rounded_rect(draw, pill_rect, 15, fill=(0, 0, 0, 60))
        draw.text((sub_x, sub_y), sub_text, font=sub_font, fill=(255, 255, 255))

    # Add channel watermark (bottom right)
    try:
        wm_font = ImageFont.truetype(font_path, 28) if font_path else ImageFont.load_default()
    except Exception:
        wm_font = ImageFont.load_default()
    wm_text = "Happy Kids Việt"
    wm_bbox = draw.textbbox((0, 0), wm_text, font=wm_font)
    wm_w = wm_bbox[2] - wm_bbox[0]
    draw.text((width - wm_w - 30, height - 50), wm_text,
              font=wm_font, fill=(255, 255, 255, 180))

    # Save
    img.save(output_path, "PNG")
    return output_path


def generate_all_scenes(scene_descriptions, output_dir):
    """Generate all scene images for a video."""
    scenes_dir = os.path.join(output_dir, "scenes")
    os.makedirs(scenes_dir, exist_ok=True)

    scene_paths = []
    for i, scene in enumerate(scene_descriptions):
        filename = f"scene_{i+1:02d}.png"
        filepath = os.path.join(scenes_dir, filename)
        create_scene_image(scene, i, filepath)
        scene_paths.append(filepath)
        print(f"  🎨 Scene {i+1}/{len(scene_descriptions)}: {filename}")

    print(f"  ✅ Generated {len(scene_paths)} scene images")
    return scene_paths


if __name__ == "__main__":
    # Test: generate a single scene
    test_scene = {
        "text": "🌈 COLORS!",
        "sub": "Learn colors with us!",
        "bg_colors": [(77, 171, 247), (218, 119, 242)],
    }
    os.makedirs("test_output", exist_ok=True)
    create_scene_image(test_scene, 0, "test_output/test_scene.png")
    print("Test scene saved to test_output/test_scene.png")
