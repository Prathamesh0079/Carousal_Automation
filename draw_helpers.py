"""
Premium carousel renderer — decorative helpers & shared drawing primitives.
"""
import math
import random
import os
from PIL import Image, ImageDraw, ImageFont
from config import (
    WIDTH, HEIGHT, PAD_X, PAD_Y,
    WHITE, PURE_BLACK, DARK_TEXT, MUTED_TEXT,
    PRIMARY_DARK, BRIGHT_ACCENT, HIGHLIGHT, LIGHT_GRAY,
    SIZE_HEADING, SIZE_SUBHEADING, SIZE_BODY, SIZE_META,
    SIZE_PILL, SIZE_ITEM, SIZE_TAGLINE, SIZE_BRAND, SIZE_DECO,
    LINE_H, LINE_B, LINE_I, BG_COLORS, BRAND_NAME, BASE_DIR,
    SCALE,
)
from collections import deque
from utils import load_font, wrap_text, hex_to_rgb, darken, lighten, draw_text


def remove_background_floodfill(image):
    """
    Remove near-white background pixels of an image using a floodfill BFS from borders.
    This preserves white details inside the character.
    """
    img = image.convert("RGBA")
    width, height = img.size
    pixels = img.load()
    
    visited = [[False] * height for _ in range(width)]
    queue = deque()
    
    # Seed queue with border pixels
    for x in range(width):
        queue.append((x, 0))
        queue.append((x, height - 1))
        visited[x][0] = True
        visited[x][height - 1] = True
    for y in range(height):
        queue.append((0, y))
        queue.append((width - 1, y))
        visited[0][y] = True
        visited[width - 1][y] = True
        
    threshold = 230  # values above this are considered background white
    
    while queue:
        cx, cy = queue.popleft()
        r, g, b, a = pixels[cx, cy]
        if r > threshold and g > threshold and b > threshold:
            pixels[cx, cy] = (r, g, b, 0)
            
            # 4-connected neighbors
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < width and 0 <= ny < height:
                    if not visited[nx][ny]:
                        visited[nx][ny] = True
                        queue.append((nx, ny))
                        
    return img


def S(val):
    """Scale a numeric value by the resolution scale factor."""
    if val is None:
        return None
    return int(val * SCALE)


# ═══════════════════════════════════════════════════════
#  REUSABLE DRAWING HELPERS
# ═══════════════════════════════════════════════════════

def draw_pill(draw, x, y, width, height, fill=None, stroke=None,
              text="", font=None, text_color=WHITE, stroke_width=2):
    """Draw a rounded-rect pill badge with optional text."""
    r = height // 2
    s_width = S(stroke_width)
    if fill:
        draw.rounded_rectangle([x, y, x+width, y+height], radius=r, fill=fill,
                               outline=stroke, width=s_width if stroke else 0)
    elif stroke:
        draw.rounded_rectangle([x, y, x+width, y+height], radius=r,
                               outline=stroke, width=s_width)
    if text and font:
        bbox = font.getbbox(text)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = x + (width - tw) // 2
        ty = y + (height - th) // 2 - S(2)
        draw_text(draw, (tx, ty), text, font=font, fill=text_color)


def draw_oval_highlight(draw, x, y, w, h, color, thickness=3):
    """Draw an ellipse outline to simulate a hand-drawn circle highlight."""
    draw.ellipse([x-S(8), y-S(4), x+w+S(8), y+h+S(4)], outline=color, width=S(thickness))


def draw_checklist(draw, items, x, y, font, check_color=BRIGHT_ACCENT,
                   text_color=WHITE, line_height=52, max_width=None):
    """Render checkmark-prefixed list with vector checkmarks. Supports multi-line wrapping."""
    for item in items:
        text_w = max_width - S(45) if max_width else None
        if text_w:
            lines = wrap_text(item, font, text_w, draw)
        else:
            lines = [item]
            
        cy = y + font.size // 4
        draw.line([(x + S(4), cy + S(12)), (x + S(12), cy + S(20))], fill=check_color, width=S(4))
        draw.line([(x + S(12), cy + S(20)), (x + S(24), cy + S(6))], fill=check_color, width=S(4))
        
        for idx, line in enumerate(lines):
            draw_text(draw, (x + S(45), y), line, font=font, fill=text_color)
            if idx < len(lines) - 1:
                y += line_height
        y += line_height
    return y


