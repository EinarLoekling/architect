
import os
import io
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini
GEN_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GEN_API_KEY:
    logger.error("GOOGLE_API_KEY not found in environment variables.")
else:
    genai.configure(api_key=GEN_API_KEY)

# Select best available model
MODEL_NAME = "gemini-1.5-flash" # Default
try:
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    logger.info(f"Available models: {available_models}")
    # Prefer 2.0 Flash as it's often more stable for audio
    if "models/gemini-2.0-flash" in available_models:
        MODEL_NAME = "gemini-2.0-flash"
    elif "models/gemini-2.5-flash" in available_models:
        MODEL_NAME = "gemini-2.5-flash"
    elif "models/gemini-1.5-flash" in available_models:
        MODEL_NAME = "gemini-1.5-flash"
    elif available_models:
        MODEL_NAME = available_models[0].replace("models/", "")
    logger.info(f"Selected model: {MODEL_NAME}")
except Exception as e:
    logger.error(f"Failed to list models: {e}")

# Point to docs/scribe for static files
# We need to go up one level from 'execution' to 'kineticus_nexus', then down to 'docs/scribe'
static_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'docs', 'scribe'))
app = Flask(__name__, static_folder=static_folder, static_url_path='')
CORS(app) 

# System Prompt for "Thought Scribe"
SCRIBE_SYSTEM_PROMPT = """
You are a professional "Thought Scribe". 
Your goal is to take raw, unstructured thoughts (transcripts or text) and convert them into high-quality, professional emails.
You must capture the user's distinct "voice" and "personality" while ensuring the output is polished and effective.
"""

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "thought-scribe-api", "model": MODEL_NAME}), 200

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    """
    Receives an audio file, sends it to Gemini (or Whisper), removes the file, and returns text.
    """
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # Save temporarily to upload to Gemini
        temp_path = "temp_audio.webm" 
        audio_file.save(temp_path)

        # Check file size
        file_size = os.path.getsize(temp_path)
        logger.info(f"Uploading file: {temp_path}, Size: {file_size} bytes")
        
        if file_size < 100:
            return jsonify({"error": "Audio file too small or empty"}), 400

        myfile = genai.upload_file(temp_path, mime_type="audio/webm")
        logger.info(f"Uploaded file {myfile.name}, state: {myfile.state.name}")
        
        # Wait for file to be active
        import time
        for _ in range(30): # Timeout 30s
            if myfile.state.name == "PROCESSING":
                time.sleep(1)
                myfile = genai.get_file(myfile.name)
                logger.info(f"Waiting for file... state: {myfile.state.name}")
            else:
                break
            
        if myfile.state.name != "ACTIVE":
            raise Exception(f"File upload failed with state: {myfile.state.name}")

        model = genai.GenerativeModel(MODEL_NAME)
        result = model.generate_content(["Transcribe the following audio exactly:", myfile])
        
        # Clean up
        os.remove(temp_path)
        
        return jsonify({"transcription": result.text})

    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/generate', methods=['POST'])
def generate_email():
    """
    Input: { "text": "raw thoughts...", "style": "Casual|Formal|...", "context": "optional context" }
    Output: { "email": "Subject: ...\n\nBody..." }
    """
    data = request.json
    raw_text = data.get('text', '')
    style = data.get('style', 'Professional')
    context = data.get('context', '')

    if not raw_text:
        return jsonify({"error": "No text provided"}), 400

    prompt = f"""
    {SCRIBE_SYSTEM_PROMPT}
    
    TASK: Write an email based on these raw thoughts.
    
    STYLE: {style}
    CONTEXT: {context}
    
    RAW THOUGHTS:
    {raw_text}
    
    OUTPUT FORMAT:
    Subject: [Subject Line]
    
    [Email Body]
    """

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        return jsonify({"email": response.text})
    except Exception as e:
        logger.error(f"Generation error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
