from PIL import Image

img = Image.open("output/slide_03.png")

bg_color = (0, 0, 128)
has_non_bg = False
for x in range(140, 284):
    for y in range(480, 624):
        pixel = img.getpixel((x, y))
        if pixel != bg_color:
            has_non_bg = True
            break
    if has_non_bg:
        break

print("Found non-background pixels in emoji area:", has_non_bg)