def draw_arrow_items(draw, items, x, y, font, color=WHITE, line_height=52, max_width=None):
    """Render chevron-prefixed bullet list with vector chevrons. Supports multi-line wrapping."""
    for item in items:
        text_w = max_width - S(45) if max_width else None
        if text_w:
            lines = wrap_text(item, font, text_w, draw)
        else:
            lines = [item]
            
        cy = y + font.size // 4
        draw.line([(x + S(8), cy + S(6)), (x + S(16), cy + S(13))], fill=color, width=S(3))
        draw.line([(x + S(16), cy + S(13)), (x + S(8), cy + S(20))], fill=color, width=S(3))
        
        for idx, line in enumerate(lines):
            draw_text(draw, (x + S(45), y), line, font=font, fill=color)
            if idx < len(lines) - 1:
                y += line_height
        y += line_height
    return y


def draw_dash_items(draw, items, x, y, font, color=WHITE, line_height=52, max_width=None):
    """Render neon-tag prefixed bullet list for modern_dark theme."""
    for item in items:
        text_w = max_width - S(50) if max_width else None
        if text_w:
            lines = wrap_text(item, font, text_w, draw)
        else:
            lines = [item]
        
        # Draw neon tag prefix
        tag_y = y + font.size // 2 - S(5)
        draw.rectangle([x, tag_y, x + S(16), tag_y + S(10)], fill="#FF6B35")
        
        for idx, line in enumerate(lines):
            draw_text(draw, (x + S(40), y), line, font=font, fill=color)
            if idx < len(lines) - 1:
                y += line_height
        y += line_height + S(12)
    return y


def draw_numbered_items(draw, items, x, y, font, number_font, 
                        number_color=BRIGHT_ACCENT, text_color=WHITE,
                        line_height=52, max_width=None, dot_radius=16):
    """Render numbered items with accent-colored number dots for blueprint theme."""
    for idx, item in enumerate(items):
        text_w = max_width - S(65) if max_width else None
        if text_w:
            lines = wrap_text(item, font, text_w, draw)
        else:
            lines = [item]
        
        # Draw number circle
        num_cy = y + font.size // 2
        r = S(dot_radius)
        draw.ellipse([x, num_cy - r, x + r * 2, num_cy + r], fill=number_color)
        num_str = str(idx + 1)
        draw_text(draw, (x + r, num_cy), num_str, font=number_font, 
                  fill=DARK_TEXT, anchor="mm")
        
        # Draw text lines
        for li, line in enumerate(lines):
            draw_text(draw, (x + S(55), y), line, font=font, fill=text_color)
            if li < len(lines) - 1:
                y += line_height
        y += line_height + S(5)
    return y


def draw_angled_badge(draw, x, y, text, font, bg_color="#FFFFFF", 
                      text_color="#FF5733", rotation=0):
    """Draw a rotated/angled label badge with a drop shadow (for bold_coral theme)."""
    tw = draw.textlength(text, font=font)
    pad_x = S(24)
    pad_y = S(14)
    badge_w = int(tw) + pad_x * 2
    badge_h = font.size + pad_y * 2
    
    # Draw drop shadow (offset by S(6) px to bottom-right)
    shadow_color = "#9E260C"  # dark coral shadow
    draw.rounded_rectangle(
        [x + S(6), y + S(6), x + badge_w + S(6), y + badge_h + S(6)],
        radius=S(8), fill=shadow_color
    )
    
    # Draw the badge rectangle
    draw.rounded_rectangle(
        [x, y, x + badge_w, y + badge_h],
        radius=S(8), fill=bg_color
    )
    # Draw text centered in badge
    draw_text(draw, (x + badge_w // 2, y + badge_h // 2), text,
              font=font, fill=text_color, anchor="mm")
    return badge_w, badge_h


def draw_dot_network(draw, region, color, count=18):
    """Draw a decorative dot-and-line network graphic."""
    x0, y0, x1, y1 = region
    pts = [(random.randint(x0, x1), random.randint(y0, y1)) for _ in range(count)]
    # draw connecting lines
    for i in range(len(pts)):
        for j in range(i+1, len(pts)):
            dx = pts[i][0] - pts[j][0]
            dy = pts[i][1] - pts[j][1]
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < S(200):
                alpha_color = lighten(color, 0.5)
                draw.line([pts[i], pts[j]], fill=alpha_color, width=S(1))
    # draw dots
    for px, py in pts:
        r = random.randint(3, 7)
        draw.ellipse([px-r, py-r, px+r, py+r], fill=color)


def draw_glass_card(img, draw, x0, y0, x1, y1, bg_color=(255, 255, 255, 30), border_color=(255, 255, 255, 80), border_width=2, radius=12):
    """Draws a beautiful semi-transparent glassmorphic card container on the image."""
    card_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    card_draw = ImageDraw.Draw(card_layer)
    card_draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=bg_color)
    card_draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, outline=border_color, width=border_width)
    
    if img.mode == "RGBA":
        img.alpha_composite(card_layer)
    else:
        rgba = img.convert("RGBA")
        rgba.alpha_composite(card_layer)
        img.paste(rgba.convert("RGB"))


