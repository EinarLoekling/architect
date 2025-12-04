import os
from dotenv import load_dotenv
import google.generativeai as genai
from pathlib import Path
import time

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

def test_config(model_name, tools, description):
    print(f"\n--- Testing {description} ---")
    print(f"Model: {model_name}")
    print(f"Tools: {tools}")
    try:
        model = genai.GenerativeModel(model_name, tools=tools)
        response = model.generate_content("What is the capital of France?")
        print(f"SUCCESS: {response.text[:50]}...")
        return True
    except Exception as e:
        print(f"FAILURE: {e}")
        return False

# Test Proto Construction
model = 'gemini-flash-latest'

try:
    from google.ai.generativelanguage import Tool, GoogleSearch
    t = Tool(google_search=GoogleSearch())
    test_config(model, [t], f"{model} - Proto Tool")
except Exception as e:
    print(f"Proto import failed: {e}")

# Try passing just the string 'google_search' (some versions support this?)
# test_config(model, 'google_search', f"{model} - String Tool")
