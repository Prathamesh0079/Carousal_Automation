from main import parse_text_script

slides = parse_text_script("test_interactive.txt")
slide_3 = [s for s in slides if s["slide_number"] == 3][0]

for k, v in slide_3.items():
    print(f"{k}: {v}")
