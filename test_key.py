import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

print(f"Testing API Key: {api_key[:10]}...")

try:
    genai.configure(api_key=api_key)
    print("Configuration successful.")
    
    print("\nListing available models:")
    models = genai.list_models()
    count = 0
    for m in models:
        print(f"- {m.name} (Supports: {m.supported_generation_methods})")
        count += 1
    
    if count == 0:
        print("No models found. Your API key might be restricted or the Generative Language API is not enabled.")
    else:
        print(f"\nFound {count} models. Attempting a test generation with 'gemini-1.5-flash'...")
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello!")
        print(f"Response: {response.text}")
        print("\nSUCCESS! Your API key is working perfectly.")

except Exception as e:
    print(f"\nFAILED! Error details:")
    print(str(e))
    print("\nTroubleshooting tips:")
    print("1. Ensure your country is supported by Gemini API.")
    print("2. Go to https://aistudio.google.com/ and create a NEW API key.")
    print("3. Ensure 'Generative Language API' is enabled in your Google Cloud Console if using a GCP project.")
