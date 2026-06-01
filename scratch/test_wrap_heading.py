from PIL import Image, ImageDraw
from config import WIDTH, HEIGHT, PAD_X, FONT_EXTRABOLD, SCALE
from utils import load_font, wrap_text

# Set up dummy draw
img = Image.new("RGB", (WIDTH, HEIGHT))
draw = ImageDraw.Draw(img)
draw.img = img

# Load heading font (72 * SCALE = 144)
font = load_font("extrabold", 72 * SCALE)

heading = "👨‍⚕️ AI-Augmented Doctor"
max_w = WIDTH - PAD_X * 2 - int(280 * SCALE) # slide 3 has illustration

print(f"WIDTH: {WIDTH}, PAD_X: {PAD_X}, max_w: {max_w}")

lines = wrap_text(heading, font, max_w, draw)
print("wrap_text returned lines:")
for idx, line in enumerate(lines):
    print(f"Line {idx+1}: '{line}' (width {draw.textlength(line, font=font)})")
