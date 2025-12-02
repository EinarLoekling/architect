# Content Multiplication Employee

Build a comprehensive AI Content Multiplication Employee that transforms domain expertise into multi-channel marketing assets.

## System Overview

This is an AI employee that takes 2 inputs and produces 3 outputs:

**INPUTS:**
1. Domain expertise (interviews, documents, transcripts, or knowledge dumps)
2. Tone of voice profile (LinkedIn posts, writing samples, or personality description)

**OUTPUTS:**
1. Long-form cornerstone resource (2000-3000 words, lead magnet quality)
2. LinkedIn post (150-200 words, engagement-optimized)
3. Nurture email (300-400 words, value-first with soft CTA)

## Technical Architecture

### Phase 1: Input Processing & Analysis (Nodes 1-8)

**Node 1: Expertise Ingestion**
- Accept multiple formats:
  - Text paste
  - File upload (.txt, .md, .docx, .pdf)
  - Google Doc URL
  - Transcript
  - Audio file (transcribe via Whisper API)
- Store in `/tmp/raw_expertise.txt`

**Node 2: Expertise Extraction**
Using Claude Sonnet 4.5, analyze the expertise input and extract:
- Core thesis/main argument
- 5-7 key insights
- Supporting data points, statistics, case studies
- Tactical frameworks or methodologies
- Common objections and how to address them
- Unique terminology or concepts
- Target audience pain points addressed

Output to: `/tmp/expertise_analysis.json`

**Node 3: Tone of Voice Ingestion**
- Accept multiple formats:
  - LinkedIn profile URL (scrape recent posts)
  - Writing samples (paste or file)
  - Personality description
  - Example posts they've written
- Store in `/tmp/raw_tone.txt`

**Node 4: Tone Analysis**
Using Claude Sonnet 4.5, analyze tone inputs and extract:
- Sentence structure patterns (long vs short, complex vs simple)
- Vocabulary level (technical vs accessible)
- Use of metaphors, analogies, or storytelling
- Formality level (casual, professional, authoritative)
- Use of questions, contractions, exclamations
- Personal vs impersonal voice
- Humor style (if any)
- Opening and closing patterns
- Punctuation habits (em dashes, ellipses, etc.)

Output to: `/tmp/tone_profile.json`

**Node 5: Audience Research**
Based on expertise domain, research:
- Industry pain points
- Common objections
- Trending topics in the space
- Competing content (what's already been said)
- Engagement patterns (what gets likes/comments)

Use web search to gather current context.
Output to: `/tmp/audience_research.json`

**Node 6: Content Strategy Generator**
Synthesize expertise + tone + audience research to create:
- Primary hook angle
- Secondary supporting angles
- Key value propositions
- Credibility builders
- CTA strategy

Output to: `/tmp/content_strategy.json`

### Phase 2: Long-Form Resource Creation (Nodes 7-15)

**Node 7: Resource Outline Generator**
Create comprehensive outline:
- Title (benefit-driven, specific)
- Introduction (hook + promise)
- 5-7 main sections with subsections
- Tactical frameworks or step-by-step processes
- Examples/case studies placement
- Conclusion with clear next steps

Output to: `/tmp/resource_outline.json`

**Node 8: Introduction Writer**
Write compelling introduction (300-400 words):
- Hook that demonstrates understanding of pain point
- Credibility establishment
- Clear promise of what reader will learn
- Brief roadmap of what's covered

**Node 9-13: Section Writers (Parallel Processing)**
For each section in outline:
- Expand into 400-600 words
- Include specific examples
- Add actionable frameworks
- Use subheadings for scanability
- Include relevant data/statistics
- Match tone profile exactly

Process sections in parallel for speed.

**Node 14: Conclusion Writer**
Write powerful conclusion (200-300 words):
- Summarize key takeaways
- Reinforce main value proposition
- Clear next steps
- Soft CTA (offer consultation, more resources, etc.)

**Node 15: Resource Assembler & Formatter**
Combine all sections into final resource:
- Add table of contents
- Format with markdown
- Add visual break suggestions (pull quotes, callout boxes)
- Include "Key Takeaways" box at end
- Optimize for PDF export

Output to: `/outputs/resource_[timestamp].md`

### Phase 3: LinkedIn Post Generation (Nodes 16-20)

**Node 16: Hook Generator**
Create 3 hook options:
- Contrarian/surprising angle
- Question that triggers curiosity
- Bold statement or prediction

Select best based on engagement prediction.

**Node 17: LinkedIn Post Writer**
Write full post (150-200 words):
- Use selected hook
- 3-5 short paragraphs (2-3 sentences each)
- Line breaks for mobile readability
- Match tone profile precisely
- One key insight from resource
- Engagement driver (question, call to action)

**Node 18: Hashtag Generator**
Generate 3-5 relevant hashtags:
- Mix of broad and niche
- Check current usage volume
- Align with content topic

**Node 19: CTA Optimizer**
Create engagement-driving CTA:
- "What's your experience with [X]?"
- "Save this for later"
- "Tag someone who needs this"
- "Drop a 🔥 if you agree"

**Node 20: Post Assembler**
Combine elements:
- Hook
- Body
- CTA
- Hashtags

Output to: `/outputs/linkedin_post_[timestamp].txt`

Also generate:
- Alternative hook options
- Image/visual suggestions
- Best posting time recommendation

### Phase 4: Nurture Email Generation (Nodes 21-27)

**Node 21: Email Strategy Selector**
Determine email angle:
- Educational (teach one concept)
- Story-driven (case study or scenario)
- Problem-solution
- Curiosity-driven

**Node 22: Subject Line Generator**
Create 5 subject line options:
- Benefit-focused
- Curiosity-driven
- Question-based
- Stat/number-driven
- Urgent/timely

Test against spam filters.
Select top 3.

**Node 23: Preview Text Generator**
Create preview text that:
- Reinforces subject line
- Adds additional curiosity
- Feels natural (not salesy)

**Node 24: Email Opening Writer**
Write opening (100-150 words):
- Acknowledge pain point or challenge
- Build rapport (match tone profile)
- Set up value delivery

**Node 25: Email Body Writer**
Write main content (200-250 words):
- Deliver one key insight from resource
- Include specific example or mini case study
- Use short paragraphs (2-3 sentences)
- Match conversational tone

**Node 26: Email CTA & Close**
Create soft CTA:
- Link to full resource
- Offer consultation/call
- Invite reply with questions
- Join community/newsletter

Add P.S. with:
- Additional insight
- Social proof
- Teaser for next email

**Node 27: Email Assembler**
Combine all elements:
- Subject line (with alternatives)
- Preview text
- Opening
- Body
- CTA
- P.S.

Output to: `/outputs/email_[timestamp].txt`
