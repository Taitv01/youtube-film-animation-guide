"""
Image Generator - Creates vibrant, kid-friendly scene images using Pillow.
Rich graphics: patterns, shapes, borders, rainbow text, themed decorations.
"""
import os
import math
import random
from PIL import Image, ImageDraw, ImageFont
from config import VIDEO_WIDTH, VIDEO_HEIGHT, get_font_path

# Seed for reproducible decorations per scene
random.seed(42)

# Kid-friendly color palettes per theme
SCENE_PALETTES = [
    [(255, 89, 94), (255, 146, 148)],     # Red
    [(52, 152, 219), (133, 193, 233)],     # Blue
    [(254, 202, 87), (255, 234, 167)],     # Yellow
    [(46, 204, 113), (130, 224, 170)],     # Green
    [(155, 89, 182), (195, 155, 211)],     # Purple
    [(255, 165, 2), (255, 202, 97)],       # Orange
    [(241, 148, 138), (245, 183, 177)],    # Pink
    [(52, 73, 94), (127, 140, 141)],       # Dark
    [(26, 188, 156), (115, 216, 198)],     # Teal
    [(230, 126, 34), (240, 178, 122)],     # Burnt Orange
    [(52, 152, 219), (174, 214, 241)],     # Sky Blue
    [(231, 76, 60), (236, 135, 126)],      # Coral
]


def _draw_star(draw, cx, cy, r, fill):
    """Draw a filled star."""
    points = []
    for i in range(10):
        angle = math.pi / 2 + i * math.pi / 5
        radius = r if i % 2 == 0 else r * 0.4
        x = cx + radius * math.cos(angle)
        y = cy - radius * math.sin(angle)
        points.append((x, y))
    draw.polygon(points, fill=fill)


def _draw_heart(draw, cx, cy, size, fill):
    """Draw a heart shape."""
    s = size
    points = []
    for t_val in range(0, 360, 5):
        t = math.radians(t_val)
        x = cx + s * 0.5 * (16 * math.sin(t)**3) / 16
        y = cy - s * 0.5 * (13*math.cos(t) - 5*math.cos(2*t) - 2*math.cos(3*t) - math.cos(4*t)) / 16
        points.append((x, y))
    if len(points) > 2:
        draw.polygon(points, fill=fill)


def _draw_cloud(draw, cx, cy, size, fill):
    """Draw a simple cloud shape."""
    s = size
    draw.ellipse([cx - s, cy - s*0.5, cx + s*0.3, cy + s*0.5], fill=fill)
    draw.ellipse([cx - s*0.5, cy - s*0.8, cx + s*0.5, cy + s*0.1], fill=fill)
    draw.ellipse([cx - s*0.1, cy - s*0.5, cx + s, cy + s*0.5], fill=fill)


def _draw_flower(draw, cx, cy, size, fill, center_fill):
    """Draw a simple flower."""
    for angle in range(0, 360, 60):
        rad = math.radians(angle)
        px = cx + size * 0.6 * math.cos(rad)
        py = cy + size * 0.6 * math.sin(rad)
        draw.ellipse([px - size*0.4, py - size*0.4, px + size*0.4, py + size*0.4], fill=fill)
    draw.ellipse([cx - size*0.3, cy - size*0.3, cx + size*0.3, cy + size*0.3], fill=center_fill)


def _draw_diamond(draw, cx, cy, size, fill):
    """Draw a diamond shape."""
    points = [(cx, cy - size), (cx + size*0.6, cy), (cx, cy + size), (cx - size*0.6, cy)]
    draw.polygon(points, fill=fill)


def _draw_polka_dots(draw, width, height, color, count=30, max_r=12):
    """Draw polka dots pattern."""
    rng = random.Random(hash((width, height, count)))
    for _ in range(count):
        x = rng.randint(0, width)
        y = rng.randint(0, height)
        r = rng.randint(4, max_r)
        alpha_color = (*color[:3], 50)
        draw.ellipse([x-r, y-r, x+r, y+r], fill=alpha_color)


