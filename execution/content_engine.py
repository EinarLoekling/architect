import os
import sys
import time
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
import anthropic

# Load environment variables
load_dotenv(Path(__file__).parent.parent / '.env')

class ContentEngine:
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in .env file")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"  # Using latest Sonnet
        self.output_dir = Path(__file__).parent.parent / "outputs"
        self.output_dir.mkdir(exist_ok=True)
        (self.output_dir / "long-form").mkdir(exist_ok=True)
        (self.output_dir / "linkedin").mkdir(exist_ok=True)
        (self.output_dir / "email").mkdir(exist_ok=True)

    def ingest_content(self, source: str) -> str:
        """Ingests content from a file path, URL, or raw text."""
        print(f"Ingesting content from: {source[:50]}...")
        
        if source.startswith("http"):
            try:
                response = requests.get(source)
                response.raise_for_status()
                # Basic HTML to text - in production use BeautifulSoup
                return response.text 
            except Exception as e:
                print(f"Error fetching URL: {e}")
                return ""
        
        elif os.path.exists(source):
            try:
                with open(source, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                print(f"Error reading file: {e}")
                return ""
        
        else:
            # Assume raw text
            return source

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

    def analyze_content(self, text: str) -> dict:
        """Phase 1: Analyzes content and creates a brief."""
        print("Phase 1: Analyzing content...")
        system_prompt = "You are an expert content strategist. Analyze the provided text and extract core themes, key insights, and audience data."
        user_prompt = f"""
        Analyze the following content and provide a JSON object with these keys:
        - main_thesis
        - key_points (list)
        - target_audience
        - tone
        - statistics (list)
        - quotes (list)
        
        Content:
        {text[:20000]}  # Truncate if too long
        """
        
        response = self.generate_with_retry(system_prompt, user_prompt)
        # Extract JSON from response if wrapped in markdown
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            return json.loads(response)
        except json.JSONDecodeError:
            print("Failed to parse analysis JSON. Using raw text.")
            return {"raw_analysis": response}

    def generate_assets(self, text: str, analysis: dict):
        """Orchestrates the generation of all assets."""
        
        # Phase 2: Long-form Resource
        print("Phase 2: Generating Long-form Resource...")
        long_form_prompt = f"""
        Create a comprehensive 2000+ word guide based on this analysis: {json.dumps(analysis)}
        
        Follow this structure:
        1. Introduction with hook
        2. 5-7 distinct sections with examples/data
        3. Actionable frameworks
        4. Conclusion with next steps
        
        Format: Markdown with headers, bullets, and a 'Key Takeaways' box.
        Voice: Direct, data-driven, authentic.
        """
        long_form = self.generate_with_retry("You are a B2B content writer.", long_form_prompt)
        self.save_file(long_form, "long-form/guide.md")

        # Phase 3: LinkedIn Posts
        print("Phase 3: Generating LinkedIn Posts...")
        li_post_1 = self.generate_with_retry(
            "You are a LinkedIn ghostwriter.",
            f"Write a Thought Leadership post (150-200 words) based on: {analysis.get('main_thesis')}. Hook: Contrarian. Tone: Authoritative."
        )
        self.save_file(li_post_1, "linkedin/post_1_thought_leadership.txt")

        li_post_2 = self.generate_with_retry(
            "You are a LinkedIn ghostwriter.",
            f"Write a Tactical/How-to post (120-180 words) based on these points: {analysis.get('key_points')}. Hook: Specific outcome. Format: Numbered list."
        )
        self.save_file(li_post_2, "linkedin/post_2_tactical.txt")

        # Phase 4: Emails
        print("Phase 4: Generating Emails...")
        email_1 = self.generate_with_retry(
            "You are an email marketing specialist.",
            f"Write an Educational email (300-400 words) teaching one concept from: {analysis.get('main_thesis')}. Subject: Curiosity-driven."
        )
        self.save_file(email_1, "email/nurture_1_educational.txt")

        email_2 = self.generate_with_retry(
            "You are an email marketing specialist.",
            f"Write a Story-driven email (250-350 words) connecting a story to: {analysis.get('main_thesis')}. Subject: Story hook."
        )
        self.save_file(email_2, "email/nurture_2_story.txt")

    def save_file(self, content: str, relative_path: str):
        path = self.output_dir / relative_path
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Saved: {relative_path}")

    def run(self, source: str):
        text = self.ingest_content(source)
        if not text:
            print("No content to process.")
            return
        
        analysis = self.analyze_content(text)
        self.generate_assets(text, analysis)
        print("\nWorkflow completed successfully. Check /outputs folder.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python content_engine.py <source_file_or_url>")
        # Test mode with dummy text if no arg provided
        print("\n--- RUNNING IN TEST MODE WITH DUMMY DATA ---")
        dummy_text = "Artificial Intelligence in B2B sales is transforming how companies qualify leads. Instead of manual research, AI agents can scrape data, analyze intent, and personalize outreach at scale. This shifts the SDR role from data entry to relationship management."
        engine = ContentEngine()
        engine.run(dummy_text)
    else:
        engine = ContentEngine()
        engine.run(sys.argv[1])
