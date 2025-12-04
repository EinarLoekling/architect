import os
import sys
import time
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
import anthropic
import google.generativeai as genai
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# Load environment variables
load_dotenv(Path(__file__).parent.parent / '.env')

class ContentEmployee:
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in .env file")
        
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        if self.google_api_key:
            genai.configure(api_key=self.google_api_key)
        else:
            print("Warning: GOOGLE_API_KEY not found. Deep Research will not work.")

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

    def ingest_content(self, source: str) -> str:
        """Ingests content from a file path or raw text."""
        if source and os.path.exists(source):
            try:
                with open(source, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                print(f"Error reading file {source}: {e}")
                return ""
        return source if source else ""

    def get_research_context(self, research_source: str = None) -> dict:
        """Reads manual research context if provided."""
        if research_source:
            print(f"Node 5: Ingesting manual research from '{research_source}'...")
            content = self.ingest_content(research_source)
            return {"summary": content}
        else:
            print("Node 5: No external research provided. Relying on expertise.")
            return {"summary": "No external research provided. Rely solely on the expertise input."}

    def analyze_inputs(self, expertise_text: str, tone_text: str) -> dict:
        """Phase 1: Analyzes expertise and tone."""
        print("Phase 1: Analyzing inputs...")
        
        # Node 2: Expertise Extraction
        expertise_analysis = self.generate_with_retry(
            "You are an expert analyst.",
            f"Analyze this expertise and extract thesis, key insights, and data:\n{expertise_text[:20000]}"
        )
        
        # Node 4: Tone Analysis
        tone_profile = self.generate_with_retry(
            "You are a linguistic expert.",
            f"Analyze this writing style. Describe sentence structure, vocabulary, and personality:\n{tone_text[:10000]}"
        )
        
        return {
            "expertise": expertise_analysis,
            "tone": tone_profile
        }

    def create_long_form(self, analysis: dict, research: dict):
        """Phase 2: Creates long-form resource with parallel section writing."""
        print("Phase 2: Creating Long-Form Resource...")
        
        # Node 7: Outline
        outline_str = self.generate_with_retry(
            "You are a content strategist.",
            f"""Create a detailed outline for a 2500-word guide based on:
            Expertise: {analysis['expertise']}
            Research/Context: {research['summary']}
            Target Audience: B2B Decision Makers
            
            Return ONLY a JSON object with this structure:
            {{
                "title": "Title",
                "intro_hook": "Hook description",
                "sections": [
                    {{"title": "Section 1 Title", "key_points": ["point 1", "point 2"]}},
                    ...
                ],
                "conclusion_theme": "Theme"
            }}
            """
        )
        
        try:
            # Clean json block
            if "```json" in outline_str:
                outline_str = outline_str.split("```json")[1].split("```")[0]
            elif "```" in outline_str:
                outline_str = outline_str.split("```")[1].split("```")[0]
            outline = json.loads(outline_str)
        except Exception as e:
            print(f"Outline parsing failed: {e}. Using raw text.")
            return

        # Node 8: Intro
        intro = self.generate_with_retry(
            "You are a professional writer.",
            f"Write a 300-word introduction for '{outline['title']}'. Hook: {outline['intro_hook']}. Tone: {analysis['tone']}"
        )

        # Node 9-13: Parallel Section Writing
        print(f"  - Writing {len(outline['sections'])} sections in parallel...")
        sections_content = {}
        
        def write_section(idx, section):
            content = self.generate_with_retry(
                "You are a professional writer.",
                f"""Write Section {idx+1}: '{section['title']}'.
                Key points: {section['key_points']}
                Tone: {analysis['tone']}
                Context: {analysis['expertise']}
                Length: 500 words. Include examples."""
            )
            return idx, f"## {section['title']}\n\n{content}"

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(write_section, i, sec) for i, sec in enumerate(outline['sections'])]
            for future in as_completed(futures):
                idx, content = future.result()
                sections_content[idx] = content

        # Node 14: Conclusion
        conclusion = self.generate_with_retry(
            "You are a professional writer.",
            f"Write a conclusion for '{outline['title']}'. Theme: {outline['conclusion_theme']}. Tone: {analysis['tone']}"
        )

        # Node 15: Assembly
        full_content = f"# {outline['title']}\n\n{intro}\n\n"
        for i in range(len(outline['sections'])):
            full_content += f"{sections_content[i]}\n\n"
        full_content += f"## Conclusion\n\n{conclusion}"
        
        self.save_file(full_content, "resource_guide.md")
        return full_content

    def create_social_assets(self, analysis: dict) -> dict:
        """Phase 3 & 4: Creates LinkedIn and Email assets."""
        print("Phase 3 & 4: Creating Social Assets...")
        
        assets = {}

        # Node 17: LinkedIn Posts (2 versions)
        for i in range(2):
            li_post = self.generate_with_retry(
                "You are a LinkedIn expert.",
                f"""Write LinkedIn Post #{i+1} based on this expertise: {analysis['expertise']}
                Tone: {analysis['tone']}
                Format: Short paragraphs, line breaks.
                Focus: {'Contrarian/Provocative' if i==0 else 'Educational/How-to'}
                Include: Hook, Value, CTA."""
            )
            filename = f"linkedin_post_{i+1}.txt"
            self.save_file(li_post, filename)
            assets[filename] = li_post
        
        # Node 25: Emails (2 versions)
        for i in range(2):
            email = self.generate_with_retry(
                "You are an email marketing expert.",
                f"""Write Nurture Email #{i+1} based on this expertise: {analysis['expertise']}
                Tone: {analysis['tone']}
                Goal: {'Story-driven' if i==0 else 'Actionable Framework'}
                Include: Subject line options."""
            )
            filename = f"nurture_email_{i+1}.txt"
            self.save_file(email, filename)
            assets[filename] = email
            
        return assets

    def perform_deep_research(self, topic: str) -> str:
        """Performs deep research on a topic using Gemini."""
        if not self.google_api_key:
            return "Error: GOOGLE_API_KEY not configured."

        print(f"Performing Deep Research on: {topic}")
        
        # Updated model list to use gemini-flash-latest which is confirmed to work
        models_to_try = ['gemini-flash-latest', 'gemini-1.5-flash-latest', 'gemini-1.5-flash']
        
        last_error = None
        for model_name in models_to_try:
            try:
                print(f"Attempting deep research with model: {model_name}")
                
                # Configure tools for Google Search Grounding
                # Using the standard tool configuration for Google Search
                tools = [{'google_search': {}}]
                
                # Define prompt outside try block to ensure it's available for fallback
                prompt = f"""
                You are an expert researcher with access to Google Search. 
                Conduct a deep dive research on the following topic: "{topic}".
                
                **CRITICAL INSTRUCTION**: Do not provide a generic summary. You must find and cite **specific, high-value signals**.
                
                Use Google Search to find:
                1. **Hard Data & Statistics**: Recent market sizing, growth rates, or survey results (with dates).
                2. **Expert Quotes**: Direct quotes from industry leaders, CTOs, or researchers.
                3. **Primary Sources**: Prioritize PDF reports, white papers, and academic journals over SEO blogs.
                4. **Contrarian Views**: What are the counter-arguments or overlooked risks?
                
                Provide a comprehensive report including:
                - **Executive Summary**: The "So What?" for a B2B decision maker.
                - **Key Trends (Backed by Data)**: Cite specific numbers.
                - **Major Players & Innovators**: Who is winning and why?
                - **Future Outlook (12-24 months)**: Based on expert projections.
                
                Format the output in Markdown. Use bolding for key stats. **Cite every claim with a [Source Name]**.
                """

                try:
                    model = genai.GenerativeModel(model_name, tools=tools)
                    
                    response = model.generate_content(prompt)
                    content = response.text
                    
                    # Save the research
                    filename = f"deep_research_{int(time.time())}.md"
                    self.save_file(content, filename)
                    
                    return content
                    
                except Exception as tool_error:
                    print(f"Tool execution failed for {model_name}: {tool_error}. Retrying without tools...")
                    # Fallback: Try without tools
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt) # Use same prompt, model will do its best
                    content = response.text
                    self.save_file(content, f"deep_research_fallback_{int(time.time())}.md")
                    return content

            except Exception as e:
                print(f"Model {model_name} failed: {e}")
                last_error = e
                continue

        return f"Error: All Gemini models failed. Last error: {str(last_error)}"

    def save_file(self, content: str, filename: str):
        path = self.run_dir / filename
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Saved: {path}")

    def run(self, expertise_source: str, tone_source: str, research_source: str = None):
        print(f"Starting Content Employee (Run ID: {self.run_id})")
        
        # Ingest
        expertise = self.ingest_content(expertise_source)
        tone = self.ingest_content(tone_source)
        
        if not expertise or not tone:
            print("Error: Missing input content.")
            return

        # Analyze
        analysis = self.analyze_inputs(expertise, tone)
        
        # Research (Manual or None)
        research = self.get_research_context(research_source)
        
        # Create
        # Create
        resource_content = self.create_long_form(analysis, research)
        social_assets = self.create_social_assets(analysis)
        
        print(f"\nJob Complete! Assets saved in: {self.run_dir}")
        
        return {
            "resource_guide.md": resource_content,
            **social_assets
        }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AI Content Employee")
    parser.add_argument("--expertise", help="Path to expertise file or text")
    parser.add_argument("--tone", help="Path to tone file or text")
    parser.add_argument("--research", help="Path to optional research/context file", default=None)
    
    args = parser.parse_args()
    
    # Default test mode if no args
    if not args.expertise:
        print("\n--- TEST MODE ---")
        dummy_expertise = "The future of SEO is agentic search. Instead of optimizing for 10 blue links, we need to optimize for AI answers. This means structured data, authoritative sourcing, and direct answers."
        dummy_tone = "I write in a punchy, direct style. I use short sentences. I hate fluff. I'm contrarian but backed by data."
        
        employee = ContentEmployee()
        employee.run(dummy_expertise, dummy_tone)
    else:
        employee = ContentEmployee()
        employee.run(args.expertise, args.tone, args.research)