def _draw_rainbow_arc(draw, cx, cy, radius, thickness=8):
    """Draw a rainbow arc."""
    rainbow = [(255,0,0), (255,127,0), (255,255,0), (0,255,0), (0,0,255), (75,0,130), (148,0,211)]
    for i, color in enumerate(rainbow):
        r = radius - i * thickness
        if r > 0:
            draw.arc([cx-r, cy-r, cx+r, cy+r], 180, 360, fill=color, width=thickness)


def _draw_border_frame(draw, width, height, color, thickness=6):
    """Draw a decorative rounded border."""
    r = 25
    # Top
    draw.rectangle([r, 0, width-r, thickness], fill=color)
    # Bottom
    draw.rectangle([r, height-thickness, width-r, height], fill=color)
    # Left
    draw.rectangle([0, r, thickness, height-r], fill=color)
    # Right
    draw.rectangle([width-thickness, r, width, height-r], fill=color)
    # Corners - small circles
    for cx, cy in [(r, r), (width-r, r), (r, height-r), (width-r, height-r)]:
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=color, width=thickness)


def _draw_confetti(draw, width, height, count=40):
    """Draw colorful confetti."""
    colors = [(255,89,94), (255,202,87), (46,204,113), (52,152,219), (155,89,182), (255,165,2)]
    rng = random.Random(hash((width, height, count, 99)))
    for _ in range(count):
        x = rng.randint(0, width)
        y = rng.randint(0, height)
        c = rng.choice(colors)
        shape = rng.choice(["rect", "circle", "star"])
        s = rng.randint(4, 10)
        alpha_c = (*c, 120)
        if shape == "rect":
            angle = rng.randint(0, 45)
            draw.rectangle([x, y, x+s*2, y+s], fill=alpha_c)
        elif shape == "circle":
            draw.ellipse([x-s, y-s, x+s, y+s], fill=alpha_c)
        else:
            _draw_star(draw, x, y, s, alpha_c)


