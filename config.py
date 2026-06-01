import os

# ── Resolution Scale (Set to 2 or 3 for ultra-crisp HD output) ─
SCALE = 2

# ── PDF Settings ───────────────────────────────────────
# Quality level (1-100) for PDF image compression.
# 100 ensures maximum crispness/sharpness (visually lossless), while 95 offers a good balance of size and quality.
PDF_QUALITY = 100

# ── Paths ──────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR  = os.path.join(BASE_DIR, "fonts")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# ── Font files ─────────────────────────────────────────
FONT_EXTRABOLD = os.path.join(FONTS_DIR, "poppins_extrabold.ttf")
FONT_BOLD      = os.path.join(FONTS_DIR, "poppins_bold.ttf")
FONT_SEMIBOLD  = os.path.join(FONTS_DIR, "poppins_semibold.ttf")
FONT_REGULAR   = os.path.join(FONTS_DIR, "poppins_regular.ttf")

# ── Slide dimensions (3:4 portrait for Instagram) ─────
WIDTH  = 940 * SCALE
HEIGHT = 1200 * SCALE

# ── Font sizes ─────────────────────────────────────────
SIZE_HEADING     = 72 * SCALE
SIZE_SUBHEADING  = 48 * SCALE
SIZE_BODY        = 30 * SCALE
SIZE_META        = 24 * SCALE
SIZE_PILL        = 26 * SCALE
SIZE_ITEM        = 30 * SCALE
SIZE_TAGLINE     = 22 * SCALE
SIZE_BRAND       = 20 * SCALE
SIZE_DECO        = 60 * SCALE

# ── Layout ─────────────────────────────────────────────
PAD_X    = 70 * SCALE    # left/right margin
PAD_Y    = 60 * SCALE    # top/bottom margin
LINE_H   = 86 * SCALE    # heading line height
LINE_B   = 42 * SCALE    # body line height
LINE_I   = 52 * SCALE    # item line height

# ── Colors (defaults, overridden by apply_theme) ──────
PRIMARY_DARK   = "#0B192C"
BRIGHT_ACCENT  = "#FFD700"
PURE_BLACK     = "#000000"
LIGHT_GRAY     = "#f5f5f5"
WHITE          = "#FFFFFF"
HIGHLIGHT      = "#FFD700"
DARK_TEXT       = "#0B192C"
MUTED_TEXT      = "#B0C4DE"

BG_COLORS = {
    "hook":     PRIMARY_DARK,
    "section":  PRIMARY_DARK,
    "dark":     PRIMARY_DARK,
    "light":    PRIMARY_DARK,
    "timeline": PRIMARY_DARK,
    "results":  PRIMARY_DARK,
    "cta":      PRIMARY_DARK,
    "content":  PRIMARY_DARK,
}

# ── Active Theme ───────────────────────────────────────
ACTIVE_THEME = "classic_dark"

