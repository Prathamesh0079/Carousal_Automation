import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

print("Listing models via google-genai client...")
try:
    for m in client.models.list():
        print(f"- {m.name} (Supported actions: {m.supported_actions})")
except Exception as e:
    print("Error listing models:", e)
