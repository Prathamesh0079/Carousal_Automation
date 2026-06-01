import os
from google import genai
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

try:
    print("Testing image generation with Imagen 4.0...")
    result = client.models.generate_images(
        model='imagen-4.0-generate-001',
        prompt='A flat 2d vector cartoon illustration of a family looking at a laptop with a lightbulb next to them, dark blue background, vibrant colors',
        config=dict(
            number_of_images=1,
            output_mime_type='image/png',
            aspect_ratio='1:1'
        )
    )
    print("Success! Number of images generated:", len(result.generated_images))
    for i, generated_image in enumerate(result.generated_images):
        img = Image.open(BytesIO(generated_image.image.image_bytes))
        img.save(f"scratch/test_output_imagen4_{i}.png")
        print(f"Saved scratch/test_output_imagen4_{i}.png")
except Exception as e:
    print("Error during image generation:", e)
