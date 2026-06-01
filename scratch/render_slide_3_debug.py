from main import parse_text_script
from renderer import render_slide
import renderer

# Monkeypatch renderer.draw_text to print its inputs
orig_draw_text = renderer.draw_text
def debug_draw_text(draw, xy, text, font, fill, anchor=None, **kwargs):
    print(f"DEBUG draw_text: xy={xy}, text='{text}', font_size={font.size if hasattr(font, 'size') else '?'}, fill={fill}")
    return orig_draw_text(draw, xy, text, font, fill, anchor=anchor, **kwargs)

renderer.draw_text = debug_draw_text

slides = parse_text_script("test_interactive.txt")
slide_3 = [s for s in slides if s["slide_number"] == 3][0]

print("Rendering Slide 3...")
render_slide(slide_3)
