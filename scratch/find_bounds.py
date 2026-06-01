from PIL import Image

img_slide = Image.open("output/slide_03.png")
img_pil = Image.open("output/test_pil_output.png")

bg = (0, 0, 128)

def find_bounds(img):
    coords = []
    for x in range(284, 1200):
        for y in range(400, 700):
            if img.getpixel((x, y)) != bg:
                coords.append((x, y))
    if not coords:
        return "None"
    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]
    return f"x: [{min(xs)}, {max(xs)}], y: [{min(ys)}, {max(ys)}], count: {len(coords)}"

print("Bounds of non-bg pixels for x > 284, y in [400, 700]:")
print("slide_03:", find_bounds(img_slide))
print("test_pil:", find_bounds(img_pil))
