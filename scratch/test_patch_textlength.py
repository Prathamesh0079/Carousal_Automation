import emoji
from PIL import Image, ImageDraw, ImageFont
from config import FONT_BOLD

def test():
    img = Image.new("RGBA", (100, 100))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT_BOLD, 48)
    
    orig_textlength = draw.textlength
    
    def emoji_aware_textlength(text, font, **kwargs):
        import emoji
        if emoji.emoji_count(text) > 0:
            font_size = font.size if hasattr(font, "size") else 24
            emoji_list = emoji.emoji_list(text)
            total_width = 0.0
            last_idx = 0
            emoji_width = font_size * 0.88
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
    
    test_str = "🧠 AI Trainer"
    print("Patched textlength:", draw.textlength(test_str, font=font))
    print("Original textlength:", orig_textlength(test_str, font=font))

if __name__ == "__main__":
    test()
