import os
from PIL import Image

def main():
    img_path = '/Users/apple/.gemini/antigravity/brain/75a0927a-21b7-4843-839e-a5d2bd38ae42/media__1779165991222.png'
    if not os.path.exists(img_path):
        print("Logo source image not found!")
        return
        
    img = Image.open(img_path)
    w, h = img.size
    
    # 1. Extract puzzle pieces (typically in the top part of the image, e.g. Y < 550)
    puzzle = img.crop((0, 0, w, 550))
    p_bbox = puzzle.getbbox()
    if p_bbox:
        puzzle_cropped = puzzle.crop(p_bbox)
        os.makedirs('assets', exist_ok=True)
        puzzle_cropped.save('assets/logo_puzzle.png')
        print("Saved logo_puzzle.png with bbox:", p_bbox)
    else:
        print("Puzzle bbox not found!")
        
    # 2. Extract text (typically in the bottom part, Y >= 550)
    text_img = img.crop((0, 550, w, h))
    t_bbox = text_img.getbbox()
    if t_bbox:
        # Shift t_bbox to original coordinates for printing
        real_t_bbox = (t_bbox[0], t_bbox[1] + 550, t_bbox[2], t_bbox[3] + 550)
        text_cropped = text_img.crop(t_bbox)
        text_cropped.save('assets/logo_text_white.png')
        print("Saved logo_text_white.png with bbox:", real_t_bbox)
    else:
        print("Text bbox not found!")

if __name__ == '__main__':
    main()
