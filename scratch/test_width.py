import emoji
from PIL import Image, ImageDraw, ImageFont
from config import FONT_BOLD

def get_text_width_emoji(draw, text, font, emoji_scale=0.88):
    # Standard fast path if no emojis are present
    if emoji.emoji_count(text) == 0:
        return draw.textlength(text, font=font)
        
    # Segment text using emoji.emoji_list
    emoji_list = emoji.emoji_list(text)
    total_width = 0.0
    last_idx = 0
    
    font_size = font.size if hasattr(font, "size") else 24
    emoji_width = font_size * emoji_scale
    
    for match in emoji_list:
        start = match['match_start']
        end = match['match_end']
        
        # Add width of the text before the emoji
        if start > last_idx:
            subtext = text[last_idx:start]
            total_width += draw.textlength(subtext, font=font)
            
        # Add emoji width
        total_width += emoji_width
        last_idx = end
        
    # Add width of remaining text after the last emoji
    if last_idx < len(text):
        subtext = text[last_idx:]
        total_width += draw.textlength(subtext, font=font)
        
    return total_width

def test():
    img = Image.new("RGBA", (100, 100))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT_BOLD, 48)
    
    test_str = "🧠 AI Trainer"
    width = get_text_width_emoji(draw, test_str, font)
    print(f"Calculated width for '{test_str}': {width}px")

if __name__ == "__main__":
    test()
