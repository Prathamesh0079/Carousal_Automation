import os
from PIL import Image, ImageDraw

def process_image(img_path, out_path, tolerance=40):
    img = Image.open(img_path).convert("RGBA")
    w, h = img.size
    
    # We will floodfill transparency from the four corners
    # We need to fill with a transparent color (0, 0, 0, 0)
    # However, ImageDraw.floodfill works on the image in-place.
    # Since we are filling RGBA with (0,0,0,0), let's see if PIL's floodfill supports transparency.
    # Let's try filling with (0, 0, 0, 0) from the 4 corners:
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    for pt in corners:
        ImageDraw.floodfill(img, pt, (0, 0, 0, 0), thresh=tolerance)
        
    img.save(out_path, "PNG")
    print(f"Processed {img_path} -> {out_path}")

if __name__ == '__main__':
    process_image('assets/illustration_slide_1.png', 'scratch/transparent_slide_1.png')
