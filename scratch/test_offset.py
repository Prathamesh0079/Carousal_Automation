import os
from PIL import Image, ImageDraw, ImageFont
from pilmoji import Pilmoji
from config import FONT_BOLD

def test_offset():
    img = Image.new("RGBA", (1000, 300), (30, 30, 30, 255))
    draw = ImageDraw.Draw(img)
    
    font_size = 80
    font = ImageFont.truetype(FONT_BOLD, font_size)
    
    # Draw with different offsets to compare
    with Pilmoji(img) as pilmoji:
        # 1. Default (no offset)
        pilmoji.text((50, 50), "🧠 AI Trainer (Default)", font=font, fill=(255, 255, 255, 255))
        
        # 2. Dynamic offset (shift down and scale slightly down)
        y_offset = int(font_size * 0.12)
        pilmoji.text(
            (50, 170), 
            "🧠 AI Trainer (Fixed)", 
            font=font, 
            fill=(255, 255, 255, 255),
            emoji_position_offset=(0, y_offset),
            emoji_scale_factor=0.88
        )
        
    os.makedirs("scratch", exist_ok=True)
    img.save("scratch/test_offset.png")
    print("Offset test image saved to scratch/test_offset.png")

if __name__ == "__main__":
    test_offset()
