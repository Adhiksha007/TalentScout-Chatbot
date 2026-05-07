import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

print("Listing models and their supported actions:")
for m in client.models.list():
    print(f"Model: {m.name}")
    print(f"Actions: {m.supported_actions}")
    # Check if 'generate_content' is exactly in there or if it's different
    break