def draw_neo_brutalism_card(img, draw, x0, y0, x1, y1, bg_color="#FFFFFF", border_color="#000000", border_width=4, shadow_color="#D13A17", shadow_offset=12, radius=16):
    """Draws a beautiful Neo-Brutalist card with a thick black outline and a solid flat offset shadow."""
    s_offset = S(shadow_offset)
    s_width = S(border_width)
    s_radius = S(radius)
    
    # 1. Draw solid flat offset shadow block
    shadow_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sh_draw = ImageDraw.Draw(shadow_layer)
    sh_draw.rounded_rectangle(
        [x0 + s_offset, y0 + s_offset, x1 + s_offset, y1 + s_offset],
        radius=s_radius, fill=shadow_color
    )
    
    # 2. Draw card base with thick black outline
    sh_draw.rounded_rectangle(
        [x0, y0, x1, y1],
        radius=s_radius, fill=bg_color, outline=border_color, width=s_width
    )
    
    # 3. Composite onto destination image
    if img.mode == "RGBA":
        img.alpha_composite(shadow_layer)
    else:
        rgba = img.convert("RGBA")
        rgba.alpha_composite(shadow_layer)
        img.paste(rgba.convert("RGB"))



def draw_brand(draw, fonts):
    """Draw brand name in top-right corner."""
    font = fonts["brand"]
    draw.text((WIDTH - PAD_X - S(10), PAD_Y), BRAND_NAME,
              font=font, fill=MUTED_TEXT, anchor="ra")


def draw_page_indicator(draw, slide_num, total, fonts):
    """Draw bottom page dots."""
    dot_r = S(5)
    spacing = S(20)
    total_w = total * spacing
    sx = (WIDTH - total_w) // 2
    y = HEIGHT - PAD_Y + S(10)
    for i in range(total):
        cx = sx + i * spacing + dot_r
        if i == slide_num - 1:
            draw.ellipse([cx-dot_r, y-dot_r, cx+dot_r, y+dot_r], fill=WHITE)
        else:
            draw.ellipse([cx-dot_r, y-dot_r, cx+dot_r, y+dot_r],
                         outline=MUTED_TEXT, width=S(1))


def draw_linear_gradient(img, start_color_hex, end_color_hex):
    """Draws a vertical linear gradient onto the image very quickly using PIL resizing."""
    r1, g1, b1 = hex_to_rgb(start_color_hex)
    r2, g2, b2 = hex_to_rgb(end_color_hex)
    grad_img = Image.new("RGB", (1, 2))
    grad_img.putpixel((0, 0), (r1, g1, b1))
    grad_img.putpixel((0, 1), (r2, g2, b2))
    resized = grad_img.resize(img.size, Image.Resampling.BILINEAR)
    img.paste(resized, (0, 0))


def draw_radial_glow(img, cx, cy, radius, color_hex, max_alpha=120):
    """Draws a smooth radial glow spotlight behind elements using a resized alpha mask."""
    r, g, b = hex_to_rgb(color_hex)
    mask_sz = 128
    mask = Image.new("L", (mask_sz, mask_sz))
    pixels = mask.load()
    center = (mask_sz - 1) / 2.0
    for y in range(mask_sz):
        for x in range(mask_sz):
            dx = x - center
            dy = y - center
            dist = math.sqrt(dx*dx + dy*dy)
            pct = dist / center
            if pct >= 1.0:
                alpha = 0
            else:
                alpha = int(max_alpha * (1.0 - pct) ** 2)
            pixels[x, y] = alpha
            
    glow_src = Image.new("RGBA", (mask_sz, mask_sz), (r, g, b, 255))
    glow_src.putalpha(mask)
    glow_resized = glow_src.resize((radius * 2, radius * 2), Image.Resampling.BILINEAR)
    img.paste(glow_resized, (cx - radius, cy - radius), glow_resized)


