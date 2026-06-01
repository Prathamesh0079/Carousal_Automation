from PIL import Image, ImageDraw
from config import WIDTH, HEIGHT, PAD_X, SCALE
from utils import load_font, wrap_text
import renderer

# Set up slide like _new_slide
bg_color = "#000080"
img, draw = renderer._new_slide(bg_color)

# Load heading font
font = renderer._load_fonts()["heading"]

heading = "👨‍⚕️ AI-Augmented Doctor"
max_w = WIDTH - PAD_X * 2 - int(280 * SCALE)

lines = wrap_text(heading, font, max_w, draw)
print("Wrap text output in generator context:")
for idx, line in enumerate(lines):
    print(f"Line {idx+1}: '{line}'")