# ── Templates ──────────────────────────────────────────
TEMPLATES = {
    "classic_dark": {
        "name": "Classic Dark",
        "desc": "Elegant dark navy & gold",
        "bg_type": "solid",
        "bg_dark": "#0B192C",
        "bg_light": "#1E3E62",
        "accent": "#FFD700",
        "text_primary": "#FFFFFF",
        "text_secondary": "#B0C4DE",
        "accent_text": "#0B192C",
        # Layout style: centered headings, logo at top, gold pill bar at bottom
        "layout": "centered_corporate",
    },
    "editorial_blush": {
        "name": "Editorial Blush",
        "desc": "Clean pink & black magazine style",
        "bg_type": "solid",
        "bg_dark": "#F5E6E0",
        "bg_light": "#FFF5F0",
        "accent": "#1A1A1A",
        "text_primary": "#1A1A1A",
        "text_secondary": "#8B7D75",
        "accent_text": "#FFFFFF",
        # Layout style: outlined pills at top, large left-aligned heading, thin HR lines, NO illustrations
        "layout": "editorial_magazine",
    },
    "bold_coral": {
        "name": "Bold Coral",
        "desc": "Vibrant orange with bold white text",
        "bg_type": "solid",
        "bg_dark": "#FF5733",
        "bg_light": "#FF6B4A",
        "accent": "#FFFFFF",
        "text_primary": "#FFFFFF",
        "text_secondary": "#FFE0D6",
        "accent_text": "#FF5733",
        # Layout style: brand top-left, giant heading, angled label badges, photo at bottom
        "layout": "bold_magazine",
    },
    "blueprint_grid": {
        "name": "Blueprint Grid",
        "desc": "Deep blue with dot grid & yellow accent",
        "bg_type": "dot_grid",
        "bg_dark": "#1A3A8C",
        "bg_light": "#2248A0",
        "accent": "#C8FF00",
        "text_primary": "#FFFFFF",
        "text_secondary": "#8EAAF0",
        "accent_text": "#1A3A8C",
        # Layout style: name left + year right, massive block text, yellow curve, asterisk+URL bottom
        "layout": "grid_impact",
    },
    "modern_dark": {
        "name": "Modern Dark",
        "desc": "Sleek black with warm orange accent",
        "bg_type": "solid",
        "bg_dark": "#111111",
        "bg_light": "#1A1A1A",
        "accent": "#FF6B35",
        "text_primary": "#FFFFFF",
        "text_secondary": "#888888",
        "accent_text": "#111111",
        # Layout style: left-aligned heading with accent underline, dash bullets, minimal
        "layout": "minimal_modern",
    },
    "business_modern": {
        "name": "Business Modern",
        "desc": "Professional corporate dark-teal with clean borders",
        "bg_type": "solid",
        "bg_dark": "#0B2B30",
        "bg_light": "#154C54",
        "accent": "#00ADB5",
        "text_primary": "#FFFFFF",
        "text_secondary": "#A8DADC",
        "accent_text": "#0B2B30",
        "layout": "business_modern",
    },
    "vibrant_marketing": {
        "name": "Vibrant Marketing",
        "desc": "Energetic dark purple with neon yellow indicators",
        "bg_type": "solid",
        "bg_dark": "#131024",
        "bg_light": "#1E1B4B",
        "accent": "#FACC15",
        "text_primary": "#FFFFFF",
        "text_secondary": "#B0A8E3",
        "accent_text": "#131024",
        "layout": "vibrant_marketing",
    },
    "adopt_pet": {
        "name": "Playful Organic",
        "desc": "Warm cream & brown with soft rounded shapes",
        "bg_type": "solid",
        "bg_dark": "#FFFBF2",
        "bg_light": "#F5EBE6",
        "accent": "#8D6E63",
        "text_primary": "#2D2520",
        "text_secondary": "#7D6C62",
        "accent_text": "#FFFBF2",
        "layout": "playful_organic",
    },
}

def apply_theme(name: str):
    """
    Dynamically update global variables in this module so that all other
    modules importing from config will receive the selected theme's values.
    """
    global PRIMARY_DARK, BRIGHT_ACCENT, WHITE, HIGHLIGHT, DARK_TEXT, MUTED_TEXT, BG_COLORS, ACTIVE_THEME
    theme = TEMPLATES.get(name)
    if not theme:
        return
    
    ACTIVE_THEME = name
    PRIMARY_DARK = theme["bg_dark"]
    BRIGHT_ACCENT = theme["accent"]
    WHITE = theme["text_primary"]
    HIGHLIGHT = theme["accent"]
    DARK_TEXT = theme["accent_text"]
    MUTED_TEXT = theme["text_secondary"]
    
    # Dynamically map BG colors based on the theme
    BG_COLORS["hook"] = theme["bg_dark"]
    BG_COLORS["section"] = theme["bg_dark"]
    BG_COLORS["dark"] = theme["bg_dark"]
    BG_COLORS["light"] = theme["bg_light"]
    BG_COLORS["timeline"] = theme["bg_dark"]
    BG_COLORS["results"] = theme["bg_dark"]
    BG_COLORS["cta"] = theme["bg_dark"]
    BG_COLORS["content"] = theme["bg_dark"]

# ── Brand ──────────────────────────────────────────────
BRAND_NAME = "WiseTribes"
BRAND_URL  = "www.wisetribes.in"

# ── LLM ────────────────────────────────────────────────
MODEL       = "gemini-flash-latest"
MAX_TOKENS  = 4096
SLIDE_COUNT = 7