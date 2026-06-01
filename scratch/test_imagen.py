import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

try:
    print("Generating image with Imagen 4.0 Fast...")
    result = client.models.generate_images(
        model='imagen-4.0-fast-generate-001',
        prompt='A cute 3D cartoon of an algorithm, vector style, white background',
        config=types.GenerateImagesConfig(
            number_of_images=1,
            output_mime_type="image/png",
            aspect_ratio="1:1",
        )
    )
    print("Success!")
    for idx, generated_image in enumerate(result.generated_images):
        output_path = f"scratch/test_imagen_out_{idx}.png"
        import io
        from PIL import Image
        image = Image.open(io.BytesIO(generated_image.image.image_bytes))
        image.save(output_path)
        print(f"Saved image to {output_path}")
except Exception as e:
    print(f"Error during image generation: {e}")
