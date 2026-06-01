import sys
import os
import json
import config

selected_theme = "classic_dark"

# Check if a custom theme is specified via command line (e.g., --theme bold_coral or -t editorial_blush)
theme_arg_idx = -1
for idx, arg in enumerate(sys.argv):
    if arg in ("--theme", "-t") and idx + 1 < len(sys.argv):
        selected_theme = sys.argv[idx + 1]
        theme_arg_idx = idx
        break

if theme_arg_idx != -1:
    # Pop them out of sys.argv so they do not interfere with script topic/file matching
    sys.argv.pop(theme_arg_idx + 1)
    sys.argv.pop(theme_arg_idx)
elif sys.stdin.isatty():
    # Prompt the user interactively in terminals
    print(f"\n{'═'*44}")
    print("  ✦  Select a Design Theme")
    print(f"{'═'*44}")
    print("  1. Classic Dark (Elegant navy & gold) [Default]")
    print("  2. Editorial Blush (Clean pink & black magazine)")
    print("  3. Bold Coral (Vibrant orange, bold white text)")
    print("  4. Blueprint Grid (Deep blue, dot grid, yellow)")
    print("  5. Modern Dark (Sleek black, warm orange accent)")
    print("  6. Business Modern (Corporate dark-teal, clean)")
    print("  7. Vibrant Marketing (Purple, neon yellow & pink)")
    print("  8. Playful Organic (Warm cream & brown, rounded)")
    print(f"{'─'*44}")
    try:
        choice = input("  Select [1-8] (or press Enter for default): ").strip()
        if choice == "2":
            selected_theme = "editorial_blush"
        elif choice == "3":
            selected_theme = "bold_coral"
        elif choice == "4":
            selected_theme = "blueprint_grid"
        elif choice == "5":
            selected_theme = "modern_dark"
        elif choice == "6":
            selected_theme = "business_modern"
        elif choice == "7":
            selected_theme = "vibrant_marketing"
        elif choice == "8":
            selected_theme = "adopt_pet"
    except (EOFError, KeyboardInterrupt):
        pass
    print(f"{'═'*44}\n")

# Apply selected theme prior to importing any renderer or generator logic
config.apply_theme(selected_theme)

# Load configuration and generators with updated theme variables
from generator import generate_slides
from renderer  import render_slide
from utils     import ensure_dir
from config    import OUTPUT_DIR, SCALE, PDF_QUALITY


