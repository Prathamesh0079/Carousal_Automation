"""
Premium carousel renderer — per-slide-type rendering functions.
"""
import os
import random
from PIL import Image, ImageDraw
from config import (
    WIDTH, HEIGHT, PAD_X, PAD_Y,
    WHITE, PURE_BLACK, DARK_TEXT, MUTED_TEXT,
    PRIMARY_DARK, BRIGHT_ACCENT, HIGHLIGHT, LIGHT_GRAY,
    SIZE_HEADING, SIZE_SUBHEADING, SIZE_BODY, SIZE_META,
    SIZE_PILL, SIZE_ITEM, SIZE_TAGLINE, SIZE_BRAND,
    LINE_H, LINE_B, LINE_I, BG_COLORS, SCALE,
)
from utils import load_font, wrap_text, slide_output_path, lighten, darken, draw_text
from draw_helpers import (
    S, draw_pill, draw_checklist, draw_arrow_items, draw_dash_items,
    draw_numbered_items, draw_angled_badge, draw_dot_network, 
    draw_page_indicator, draw_divider, draw_thin_hr, draw_theme_background,
    draw_corner_decoration, draw_logo, draw_brand_logo, draw_slide_illustration,
    draw_bottom_bar_classic, draw_bottom_bar_editorial, draw_bottom_bar_coral,
    draw_bottom_bar_blueprint, draw_bottom_bar_modern,
    draw_top_pills_editorial, draw_top_bar_coral, draw_top_bar_blueprint,
    draw_decorative_curve, draw_glass_card, draw_neo_brutalism_card
)


def _load_fonts():
    return {
        "heading":    load_font("extrabold", SIZE_HEADING),
        "subheading": load_font("bold", SIZE_SUBHEADING),
        "body":       load_font("semibold", SIZE_BODY),
        "meta":       load_font("regular", SIZE_META),
        "pill":       load_font("bold", SIZE_PILL),
        "item":       load_font("semibold", SIZE_ITEM),
        "tagline":    load_font("regular", SIZE_TAGLINE),
        "brand":      load_font("regular", SIZE_BRAND),
    }


def _new_slide(bg_color):
    img = Image.new("RGB", (WIDTH, HEIGHT), bg_color)
    draw = ImageDraw.Draw(img)
    draw.img = img
    
    # Draw dynamic theme background
    draw_theme_background(img, draw, bg_color)
    
    # Monkeypatch draw.textlength to calculate correct width with emojis
    orig_textlength = draw.textlength
    def emoji_aware_textlength(text, font, **kwargs):
        import emoji
        if emoji.emoji_count(text) > 0:
            font_size = font.size if hasattr(font, "size") else 24
            emoji_list = emoji.emoji_list(text)
            total_width = 0.0
            last_idx = 0
            emoji_width = font_size
            for match in emoji_list:
                start = match['match_start']
                end = match['match_end']
                if start > last_idx:
                    subtext = text[last_idx:start]
                    total_width += orig_textlength(subtext, font=font, **kwargs)
                total_width += emoji_width
                last_idx = end
            if last_idx < len(text):
                subtext = text[last_idx:]
                total_width += orig_textlength(subtext, font=font, **kwargs)
            return total_width
        else:
            return orig_textlength(text, font=font, **kwargs)
            
    draw.textlength = emoji_aware_textlength
    return img, draw


def _common_decorations(img, draw, slide, fonts):
    """Shared decorations across all slide types."""
    from config import ACTIVE_THEME, TEMPLATES, BRAND_NAME, BRAND_URL
    theme = TEMPLATES.get(ACTIVE_THEME, TEMPLATES["classic_dark"])
    layout = theme.get("layout", "centered_corporate")
    sn = slide.get("slide_number", 1)
    total = slide.get("total", 7)
    stype = slide.get("type", "content")
    
    # 1. Corner decorations
    draw_corner_decoration(draw, "tl", MUTED_TEXT)
    draw_corner_decoration(draw, "tr", MUTED_TEXT)
    draw_corner_decoration(draw, "bl", MUTED_TEXT)
    draw_corner_decoration(draw, "br", MUTED_TEXT)
    
    # 2. Page indicator dots (only for classic and modern)
    if layout in ("centered_corporate", "minimal_modern"):
        draw_page_indicator(draw, sn, total, fonts)
        
    # 3. Draw brand logo on top right of every page in all designs
    draw_brand_logo(img, WIDTH - PAD_X - S(38), PAD_Y + S(38), size=120)
        
    # 4. Top Header Bars (decorations/metadata)
    if layout == "editorial_magazine":
        draw_top_pills_editorial(draw, BRAND_NAME, "@wisetribes", fonts["meta"])
    elif layout == "bold_magazine":
        draw_top_bar_coral(draw, BRAND_NAME, BRAND_URL, fonts["brand"], fonts["meta"])
    elif layout == "grid_impact":
        draw_top_bar_blueprint(draw, BRAND_NAME, "2026", fonts["meta"])
        draw_decorative_curve(draw, BRIGHT_ACCENT)

            
    # 4. Bottom Footer Bars
    y_footer = HEIGHT - PAD_Y - S(10)
    if layout == "editorial_magazine":
        draw_bottom_bar_editorial(draw, y_footer - S(20), BRAND_URL, fonts["meta"])
    elif layout == "bold_magazine":
        draw_bottom_bar_coral(draw, y_footer, BRAND_URL, fonts["meta"])
    elif layout == "grid_impact":
        draw_bottom_bar_blueprint(draw, y_footer, BRAND_URL, fonts["meta"])
    elif layout == "minimal_modern":
        draw_bottom_bar_modern(draw, y_footer, BRAND_NAME, fonts["meta"])
    else:
        # Classic joined pill bar
        tagline = slide.get("tagline", "")
        if not tagline:
            tagline = "Join the tribe!" if (sn == total or stype == "cta") else "Swipe to learn >"
        font_brand = load_font("bold", S(22))
        font_tagline = fonts["pill"]
        draw_bottom_pill_bar_classic(
            draw, WIDTH // 2, HEIGHT - PAD_Y - S(50),
            BRAND_NAME, tagline, font_brand, font_tagline
        )


def draw_bottom_pill_bar_classic(draw, cx, cy, brand_text, tagline, font_brand, font_tagline):
    """Fallback router to Classic Dark pill bar draw helper."""
    draw_bottom_bar_classic(draw, cx, cy, brand_text, tagline, font_brand, font_tagline)


