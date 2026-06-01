from main import parse_text_script

slides = parse_text_script("test_interactive.txt")
for slide in slides:
    print(f"Slide {slide['slide_number']}: heading='{slide['heading']}'")