def parse_json_script(filepath: str) -> list[dict]:
    """Parse slide structure from a JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        slides = json.load(f)
    
    for i, slide in enumerate(slides):
        slide.setdefault("slide_number", i + 1)
        slide.setdefault("type", "content")
        slide.setdefault("heading", "")
        slide.setdefault("body", "")
        slide.setdefault("items", [])
        slide.setdefault("highlight_word", "")
        slide.setdefault("tagline", "")
        slide["total"] = len(slides)
        
    return slides


def parse_text_script(filepath: str) -> list[dict]:
    """Parse slide structure from a plain text script file, supporting natural draft layouts."""
    import re
    raw_lines = []
    with open(filepath, 'r', encoding='utf-8') as f:
        raw_lines = f.readlines()
        
    # Check if there is any slide separator in the file
    has_any_separator = False
    for line in raw_lines:
        line_str = line.strip()
        if not line_str:
            continue
        if line_str.startswith('---') or line_str.startswith('==='):
            has_any_separator = True
            break
        if 'slide' in line_str.lower() and re.search(r'\d+', line_str):
            has_any_separator = True
            break
            
    slides_raw = []
    current_lines = []
    started = not has_any_separator
    
    for line in raw_lines:
        line_str = line.strip()
        if not line_str:
            continue
            
        lower_line = line_str.lower()
        is_sep = False
        if line_str.startswith('---') or line_str.startswith('==='):
            is_sep = True
        elif 'slide' in lower_line:
            if re.search(r'\d+', line_str):
                is_sep = True
                
        if is_sep:
            started = True
            if current_lines:
                has_content = False
                for cl in current_lines:
                    cl_clean = cl.strip()
                    is_cl_sep = cl_clean.startswith('---') or cl_clean.startswith('==='[-3:]) or ('slide' in cl_clean.lower() and re.search(r'\d+', cl_clean))
                    if not is_cl_sep:
                        has_content = True
                        break
                if has_content:
                    slides_raw.append(current_lines)
                    current_lines = [line_str]
                else:
                    current_lines = [line_str]
            else:
                current_lines.append(line_str)
        else:
            if started:
                current_lines.append(line_str)
            
    if current_lines:
        has_content = False
        for cl in current_lines:
            cl_clean = cl.strip()
            is_cl_sep = cl_clean.startswith('---') or cl_clean.startswith('===') or ('slide' in cl_clean.lower() and re.search(r'\d+', cl_clean))
            if not is_cl_sep:
                has_content = True
                break
        if has_content:
            slides_raw.append(current_lines)
        
    slides = []
    for block in slides_raw:
        if not block:
            continue
            
        slide_num = len(slides) + 1
        slide_type = 'content'
        first_line = block[0]
        
        is_sep = False
        if first_line.startswith('---') or first_line.startswith('===') or 'slide' in first_line.lower():
            is_sep = True
            
        content_lines = block[1:] if is_sep else block
        
        if is_sep:
            num_match = re.search(r'\d+', first_line)
            if num_match:
                slide_num = int(num_match.group())
            
            clean_sep = first_line.replace('###', '').replace('---', '').replace('**', '').replace('*', '')
            for t in ('hook', 'section', 'dark', 'light', 'timeline', 'results', 'cta', 'content'):
                if t in clean_sep.lower():
                    slide_type = t
                    break
        
        heading = ''
        body_parts = []
        items = []
        tagline = ''
        highlight_word = ''
        
        for line in content_lines:
            clean = line.strip('*_ #')
            if not clean:
                continue
                
            if not heading:
                heading = clean
                if '**' in line:
                    parts = line.split('**')
                    if len(parts) >= 3 and parts[1].strip():
                        highlight_word = parts[1].strip().split()[0]
                continue
                
            is_bullet = False
            for prefix in ('- ', '* ', '→ ', '• '):
                if clean.startswith(prefix):
                    is_bullet = True
                    clean = clean[len(prefix):].strip()
                    break
            
            if ':' in clean:
                lower_clean = clean.lower()
                if not any(lower_clean.startswith(k) for k in ('tagline:', 'tag:', 'badge:', 'type:', 'highlight:')):
                    is_bullet = True
            
            if ':' in clean:
                parts = clean.split(':', 1)
                k_lower = parts[0].strip().lower()
                v_strip = parts[1].strip()
                if k_lower in ('tagline', 'tag', 'badge'):
                    tagline = v_strip
                    continue
                elif k_lower == 'highlight':
                    highlight_word = v_strip
                    continue
                elif k_lower == 'type':
                    slide_type = v_strip
                    continue
                    
            if is_bullet:
                items.append(clean)
            else:
                if (line.startswith('*') and line.endswith('*')) or (line.startswith('_') and line.endswith('_')):
                    if not tagline:
                        tagline = clean
                    else:
                        body_parts.append(clean)
                else:
                    body_parts.append(clean)
                    
        body = ' '.join(body_parts)
        
        slide = {
            'slide_number': slide_num,
            'type': slide_type,
            'heading': heading,
            'body': body,
            'items': items,
            'highlight_word': highlight_word,
            'tagline': tagline
        }
        slides.append(slide)
        
    slides.sort(key=lambda s: s['slide_number'])
    for slide in slides:
        slide['total'] = len(slides)
        
    return slides


def make_carousel(source: str):
    ensure_dir(OUTPUT_DIR)
    


    is_file = os.path.isfile(source)
    
    if is_file:
        print(f"\n{'═'*44}")
        print(f"  ✦  Carousel Generator")
        print(f"{'═'*44}")
        print(f"  Script File : {source}")
        print(f"{'─'*44}\n")
        
        ext = os.path.splitext(source)[1].lower()
        if ext == ".json":
            slides = parse_json_script(source)
        else:
            slides = parse_text_script(source)
            
        print(f"  Parsed {len(slides)} slides from script file\n")
        first_heading = slides[0].get("heading", "") if slides else ""
        if first_heading:
            topic_for_pdf = first_heading
        else:
            topic_for_pdf = os.path.splitext(os.path.basename(source))[0]



        for slide in slides:
            sn = slide.get("slide_number", 1)
            stype = slide.get("type", "content")
            # Skip only the last/CTA slide to avoid clutter
            if sn == len(slides) or stype == "cta":
                slide["image_prompt"] = ""
            else:
                # Build a prompt from the slide heading
                heading = slide.get("heading", "")
                if heading:
                    slide["image_prompt"] = heading
                else:
                    slide["image_prompt"] = ""

    else:
        topic_for_pdf = source
        print(f"\n{'═'*44}")
        print(f"  ✦  Carousel Generator")
        print(f"{'═'*44}")
        print(f"  Topic : {source}")
        print(f"{'─'*44}\n")
        

        
        slides = generate_slides(source)
        print(f"  Got {len(slides)} slides from LLM\n")

    # Step 2: render each slide as PNG
    print("  Rendering slides...")
    paths = []
    for slide in slides:
        path = render_slide(slide)
        paths.append(path)

    # Step 3: combine into PDF
    print("\n  Generating PDF...")
    pdf_path = _make_pdf(paths, topic_for_pdf)

    # Done
    print(f"\n{'═'*44}")
    print(f"  ✓  {len(paths)} slides saved to ./output/")
    print(f"  ✓  PDF: {os.path.basename(pdf_path)}")
    print(f"{'═'*44}\n")


def _make_pdf(image_paths: list[str], topic: str) -> str:
    """Combine slide PNGs into a single PDF file."""
    from PIL import Image

    # Sanitize topic for filename
    safe_name = "".join(c if c.isalnum() or c in " -_" else "" for c in topic)
    safe_name = safe_name.strip().replace(" ", "_")[:50]
    pdf_path = os.path.join(OUTPUT_DIR, f"carousel_{safe_name}.pdf")

    images = []
    for p in image_paths:
        img = Image.open(p).convert("RGB")
        images.append(img)

    if images:
        images[0].save(
            pdf_path, "PDF", save_all=True,
            append_images=images[1:],
            resolution=150.0 * SCALE,
            quality=PDF_QUALITY,
        )
        print(f"  ✓  {os.path.basename(pdf_path)}")

    return pdf_path


if __name__ == "__main__":
    if len(sys.argv) > 1:
        source = " ".join(sys.argv[1:])
        make_carousel(source)
    else:
        while True:
            print("\nChoose input mode:")
            print("1. Enter a topic (generate content using Gemini)")
            print("2. Paste your script directly in terminal")
            print("3. Enter path to a script file (e.g. script.txt)")
            choice = input("Select [1-3]: ").strip()
            
            if choice == "1":
                source = input("\nEnter carousel topic: ").strip()
                if not source:
                    print("No topic provided. Exiting.")
                    sys.exit(1)
                make_carousel(source)
                break
                
            elif choice == "2":
                print("\nPaste your script below. When finished, type 'END' on a new line and press Enter:")
                print("─" * 60)
                lines = []
                while True:
                    try:
                        line = input()
                        if line.strip() == "END":
                            break
                        lines.append(line)
                    except EOFError:
                        break
                print("─" * 60)
                script_text = "\n".join(lines)
                
                # Save temporary file to parse
                temp_path = "temp_interactive_script.txt"
                with open(temp_path, "w", encoding="utf-8") as f:
                    f.write(script_text)
                
                try:
                    make_carousel(temp_path)
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                break
                
            elif choice == "3":
                file_path = input("\nEnter script file path: ").strip()
                if not file_path or not os.path.exists(file_path):
                    print(f"File not found: {file_path}. Exiting.")
                    sys.exit(1)
                make_carousel(file_path)
                break
                
            else:
                print("Invalid choice, please select 1, 2, or 3.")