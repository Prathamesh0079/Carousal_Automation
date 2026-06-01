import os
import math
from PIL import ImageFont, ImageDraw
from config import (
    FONT_EXTRABOLD, FONT_BOLD, FONT_SEMIBOLD, FONT_REGULAR,
    OUTPUT_DIR, PAD_X,
)


def ensure_dir(path: str):
    """Create directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)


_font_cache = {}

def load_font(variant: str, size: int):
    """
    Load a Poppins font by variant name.
    variant: 'extrabold', 'bold', 'semibold', or 'regular'
    Falls back to Pillow default if .ttf not found.
    """
    key = (variant, size)
    if key in _font_cache:
        return _font_cache[key]

    paths = {
        "extrabold": FONT_EXTRABOLD,
        "bold":      FONT_BOLD,
        "semibold":  FONT_SEMIBOLD,
        "regular":   FONT_REGULAR,
    }
    path = paths.get(variant, FONT_REGULAR)
    try:
        font = ImageFont.truetype(path, size)
    except IOError:
        print(f"  [warn] Font not found: {path}. Using default.")
        font = ImageFont.load_default()
    _font_cache[key] = font
    return font


def draw_text(draw, xy, text, font, fill, anchor=None, **kwargs):
    """
    Draw text with full emoji support. Segments the string into
    text and emoji parts, renders text with PIL and emoji images
    from Twemoji, giving pixel-perfect alignment control.
    """
    import emoji as emoji_lib
    if emoji_lib.emoji_count(text) == 0 or not hasattr(draw, "img"):
        draw.text(xy, text, font=font, fill=fill, anchor=anchor, **kwargs)
        return

    from PIL import Image as PILImage
    from pilmoji.source import Twemoji

    font_size = font.size if hasattr(font, "size") else 24
    emoji_size = font_size  # render emoji at 1:1 with font height
    emoji_list = emoji_lib.emoji_list(text)

    # --- calculate total width for anchor adjustment ---
    total_w = 0.0
    last_idx = 0
    for match in emoji_list:
        s, e = match["match_start"], match["match_end"]
        if s > last_idx:
            total_w += font.getlength(text[last_idx:s])
        total_w += emoji_size
        last_idx = e
    if last_idx < len(text):
        total_w += font.getlength(text[last_idx:])

    x, y = float(xy[0]), float(xy[1])

    # horizontal anchor
    if anchor and len(anchor) >= 1:
        if anchor[0] == "m":
            x -= total_w / 2
        elif anchor[0] == "r":
            x -= total_w

    # vertical anchor (approximate with font metrics)
    if anchor and len(anchor) >= 2:
        ascent, descent = font.getmetrics()
        line_h = ascent + descent
        if anchor[1] == "m":
            y -= line_h / 2
        elif anchor[1] == "d":
            y -= line_h

    # --- render segments left-to-right ---
    source = Twemoji()
    last_idx = 0
    for match in emoji_list:
        s, e = match["match_start"], match["match_end"]
        emoji_char = match["emoji"]

        # 1) draw the text segment before this emoji
        if s > last_idx:
            segment = text[last_idx:s]
            draw.text((int(x), int(y)), segment, font=font, fill=fill)
            x += font.getlength(segment)

        # 2) draw the emoji image
        stream = source.get_emoji(emoji_char)
        if stream:
            stream.seek(0)
            with PILImage.open(stream).convert("RGBA") as asset:
                resized = asset.resize(
                    (emoji_size, emoji_size), PILImage.Resampling.LANCZOS
                )
                # vertically center the emoji relative to the text ascent
                ascent, _ = font.getmetrics()
                ey = int(y + (ascent - emoji_size) / 2)
                draw.img.paste(resized, (int(x), ey), resized)
            x += emoji_size
        else:
            # fallback: render as text (will be a box, but keeps spacing)
            draw.text((int(x), int(y)), emoji_char, font=font, fill=fill)
            x += font.getlength(emoji_char)

        last_idx = e

    # 3) draw the remaining text after the last emoji
    if last_idx < len(text):
        segment = text[last_idx:]
        draw.text((int(x), int(y)), segment, font=font, fill=fill)


def wrap_text(text: str, font, max_width: int, draw) -> list[str]:
    """
    Word-wrap text so each line fits within max_width pixels.
    Returns a list of line strings.
    Precludes emojis from wrapping to a line by themselves by grouping
    them with the subsequent word.
    """
    import emoji
    raw_words = text.split()
    words = []
    i = 0
    while i < len(raw_words):
        word = raw_words[i]
        # If the word contains an emoji and has no alphanumeric characters (e.g., 🧠 or 👨‍⚕️),
        # merge it with the subsequent word to prevent it from wrapping alone.
        if emoji.emoji_count(word) > 0 and not any(c.isalnum() for c in word) and i + 1 < len(raw_words):
            words.append(word + " " + raw_words[i+1])
            i += 2
        else:
            words.append(word)
            i += 1

    lines   = []
    current = ""

    for word in words:
        test = f"{current} {word}".strip()
        if draw.textlength(test, font=font) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines


def slide_output_path(slide_number: int) -> str:
    """Return the full output path for a slide PNG."""
    ensure_dir(OUTPUT_DIR)
    return os.path.join(OUTPUT_DIR, f"slide_{slide_number:02d}.png")


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def darken(hex_color: str, factor: float = 0.7) -> str:
    """Darken a hex color by a factor."""
    r, g, b = hex_to_rgb(hex_color)
    r = int(r * factor)
    g = int(g * factor)
    b = int(b * factor)
    return f"#{r:02x}{g:02x}{b:02x}"


def lighten(hex_color: str, factor: float = 0.3) -> str:
    """Lighten a hex color by blending with white."""
    r, g, b = hex_to_rgb(hex_color)
    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)
    return f"#{r:02x}{g:02x}{b:02x}"