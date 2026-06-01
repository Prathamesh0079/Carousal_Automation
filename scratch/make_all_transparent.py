import os
import glob
from PIL import Image, ImageDraw

def make_transparent(img_path, tolerance=40):
    img = Image.open(img_path).convert("RGBA")
    w, h = img.size
    
    # Floodfill from the 4 corners
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    for pt in corners:
        ImageDraw.floodfill(img, pt, (0, 0, 0, 0), thresh=tolerance)
        
    img.save(img_path, "PNG")
    print(f"Made background of {os.path.basename(img_path)} transparent.")

def main():
    assets_dir = 'assets'
    pattern = os.path.join(assets_dir, 'illustration_slide_*.png')
    files = glob.glob(pattern)
    if not files:
        print("No illustrations found!")
        return
        
    for f in sorted(files):
        make_transparent(f)

if __name__ == '__main__':
    main()
