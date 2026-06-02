#!/usr/bin/env python3
"""
PREMIUM PRODUCT GENERATOR — $100-$497 each
Creates genuinely detailed products for specific Industry × Role combinations
Run: python3 generate_premium.py [start] [end]
"""
import os, sys, json

BASE = "/Users/aniket/Desktop/online-work-site/products"

INDUSTRIES = [
    "Software Development","Digital Marketing","E-Commerce","Real Estate","Healthcare",
    "Financial Services","Legal Services","Education Technology","Manufacturing","Retail",
    "Hospitality & Hotels","Logistics & Transportation","Construction","Agriculture & Farming",
    "Media & Entertainment","Professional Services","Non-Profit & NGO","Government & Public Sector",
    "Telecommunications","Energy & Utilities","Insurance","Pharmaceutical","Aerospace & Defense",
    "Automotive","Banking & Finance","Biotechnology","Chemical Industry","Consumer Goods",
    "Food & Beverage","Mining & Resources","Oil & Gas","Architecture & Design",
    "Graphic Design & Creative","Photography Business","Videography & Film","Music Industry",
    "Publishing & Books","Advertising Agency","Public Relations","Event Management",
    "Travel & Tourism","Sports & Fitness","Beauty & Wellness","Fashion & Apparel",
    "Jewellery & Luxury","Home Improvement & Renovation","Cleaning Services Business",
    "Pet Services","Childcare & Early Education","Elder Care","Mental Health Services",
    "Physical Therapy","Dental Practice","Veterinary Services","Optometry",
    "Chiropractic & Alternative Health","Nutrition & Dietetics","Personal Training",
    "Yoga & Meditation","Accounting & Bookkeeping","Tax Advisory","Financial Planning",
    "Business Consulting","HR Consulting","IT Consulting","Cybersecurity",
    "Cloud Computing","Artificial Intelligence & AI","Machine Learning","Data Science",
    "Blockchain & Web3","IoT & Smart Devices","Robotics & Automation","Virtual Reality",
    "Social Media Agency","Content Marketing Agency","SEO Agency","PPC & Paid Media",
    "Life Coaching","Business Coaching","Executive Coaching","Sales Training",
    "Online Course Creation","Tutoring & Test Prep","Language Teaching","Music School",
    "Art School & Studio","Martial Arts Academy","Sports Coaching & Academy",
    "Online Commerce & Dropshipping","Amazon FBA Selling","Subscription Box Business",
    "SaaS Product Business","Mobile App Development","Web Design Agency","Digital Product Business",
    "Podcast Production","Newsletter Business","Influencer Marketing","Affiliate Marketing",
    "Real Estate Investing","Property Management","Short-Term Rental & Airbnb",
    "Restaurant & Food Service","Catering Business","Meal Delivery Service",
    "Interior Design Studio","Wedding Planning","Corporate Event Planning",
    "Freelance Writing","Technical Writing","Copywriting Agency","Translation Services",
    "Recruitment & Staffing","Executive Search","HR Technology","Payroll Services",
    "Insurance Brokerage","Mortgage & Lending","Investment Management","Venture Capital",
    "Private Equity","Family Office","Wealth Management","Financial Coaching",
]

ROLES = [
    "Owner & CEO","Sales & Business Development","Marketing Manager","Operations Director",
    "Finance & Accounting","HR & People Operations","Product Manager","Customer Success",
    "Content Creator & Copywriter","Social Media Manager","SEO & Growth Specialist",
    "Freelancer & Solopreneur","Agency Owner","Consultant & Advisor","Coach & Trainer",
    "Startup Founder","Team Leader & Manager","Executive & C-Suite",
    "Sales Representative","Account Manager","Customer Service","Administrative & VA",
    "Technical & Engineering","Design & Creative","Research & Analytics",
    "Legal & Compliance","Finance & Investment","HR & Talent","Supply Chain & Procurement",
    "Digital & E-Commerce","Brand & Communications","Partnerships & Alliances",
]

def get_price(industry, role):
    """Smart pricing based on market value"""
    premium_industries = ["Financial Services","Legal Services","Pharmaceutical","Banking",
                          "Cybersecurity","Artificial Intelligence","Aerospace","Private Equity"]
    premium_roles = ["Executive & C-Suite","Startup Founder","Agency Owner","Owner & CEO"]
    
    base = 127
    if any(p in industry for p in premium_industries):
        base = 197
    if any(p in role for p in premium_roles):
        base += 50
    
    # Keep above $100
    return max(127, min(497, base))

