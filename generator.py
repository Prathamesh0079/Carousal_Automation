import os
import json
from google import genai
from dotenv import load_dotenv
from config import MODEL, MAX_TOKENS, SLIDE_COUNT

load_dotenv()


def _build_prompt(topic: str) -> str:
    return f"""
You are a premium LinkedIn/Instagram carousel content expert.

Create a {SLIDE_COUNT}-slide carousel about: "{topic}"

SLIDE TYPES (use this exact sequence):
- Slide 1: type "hook" — bold attention-grabbing opening
- Slide 2: type "content" — first key insight
- Slide 3: type "section" — detailed breakdown with bullet items
- Slide 4: type "content" — second key insight  
- Slide 5: type "dark" — powerful statement or statistic
- Slide 6: type "results" — checklist of key takeaways
- Slide {SLIDE_COUNT}: type "cta" — call to action (follow, share, save)
Rules:
- heading: max 8 words, punchy and impactful
- body: max 30 words, practical and specific. Must be complete, grammatically correct sentences (do not truncate or end mid-sentence).
- items: list of 3-5 short bullet points (max 8 words each), only for section/results/content types
- highlight_word: one powerful keyword from the heading to visually emphasize
- tagline: short label for badges/pills (max 5 words), for section/dark/results/cta types
- image_prompt: A clear, descriptive prompt for a simple, clean, cute 2D cartoon style illustration representing this slide's concept (e.g. 'a cute laptop with a lightbulb'). Provide this for Slide 1 (Hook) and all inner slides (Slides 1 to 7). Leave as an empty string "" only for the last CTA slide to prevent clutter. Keep it short (max 10 words).

Return ONLY a valid JSON array.

Format:
[
  {{
    "slide_number": 1,
    "type": "hook",
    "heading": "...",
    "body": "...",
    "items": [],
    "highlight_word": "...",
    "tagline": "",
    "image_prompt": ""
  }},
  ...
]
"""


def generate_slides(topic: str) -> list[dict]:
    """Call Gemini and return a list of slide dicts."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY not set in .env")

    client = genai.Client(api_key=api_key)

    print("  Calling Gemini...")
    response = client.models.generate_content(
        model=MODEL,
        contents=_build_prompt(topic),
        config={
            'max_output_tokens': MAX_TOKENS,
            'temperature': 0.7,
            'response_mime_type': 'application/json',
        }
    )

    raw = response.text.strip()

    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        slides = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Gemini returned invalid JSON: {e}\n\nRaw output:\n{raw}")

    # Inject total count and ensure required keys
    for slide in slides:
        slide["total"] = len(slides)
        slide.setdefault("items", [])
        slide.setdefault("highlight_word", "")
        slide.setdefault("tagline", "")
        slide.setdefault("body", "")
        slide.setdefault("image_prompt", "")

    return slides