def draw_floating_blobs(img):
    """Draws elegant floating blobs with translucent gradient glow for Bold Coral."""
    draw_radial_glow(img, WIDTH, S(200), S(350), "#FFFFFF", max_alpha=45)
    draw_radial_glow(img, 0, HEIGHT - S(300), S(450), "#FFD700", max_alpha=35)
    draw_radial_glow(img, WIDTH, HEIGHT // 2, S(300), "#FFFFFF", max_alpha=25)


def draw_blueprint_geometry(draw):
    """Draws beautiful blueprint engineering geometry: concentric rings, coordinates, and crosshairs."""
    from config import ACTIVE_THEME, TEMPLATES
    theme = TEMPLATES.get(ACTIVE_THEME)
    line_color = lighten(theme["bg_dark"], 0.20)
    
    # Horizontal center-line
    cy = HEIGHT // 2
    draw.line([(0, cy), (WIDTH, cy)], fill=line_color, width=S(1))
    
    # Vertical line on the right side where the curve is
    cx = WIDTH - PAD_X - S(80)
    draw.line([(cx, 0), (cx, HEIGHT)], fill=line_color, width=S(1))
    
    # Coordinate ticks on crosshairs
    tick_sz = S(8)
    for y in range(0, HEIGHT, S(100)):
        draw.line([(cx - tick_sz, y), (cx + tick_sz, y)], fill=line_color, width=S(1))
    for x in range(0, WIDTH, S(100)):
        draw.line([(x, cy - tick_sz), (x, cy + tick_sz)], fill=line_color, width=S(1))
        
    # Draw concentric circles
    for r in [S(200), S(400), S(600)]:
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=line_color, width=S(1))


def draw_editorial_borders(draw):
    """Draws a sophisticated thin double frame border around the slide."""
    pad1 = S(20)
    draw.rectangle([pad1, pad1, WIDTH - pad1, HEIGHT - pad1], outline="#E5D9D3", width=S(1))
    pad2 = S(26)
    draw.rectangle([pad2, pad2, WIDTH - pad2, HEIGHT - pad2], outline="#E5D9D3", width=S(1))


def draw_divider(draw, y, color=WHITE, width_ratio=0.3):
    """Draw a horizontal divider line."""
    lw = int(WIDTH * width_ratio)
    x0 = PAD_X
    draw.line([(x0, y), (x0 + lw, y)], fill=color, width=S(2))
    return y + S(20)


def draw_thin_hr(draw, y, color="#D0C4BE", full_width=True):
    """Draw a thin full-width horizontal rule (for editorial_blush theme)."""
    if full_width:
        draw.line([(PAD_X, y), (WIDTH - PAD_X, y)], fill=color, width=S(1))
    else:
        draw.line([(PAD_X, y), (PAD_X + int(WIDTH * 0.3), y)], fill=color, width=S(1))
    return y + S(20)