def _highlight_word_in_heading(draw, lines, font, x, y, line_h,
                                text_color, highlight_word, highlight_color, align="left"):
    """Draw heading lines, highlighting the highlight_word in highlight_color."""
    for line in lines:
        if not highlight_word or highlight_word.lower() not in line.lower():
            if align == "center":
                w = draw.textlength(line, font=font)
                sx = (WIDTH - w) // 2
                draw_text(draw, (sx, y), line, font=font, fill=text_color)
            elif align == "right":
                w = draw.textlength(line, font=font)
                sx = WIDTH - PAD_X - w
                draw_text(draw, (sx, y), line, font=font, fill=text_color)
            else:
                draw_text(draw, (x, y), line, font=font, fill=text_color)
        else:
            idx = line.lower().find(highlight_word.lower())
            before = line[:idx]
            word = line[idx:idx+len(highlight_word)]
            after = line[idx+len(highlight_word):]
            
            w_before = draw.textlength(before, font=font)
            w_word = draw.textlength(word, font=font)
            w_after = draw.textlength(after, font=font)
            total_w = w_before + w_word + w_after
            
            if align == "center":
                sx = (WIDTH - total_w) // 2
            elif align == "right":
                sx = WIDTH - PAD_X - total_w
            else:
                sx = x
                
            draw_text(draw, (sx, y), before, font=font, fill=text_color)
            draw_text(draw, (sx + w_before, y), word, font=font, fill=highlight_color)
            draw_text(draw, (sx + w_before + w_word, y), after, font=font, fill=text_color)
        y += line_h
    return y


