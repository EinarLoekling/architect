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

class VisualEmployee:
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in .env file")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"
        self.output_dir = Path(__file__).parent.parent / "outputs"
        self.output_dir.mkdir(exist_ok=True)
        
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
                    max_tokens=4096,
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

    def generate_visuals(self, post_text: str) -> list:
        """Generates 3 visual concepts with SVGs based on a LinkedIn post."""
        print("Generating Visual Concepts...")
        
        prompt = f"""
        You are a world-class visual designer and creative director.
        Analyze the following LinkedIn post and generate 3 DISTINCT visual concepts that would capture attention.
        
        LinkedIn Post:
        "{post_text}"
        
        For EACH concept, provide:
        1. A Title (e.g., "The Contrarian Chart").
        2. A Rationale (Why this works for this post).
        3. A High-End Image Generation Prompt (for Midjourney/DALL-E) that is detailed and artistic.
        4. A simplified SVG representation of the concept (using 800x800 viewBox).
           - The SVG should be modern, clean, and professional (dark mode compatible).
           - Use Kineticus brand colors: Blue (#00A3FF), Black (#050505), White (#FFFFFF), Grey (#333333).
           - Font: sans-serif.
        
        Return ONLY a JSON array of objects. Format:
        [
            {{
                "title": "...",
                "rationale": "...",
                "image_prompt": "...",
                "svg_code": "<svg>...</svg>" 
            }},
            ...
        ]
        """
        
        response_text = self.generate_with_retry(
            "You are a visual design expert. Return only JSON.",
            prompt
        )
        
        try:
            # Clean json block
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            visuals = json.loads(response_text)
            
            # Save visuals for debugging
            self.save_file(json.dumps(visuals, indent=2), "visual_concepts.json")
            
            # Save individual SVGs
            for i, vis in enumerate(visuals):
                safe_title = "".join([c for c in vis['title'] if c.isalnum() or c in (' ', '-', '_')]).strip().replace(' ', '_').lower()
                svg_filename = f"visual_{i+1}_{safe_title}.svg"
                self.save_file(vis['svg_code'], svg_filename)
            
            return visuals
            
        except Exception as e:
            print(f"Visual generation parsing failed: {e}. Raw response: {response_text[:100]}...")
            # Fallback simple error object
            return [{
                "title": "Error Generating Visuals",
                "rationale": "The model failed to produce valid JSON.",
                "image_prompt": "Error",
                "svg_code": f"<svg viewBox='0 0 800 800' xmlns='http://www.w3.org/2000/svg'><text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' fill='white'>Generation Failed: {str(e)}</text></svg>"
            }]

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AI Visual Employee")
    parser.add_argument("post_text", nargs='?', help="LinkedIn post text")
    args = parser.parse_args()
    
    if args.post_text:
        employee = VisualEmployee()
        employee.generate_visuals(args.post_text)
    else:
        print("Please provide post text as an argument.")
