from PIL import Image, ImageDraw
from config import FONT_EXTRABOLD, SCALE
from utils import load_font, draw_text

img = Image.new("RGB", (1880, 1200), (0, 0, 128))
draw = ImageDraw.Draw(img)
draw.img = img

font = load_font("extrabold", 72 * SCALE)

# Draw the text using the exact draw_text utility
draw_text(draw, (140, 480), "👨‍⚕️ AI-Augmented", font=font, fill="#ffffff")

img.save("output/test_pil_output.png")
print("Saved test_pil_output.png")