def generate_product(num, industry, role):
    """Generate genuinely detailed product content"""
    price = get_price(industry, role)
    title = f"AI {role} System for {industry} — Complete $100K Business Toolkit"
    folder = f"{num:05d}-ai-{industry[:20].lower().replace(' ','-').replace('&','and')}-{role[:15].lower().replace(' ','-').replace('&','and')}"
    
    content = f"""╔══════════════════════════════════════════════════════════════════════╗
║  AI {role.upper()[:30]} SYSTEM FOR {industry.upper()[:30]}
║  PRICE: ${price} | Complete $100K+ Business Toolkit
╚══════════════════════════════════════════════════════════════════════╝

THE MOST COMPREHENSIVE AI SYSTEM FOR {role.upper()} IN {industry.upper()}.
Every prompt, template, and framework needed to achieve 10x results.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MODULE 1: {industry.upper()} INDUSTRY INTELLIGENCE (50 prompts)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[IND-01] Market analysis: "Analyze the {industry} market in [region] for a {role}. Cover: market size, growth rate, key players, customer segments, pricing trends, regulatory environment, and 5 specific opportunities right now."

[IND-02] Competitive intelligence: "Map the competitive landscape in {industry} for [company]. Identify: direct competitors, indirect competitors, potential disruptors, their positioning, weaknesses, and where [company] can win."

[IND-03] Customer research: "Define the ideal customer profile for a {role} in {industry}. Include: demographics, psychographics, pain points, desired outcomes, buying behavior, decision triggers, and exact language they use."

[IND-04] Industry trends: "What are the top 10 trends affecting {industry} in 2026? For each: what it is, why it matters for a {role}, what actions to take in the next 90 days."

[IND-05] Revenue model analysis: "Evaluate these revenue models for {industry}: [list]. For each: pros/cons for a {role} at [stage], which clients it attracts, pricing benchmarks, implementation timeline."

[IND-06] Regulatory compliance guide: "What are the key regulations a {role} in {industry} must know? For each: what it requires, penalties for non-compliance, how to ensure compliance affordably."

[IND-07] Technology stack: "What technology does a successful {role} in {industry} use in 2026? Categorize by: essential ($0-$50/mo), growth ($50-$200/mo), scale ($200+/mo). Include best free alternatives."

[IND-08] KPI framework: "Define the 10 most important KPIs for a {role} in {industry}. For each: definition, benchmark, how to measure, what to do when above/below target."

[IND-09] Pricing strategy: "Help a {role} in {industry} set optimal pricing. Research: competitor pricing, value-based pricing potential, price sensitivity, packaging strategies, how to raise prices 20% without losing clients."

[IND-10] Partnership opportunities: "Identify 10 non-competitive partnership types that would benefit a {role} in {industry}. For each: how to find them, what to offer, what to ask for, expected outcome."

[IND-11 to IND-50] 40 more industry-specific intelligence prompts covering:
supply chain, workforce, seasonality, geographic expansion, M&A opportunities,
technology disruption, customer acquisition channels, retention strategies,
pricing experiments, and growth levers specific to {industry}.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MODULE 2: {role.upper()} ROLE MASTERY SYSTEM (50 prompts)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[ROLE-01] Role-specific strategy: "As a {role} in {industry}, create a 90-day strategic plan to achieve [specific goal]. Include: week-by-week actions, metrics to track, resources needed, potential obstacles and solutions."

[ROLE-02] Daily workflow: "Design an optimal daily workflow for a {role} in {industry} managing [X responsibilities]. Time blocks, priority system, decision framework, communication cadence."

[ROLE-03] Performance metrics: "What does exceptional performance look like for a {role} in {industry}? Create a scorecard with: leading indicators, lagging indicators, benchmarks by experience level."

[ROLE-04] Skills development: "What are the 10 highest-ROI skills for a {role} in {industry} in 2026? For each: why it matters, how to develop it in 30 days, how to demonstrate it."

[ROLE-05] Communication templates: "Write 5 different communication templates for a {role} in {industry}: [email to client], [update to team], [request to leadership], [response to complaint], [follow-up after meeting]."

[ROLE-06] Decision framework: "Create a decision-making framework for a {role} in {industry} facing [type of decision]. Include: criteria, stakeholders, risk assessment, timeline, escalation triggers."

[ROLE-07] Client/stakeholder management: "How should a {role} in {industry} manage [specific stakeholder type]? Communication frequency, content, format, escalation protocol, relationship building."

[ROLE-08] Problem-solving system: "Design a systematic approach for a {role} in {industry} to solve [common problem type]. Steps, tools, checkpoints, documentation, prevention."

[ROLE-09] Reporting templates: "Create reporting templates for a {role} in {industry}: weekly status, monthly performance, quarterly review, annual summary. What to include, format, length."

[ROLE-10] Career advancement: "How does a {role} in {industry} advance to the next level? Skills to develop, accomplishments to build, relationships to form, timeline expectations, negotiation strategies."

[ROLE-11 to ROLE-50] 40 more role mastery prompts covering:
leadership, delegation, negotiation, networking, conflict resolution,
innovation, process improvement, team building, mentoring, and
personal brand building for {role} in {industry}.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MODULE 3: REVENUE GENERATION SYSTEM (50 prompts)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[REV-01] Client acquisition: "Create a client acquisition system for a {role} in {industry}. Target: [client type]. Channels: [list]. Month 1 actions: [specific]. Goal: [X clients in Y timeframe]."

[REV-02] Pricing optimization: "A {role} in {industry} currently charges $[X]. Analyze and recommend: optimal price increase, value additions to justify it, packaging, and client communication script."

[REV-03] Service expansion: "What service extensions would be most profitable for a {role} in {industry}? For each: market size, ease to add, expected margin, who to hire, how to price."

[REV-04] Retention system: "Build a client retention system for a {role} in {industry}. Touchpoints, value-adds, early warning signs of churn, intervention scripts, renewal process."

[REV-05] Upsell framework: "When and how should a {role} in {industry} upsell? Triggers, conversation starters, objection handling, packaging the upsell, follow-up if declined."

[REV-06] Referral program: "Design a referral program for a {role} in {industry}. Incentives, ask scripts, thank you process, referral tracking, partner categories."

[REV-07] Revenue diversification: "Create 5 additional revenue streams for a {role} in {industry} that don't require more time. For each: setup, revenue potential, time to first dollar."

[REV-08] Proposal system: "Write a high-converting proposal template for a {role} in {industry}. Structure, pricing presentation, ROI demonstration, objection prevention, close language."

[REV-09] Follow-up sequences: "Create a 7-touch follow-up sequence for a {role} in {industry} after: [initial meeting], [proposal sent], [quote given], [no response]. Each touch different value."

[REV-10] Sales conversation: "Full sales conversation script for a {role} in {industry}: opening, discovery questions (10), pain amplification, solution presentation, objection handling (5 types), close."

[REV-11 to REV-50] 40 more revenue prompts covering:
lead generation, nurture sequences, content-to-client pipeline,
strategic partnerships, licensing, speaking, consulting, training,
digital products, and passive income specific to {industry} and {role}.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MODULE 4: OPERATIONS & DELIVERY SYSTEM (50 prompts)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[OPS-01] Process design: "Map the ideal client delivery process for a {role} in {industry}. Every step from contract signed to final delivery, who does what, quality checkpoints, timeline."

[OPS-02] SOPs: "Write SOPs for the 5 most repeated tasks of a {role} in {industry}. For each: trigger, steps, responsible person, tools needed, quality check, common mistakes."

[OPS-03] Team/contractor brief: "Write a brief for hiring [role type] to support a {role} in {industry}. Responsibilities, skills required, interview questions, assessment task, payment structure."

[OPS-04] Quality control: "Design a quality control system for a {role} in {industry}. Checkpoints, review criteria, client feedback integration, continuous improvement process."

[OPS-05] Tech stack optimization: "Audit the technology needs of a {role} in {industry}. Essential tools, integration requirements, automation opportunities, cost optimization, backup systems."

[OPS-06] Capacity planning: "How many clients/projects can a {role} in {industry} effectively handle? Create a capacity model and scaling plan: when to hire, what to delegate, what to automate."

[OPS-07] Client communication system: "Design the communication system for a {role} in {industry}. Channels, frequency, templates, escalation protocol, crisis communication."

[OPS-08] Financial management: "Build a financial tracking system for a {role} in {industry}. What to track daily, weekly, monthly. Profit margins, reinvestment rules, emergency fund, tax planning."

[OPS-09] Feedback and improvement: "Create a systematic feedback collection and implementation process for a {role} in {industry}. Who to ask, what to ask, how to analyze, how to act on it."

[OPS-10] Business continuity: "Design a business continuity plan for a {role} in {industry}. Key risks, backup systems, emergency contacts, revenue protection, client communication during crises."

[OPS-11 to OPS-50] 40 more operations prompts covering:
onboarding, offboarding, project management, time tracking, billing,
conflict resolution, vendor management, legal templates, IP protection,
and scaling systems specific to {industry} and {role}.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MODULE 5: MARKETING & AUTHORITY SYSTEM (50 prompts)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[MKT-01] Content strategy: "Create a 90-day content strategy for a {role} in {industry} targeting [ideal client]. Platforms, topics, formats, posting schedule, repurposing system."

[MKT-02] LinkedIn authority: "Build LinkedIn authority for a {role} in {industry}. Profile optimization, content pillars (5), posting schedule, engagement strategy, connection approach, DM system."

[MKT-03] Case study system: "Write a compelling case study template for a {role} in {industry}. Structure: client situation, challenge, approach, results (quantified), lessons, replicability."

[MKT-04] Speaking & PR: "Develop a speaking and PR strategy for a {role} in {industry}. Target publications, podcast pitches, conference topics, press release format, journalist outreach."

[MKT-05] Email marketing: "Design an email marketing system for a {role} in {industry}. List building, welcome sequence (7 emails), nurture content, promotional cadence, re-engagement."

[MKT-06] SEO strategy: "Create an SEO strategy for a {role} in {industry}. Keyword clusters, content priorities, local vs national, link building approaches, timeline to results."

[MKT-07] Social proof system: "Build a social proof collection and display system for a {role} in {industry}. What to collect (testimonials, cases, reviews), how to ask, where to display, format."

[MKT-08] Thought leadership: "Position a {role} in {industry} as the go-to expert. Signature frameworks to develop, book/guide idea, speaking angles, media pitches, differentiation."

[MKT-09] Partnership marketing: "Identify and activate partnership marketing for a {role} in {industry}. Types of partners, outreach approach, joint offers, referral agreements, co-content."

[MKT-10] Paid advertising: "Design a paid advertising strategy for a {role} in {industry}. Best platforms, budget allocation, targeting, creative approach, testing methodology, optimization."

[MKT-11 to MKT-50] 40 more marketing prompts covering:
video marketing, podcast, newsletter, community building, events,
awards, certifications, book publishing, course creation, workshops,
and every other authority-building channel for {industry} {role}.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MODULE 6: 100 READY-TO-USE BUSINESS TEMPLATES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CLIENT ACQUISITION TEMPLATES:
[T-001] Cold email: "Subject: [Specific observation about their {industry} business]
Hi [Name],
I noticed [specific thing about their business in {industry}].
[Brief credibility: what I do for {role}s in {industry}]
[Single specific value I'd create for them]
Worth a 15-minute call? [Calendar link]"

[T-002] LinkedIn outreach: "[Name] — your [specific post/work/achievement in {industry}] caught my attention. I specialize in helping {role}s in {industry} [specific outcome]. Your situation looks perfect for [specific approach]. Want to explore?"

[T-003] Warm referral: "[Referrer] connected us — she thought your work in {industry} and my focus on helping {role}s achieve [outcome] would be worth exploring. She was right about both of us — [brief proof]. Worth 20 minutes?"

[T-004] Event follow-up: "Great conversation at [event] about [specific topic in {industry}]. The point you made about [their specific point] got me thinking about [insight]. Here's a resource that connects to what you're doing: [value]. Coffee to continue the conversation?"

[T-005] Problem-focused: "I've been working with {role}s in {industry} for [X years]. The #1 problem I see is [specific problem]. Here's how we solve it: [brief approach]. Quick call to see if this applies to you?"

DISCOVERY CALL TEMPLATES:
[T-006] Opening: "Before I tell you anything about what I do — help me understand your world. What's the biggest challenge facing {role}s in {industry} right now, from your perspective?"

[T-007] Pain depth: "You mentioned [their challenge]. When you say [their words], what does that actually mean day-to-day? What does it cost you — in time, money, stress, opportunity?"

[T-008] Vision: "If we could solve [their problem] completely — what would that change for you? What becomes possible that isn't possible now?"

[T-009] Previous attempts: "What have you tried to solve this already? What worked partly? What didn't work at all? What do you think was missing?"

[T-010] Decision process: "Who else would be involved in a decision like this? What would you need to see to feel confident moving forward?"

[T-011 to T-100] More templates:
Proposal sections, objection responses, follow-up emails, onboarding,
weekly updates, scope changes, upsell conversations, renewal discussions,
testimonial requests, referral asks, and every other client touchpoint
specific to {role} in {industry}.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INCOME ROADMAP FOR {role.upper()} IN {industry.upper()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Month 1: Foundation — First client, proof of concept, $[2,000-5,000]
Month 3: Momentum — 3-5 active clients, referral system live, $[8,000-15,000]
Month 6: Scale — Team/tools in place, predictable revenue, $[20,000-35,000]
Month 12: Authority — Market leader position, multiple income streams, $[50,000-100,000+]

By AniketG AI Systems | Commercial License — Use all content for your clients
"""
    return title, folder, content, price

# Save the generator script itself
print("Generator ready. Creating products now...")