def create_scene_image(scene_desc, scene_index, output_path,
                       width=None, height=None):
    """
    Create a rich, kid-friendly scene image.
    """
    width = width or VIDEO_WIDTH
    height = height or VIDEO_HEIGHT

    text = scene_desc.get("text", "")
    subtext = scene_desc.get("subtext", "")
    bg_colors = scene_desc.get("bg_colors", [(77, 171, 247), (218, 119, 242)])

    # Use RGBA for transparency effects
    img = Image.new("RGBA", (width, height))
    pixels = img.load()

    # === Gradient Background ===
    bg1, bg2 = bg_colors[0], bg_colors[1]
    # Alternate gradient directions per scene
    for y in range(height):
        for x in range(width):
            if scene_index % 3 == 0:
                ratio = y / height  # Vertical
            elif scene_index % 3 == 1:
                ratio = (x + y) / (width + height)  # Diagonal
            else:
                # Radial from center
                dx = (x - width/2) / (width/2)
                dy = (y - height/2) / (height/2)
                ratio = min(1.0, math.sqrt(dx*dx + dy*dy))
            r = int(bg1[0] * (1-ratio) + bg2[0] * ratio)
            g = int(bg1[1] * (1-ratio) + bg2[1] * ratio)
            b = int(bg1[2] * (1-ratio) + bg2[2] * ratio)
            pixels[x, y] = (r, g, b, 255)

    draw = ImageDraw.Draw(img)
    font_path = get_font_path()

    # === Background Patterns ===
    if scene_index % 2 == 0:
        _draw_polka_dots(draw, width, height, (255, 255, 255), count=35, max_r=15)
    else:
        _draw_confetti(draw, width, height, count=50)

    # === Decorative Border ===
    border_color = (*bg2, 180)
    _draw_border_frame(draw, width, height, border_color, thickness=5)

    # === Decorative Shapes ===
    rng = random.Random(scene_index * 7 + 13)

    # Stars (always present, varied positions)
    star_colors = [(255, 255, 255), (255, 234, 167), (255, 255, 200)]
    for _ in range(6):
        sx = rng.randint(40, width - 40)
        sy = rng.randint(40, height - 40)
        sr = rng.randint(12, 30)
        sc = rng.choice(star_colors)
        _draw_star(draw, sx, sy, sr, sc)

    # Hearts (some scenes)
    if scene_index % 3 == 0:
        for _ in range(3):
            hx = rng.randint(60, width - 60)
            hy = rng.randint(60, height - 60)
            hs = rng.randint(15, 30)
            _draw_heart(draw, hx, hy, hs, (255, 100, 120, 180))

    # Clouds (some scenes)
    if scene_index % 3 == 1:
        for _ in range(2):
            cx = rng.randint(100, width - 100)
            cy = rng.randint(40, 180)
            cs = rng.randint(30, 50)
            _draw_cloud(draw, cx, cy, cs, (255, 255, 255, 100))

    # Flowers (some scenes)
    if scene_index % 3 == 2:
        for _ in range(3):
            fx = rng.randint(60, width - 60)
            fy = rng.randint(height - 300, height - 80)
            fs = rng.randint(15, 25)
            petal = rng.choice([(255,182,193), (255,218,185), (221,160,221), (173,216,230)])
            _draw_flower(draw, fx, fy, fs, petal, (255, 255, 100))

    # Rainbow arc (every 4th scene)
    if scene_index % 4 == 0:
        _draw_rainbow_arc(draw, width // 2, height - 50, 180, 6)

    # Diamonds (scattered)
    for _ in range(rng.randint(2, 5)):
        dx = rng.randint(30, width - 30)
        dy = rng.randint(30, height - 30)
        ds = rng.randint(6, 14)
        dc = rng.choice([(255,255,255,150), (255,234,167,150), (174,214,241,150)])
        _draw_diamond(draw, dx, dy, ds, dc)

    # Large decorative circles
    for _ in range(rng.randint(2, 4)):
        cx = rng.randint(0, width)
        cy = rng.randint(0, height)
        cr = rng.randint(40, 120)
        draw.ellipse([cx-cr, cy-cr, cx+cr, cy+cr],
                     outline=(255, 255, 255, 60), width=3)

    # === Main Text ===
    try:
        title_font = ImageFont.truetype(font_path, 120) if font_path else ImageFont.load_default()
    except Exception:
        title_font = ImageFont.load_default()

    display_text = text.upper() if text else ""
    if display_text:
        # Auto-scale to fit
        max_w = int(width * 0.85)
        fsize = 120
        while fsize > 40:
            try:
                title_font = ImageFont.truetype(font_path, fsize) if font_path else ImageFont.load_default()
            except:
                break
            bbox = draw.textbbox((0, 0), display_text, font=title_font)
            if (bbox[2] - bbox[0]) <= max_w:
                break
            fsize -= 5

        bbox = draw.textbbox((0, 0), display_text, font=title_font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = (width - tw) // 2
        ty = (height - th) // 2 - 40

        # Text shadow (3D effect)
        for ox, oy in [(4,4), (3,3), (2,2)]:
            shadow_alpha = 80 + ox * 30
            draw.text((tx+ox, ty+oy), display_text, font=title_font,
                      fill=(0, 0, 0, shadow_alpha))

        # White outline
        for ox in [-2, 0, 2]:
            for oy in [-2, 0, 2]:
                if ox != 0 or oy != 0:
                    draw.text((tx+ox, ty+oy), display_text, font=title_font,
                              fill=(255, 255, 255, 255))

        # Main text in vibrant color
        text_color = (255, 255, 255, 255)
        draw.text((tx, ty), display_text, font=title_font, fill=text_color)

    # === Subtitle with pill background ===
    if subtext:
        try:
            sub_font = ImageFont.truetype(font_path, 40) if font_path else ImageFont.load_default()
        except:
            sub_font = ImageFont.load_default()

        sub_bbox = draw.textbbox((0, 0), subtext, font=sub_font)
        sub_w = sub_bbox[2] - sub_bbox[0]
        sub_h = sub_bbox[3] - sub_bbox[1]
        sub_x = (width - sub_w) // 2
        sub_y = ty + th + 50 if display_text else (height - sub_h) // 2

        # Rounded pill background
        pad = 18
        pill_coords = (sub_x - pad*2, sub_y - pad, sub_x + sub_w + pad*2, sub_y + sub_h + pad)
        # Draw rounded rectangle manually
        rx, ry, rx2, ry2 = pill_coords
        r = 15
        draw.rectangle([rx+r, ry, rx2-r, ry2], fill=(0, 0, 0, 200))
        draw.rectangle([rx, ry+r, rx2, ry2-r], fill=(0, 0, 0, 200))
        draw.pieslice([rx, ry, rx+2*r, ry+2*r], 180, 270, fill=(0, 0, 0, 200))
        draw.pieslice([rx2-2*r, ry, rx2, ry+2*r], 270, 360, fill=(0, 0, 0, 200))
        draw.pieslice([rx, ry2-2*r, rx+2*r, ry2], 90, 180, fill=(0, 0, 0, 200))
        draw.pieslice([rx2-2*r, ry2-2*r, rx2, ry2], 0, 90, fill=(0, 0, 0, 200))

        draw.text((sub_x, sub_y), subtext, font=sub_font, fill=(255, 255, 255, 255))

    # === Channel Watermark ===
    try:
        wm_font = ImageFont.truetype(font_path, 28) if font_path else ImageFont.load_default()
    except:
        wm_font = ImageFont.load_default()

    wm_text = "★ Happy Kids Việt ★"
    wm_bbox = draw.textbbox((0, 0), wm_text, font=wm_font)
    wm_w = wm_bbox[2] - wm_bbox[0]
    # Shadow
    draw.text((width - wm_w - 22, height - 52), wm_text, font=wm_font, fill=(0, 0, 0, 120))
    draw.text((width - wm_w - 20, height - 50), wm_text, font=wm_font, fill=(255, 255, 255, 220))

    # === Musical Notes (some scenes) ===
    if scene_index % 2 == 1:
        try:
            note_font = ImageFont.truetype(font_path, 36) if font_path else ImageFont.load_default()
        except:
            note_font = ImageFont.load_default()
        notes = ["♪", "♫", "♬"]
        for _ in range(4):
            nx = rng.randint(50, width - 50)
            ny = rng.randint(50, height - 50)
            note = rng.choice(notes)
            draw.text((nx, ny), note, font=note_font, fill=(255, 255, 255, 150))

    # Convert to RGB for saving
    img_rgb = img.convert("RGB")
    img_rgb.save(output_path, "PNG")
    return output_path


def generate_all_scenes(scene_descriptions, output_dir):
    """Generate all scene images."""
    os.makedirs(output_dir, exist_ok=True)
    scene_paths = []

    for i, scene_desc in enumerate(scene_descriptions):
        filename = f"scene_{i+1:02d}.png"
        output_path = os.path.join(output_dir, filename)
        create_scene_image(scene_desc, i, output_path)
        scene_paths.append(output_path)
        print(f"  🎨 Scene {i+1}/{len(scene_descriptions)}: {filename}")

    return scene_paths


if __name__ == "__main__":
    os.makedirs("test_output", exist_ok=True)
    test_scenes = [
        {"text": "🔴 RED", "subtext": "Red like apples!", "bg_colors": [(255, 89, 94), (255, 146, 148)]},
        {"text": "🔵 BLUE", "subtext": "Blue like the sky!", "bg_colors": [(52, 152, 219), (133, 193, 233)]},
        {"text": "🌈 COLORS!", "subtext": "Colors all around!", "bg_colors": [(155, 89, 182), (254, 202, 87)]},
    ]
    paths = generate_all_scenes(test_scenes, "test_output/scenes")
    print(f"\nGenerated {len(paths)} test scenes!")
