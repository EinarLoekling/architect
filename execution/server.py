import sys
import os
import traceback

# Add current directory to path so we can import content_employee
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
from flask_cors import CORS
from content_employee import ContentEmployee

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/generate', methods=['POST'])
def generate_content():
    try:
        data = request.json
        password = data.get('password')
        if password != "kineticus_admin":
            return jsonify({"error": "Unauthorized: Invalid Password"}), 401

        expertise_text = data.get('expertise')
        tone_text = data.get('tone')
        
        if not expertise_text or not tone_text:
            return jsonify({"error": "Missing expertise or tone"}), 400

        print("Received generation request...")
        
        # Initialize Employee
        employee = ContentEmployee()
        
        # Run generation
        # We need to bypass the ingest_content file check since we are passing raw text
        # But ingest_content handles raw text if file doesn't exist, so we are good.
        
        assets = employee.run(expertise_text, tone_text)
        
        return jsonify({
            "status": "success",
            "assets": assets
        })

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/research', methods=['POST'])
def deep_research():
    try:
        data = request.json
        password = data.get('password')
        if password != "kineticus_admin":
            return jsonify({"error": "Unauthorized: Invalid Password"}), 401

        topic = data.get('topic')
        
        if not topic:
            return jsonify({"error": "Missing topic"}), 400

        print(f"Received research request for: {topic}")
        
        # Initialize Employee
        employee = ContentEmployee()
        
        # Run research
        research_content = employee.perform_deep_research(topic)
        
        return jsonify({
            "status": "success",
            "research": research_content
        })

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
