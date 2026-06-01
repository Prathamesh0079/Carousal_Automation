import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

print("Listing all models...")
try:
    for m in client.models.list():
        # filter for imagen or list all
        if 'image' in m.name or 'imagen' in m.name:
            print(f"- {m.name} ({m.supported_actions})")
except Exception as e:
    print("Failed to list models:", e)
