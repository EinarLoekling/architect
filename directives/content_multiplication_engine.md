# Content Multiplication Engine

Build a comprehensive content multiplication workflow that transforms one piece of raw content into multiple high-value assets optimized for different channels.

## Input
- Raw content (transcript, article, podcast notes, or research doc)
- Can be provided as: text file, URL, Google Doc link, or pasted text

## Output Assets (5 total)
1. **Long-form resource** (2000-3000 words) - Lead magnet quality
2. **LinkedIn Post #1** - Thought leadership angle
3. **LinkedIn Post #2** - Tactical/how-to angle  
4. **Nurture Email #1** - Educational/value-first
5. **Nurture Email #2** - Story-driven with soft CTA

## Detailed Requirements

### Phase 1: Content Ingestion & Analysis (Nodes 1-6)
1. Accept input in multiple formats (text, URL, file path, Google Doc)
2. Extract and clean the raw text
3. Identify core topics, themes, and key insights (use Claude for analysis)
4. Extract statistics, quotes, and data points
5. Determine the primary value proposition
6. Create a content brief with: main thesis, supporting points, target audience insights

### Phase 2: Long-Form Resource Creation (Nodes 7-15)
7. Generate outline for comprehensive guide (5-7 sections)
8. Research additional context via web search if needed
9. Write introduction with hook
10. Generate Section 1 with examples
11. Generate Section 2 with case studies or data
12. Generate Section 3 with actionable frameworks
13. Generate Section 4-5 (tactical implementation)
14. Write conclusion with clear next steps
15. Format as professional markdown with:
    - Table of contents
    - Section headers
    - Pull quotes
    - Bullet points for scanability
    - Key takeaways box at end

### Phase 3: LinkedIn Post Generation (Nodes 16-21)
16. Analyze top-performing LinkedIn posts in B2B/AI space for pattern recognition
17. **LinkedIn Post #1 - Thought Leadership:**
    - Hook: Contrarian or surprising insight from content
    - Body: 3-5 short paragraphs building the argument
    - Format: Use line breaks for readability
    - Tone: Authoritative but conversational
    - CTA: Ask a question to drive comments
    - Length: 150-200 words
    - Include 3-5 relevant hashtags
18. **LinkedIn Post #2 - Tactical/How-To:**
    - Hook: Promise a specific outcome
    - Body: 3-5 step framework or checklist
    - Format: Numbered list or clear steps
    - Tone: Helpful, direct, actionable
    - CTA: "Save this for later" or "Tag someone who needs this"
    - Length: 120-180 words
    - Include 3-5 relevant hashtags

### Phase 4: Email Sequence Creation (Nodes 22-28)
19. **Nurture Email #1 - Educational/Value-First:**
    - Subject line: Curiosity-driven, benefit-focused
    - Preview text: Reinforce the value
    - Opening: Acknowledge a pain point or challenge
    - Body: Teach one key concept from the content
    - Include 2-3 concrete examples or mini case studies
    - Soft CTA: Link to full resource or book a call
    - Tone: Peer-to-peer, not salesy
    - Length: 300-400 words
    - P.S. with additional insight or teaser

20. **Nurture Email #2 - Story-Driven:**
    - Subject line: Story hook or transformation promise
    - Preview text: Continue the narrative
    - Opening: Start with a relatable story or scenario
    - Body: Connect story to key insight from content
    - Show before/after or problem/solution
    - Medium CTA: "Here's how we can help" with low-friction offer
    - Tone: Personal, conversational, authentic
    - Length: 250-350 words
    - P.S. with social proof or success metric

### Phase 5: Quality Control & Optimization (Nodes 29-35)
21. Verify all outputs maintain consistent brand voice
22. Check that long-form resource has no AI detection red flags (vary sentence structure, use contractions, include specific examples)
23. Validate LinkedIn posts are mobile-readable (line breaks, emoji usage optional)
24. Ensure emails pass spam filters (check subject lines, avoid trigger words)
25. Generate alternative subject lines for emails (provide 3 options each)
26. Create a content calendar suggestion for publishing sequence
27. Output all assets to organized folders:
    - `/outputs/long-form/[title].md`
    - `/outputs/linkedin/post_1_thought_leadership.txt`
    - `/outputs/linkedin/post_2_tactical.txt`
    - `/outputs/email/nurture_1_educational.txt`
    - `/outputs/email/nurture_2_story.txt`

### Phase 6: Metadata & Tracking (Nodes 36-38)
28. Generate a content summary document with:
    - Source content overview
    - Key themes extracted
    - Target audience profile
    - Suggested publishing schedule
    - Performance tracking template (engagement metrics to monitor)
29. Create a Google Sheet with all content laid out in columns for easy review
30. Generate thumbnail/image suggestions for each asset (text descriptions for designer)

## Technical Requirements

- Use Claude Sonnet 4.5 for all content generation (quality over speed)
- Implement parallel processing where possible (generate LinkedIn posts simultaneously)
- Add validation checks: word counts, formatting, brand voice consistency
- Store intermediate outputs for debugging/iteration
- Self-anneal if content quality is below threshold (regenerate with adjusted prompts)
- Include progress notifications at each phase

## Brand Voice Guidelines for Kineticus
- Direct and concise - no corporate jargon
- Data-driven but not academic
- Authentic - real examples over hypotheticals  
- Charismatic - confident without arrogance
- Trust-first - educate before selling
- Anti-hype - prove with results, not promises

## Success Criteria
All 5 assets should be immediately publishable with minimal editing. The long-form resource should be lead-magnet quality. LinkedIn posts should drive engagement. Emails should feel personal, not automated.
