from PIL import Image

img = Image.open("output/slide_03.png")
print("Pixel color at (350, 480):", img.getpixel((350, 480)))
print("Pixel color at (140, 480):", img.getpixel((140, 480))) # should be background unless covered
