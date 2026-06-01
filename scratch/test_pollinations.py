import urllib.request
import urllib.parse
import os
import ssl

prompt = "A cute 3D cartoon style illustration of Cristiano Ronaldo playing football, digital art, white background"
encoded_prompt = urllib.parse.quote(prompt)
url = f"https://image.pollinations.ai/p/{encoded_prompt}?width=512&height=512&nologo=true"

print(f"Requesting free image from: {url}")
try:
    os.makedirs("output", exist_ok=True)
    
    # Create unverified SSL context to bypass macOS local issuer cert issues
    ssl_context = ssl._create_unverified_context()
    
    # Request with user-agent
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=ssl_context) as response:
        with open("output/test_pollinations_output.png", "wb") as f:
            f.write(response.read())
            
    print("Success! Free generated image saved to output/test_pollinations_output.png")
except Exception as e:
    print(f"Failed to fetch image: {e}")
