from PIL import Image

img = Image.open("output/slide_03.png")
# Let's inspect the area next to the emoji (x = 350 to 500, y = 480 to 520)
# The background color is primary dark: #000080 (RGB: 0, 0, 128)
# The text color is white: #ffffff (RGB: 255, 255, 255)

bg_color = (0, 0, 128)
has_non_bg = False
for x in range(350, 600):
    for y in range(480, 520):
        pixel = img.getpixel((x, y))
        if pixel != bg_color:
            has_non_bg = True
            break
    if has_non_bg:
        break

print("Found non-background pixels next to emoji:", has_non_bg)