# ═══════════════════════════════════════════════════════
#  SLIDE TYPE: HOOK (COVER)
# ═══════════════════════════════════════════════════════
def _render_hook(slide, fonts):
    from config import ACTIVE_THEME, TEMPLATES, WHITE, BRIGHT_ACCENT, HIGHLIGHT, DARK_TEXT, MUTED_TEXT
    theme = TEMPLATES.get(ACTIVE_THEME, TEMPLATES["classic_dark"])
    layout = theme.get("layout", "centered_corporate")
    
    bg = slide.get("bg_override", BG_COLORS["hook"])
    img, draw = _new_slide(bg)
    sn = slide.get("slide_number", 1)
    
    heading = slide.get("heading", "")
    body = slide.get("body", "")
    hw = slide.get("highlight_word", "")
    
    if layout == "editorial_magazine":
        # Typographic-only, elegant blush layout
        y = PAD_Y + S(180)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        
        y += S(60)
        b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*2, draw)
        for line in b_lines:
            draw_text(draw, (PAD_X, y), line, font=fonts["body"], fill=MUTED_TEXT)
            y += LINE_B
            
        # Draw illustration at bottom
        draw_slide_illustration(img, WIDTH // 2, S(880), sn, size=300, image_prompt=slide.get("image_prompt", ""))
            
    elif layout == "bold_magazine":
        # Vibrant bold magazine layout
        y = PAD_Y + S(160)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        
        y += S(20)
        if body:
            b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*3, draw)
            card_h = len(b_lines) * LINE_B + S(40)
            draw_glass_card(img, draw, PAD_X - S(20), y - S(10), WIDTH - PAD_X + S(20), y + card_h,
                            bg_color=(255, 255, 255, 20), border_color=(255, 255, 255, 60), radius=S(12))
            for line in b_lines:
                draw_text(draw, (PAD_X, y + S(10)), line, font=fonts["body"], fill=WHITE)
                y += LINE_B
            y += S(20)
            
        # Draw illustration at bottom half
        draw_slide_illustration(img, WIDTH // 2, S(820), sn, size=400, image_prompt=slide.get("image_prompt", ""))
        
    elif layout == "grid_impact":
        # Blueprint grid layout
        y = PAD_Y + S(160)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*3, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        
        y += S(40)
        if body:
            b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*3, draw)
            card_h = len(b_lines) * LINE_B + S(40)
            border_color = lighten("#0C1F4A", 0.30)
            draw.rectangle([PAD_X - S(20), y - S(10), WIDTH - PAD_X + S(20), y + card_h], outline=border_color, width=S(2))
            plus_len = S(6)
            for cx, cy_corner in [(PAD_X - S(20), y - S(10)), (WIDTH - PAD_X + S(20), y - S(10)), 
                                  (PAD_X - S(20), y + card_h), (WIDTH - PAD_X + S(20), y + card_h)]:
                draw.line([(cx - plus_len, cy_corner), (cx + plus_len, cy_corner)], fill=BRIGHT_ACCENT, width=S(2))
                draw.line([(cx, cy_corner - plus_len), (cx, cy_corner + plus_len)], fill=BRIGHT_ACCENT, width=S(2))
                
            for line in b_lines:
                draw_text(draw, (PAD_X, y + S(10)), line, font=fonts["body"], fill=MUTED_TEXT)
                y += LINE_B
            y += S(20)
            
        draw_slide_illustration(img, WIDTH // 2, S(820), sn, size=350, image_prompt=slide.get("image_prompt", ""))
        
    elif layout == "minimal_modern":
        # Clean modern dark
        y = PAD_Y + S(180)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        
        # Heading underline
        draw.rectangle([PAD_X, y + S(10), PAD_X + S(120), y + S(16)], fill=BRIGHT_ACCENT)
        y += S(50)
        
        if body:
            b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*3, draw)
            card_h = len(b_lines) * LINE_B + S(40)
            draw_glass_card(img, draw, PAD_X - S(20), y - S(10), WIDTH - PAD_X + S(20), y + card_h,
                            bg_color=(255, 255, 255, 12), border_color=(255, 255, 255, 45), radius=S(12))
            for line in b_lines:
                draw_text(draw, (PAD_X, y + S(10)), line, font=fonts["body"], fill=MUTED_TEXT)
                y += LINE_B
            y += S(20)
            
        draw_slide_illustration(img, WIDTH // 2, S(840), sn, size=320, image_prompt=slide.get("image_prompt", ""))
        
    elif layout == "business_modern":
        # Professional corporate dark-teal with diagonal split panel division
        y = PAD_Y + S(180)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        
        y += S(40)
        b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*2, draw)
        for line in b_lines:
            draw_text(draw, (PAD_X, y), line, font=fonts["body"], fill=MUTED_TEXT)
            y += LINE_B
            
        # Diagonal panel at bottom half
        draw.polygon([(0, HEIGHT), (WIDTH, HEIGHT), (WIDTH, S(780)), (0, S(860))], fill=BG_COLORS["light"])
        draw.line([(0, S(860)), (WIDTH, S(780))], fill=BRIGHT_ACCENT, width=S(4))
        
        draw_slide_illustration(img, WIDTH // 2, S(820), sn, size=320, image_prompt=slide.get("image_prompt", ""))
        
    elif layout == "vibrant_marketing":
        # Energetic dark purple with neon yellow highlights and a background target circle
        y = PAD_Y + S(160)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        
        y += S(40)
        b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*2, draw)
        for line in b_lines:
            draw_text(draw, (PAD_X, y), line, font=fonts["body"], fill=MUTED_TEXT)
            y += LINE_B
            
        # Draw glowing neon background target ellipse
        glow_cx, glow_cy = WIDTH // 2, S(840)
        draw.ellipse([glow_cx - S(220), glow_cy - S(220), glow_cx + S(220), glow_cy + S(220)],
                     outline=(250, 204, 21, 60), width=S(4))
        draw.ellipse([glow_cx - S(250), glow_cy - S(250), glow_cx + S(250), glow_cy + S(250)],
                     outline=(236, 72, 153, 40), width=S(2))
        
        draw_slide_illustration(img, glow_cx, glow_cy, sn, size=340, image_prompt=slide.get("image_prompt", ""))
        
    elif layout == "playful_organic":
        # Warm cream & brown layout with playful polaroid frame
        y = PAD_Y + S(160)
        # Using dark brown/charcoal text color
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        
        y += S(40)
        b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*2, draw)
        for line in b_lines:
            draw_text(draw, (PAD_X, y), line, font=fonts["body"], fill=MUTED_TEXT)
            y += LINE_B
            
        # Polaroid-like white frame container for illustration
        f_cx, f_cy = WIDTH // 2, S(820)
        f_w, f_h = S(360), S(420)
        draw.rounded_rectangle([f_cx - f_w//2, f_cy - f_h//2, f_cx + f_w//2, f_cy + f_h//2],
                                radius=S(24), fill="#FFFFFF", outline="#8D6E63", width=S(4))
        # Polaroid bottom band offset
        draw.rectangle([f_cx - f_w//2 + S(4), f_cy + f_h//2 - S(70), f_cx + f_w//2 - S(4), f_cy + f_h//2 - S(4)],
                       fill="#F5EBE6")
        
        draw_slide_illustration(img, f_cx, f_cy - S(25), sn, size=280, image_prompt=slide.get("image_prompt", ""))
        
    else: # centered_corporate
        y = PAD_Y + S(280)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="center")
        
        y += S(30)
        b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*2, draw)
        for line in b_lines:
            tw = draw.textlength(line, font=fonts["body"])
            draw_text(draw, ((WIDTH - tw) // 2, y), line, font=fonts["body"], fill=WHITE)
            y += LINE_B
            
        draw_slide_illustration(img, WIDTH // 2, S(880), sn, size=300, image_prompt=slide.get("image_prompt", ""))
        
    _common_decorations(img, draw, slide, fonts)
    return img


# ═══════════════════════════════════════════════════════
#  SLIDE TYPE: SECTION
# ═══════════════════════════════════════════════════════
def _render_section(slide, fonts):
    from config import ACTIVE_THEME, TEMPLATES, WHITE, BRIGHT_ACCENT, MUTED_TEXT, DARK_TEXT
    theme = TEMPLATES.get(ACTIVE_THEME, TEMPLATES["classic_dark"])
    layout = theme.get("layout", "centered_corporate")
    
    bg = slide.get("bg_override", BG_COLORS["section"])
    img, draw = _new_slide(bg)
    sn = slide.get("slide_number", 1)
    
    heading = slide.get("heading", "")
    items = slide.get("items", [])
    hw = slide.get("highlight_word", "")
    
    if layout == "editorial_magazine":
        y = PAD_Y + S(140)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        y += S(50)
        # Render clean vertical sections instead of bullet badges
        for item in items[:3]:
            draw_thin_hr(draw, y, color="#D0C4BE", full_width=False)
            y += S(15)
            # Parse title & desc if split by colon
            if ":" in item:
                parts = item.split(":", 1)
                item_title = parts[0].strip() + ":"
                item_desc = parts[1].strip()
                
                # Title line
                draw_text(draw, (PAD_X, y), item_title, font=fonts["subheading"], fill=WHITE)
                y += S(40)
                # Desc line
                d_lines = wrap_text(item_desc, fonts["body"], WIDTH - PAD_X*2, draw)
                for line in d_lines:
                    draw_text(draw, (PAD_X, y), line, font=fonts["body"], fill=MUTED_TEXT)
                    y += LINE_B
            else:
                lines = wrap_text(item, fonts["body"], WIDTH - PAD_X*2, draw)
                for line in lines:
                    draw_text(draw, (PAD_X, y), line, font=fonts["body"], fill=WHITE)
                    y += LINE_B
            y += S(20)
            
    elif layout == "bold_magazine":
        y = PAD_Y + S(140)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        
        y += S(50)
        # Rotated staggered badges
        for idx, item in enumerate(items[:3]):
            angle_offset = -2 if idx % 2 == 0 else 2
            # For drawing badges directly without rotation, or staggered offset
            badge_x = PAD_X + idx * S(40)
            badge_w, badge_h = draw_angled_badge(draw, badge_x, y, item, 
                                                 fonts["item"], bg_color=WHITE, text_color=DARK_TEXT)
            y += badge_h + S(35)
            
    elif layout == "grid_impact":
        y = PAD_Y + S(140)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*3, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        y += S(60)
        # Numbered list items with accent numbers
        number_font = load_font("bold", S(20))
        draw_numbered_items(draw, items, PAD_X, y, fonts["body"], number_font,
                            number_color=BRIGHT_ACCENT, text_color=WHITE,
                            line_height=LINE_I, max_width=WIDTH - PAD_X*2)
                            
    elif layout == "minimal_modern":
        y = PAD_Y + S(140)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        y += S(60)
        # Dash items
        draw_dash_items(draw, items, PAD_X, y, fonts["body"], color=WHITE,
                        line_height=LINE_I, max_width=WIDTH - PAD_X*2)
                        
    else: # centered_corporate
        y = PAD_Y + S(180)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="center")
        y += S(60)
        draw_checklist(draw, items, PAD_X + S(60), y, fonts["body"],
                       check_color=BRIGHT_ACCENT, text_color=WHITE,
                       line_height=LINE_I, max_width=WIDTH - PAD_X*2)
                       
    _common_decorations(img, draw, slide, fonts)
    return img


# ═══════════════════════════════════════════════════════
#  SLIDE TYPE: DARK
# ═══════════════════════════════════════════════════════
def _render_dark(slide, fonts):
    from config import ACTIVE_THEME, TEMPLATES, WHITE, BRIGHT_ACCENT, MUTED_TEXT
    theme = TEMPLATES.get(ACTIVE_THEME, TEMPLATES["classic_dark"])
    layout = theme.get("layout", "centered_corporate")
    
    # Note: slide type DARK is intentionally styled on dark background override
    bg = slide.get("bg_override", BG_COLORS["dark"])
    img, draw = _new_slide(bg)
    sn = slide.get("slide_number", 1)
    
    heading = slide.get("heading", "")
    body = slide.get("body", "")
    hw = slide.get("highlight_word", "")
    
    if layout == "editorial_magazine":
        y = PAD_Y + S(220)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        
        y += S(60)
        b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*2, draw)
        for line in b_lines:
            draw_text(draw, (PAD_X, y), line, font=fonts["body"], fill=MUTED_TEXT)
            y += LINE_B
            
    elif layout == "bold_magazine":
        y = PAD_Y + S(180)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        y += S(40)
        b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*2, draw)
        for line in b_lines:
            draw_text(draw, (PAD_X, y), line, font=fonts["body"], fill=MUTED_TEXT)
            y += LINE_B
            
    elif layout == "grid_impact":
        y = PAD_Y + S(200)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*3, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        y += S(50)
        b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*2, draw)
        for line in b_lines:
            draw_text(draw, (PAD_X, y), line, font=fonts["body"], fill=MUTED_TEXT)
            y += LINE_B
            
    elif layout == "minimal_modern":
        y = PAD_Y + S(200)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        # Underline
        draw.rectangle([PAD_X, y + S(10), PAD_X + S(150), y + S(16)], fill=BRIGHT_ACCENT)
        y += S(60)
        b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*2, draw)
        for line in b_lines:
            draw_text(draw, (PAD_X, y), line, font=fonts["body"], fill=MUTED_TEXT)
            y += LINE_B
            
    else: # centered_corporate
        y = PAD_Y + S(280)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="center")
        y += S(50)
        b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*2, draw)
        for line in b_lines:
            tw = draw.textlength(line, font=fonts["body"])
            draw_text(draw, ((WIDTH - tw) // 2, y), line, font=fonts["body"], fill=WHITE)
            y += LINE_B
            
    _common_decorations(img, draw, slide, fonts)
    return img


# ═══════════════════════════════════════════════════════
#  SLIDE TYPE: LIGHT
# ═══════════════════════════════════════════════════════
def _render_light(slide, fonts):
    from config import ACTIVE_THEME, TEMPLATES, WHITE, BRIGHT_ACCENT, MUTED_TEXT
    theme = TEMPLATES.get(ACTIVE_THEME, TEMPLATES["classic_dark"])
    layout = theme.get("layout", "centered_corporate")
    
    bg = slide.get("bg_override", BG_COLORS["light"])
    img, draw = _new_slide(bg)
    sn = slide.get("slide_number", 1)
    
    heading = slide.get("heading", "")
    body = slide.get("body", "")
    hw = slide.get("highlight_word", "")
    
    if layout == "editorial_magazine":
        y = PAD_Y + S(220)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        y += S(60)
        b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*2, draw)
        for line in b_lines:
            draw_text(draw, (PAD_X, y), line, font=fonts["body"], fill=MUTED_TEXT)
            y += LINE_B
            
    elif layout == "bold_magazine":
        y = PAD_Y + S(180)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        y += S(40)
        b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*2, draw)
        for line in b_lines:
            draw_text(draw, (PAD_X, y), line, font=fonts["body"], fill=MUTED_TEXT)
            y += LINE_B
            
    elif layout == "grid_impact":
        y = PAD_Y + S(200)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*3, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        y += S(50)
        b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*2, draw)
        for line in b_lines:
            draw_text(draw, (PAD_X, y), line, font=fonts["body"], fill=MUTED_TEXT)
            y += LINE_B
            
    elif layout == "minimal_modern":
        y = PAD_Y + S(200)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        draw.rectangle([PAD_X, y + S(10), PAD_X + S(150), y + S(16)], fill=BRIGHT_ACCENT)
        y += S(60)
        b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*2, draw)
        for line in b_lines:
            draw_text(draw, (PAD_X, y), line, font=fonts["body"], fill=MUTED_TEXT)
            y += LINE_B
            
    else: # centered_corporate
        y = PAD_Y + S(280)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        # Highlight on light background uses highlight color
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="center")
        y += S(50)
        b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*2, draw)
        for line in b_lines:
            tw = draw.textlength(line, font=fonts["body"])
            draw_text(draw, ((WIDTH - tw) // 2, y), line, font=fonts["body"], fill=WHITE)
            y += LINE_B
            
    _common_decorations(img, draw, slide, fonts)
    return img


# ═══════════════════════════════════════════════════════
#  SLIDE TYPE: TIMELINE
# ═══════════════════════════════════════════════════════
def _render_timeline(slide, fonts):
    from config import ACTIVE_THEME, TEMPLATES, WHITE, BRIGHT_ACCENT, MUTED_TEXT, DARK_TEXT
    theme = TEMPLATES.get(ACTIVE_THEME, TEMPLATES["classic_dark"])
    layout = theme.get("layout", "centered_corporate")
    
    bg = slide.get("bg_override", BG_COLORS["timeline"])
    img, draw = _new_slide(bg)
    sn = slide.get("slide_number", 1)
    
    heading = slide.get("heading", "")
    items = slide.get("items", []) # or steps
    if not items:
        items = slide.get("steps", [])
    hw = slide.get("highlight_word", "")
    
    if layout == "editorial_magazine":
        y = PAD_Y + S(140)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        y += S(60)
        # Vertical list with thin rules
        for idx, item in enumerate(items[:4]):
            draw_thin_hr(draw, y, color="#D0C4BE", full_width=False)
            y += S(12)
            lbl = f"Phase 0{idx+1}: "
            draw_text(draw, (PAD_X, y), lbl, font=fonts["subheading"], fill=BRIGHT_ACCENT)
            tx = PAD_X + draw.textlength(lbl, font=fonts["subheading"]) + S(10)
            
            lines = wrap_text(item, fonts["body"], WIDTH - tx - PAD_X, draw)
            for idx2, line in enumerate(lines):
                draw_text(draw, (tx, y + idx2 * LINE_B), line, font=fonts["body"], fill=WHITE)
            y += max(len(lines) * LINE_B, S(45)) + S(15)
            
    elif layout == "bold_magazine":
        y = PAD_Y + S(140)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        y += S(60)
        # Rotated staggered badges
        for idx, item in enumerate(items[:3]):
            badge_x = PAD_X + idx * S(50)
            # Prepend number
            label = f"{idx+1}. {item}"
            badge_w, badge_h = draw_angled_badge(draw, badge_x, y, label, 
                                                 fonts["item"], bg_color=WHITE, text_color=DARK_TEXT)
            y += badge_h + S(35)
            
    elif layout == "grid_impact":
        y = PAD_Y + S(140)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*3, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        y += S(65)
        # Numbered list items with accent numbers
        number_font = load_font("bold", S(20))
        draw_numbered_items(draw, items, PAD_X, y, fonts["body"], number_font,
                            number_color=BRIGHT_ACCENT, text_color=WHITE,
                            line_height=LINE_I, max_width=WIDTH - PAD_X*2)
                            
    elif layout == "minimal_modern":
        y = PAD_Y + S(140)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        y += S(60)
        # Dash items
        draw_dash_items(draw, items, PAD_X, y, fonts["body"], color=WHITE,
                        line_height=LINE_I, max_width=WIDTH - PAD_X*2)
                        
    else: # centered_corporate
        y = PAD_Y + S(180)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="center")
        y += S(60)
        draw_arrow_items(draw, items, PAD_X + S(60), y, fonts["body"], 
                         color=WHITE, line_height=LINE_I, max_width=WIDTH - PAD_X*2)
                         
    _common_decorations(img, draw, slide, fonts)
    return img


# ═══════════════════════════════════════════════════════
#  SLIDE TYPE: RESULTS
# ═══════════════════════════════════════════════════════
def _render_results(slide, fonts):
    from config import ACTIVE_THEME, TEMPLATES, WHITE, BRIGHT_ACCENT, MUTED_TEXT, DARK_TEXT
    theme = TEMPLATES.get(ACTIVE_THEME, TEMPLATES["classic_dark"])
    layout = theme.get("layout", "centered_corporate")
    
    bg = slide.get("bg_override", BG_COLORS["results"])
    img, draw = _new_slide(bg)
    sn = slide.get("slide_number", 1)
    
    heading = slide.get("heading", "")
    items = slide.get("items", [])
    hw = slide.get("highlight_word", "")
    
    if layout == "editorial_magazine":
        y = PAD_Y + S(140)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        y += S(60)
        # Editorial rows with thin dividers
        for idx, item in enumerate(items[:3]):
            draw_thin_hr(draw, y, color="#D0C4BE", full_width=False)
            y += S(15)
            lines = wrap_text(item, fonts["body"], WIDTH - PAD_X*2, draw)
            for line in lines:
                draw_text(draw, (PAD_X, y), line, font=fonts["body"], fill=WHITE)
                y += LINE_B
            y += S(20)
            
    elif layout == "bold_magazine":
        y = PAD_Y + S(140)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        y += S(60)
        # Rotated staggered badges
        for idx, item in enumerate(items[:3]):
            badge_x = PAD_X + idx * S(50)
            badge_w, badge_h = draw_angled_badge(draw, badge_x, y, item, 
                                                 fonts["item"], bg_color=WHITE, text_color=DARK_TEXT)
            y += badge_h + S(35)
            
    elif layout == "grid_impact":
        y = PAD_Y + S(140)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*3, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        y += S(65)
        # Numbered list items with accent numbers
        number_font = load_font("bold", S(20))
        draw_numbered_items(draw, items, PAD_X, y, fonts["body"], number_font,
                            number_color=BRIGHT_ACCENT, text_color=WHITE,
                            line_height=LINE_I, max_width=WIDTH - PAD_X*2)
                            
    elif layout == "minimal_modern":
        y = PAD_Y + S(140)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        y += S(60)
        # Dash items
        draw_dash_items(draw, items, PAD_X, y, fonts["body"], color=WHITE,
                        line_height=LINE_I, max_width=WIDTH - PAD_X*2)
                        
    else: # centered_corporate
        y = PAD_Y + S(180)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="center")
        y += S(60)
        draw_checklist(draw, items, PAD_X + S(60), y, fonts["body"],
                       check_color=BRIGHT_ACCENT, text_color=WHITE,
                       line_height=LINE_I, max_width=WIDTH - PAD_X*2)
                       
    _common_decorations(img, draw, slide, fonts)
    return img