def draw_theme_background(img, draw, bg_color):
    """Draw a dynamic premium background based on the active template's style."""
    width, height = img.size
    from config import ACTIVE_THEME, TEMPLATES
    theme = TEMPLATES.get(ACTIVE_THEME, TEMPLATES["classic_dark"])
    
    if ACTIVE_THEME == "classic_dark":
        # Deep Indigo-Black canvas with multiple floating, soft-glowing orbs for SupaUI aesthetic
        draw_linear_gradient(img, "#080C14", "#0E1420")
        draw_radial_glow(img, width // 4, height // 3, S(320), "#9B5DE5", max_alpha=30)
        draw_radial_glow(img, width - width // 4, height // 2, S(380), "#00F5D4", max_alpha=25)
        draw_radial_glow(img, width // 2, height - height // 4, S(420), "#FFD700", max_alpha=20)
        
    elif ACTIVE_THEME == "editorial_blush":
        # Warm rose-to-cream textured gradient with double borders
        draw_linear_gradient(img, "#EAE0DA", "#FFFDFB")
        draw_editorial_borders(draw)
        
    elif ACTIVE_THEME == "bold_coral":
        # Vibrant coral gradient with floating glassmorphic gradient circles
        draw_linear_gradient(img, "#FF5733", "#D13A17")
        draw_floating_blobs(img)
        
    elif ACTIVE_THEME == "blueprint_grid":
        # Deep blue gradient background with blueprint grid and geometry overlays
        draw_linear_gradient(img, "#0C1F4A", "#1D429F")
        dot_color = lighten("#0C1F4A", 0.12)
        spacing = S(30)
        dot_r = S(2)
        for gx in range(spacing, width, spacing):
            for gy in range(spacing, height, spacing):
                draw.ellipse([gx - dot_r, gy - dot_r, gx + dot_r, gy + dot_r], fill=dot_color)
        draw_blueprint_geometry(draw)
        
    elif ACTIVE_THEME == "modern_dark":
        # Sleek pitch black/charcoal gradient with central warm orange spotlight
        draw_linear_gradient(img, "#080808", "#1A1A1A")
        draw_radial_glow(img, width // 2, height // 2, S(400), "#FF6B35", max_alpha=40)


def draw_decorative_curve(draw, color="#C8FF00"):
    """Draw a decorative yellow/green swoosh curve on the right side (for blueprint theme)."""
    # Draw a thick curved accent line on the right side of the canvas
    cx = WIDTH - PAD_X - S(80)
    start_y = HEIGHT // 3
    end_y = HEIGHT // 3 * 2
    
    points = []
    for i in range(50):
        t = i / 49.0
        y = start_y + (end_y - start_y) * t
        # Create a smooth S-curve
        x_offset = math.sin(t * math.pi) * S(60)
        points.append((cx + x_offset, y))
    
    # Draw as thick polyline
    for i in range(len(points) - 1):
        draw.line([points[i], points[i+1]], fill=color, width=S(8))


def draw_corner_decoration(draw, corner, color, size=40):
    """Draw small decorative corner elements based on the active theme."""
    from config import ACTIVE_THEME, TEMPLATES
    theme = TEMPLATES.get(ACTIVE_THEME, TEMPLATES["classic_dark"])
    layout = theme.get("layout", "centered_corporate")
    
    if layout == "centered_corporate":
        # Small dot grid in corners
        spacing = S(18)
        cols, rows = 4, 5
        if corner == "tl":
            draw_dot_grid(draw, PAD_X, PAD_Y + S(40), rows=rows, cols=cols, color=color, spacing=spacing)
        elif corner == "tr":
            grid_w = (cols - 1) * spacing
            draw_dot_grid(draw, WIDTH - PAD_X - grid_w, PAD_Y + S(40), rows=rows, cols=cols, color=color, spacing=spacing)
    elif layout == "grid_impact":
        # Small corner brackets for blueprint
        sz = S(20)
        w = S(3)
        pad = S(40)
        if corner == "tl":
            draw.line([(pad, pad), (pad + sz, pad)], fill=color, width=w)
            draw.line([(pad, pad), (pad, pad + sz)], fill=color, width=w)
        elif corner == "br":
            draw.line([(WIDTH - pad, HEIGHT - pad), (WIDTH - pad - sz, HEIGHT - pad)], fill=color, width=w)
            draw.line([(WIDTH - pad, HEIGHT - pad), (WIDTH - pad, HEIGHT - pad - sz)], fill=color, width=w)
    # Other themes: no corner decorations (clean look)


def draw_dot_grid(draw, x, y, rows=5, cols=4, color=WHITE, spacing=18, radius=3):
    """Draw a decorative grid of dots."""
    r_val = S(radius)
    for r in range(rows):
        for c in range(cols):
            cx = x + c * spacing
            cy = y + r * spacing
            draw.ellipse([cx - r_val, cy - r_val, cx + r_val, cy + r_val], fill=color)


_logo_puzzle_cache = None
_logo_text_cache = None

def _get_logo_images():
    global _logo_puzzle_cache, _logo_text_cache
    if _logo_puzzle_cache is None:
        puzzle_path = os.path.join(BASE_DIR, "assets", "logo_puzzle_fixed.png")
        if os.path.exists(puzzle_path):
            _logo_puzzle_cache = Image.open(puzzle_path)
        else:
            print(f"  [warn] fixed puzzle logo image not found at {puzzle_path}")
            
    if _logo_text_cache is None:
        text_path = os.path.join(BASE_DIR, "assets", "logo_text_white.png")
        if os.path.exists(text_path):
            _logo_text_cache = Image.open(text_path)
        else:
            print(f"  [warn] text logo image not found at {text_path}")
            
    return _logo_puzzle_cache, _logo_text_cache


def draw_logo(img, cx, cy, puzzle_h=70, text_h=30, spacing=8):
    """Draw the WiseTribes logo (puzzle pieces + text) centered at (cx, cy)."""
    puzzle_h = S(puzzle_h)
    text_h = S(text_h)
    spacing = S(spacing)
    
    puzzle_img, text_img = _get_logo_images()
    if not puzzle_img or not text_img:
        return
        
    p_w, p_h = puzzle_img.size
    aspect_p = p_w / p_h
    new_p_h = puzzle_h
    new_p_w = int(puzzle_h * aspect_p)
    puzzle_resized = puzzle_img.resize((new_p_w, new_p_h), Image.Resampling.LANCZOS)
    
    t_w, t_h = text_img.size
    aspect_t = t_w / t_h
    new_t_h = text_h
    new_t_w = int(text_h * aspect_t)
    text_resized = text_img.resize((new_t_w, new_t_h), Image.Resampling.LANCZOS)
    
    # Dynamically tint the logo text to match the theme's primary text color (WHITE constant)
    from config import WHITE as PRIMARY_TEXT_COLOR
    from utils import hex_to_rgb
    try:
        tr, tg, tb = hex_to_rgb(PRIMARY_TEXT_COLOR)
        if text_resized.mode == "RGBA":
            _, _, _, a_chan = text_resized.split()
            new_r = Image.new("L", text_resized.size, tr)
            new_g = Image.new("L", text_resized.size, tg)
            new_b = Image.new("L", text_resized.size, tb)
            text_resized = Image.merge("RGBA", (new_r, new_g, new_b, a_chan))
    except Exception as e:
        print(f"  Warning: failed to dynamically tint logo text: {e}")
        
    total_h = new_p_h + spacing + new_t_h
    
    px = cx - new_p_w // 2
    py = cy - total_h // 2
    
    # Top-left of the text
    tx = cx - new_t_w // 2
    ty = py + new_p_h + spacing
    
    # Paste both onto img with alpha mask
    img.paste(puzzle_resized, (px, py), puzzle_resized)
    img.paste(text_resized, (tx, ty), text_resized)


_brand_logo_cache = None

def draw_brand_logo(img, cx, cy, size=60):
    """Draw the logo.png from the root directory centered at (cx, cy)."""
    global _brand_logo_cache
    if _brand_logo_cache is None:
        logo_path = os.path.join(BASE_DIR, "logo.png")
        if os.path.exists(logo_path):
            try:
                _brand_logo_cache = Image.open(logo_path).convert("RGBA")
            except Exception as e:
                print(f"  Warning: failed to load brand logo from {logo_path}: {e}")
        else:
            print(f"  [warn] brand logo not found at {logo_path}")
            
    if _brand_logo_cache:
        sz = S(size)
        resized = _brand_logo_cache.resize((sz, sz), Image.Resampling.LANCZOS)
        img.paste(resized, (cx - sz // 2, cy - sz // 2), resized)
        return True
    return False



def draw_bottom_bar_classic(draw, cx, cy, brand_text, tagline, font_brand, font_tagline):
    """Classic Dark: Joined pill bar (white + gold)."""
    from config import WHITE, BRIGHT_ACCENT, DARK_TEXT
    h = S(56)
    w_brand = draw.textlength(brand_text, font=font_brand)
    w_tag = draw.textlength(tagline, font=font_tagline)
    pad_b = S(40)
    pad_t = S(45)
    w1 = int(w_brand + pad_b)
    w2 = int(w_tag + pad_t)
    overlap = S(20)
    total_w = w1 + w2 - overlap
    x_start = cx - total_w // 2
    
    draw.rounded_rectangle(
        [x_start, cy - h//2, x_start + w1, cy + h//2],
        radius=h//2, fill=WHITE
    )
    x_yellow = x_start + w1 - overlap
    draw.rounded_rectangle(
        [x_yellow, cy - h//2, x_yellow + w2, cy + h//2],
        radius=h//2, fill=BRIGHT_ACCENT
    )
    brand_cx = x_start + (w1 - overlap // 2) // 2
    draw.text((brand_cx, cy), brand_text, font=font_brand, fill=DARK_TEXT, anchor="mm")
    tag_cx = x_yellow + w2 // 2
    draw_text(draw, (tag_cx, cy), tagline, font=font_tagline, fill=DARK_TEXT, anchor="mm")


def draw_bottom_bar_editorial(draw, y, url_text, font):
    """Editorial Blush: Thin HR lines above and below centered URL."""
    color = "#D0C4BE"
    draw.line([(PAD_X, y), (WIDTH - PAD_X, y)], fill=color, width=S(1))
    y += S(18)
    tw = draw.textlength(url_text, font=font)
    draw_text(draw, ((WIDTH - tw) // 2, y), url_text.upper(), font=font, fill="#1A1A1A")
    y += S(30)
    draw.line([(PAD_X, y), (WIDTH - PAD_X, y)], fill=color, width=S(1))


def draw_bottom_bar_coral(draw, y, url_text, font):
    """Bold Coral: Simple white text URL at bottom center."""
    tw = draw.textlength(url_text, font=font)
    draw_text(draw, ((WIDTH - tw) // 2, y), url_text.upper(), font=font, fill="#FFFFFF")


def draw_bottom_bar_blueprint(draw, y, url_text, font):
    """Blueprint Grid: Asterisk icon + URL at bottom center."""
    from config import BRIGHT_ACCENT
    full_text = f"✦  {url_text.upper()}"
    tw = draw.textlength(full_text, font=font)
    draw_text(draw, ((WIDTH - tw) // 2, y), full_text, font=font, fill=BRIGHT_ACCENT)


def draw_bottom_bar_modern(draw, y, brand_text, font):
    """Modern Dark: Small brand text at bottom right with accent dot."""
    from config import BRIGHT_ACCENT
    draw.ellipse([WIDTH - PAD_X - S(8), y + S(4), WIDTH - PAD_X, y + S(12)], fill=BRIGHT_ACCENT)
    draw_text(draw, (WIDTH - PAD_X - S(16), y), brand_text.upper(), font=font, fill="#888888", anchor="ra")


def draw_top_pills_editorial(draw, brand_text, handle_text, font):
    """Editorial Blush: Two outlined pill buttons at top."""
    y = PAD_Y + S(20)
    
    # Brand pill (outlined)
    tw1 = draw.textlength(brand_text, font=font)
    pw1 = int(tw1) + S(30)
    ph = S(36)
    draw.rounded_rectangle([PAD_X, y, PAD_X + pw1, y + ph], radius=ph//2, 
                            outline="#1A1A1A", width=S(2))
    draw_text(draw, (PAD_X + pw1//2, y + ph//2), brand_text, font=font, fill="#1A1A1A", anchor="mm")
    
    # Handle pill (outlined)
    tw2 = draw.textlength(handle_text, font=font)
    pw2 = int(tw2) + S(30)
    x2 = PAD_X + pw1 + S(12)
    draw.rounded_rectangle([x2, y, x2 + pw2, y + ph], radius=ph//2, 
                            outline="#1A1A1A", width=S(2))
    draw_text(draw, (x2 + pw2//2, y + ph//2), handle_text, font=font, fill="#1A1A1A", anchor="mm")


def draw_top_bar_coral(draw, brand_text, url_text, font_brand, font_url):
    """Bold Coral: Brand name + URL at top-left in white."""
    y = PAD_Y + S(20)
    draw_text(draw, (PAD_X, y), brand_text.upper(), font=font_brand, fill="#FFFFFF")
    y += S(30)
    draw_text(draw, (PAD_X, y), url_text, font=font_url, fill="#FFE0D6")


def draw_top_bar_blueprint(draw, brand_text, year_text, font):
    """Blueprint Grid: Name at top-left, year at top-right (shifted left to clear logo)."""
    y = PAD_Y + S(20)
    draw_text(draw, (PAD_X, y), brand_text.upper(), font=font, fill="#FFFFFF")
    tw = draw.textlength(year_text, font=font)
    draw_text(draw, (WIDTH - PAD_X - S(100) - tw, y), year_text, font=font, fill="#FFFFFF")


def draw_slide_illustration(img, cx, cy, sn, size=350, image_prompt=None):
    """
    Dynamically fetch a cartoonish illustration from Pollinations using the slide prompt,
    cache it locally in the output folder, and draw it centered at (cx, cy).
    """
    import os
    import urllib.request
    import urllib.parse
    import ssl
    from PIL import Image
    from config import ACTIVE_THEME, TEMPLATES, OUTPUT_DIR, BASE_DIR
    
    size = S(size)
    
    # 1. Determine background style based on active theme to blend the illustration perfectly
    theme = TEMPLATES.get(ACTIVE_THEME, {})
    bg_style = "white background"
    
    if ACTIVE_THEME == "editorial_blush":
        bg_style = "soft pastel pink background"
    elif ACTIVE_THEME == "bold_coral":
        bg_style = "vibrant coral orange background"
    elif ACTIVE_THEME == "blueprint_grid":
        bg_style = "deep blue background"
    elif ACTIVE_THEME == "classic_dark":
        bg_style = "dark navy background"
    elif ACTIVE_THEME == "modern_dark":
        bg_style = "black background"
        
    prompt_text = image_prompt or ""
    import hashlib
    h_str = f"{sn}_{prompt_text}"
    h = hashlib.md5(h_str.encode("utf-8")).hexdigest()[:8]
    cache_path = os.path.join(OUTPUT_DIR, f"dynamic_illustration_{sn}_{h}.png")
    
    # If no prompt, fallback to rendering existing cache or local assets
    if not prompt_text:
        if os.path.exists(cache_path):
            try:
                ill = Image.open(cache_path).convert("RGBA")
                ill = ill.resize((size, size), Image.Resampling.LANCZOS)
                img.paste(ill, (cx - size // 2, cy - size // 2), ill)
                return True
            except Exception:
                pass
        
        static_path = os.path.join(BASE_DIR, "assets", f"illustration_slide_{sn}.png")
        if os.path.exists(static_path):
            try:
                ill = Image.open(static_path).convert("RGBA")
                ill = ill.resize((size, size), Image.Resampling.LANCZOS)
                img.paste(ill, (cx - size // 2, cy - size // 2), ill)
                return True
            except Exception:
                pass
        return False
        
    # Styled prompt to ensure cartoonish, clean, vector style, and white background
    styled_prompt = f"A simple cute 2D flat cartoon illustration of {prompt_text}, clean vector graphic, flat colors, isolated on pure white background, minimal design, no clutter, no text"
    
    if not os.path.exists(cache_path):
        print(f"  Fetching dynamic illustration for Slide {sn} ('{prompt_text}') from Pollinations...")
        import time
        max_retries = 3
        for attempt in range(max_retries):
            try:
                encoded_prompt = urllib.parse.quote(styled_prompt)
                url = f"https://image.pollinations.ai/p/{encoded_prompt}?model=flux&width=512&height=512&nologo=true"
                
                # If retrying, wait 4s to allow rate limits to clear
                if attempt > 0:
                    print(f"    [warn] Retrying in 4s (attempt {attempt+1}/{max_retries})...")
                    time.sleep(4)
                else:
                    # Small 1s delay on initial request to prevent concurrent request flooding
                    time.sleep(1)
                    
                ssl_context = ssl._create_unverified_context()
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, context=ssl_context, timeout=45) as response:
                    with open(cache_path, "wb") as f:
                        f.write(response.read())
                print(f"  ✓ Saved slide {sn} illustration to cache")
                break
            except Exception as e:
                print(f"    [warn] Attempt {attempt+1} failed: {e}")
                if attempt == max_retries - 1:
                    print(f"  [warn] Failed to fetch dynamic illustration after {max_retries} attempts.")
                    # Fallback to local asset if available
                    static_path = os.path.join(BASE_DIR, "assets", f"illustration_slide_{sn}.png")
                    if os.path.exists(static_path):
                        try:
                            ill = Image.open(static_path).convert("RGBA")
                            ill = ill.resize((size, size), Image.Resampling.LANCZOS)
                            img.paste(ill, (cx - size // 2, cy - size // 2), ill)
                            return True
                        except Exception:
                            pass
                    return False
            
    if os.path.exists(cache_path):
        try:
            ill = Image.open(cache_path)
            ill = remove_background_floodfill(ill)
            ill = ill.resize((size, size), Image.Resampling.LANCZOS)
            img.paste(ill, (cx - size // 2, cy - size // 2), ill)
            return True
        except Exception as e:
            print(f"  Warning: failed to render illustration {cache_path}: {e}")
            
    return False
