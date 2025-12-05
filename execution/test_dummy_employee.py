import os
import sys
import time
import json
from pathlib import Path
from dotenv import load_dotenv
import anthropic
from datetime import datetime

# Load environment variables
load_dotenv(Path(__file__).parent.parent / '.env')

class TestDummyEmployee:
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in .env file")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"
        self.output_dir = Path(__file__).parent.parent / "outputs" / "test_dummy"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create timestamped folder for this run
        self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_dir = self.output_dir / self.run_id
        self.run_dir.mkdir(exist_ok=True)

    def generate_with_retry(self, system_prompt: str, user_prompt: str, max_retries=3) -> str:
        """Generates content with self-annealing retry logic."""
        for attempt in range(max_retries):
            try:
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    temperature=0.7,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_prompt}
                    ]
                )
                return message.content[0].text
            except Exception as e:
                print(f"Generation failed (attempt {attempt+1}/{max_retries}): {e}")
                time.sleep(2)
        raise Exception("Failed to generate content after multiple retries")

    def save_file(self, content: str, filename: str):
        path = self.run_dir / filename
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Saved: {path}")

    def run(self, input_text: str):
        print(f"Test Dummy Employee starting. Run ID: {self.run_id}")
        print(f"Input: {input_text}")
        
        prompt = f"""
        You are a Test Dummy agent.
        Your task is simple:
        1. Reverse the following text: "{input_text}"
        2. Analyze the sentiment of the text (Positive, Negative, Neutral).
        
        Return the result as a JSON object:
        {{
            "original": "{input_text}",
            "reversed": "...",
            "sentiment": "..."
        }}
        """
        
        response = self.generate_with_retry(
            "You are a test assistant. Return ONLY JSON.",
            prompt
        )
        
        try:
            # Clean json block if needed
            cleaned_response = response
            if "```json" in response:
                cleaned_response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                cleaned_response = response.split("```")[1].split("```")[0]
                
            result = json.loads(cleaned_response)
            self.save_file(json.dumps(result, indent=2), "test_result.json")
            print("Test successful.")
            return result
            
        except Exception as e:
            print(f"Failed to parse response: {e}")
            self.save_file(response, "test_failure.txt")
            return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_text = sys.argv[1]
    else:
        input_text = "This is a default test message to verify the system."
        
    employee = TestDummyEmployee()
    employee.run(input_text)
