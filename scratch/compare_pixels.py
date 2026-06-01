from PIL import Image

img_slide = Image.open("output/slide_03.png")
img_pil = Image.open("output/test_pil_output.png")

print("Checking pixels on row y = 520:")
bg = (0, 0, 128)

non_bg_slide = []
non_bg_pil = []

for x in range(140, 1000):
    p_slide = img_slide.getpixel((x, 520))
    p_pil = img_pil.getpixel((x, 520))
    
    if p_slide != bg:
        non_bg_slide.append(x)
    if p_pil != bg:
        non_bg_pil.append(x)

print(f"slide_03 non-bg x coords on y=520 (len {len(non_bg_slide)}):", non_bg_slide[:10], "... to ...", non_bg_slide[-10:] if non_bg_slide else [])
print(f"test_pil non-bg x coords on y=520 (len {len(non_bg_pil)}):", non_bg_pil[:10], "... to ...", non_bg_pil[-10:] if non_bg_pil else [])