# ═══════════════════════════════════════════════════════
#  SLIDE TYPE: CTA (FINAL CALL TO ACTION)
# ═══════════════════════════════════════════════════════
def _render_cta(slide, fonts):
    from config import ACTIVE_THEME, TEMPLATES, WHITE, BRIGHT_ACCENT, MUTED_TEXT, DARK_TEXT
    theme = TEMPLATES.get(ACTIVE_THEME, TEMPLATES["classic_dark"])
    layout = theme.get("layout", "centered_corporate")
    
    bg = slide.get("bg_override", BG_COLORS["cta"])
    img, draw = _new_slide(bg)
    sn = slide.get("slide_number", 1)
    
    heading = slide.get("heading", "")
    body = slide.get("body", "")
    hw = slide.get("highlight_word", "")
    cta_text = slide.get("cta_text", "GET THE PDF")
    
    if layout == "editorial_magazine":
        # Centered clean editorial text block with thin borders
        y = PAD_Y + S(220)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="center")
        
        y += S(40)
        b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*2, draw)
        for line in b_lines:
            tw = draw.textlength(line, font=fonts["body"])
            draw_text(draw, ((WIDTH - tw) // 2, y), line, font=fonts["body"], fill=MUTED_TEXT)
            y += LINE_B
            
        y += S(60)
        # Drawn simple black rectangle button
        btn_w = S(320)
        btn_h = S(60)
        bx = (WIDTH - btn_w) // 2
        draw.rectangle([bx, y, bx + btn_w, y + btn_h], fill="#1A1A1A")
        draw_text(draw, (bx + btn_w//2, y + btn_h//2), cta_text.upper(), font=fonts["pill"], fill=WHITE, anchor="mm")
        
    elif layout == "bold_magazine":
        y = PAD_Y + S(180)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        
        y += S(40)
        b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*2, draw)
        for line in b_lines:
            draw_text(draw, (PAD_X, y), line, font=fonts["body"], fill=MUTED_TEXT)
            y += LINE_B
            
        y += S(60)
        # Neo-Brutalist button with bold black text on bright yellow base, black outline & offset shadow
        btn_w = S(300)
        btn_h = S(65)
        draw_neo_brutalism_card(img, draw, PAD_X, y, PAD_X + btn_w, y + btn_h,
                                bg_color="#FFEB3B", border_color="#000000", border_width=3,
                                shadow_color="#000000", shadow_offset=8, radius=8)
        draw_text(draw, (PAD_X + btn_w//2, y + btn_h//2), cta_text.upper(), font=fonts["pill"], fill="#000000", anchor="mm")
        
    elif layout == "grid_impact":
        y = PAD_Y + S(200)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*3, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        
        y += S(40)
        b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*2, draw)
        for line in b_lines:
            draw_text(draw, (PAD_X, y), line, font=fonts["body"], fill=MUTED_TEXT)
            y += LINE_B
            
        y += S(60)
        # Yellow accent button
        btn_w = S(300)
        btn_h = S(60)
        draw.rounded_rectangle([PAD_X, y, PAD_X + btn_w, y + btn_h], radius=S(8), fill=BRIGHT_ACCENT)
        draw_text(draw, (PAD_X + btn_w//2, y + btn_h//2), cta_text.upper(), font=fonts["pill"], fill=DARK_TEXT, anchor="mm")
        
    elif layout == "minimal_modern":
        y = PAD_Y + S(200)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        
        draw.rectangle([PAD_X, y + S(10), PAD_X + S(150), y + S(16)], fill=BRIGHT_ACCENT)
        y += S(60)
        
        b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*2, draw)
        for line in b_lines:
            draw_text(draw, (PAD_X, y), line, font=fonts["body"], fill=MUTED_TEXT)
            y += LINE_B
            
        y += S(60)
        # Minimal white outlined button
        btn_w = S(320)
        btn_h = S(60)
        draw.rounded_rectangle([PAD_X, y, PAD_X + btn_w, y + btn_h], radius=S(8), outline=WHITE, width=S(2))
        draw_text(draw, (PAD_X + btn_w//2, y + btn_h//2), cta_text.upper(), font=fonts["pill"], fill=WHITE, anchor="mm")
        
    elif layout == "business_modern":
        y = PAD_Y + S(200)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        
        y += S(40)
        b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*2, draw)
        for line in b_lines:
            draw_text(draw, (PAD_X, y), line, font=fonts["body"], fill=MUTED_TEXT)
            y += LINE_B
            
        y += S(60)
        btn_w = S(320)
        btn_h = S(60)
        draw.rounded_rectangle([PAD_X, y, PAD_X + btn_w, y + btn_h], radius=S(8), fill=BRIGHT_ACCENT)
        draw_text(draw, (PAD_X + btn_w//2, y + btn_h//2), cta_text.upper(), font=fonts["pill"], fill=DARK_TEXT, anchor="mm")
        
    elif layout == "vibrant_marketing":
        y = PAD_Y + S(200)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        
        y += S(40)
        b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*2, draw)
        for line in b_lines:
            draw_text(draw, (PAD_X, y), line, font=fonts["body"], fill=MUTED_TEXT)
            y += LINE_B
            
        y += S(60)
        btn_w = S(320)
        btn_h = S(60)
        draw.rounded_rectangle([PAD_X, y, PAD_X + btn_w, y + btn_h], radius=S(30), fill=BRIGHT_ACCENT)
        draw_text(draw, (PAD_X + btn_w//2, y + btn_h//2), cta_text.upper(), font=fonts["pill"], fill=DARK_TEXT, anchor="mm")
        
    elif layout == "playful_organic":
        y = PAD_Y + S(200)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        
        y += S(40)
        b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*2, draw)
        for line in b_lines:
            draw_text(draw, (PAD_X, y), line, font=fonts["body"], fill=MUTED_TEXT)
            y += LINE_B
            
        y += S(60)
        btn_w = S(320)
        btn_h = S(60)
        draw.rounded_rectangle([PAD_X, y, PAD_X + btn_w, y + btn_h], radius=S(16), fill=BRIGHT_ACCENT)
        draw_text(draw, (PAD_X + btn_w//2, y + btn_h//2), cta_text.upper(), font=fonts["pill"], fill=DARK_TEXT, anchor="mm")
        
    else: # centered_corporate
        # Classic centered large logo CTA
        y = PAD_Y + S(320)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="center")
        
        y += S(40)
        b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*2, draw)
        for line in b_lines:
            tw = draw.textlength(line, font=fonts["body"])
            draw_text(draw, ((WIDTH - tw) // 2, y), line, font=fonts["body"], fill=WHITE)
            y += LINE_B
            
        y += S(60)
        # White & Gold joined badge button
        btn_w = S(320)
        btn_h = S(60)
        bx = (WIDTH - btn_w) // 2
        draw.rounded_rectangle([bx, y, bx + btn_w, y + btn_h], radius=btn_h//2, fill=BRIGHT_ACCENT)
        draw_text(draw, (bx + btn_w//2, y + btn_h//2), cta_text.upper(), font=fonts["pill"], fill=DARK_TEXT, anchor="mm")
        
    _common_decorations(img, draw, slide, fonts)
    return img


# ═══════════════════════════════════════════════════════
#  SLIDE TYPE: CONTENT
# ═══════════════════════════════════════════════════════
def _render_content(slide, fonts):
    from config import ACTIVE_THEME, TEMPLATES, WHITE, BRIGHT_ACCENT, MUTED_TEXT, DARK_TEXT
    theme = TEMPLATES.get(ACTIVE_THEME, TEMPLATES["classic_dark"])
    layout = theme.get("layout", "centered_corporate")
    
    bg = slide.get("bg_override", BG_COLORS["content"])
    img, draw = _new_slide(bg)
    sn = slide.get("slide_number", 1)
    
    heading = slide.get("heading", "")
    body = slide.get("body", "")
    items = slide.get("items", [])
    hw = slide.get("highlight_word", "")
    
    if layout == "editorial_magazine":
        y = PAD_Y + S(160)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        y += S(30)
        
        # Add a full width divider
        draw_thin_hr(draw, y, color="#D0C4BE", full_width=True)
        y += S(35)
        
        if body:
            b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*2, draw)
            for line in b_lines:
                draw_text(draw, (PAD_X, y), line, font=fonts["body"], fill=WHITE)
                y += LINE_B
            y += S(30)
            
        if items:
            for item in items[:3]:
                # Draw a very light dash/dot
                draw_text(draw, (PAD_X, y), "•", font=fonts["body"], fill=WHITE)
                lines = wrap_text(item, fonts["body"], WIDTH - PAD_X*2 - S(30), draw)
                for idx, line in enumerate(lines):
                    draw_text(draw, (PAD_X + S(30), y), line, font=fonts["body"], fill=WHITE)
                    y += LINE_B
                y += S(20)
                
        # Draw illustration at bottom
        draw_slide_illustration(img, WIDTH // 2, S(920), sn, size=300, image_prompt=slide.get("image_prompt", ""))
                
    elif layout == "bold_magazine":
        y = PAD_Y + S(140)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        y += S(40)
        
        # Calculate dynamic card size
        card_y0 = y - S(30)
        temp_y = card_y0 + S(40)
        if body:
            b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*3, draw)
            temp_y += len(b_lines) * LINE_B + S(30)
        if items:
            for item in items[:2]:
                temp_y += S(80) + S(35)
                
        card_y1 = temp_y + S(10)
        
        # Draw Neo-Brutalist white card with black outline and solid offset shadow
        draw_neo_brutalism_card(img, draw, PAD_X - S(30), card_y0, WIDTH - PAD_X + S(30), card_y1,
                                bg_color="#FFFFFF", border_color="#000000", border_width=3,
                                shadow_color="#9E260C", shadow_offset=12, radius=16)
        
        # Draw overlapping step indicator circle
        step_r = S(32)
        step_cx = PAD_X - S(30)
        step_cy = card_y0
        draw.ellipse([step_cx - step_r, step_cy - step_r, step_cx + step_r, step_cy + step_r],
                     fill="#FFEB3B", outline="#000000", width=S(3))
        step_num = str(sn - 1)
        draw_text(draw, (step_cx, step_cy), step_num, font=fonts["brand"], fill="#000000", anchor="mm")
        
        # Now draw the text/items inside the card
        y = card_y0 + S(40)
        if body:
            b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*3, draw)
            for line in b_lines:
                draw_text(draw, (PAD_X, y), line, font=fonts["body"], fill=DARK_TEXT)
                y += LINE_B
            y += S(30)
            
        if items:
            for idx, item in enumerate(items[:2]):
                badge_x = PAD_X + idx * S(50)
                badge_w, badge_h = draw_angled_badge(draw, badge_x, y, item, 
                                                     fonts["item"], bg_color="#FFEB3B", text_color="#1A1A1A")
                y += badge_h + S(35)
                
        # Draw illustration at bottom
        draw_slide_illustration(img, WIDTH // 2, S(920), sn, size=300, image_prompt=slide.get("image_prompt", ""))
        
    elif layout == "grid_impact":
        y = PAD_Y + S(140)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*3, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        y += S(50)
        
        # Calculate dynamic box height
        card_y0 = y - S(30)
        temp_y = card_y0 + S(40)
        if body:
            b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*3, draw)
            temp_y += len(b_lines) * LINE_B + S(30)
        if items:
            for item in items:
                lines = wrap_text(item, fonts["body"], WIDTH - PAD_X*3 - S(65), draw)
                temp_y += len(lines) * LINE_I + S(25)
                
        card_y1 = temp_y + S(10)
        
        # Draw blueprint coordinate frame border box
        border_color = lighten("#0C1F4A", 0.30)
        draw.rectangle([PAD_X - S(30), card_y0, WIDTH - PAD_X + S(30), card_y1], outline=border_color, width=S(2))
        plus_len = S(8)
        for cx, cy_corner in [(PAD_X - S(30), card_y0), (WIDTH - PAD_X + S(30), card_y0), 
                              (PAD_X - S(30), card_y1), (WIDTH - PAD_X + S(30), card_y1)]:
            draw.line([(cx - plus_len, cy_corner), (cx + plus_len, cy_corner)], fill=BRIGHT_ACCENT, width=S(2))
            draw.line([(cx, cy_corner - plus_len), (cx, cy_corner + plus_len)], fill=BRIGHT_ACCENT, width=S(2))
            
        # Draw contents
        y = card_y0 + S(40)
        if body:
            b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*3, draw)
            for line in b_lines:
                draw_text(draw, (PAD_X, y), line, font=fonts["body"], fill=MUTED_TEXT)
                y += LINE_B
            y += S(30)
            
        if items:
            number_font = load_font("bold", S(20))
            draw_numbered_items(draw, items, PAD_X, y, fonts["body"], number_font,
                                number_color=BRIGHT_ACCENT, text_color=WHITE,
                                line_height=LINE_I, max_width=WIDTH - PAD_X*3)
        
        # Always draw illustration at the bottom
        draw_slide_illustration(img, WIDTH // 2, S(920), sn, size=300, image_prompt=slide.get("image_prompt", ""))
            
    elif layout == "minimal_modern":
        y = PAD_Y + S(140)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        # Underline
        draw.rectangle([PAD_X, y + S(10), PAD_X + S(150), y + S(16)], fill=BRIGHT_ACCENT)
        y += S(60)
        
        # Calculate card height dynamically
        card_y0 = y - S(30)
        temp_y = card_y0 + S(40)
        
        if body:
            b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*3, draw)
            temp_y += len(b_lines) * LINE_B + S(30)
        if items:
            for item in items:
                lines = wrap_text(item, fonts["body"], WIDTH - PAD_X*3 - S(50), draw)
                temp_y += len(lines) * LINE_I + S(20)
        
        card_y1 = temp_y + S(10)
        # Draw the card container
        draw_glass_card(img, draw, PAD_X - S(30), card_y0, WIDTH - PAD_X + S(30), card_y1,
                        bg_color=(255, 255, 255, 12), border_color=(255, 255, 255, 45), radius=S(16))
        
        # Now draw the text inside
        y = card_y0 + S(40)
        if body:
            b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*3, draw)
            for line in b_lines:
                draw_text(draw, (PAD_X, y), line, font=fonts["body"], fill=MUTED_TEXT)
                y += LINE_B
            y += S(30)
            
        if items:
            draw_dash_items(draw, items, PAD_X, y, fonts["body"], color=WHITE,
                            line_height=LINE_I, max_width=WIDTH - PAD_X*3)
        
        # Always draw illustration at the bottom
        draw_slide_illustration(img, WIDTH // 2, S(940), sn, size=300, image_prompt=slide.get("image_prompt", ""))
            
    elif layout == "business_modern":
        y = PAD_Y + S(140)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        y += S(40)
        
        # Calculate dynamic card size
        card_y0 = y - S(30)
        temp_y = card_y0 + S(40)
        if body:
            b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*3, draw)
            temp_y += len(b_lines) * LINE_B + S(30)
        if items:
            for item in items:
                lines = wrap_text(item, fonts["body"], WIDTH - PAD_X*3 - S(45), draw)
                temp_y += len(lines) * LINE_I + S(20)
                
        card_y1 = temp_y + S(10)
        
        # Draw professional dark teal card with sharp borders and left vertical divider
        draw_glass_card(img, draw, PAD_X - S(30), card_y0, WIDTH - PAD_X + S(30), card_y1,
                        bg_color=(21, 76, 84, 200), border_color=(255, 255, 255, 30), radius=S(16))
        draw.line([(PAD_X - S(25), card_y0 + S(20)), (PAD_X - S(25), card_y1 - S(20))], fill=BRIGHT_ACCENT, width=S(5))
        
        # Draw the text inside
        y = card_y0 + S(40)
        if body:
            b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*3, draw)
            for line in b_lines:
                draw_text(draw, (PAD_X, y), line, font=fonts["body"], fill=WHITE)
                y += LINE_B
            y += S(30)
            
        if items:
            draw_dash_items(draw, items, PAD_X, y, fonts["body"], color=MUTED_TEXT,
                            line_height=LINE_I, max_width=WIDTH - PAD_X*3)
        
        # Always draw illustration at the bottom
        draw_slide_illustration(img, WIDTH // 2, S(940), sn, size=300, image_prompt=slide.get("image_prompt", ""))
        
    elif layout == "vibrant_marketing":
        y = PAD_Y + S(140)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        y += S(40)
        
        # Calculate dynamic card size
        card_y0 = y - S(30)
        temp_y = card_y0 + S(40)
        if body:
            b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*3, draw)
            temp_y += len(b_lines) * LINE_B + S(30)
        if items:
            for item in items:
                lines = wrap_text(item, fonts["body"], WIDTH - PAD_X*3 - S(45), draw)
                temp_y += len(lines) * LINE_I + S(20)
                
        card_y1 = temp_y + S(10)
        
        # Draw vibrant card with neon yellow/gold border and pink step bubble
        draw_glass_card(img, draw, PAD_X - S(30), card_y0, WIDTH - PAD_X + S(30), card_y1,
                        bg_color=(30, 27, 75, 220), border_color=(250, 204, 21, 120), radius=S(20))
        
        # Step bubble overlapping top-left corner
        step_r = S(32)
        draw.ellipse([PAD_X - S(30) - step_r, card_y0 - step_r, PAD_X - S(30) + step_r, card_y0 + step_r],
                     fill="#EC4899", outline="#FFFFFF", width=S(2))
        draw_text(draw, (PAD_X - S(30), card_y0), str(sn - 1), font=fonts["brand"], fill="#FFFFFF", anchor="mm")
        
        # Draw text inside
        y = card_y0 + S(40)
        if body:
            b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*3, draw)
            for line in b_lines:
                draw_text(draw, (PAD_X, y), line, font=fonts["body"], fill=WHITE)
                y += LINE_B
            y += S(30)
            
        if items:
            draw_arrow_items(draw, items, PAD_X + S(20), y, fonts["body"], 
                             color=BRIGHT_ACCENT, line_height=LINE_I, max_width=WIDTH - PAD_X*3)
            
        draw_slide_illustration(img, WIDTH // 2, S(940), sn, size=300, image_prompt=slide.get("image_prompt", ""))
        
    elif layout == "playful_organic":
        # Warm cream & brown layout with playful organic card
        y = PAD_Y + S(140)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="left")
        y += S(40)
        
        # Calculate dynamic card size
        card_y0 = y - S(30)
        temp_y = card_y0 + S(40)
        if body:
            b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*3, draw)
            temp_y += len(b_lines) * LINE_B + S(30)
        if items:
            for item in items:
                lines = wrap_text(item, fonts["body"], WIDTH - PAD_X*3 - S(45), draw)
                temp_y += len(lines) * LINE_I + S(20)
                
        card_y1 = temp_y + S(10)
        
        # Draw large rounded beige card with thick brown border
        draw_glass_card(img, draw, PAD_X - S(30), card_y0, WIDTH - PAD_X + S(30), card_y1,
                        bg_color=(245, 235, 230, 240), border_color=(141, 110, 99, 120), radius=S(40))
        
        # Draw the text inside
        y = card_y0 + S(40)
        if body:
            b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*3, draw)
            for line in b_lines:
                draw_text(draw, (PAD_X, y), line, font=fonts["body"], fill=WHITE) # WHITE maps to primary text (dark brown)
                y += LINE_B
            y += S(30)
            
        if items:
            # Custom soft brown bullet items (circles)
            for item in items:
                draw.ellipse([PAD_X, y + S(8), PAD_X + S(10), y + S(18)], fill=BRIGHT_ACCENT) # BRIGHT_ACCENT maps to accent brown
                lines = wrap_text(item, fonts["body"], WIDTH - PAD_X*3 - S(30), draw)
                for line in lines:
                    draw_text(draw, (PAD_X + S(35), y), line, font=fonts["body"], fill=WHITE)
                    y += LINE_I
                y += S(10)
                
        draw_slide_illustration(img, WIDTH // 2, S(940), sn, size=300, image_prompt=slide.get("image_prompt", ""))
        
    else: # centered_corporate
        y = PAD_Y + S(180)
        h_lines = wrap_text(heading, fonts["heading"], WIDTH - PAD_X*2, draw)
        y = _highlight_word_in_heading(draw, h_lines, fonts["heading"], PAD_X, y,
                                       LINE_H, WHITE, hw, BRIGHT_ACCENT, align="center")
        y += S(40)
        
        # Calculate gold outline card height dynamically
        card_y0 = y - S(30)
        temp_y = card_y0 + S(40)
        if body:
            b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*3, draw)
            temp_y += len(b_lines) * LINE_B + S(30)
        if items:
            for item in items:
                lines = wrap_text(item, fonts["body"], WIDTH - PAD_X*3 - S(45), draw)
                temp_y += len(lines) * LINE_I + S(20)
                
        card_y1 = temp_y + S(10)
        
        # Draw elegant charcoal-black card with delicate border and large corner radius (SupaUI style)
        draw_glass_card(img, draw, PAD_X - S(30), card_y0, WIDTH - PAD_X + S(30), card_y1,
                        bg_color=(18, 22, 32, 230), border_color=(255, 255, 255, 25), radius=S(32))
        
        # Draw the text inside
        y = card_y0 + S(40)
        if body:
            b_lines = wrap_text(body, fonts["body"], WIDTH - PAD_X*3, draw)
            for line in b_lines:
                tw = draw.textlength(line, font=fonts["body"])
                draw_text(draw, ((WIDTH - tw) // 2, y), line, font=fonts["body"], fill=WHITE)
                y += LINE_B
            y += S(30)
            
        if items:
            draw_arrow_items(draw, items, PAD_X + S(40), y, fonts["body"], 
                             color=WHITE, line_height=LINE_I, max_width=WIDTH - PAD_X*3)
        
        # Always draw illustration at the bottom
        draw_slide_illustration(img, WIDTH // 2, S(940), sn, size=300, image_prompt=slide.get("image_prompt", ""))
            
    _common_decorations(img, draw, slide, fonts)
    return img


# ═══════════════════════════════════════════════════════
#  PUBLIC API
# ═══════════════════════════════════════════════════════
_RENDERERS = {
    "hook":     _render_hook,
    "section":  _render_section,
    "dark":     _render_dark,
    "light":    _render_light,
    "timeline": _render_timeline,
    "results":  _render_results,
    "cta":      _render_cta,
    "content":  _render_content,
}


def render_slide(slide: dict) -> str:
    """Render a single slide dict to a PNG. Returns the output file path."""
    fonts = _load_fonts()
    slide_type = slide.get("type", "content")
    renderer = _RENDERERS.get(slide_type, _render_content)
    img = renderer(slide, fonts)

    out_path = slide_output_path(slide["slide_number"])
    img.save(out_path, format="PNG", quality=95)
    print(f"  ✓  slide_{slide['slide_number']:02d}.png")
    return out_path