import os
from dotenv import load_dotenv
import google.generativeai as genai
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
print(f"Loading .env from: {env_path}")
load_dotenv(env_path)

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Error: GOOGLE_API_KEY not found in .env")
else:
    print(f"GOOGLE_API_KEY found: {api_key[:5]}...{api_key[-5:]}")
    try:
        genai.configure(api_key=api_key)
        print("Listing available models...")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
    except Exception as e:
        print(f"Error listing models: {e}")
