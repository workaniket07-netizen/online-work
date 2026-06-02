# Zapier / Make.com Automation Setup

## FOLDER STRUCTURE
```
MARKETING-AUTO/
├── BUSINESS-DATA.md          ← Master data (what we sell)
├── SOCIAL-POSTS-TEMPLATE.md  ← All post templates
├── ZAPIER-SETUP.md           ← This file (automation setup)
├── GENERATED-POSTS/          ← Auto-generated daily posts
└── LOGS/                     ← Posting logs
```

## ZAPIER ZAPS TO BUILD

### Zap 1: Daily Twitter Post
Trigger: Schedule → Every day 9AM
Action 1: Claude API → generate fresh post using BUSINESS-DATA.md
Action 2: Twitter → post tweet
Action 3: Google Sheets → log

### Zap 2: Daily Instagram Caption
Trigger: Schedule → Every day 11AM  
Action 1: Claude API → generate Instagram caption
Action 2: Buffer/Later → schedule Instagram post
Action 3: Log to sheet

### Zap 3: Weekly Reddit Post
Trigger: Schedule → Every Monday 7AM
Action 1: Claude API → generate Reddit post
Action 2: Reddit API → post to r/ChatGPT
Action 3: Log

### Zap 4: New Sale → Email Sequence
Trigger: Polar.sh webhook (new order)
Action 1: Get order details
Action 2: Send welcome email (Email 1)
Action 3: Schedule Email 2 (3 days later)
Action 4: Schedule Email 3 (7 days later)

## CLAUDE API PROMPT FOR DAILY POSTS

```
You are a marketing assistant for AniketG AI, selling AI prompt packs.

BUSINESS: We sell 99,440 specialized AI prompt packs for professionals.
Each pack has 100+ prompts specific to industry + role + country.
Price: $127-$397. Instant digital download. Commercial license.
Store: polar.sh/aniketg-ai

TODAY'S PLATFORM: [Twitter/Instagram/Reddit]
TODAY'S ANGLE: [Problem/Social Proof/Use Case/Value]

Write a high-converting [platform] post for our AI prompt packs.
- Be specific and authentic (not salesy)
- Include 1 clear CTA to polar.sh/aniketg-ai
- Match platform tone (Twitter=punchy, Instagram=visual, Reddit=helpful)
- Include relevant hashtags for Twitter/Instagram
- Length: Twitter=280 chars, Instagram=150 words, Reddit=300 words
```

## MAKE.COM SCENARIO

Module 1: Schedule (daily)
Module 2: HTTP Request → Claude API
  - Method: POST
  - URL: https://api.anthropic.com/v1/messages
  - Headers: x-api-key: [CLAUDE_KEY]
  - Body: {prompt from above}
Module 3: Choose platform (Twitter/Instagram/Reddit by day)
Module 4: Post to platform
Module 5: Log to Google Sheet

## WHAT YOU NEED

1. **Claude API key** → console.anthropic.com
2. **Twitter Developer** → developer.twitter.com
3. **Instagram Business** → through Facebook Business
4. **Reddit App** → reddit.com/prefs/apps
5. **Buffer account** (free) → for scheduling
6. **Google Sheets** → for logging
7. **Zapier/Make.com** → for connecting all

## POLAR.SH WEBHOOK (for sale notifications)

1. polar.sh → Settings → Webhooks → New
2. URL: [Your Zapier webhook URL]
3. Events: order.created
4. This triggers email sequence on every sale

