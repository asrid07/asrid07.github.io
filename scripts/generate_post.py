#!/usr/bin/env python3
"""
TrendPulse Daily - Automatic Blog Post Generator
=================================================
Generates SEO-optimized blog posts across multiple niches,
writes them as Jekyll-compatible markdown files, and commits
them to the repository for automatic GitHub Pages deployment.

Usage:
  python generate_post.py                   # Generate 1 random post
  python generate_post.py --count 3         # Generate 3 posts
  python generate_post.py --category Tech   # Generate post in specific category
  python generate_post.py --dry-run         # Preview without writing files
"""

import os
import re
import random
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================

REPO_ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = REPO_ROOT / "_posts"

CATEGORIES = {
    "Technology": {
        "emoji": "🖥️",
        "topics": [
            ("The Rise of {tech} in {year}: What You Need to Know",
             "{tech} is transforming how we work and live. Here's a comprehensive look at the latest developments and what they mean for you.",
             ["AI and Machine Learning", "Quantum Computing", "Edge Computing", "WebAssembly",
              "Rust Programming", "Kubernetes", "Blockchain 2.0", "5G Applications",
              "AR/VR Technology", "Cybersecurity Mesh", "Low-Code Platforms", "Digital Twins",
              "Autonomous Systems", "Green Tech", "Privacy-First Computing"]),
            ("Top {n} {tech} Tools Every Developer Should Know in {year}",
             "Boost your productivity with these essential {tech} tools that are changing the developer landscape.",
             ["VS Code Extensions", "AI Coding Assistants", "DevOps", "Cloud Native",
              "API Development", "Testing Frameworks", "CI/CD Pipeline", "Database Management",
              "Containerization", "Monitoring and Observability"]),
            ("How {tech} Will Change {industry} Forever",
             "The intersection of {tech} and {industry} is creating unprecedented opportunities. Discover what's happening right now.",
             ["Generative AI", "IoT Sensors", "Computer Vision", "Natural Language Processing",
              "Robotic Process Automation", "Federated Learning", "Neural Networks",
              "Reinforcement Learning", "Transfer Learning", "AutoML"]),
        ],
        "industries": ["Healthcare", "Education", "Finance", "Manufacturing", "Agriculture",
                       "Retail", "Transportation", "Entertainment", "Real Estate", "Energy"],
    },
    "Finance": {
        "emoji": "💰",
        "topics": [
            ("{topic}: A Complete Guide for {year}",
             "Everything you need to know about {topic} to make smarter financial decisions this year.",
             ["Index Fund Investing", "Cryptocurrency Regulations", "Tax-Loss Harvesting",
              "Dividend Growth Strategy", "Real Estate Investment Trusts (REITs)",
              "Peer-to-Peer Lending", "Robo-Advisors Comparison", "Emergency Fund Planning",
              "Debt Avalanche Method", "Retirement Planning for Millennials"]),
            ("Why {topic} Is the Smartest Money Move You Can Make Right Now",
             "In uncertain economic times, {topic} stands out as a reliable strategy for building and protecting wealth.",
             ["SIP Investing", "Gold ETFs", "International Diversification",
              "High-Yield Savings Accounts", "Government Bonds", "Value Investing",
              "Dollar-Cost Averaging", "Tax-Advantaged Accounts", "Budget Automation",
              "Side Income Streams"]),
        ],
    },
    "Health": {
        "emoji": "🏥",
        "topics": [
            ("{topic}: What Science Says in {year}",
             "New research sheds light on {topic}. Here's what the latest studies reveal and how to apply these findings to your life.",
             ["Intermittent Fasting", "Gut Microbiome Health", "Sleep Optimization",
              "High-Intensity Interval Training", "Plant-Based Diets", "Cold Therapy Benefits",
              "Nootropics and Cognitive Enhancement", "Wearable Health Monitors",
              "Mental Health Apps", "Longevity Research", "Stress Hormone Management",
              "Vitamin D Optimization", "Hydration Science"]),
            ("Top {n} Habits for Better {aspect} in {year}",
             "Small changes, big results. These evidence-based habits can dramatically improve your {aspect}.",
             ["Morning Routines", "Meditation Techniques", "Anti-Inflammatory Foods",
              "Posture Correction", "Eye Health in the Digital Age", "Immune System Boosting",
              "Metabolic Health", "Heart Health", "Brain Health"]),
        ],
        "aspects": ["Physical Health", "Mental Wellness", "Sleep Quality", "Energy Levels",
                    "Immune Function", "Cognitive Performance", "Emotional Resilience"],
    },
    "Science": {
        "emoji": "🔬",
        "topics": [
            ("Breakthrough: {topic} Could Change Everything We Know About {field}",
             "Scientists have made a groundbreaking discovery in {field}. Here's why it matters and what comes next.",
             ["CRISPR Gene Editing Advances", "Dark Matter Detection", "Fusion Energy Progress",
              "Mars Colonization Plans", "Quantum Entanglement Applications",
              "Neural Interface Technology", "Synthetic Biology", "Ocean Exploration Drones",
              "Asteroid Mining Feasibility", "Climate Engineering Solutions"]),
            ("{topic}: The Science Behind the Headlines",
             "Cutting through the noise to explain what {topic} really means for humanity's future.",
             ["Gravitational Wave Discoveries", "Exoplanet Habitability", "AI Drug Discovery",
              "Plastic-Eating Enzymes", "Room-Temperature Superconductors",
              "Space Debris Solutions", "Carbon Capture Technology", "Lab-Grown Organs"]),
        ],
        "fields": ["Physics", "Biology", "Space Science", "Medicine", "Environmental Science",
                   "Materials Science", "Neuroscience", "Genetics"],
    },
    "Business": {
        "emoji": "📈",
        "topics": [
            ("{topic}: Lessons for Entrepreneurs in {year}",
             "The business landscape is evolving rapidly. Here are the key {topic} strategies that top founders are using.",
             ["Remote Team Management", "AI-Powered Marketing", "Bootstrapping vs VC Funding",
              "Building in Public", "Creator Economy Monetization", "SaaS Growth Strategies",
              "Personal Branding", "Lean Startup Methodology", "Product-Market Fit",
              "Community-Led Growth", "Subscription Business Models"]),
            ("How to {action} in {year}: A Step-by-Step Guide",
             "Practical, actionable advice on how to {action} — whether you're a beginner or scaling up.",
             ["Start a Profitable Side Business", "Build an Online Course Empire",
              "Launch a Newsletter That Makes Money", "Scale Your Freelance Business",
              "Automate Your Small Business", "Build a Personal Brand on LinkedIn",
              "Create Passive Income Streams", "Negotiate a Higher Salary"]),
        ],
    },
    "Education": {
        "emoji": "📚",
        "topics": [
            ("{topic}: The Best Resources for Self-Learners in {year}",
             "Whether you're picking up a new skill or deepening your expertise, these {topic} resources are the best available.",
             ["Python Programming", "Data Science and Analytics", "UX/UI Design",
              "Digital Marketing", "Cloud Computing Certifications", "Prompt Engineering",
              "Cybersecurity Fundamentals", "Technical Writing", "Open Source Contributing",
              "System Design", "Mobile App Development"]),
            ("Why Learning {skill} in {year} Will Give You a Career Edge",
             "The job market is shifting fast. Here's why {skill} is one of the most valuable skills you can add to your resume.",
             ["AI and Machine Learning", "Data Engineering", "Product Management",
              "Blockchain Development", "DevOps and SRE", "Technical Communication",
              "API Design", "Cloud Architecture", "Sustainability Analytics"]),
        ],
    },
    "Lifestyle": {
        "emoji": "🌍",
        "topics": [
            ("{topic}: Practical Tips for a Better Life in {year}",
             "Simple but powerful changes that can make a real difference in your daily life. Here's our guide to {topic}.",
             ["Minimalist Living", "Digital Nomad Lifestyle", "Sustainable Daily Habits",
              "Productivity Systems That Actually Work", "Building Better Relationships",
              "Time Management for Busy Professionals", "Home Office Optimization",
              "Mindful Consumption", "Travel Hacking on a Budget", "Journaling for Growth"]),
        ],
    },
    "Entertainment": {
        "emoji": "🎬",
        "topics": [
            ("The Best {medium} of {year} So Far: Our Top Picks",
             "From hidden gems to blockbuster hits, here are the {medium} that have captured our attention this year.",
             ["Streaming Shows", "Indie Video Games", "Podcasts", "Documentaries",
              "Anime Series", "Board Games", "Science Fiction Books", "Tech YouTube Channels"]),
            ("How {topic} Is Reshaping Entertainment in {year}",
             "The entertainment industry is being transformed by {topic}. Here's what audiences and creators need to know.",
             ["AI-Generated Content", "Virtual Reality Experiences", "Interactive Storytelling",
              "Cloud Gaming", "Short-Form Video", "AI Music Generation",
              "Deepfake Technology in Film", "Metaverse Events"]),
        ],
    },
}


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')[:80]


def generate_section_content(heading: str, topic: str, category: str) -> str:
    """Generate a detailed section for a blog post."""
    section_templates = [
        f"""
### {heading}

Understanding {topic} requires looking at both the opportunities and challenges it presents. Industry experts have noted significant shifts in how {category.lower()} professionals approach this area.

Key points to consider:

- **Accessibility**: More people than ever can engage with {topic}
- **Scalability**: Solutions in this space are becoming increasingly efficient
- **Integration**: {topic} is connecting with other domains in unexpected ways
- **Sustainability**: Long-term viability is a growing focus area

The data speaks for itself — adoption rates have increased by over 40% in the past year alone, and this trend shows no signs of slowing down.
""",
        f"""
### {heading}

The landscape of {topic} has evolved dramatically. What was once considered cutting-edge is now standard practice, and new innovations continue to push boundaries.

Here's what makes this particularly interesting:

1. **Lower barriers to entry** — Getting started is easier than ever
2. **Community-driven development** — Open collaboration is accelerating progress  
3. **Real-world impact** — Practical applications are multiplying rapidly
4. **Cross-industry potential** — Benefits extend far beyond {category.lower()}

> "The most exciting developments in {topic} are happening at the intersection of different disciplines." — Industry Report, 2026
""",
        f"""
### {heading}

If you're looking to get involved with {topic}, here's a practical roadmap:

**Phase 1: Foundation (Week 1-2)**
- Research current trends and key players
- Identify your specific area of interest
- Join relevant communities and forums

**Phase 2: Development (Week 3-6)**
- Start with hands-on projects or experiments
- Connect with experienced practitioners
- Track your progress and learnings

**Phase 3: Growth (Month 2+)**
- Share your knowledge through content creation
- Collaborate with others in the space
- Explore advanced techniques and strategies

The most successful people in {category.lower()} emphasize that **consistency beats intensity** — showing up regularly matters more than occasional bursts of effort.
""",
    ]
    return random.choice(section_templates)


def generate_post(category: str = None, post_date: datetime = None) -> dict:
    """Generate a complete blog post."""
    if category is None:
        category = random.choice(list(CATEGORIES.keys()))

    if post_date is None:
        post_date = datetime.now()

    cat_data = CATEGORIES[category]
    topic_template = random.choice(cat_data["topics"])
    title_template, desc_template, subjects = topic_template[0], topic_template[1], topic_template[2]

    subject = random.choice(subjects)
    year = post_date.strftime("%Y")
    n = random.choice([5, 7, 8, 10, 12])

    # Build title and description
    replacements = {
        "{tech}": subject, "{topic}": subject, "{year}": year,
        "{n}": str(n), "{skill}": subject, "{medium}": subject,
        "{action}": subject, "{aspect}": random.choice(cat_data.get("aspects", ["overall wellbeing"])),
        "{industry}": random.choice(cat_data.get("industries", ["Multiple Industries"])),
        "{field}": random.choice(cat_data.get("fields", ["Modern Science"])),
    }

    title = title_template
    description = desc_template
    for k, v in replacements.items():
        title = title.replace(k, v)
        description = description.replace(k, v)

    # Generate keywords
    keywords = [subject.lower(), category.lower(), year, "trends",
                f"{category.lower()} {year}", slugify(subject)]

    # Generate article sections
    section_headings = [
        f"Understanding {subject}",
        f"Why {subject} Matters in {year}",
        f"Getting Started with {subject}",
        f"The Future of {subject}",
    ]

    content_sections = []
    for heading in section_headings:
        content_sections.append(generate_section_content(heading, subject, category))

    # Build the full post content
    intro = f"""## Introduction

{description}

In this article, we'll dive deep into **{subject}** — exploring what it is, why it matters, and how you can take advantage of the opportunities it presents in {year}.

Whether you're a seasoned professional or just getting started, there's something here for everyone interested in {category.lower()}.

---
"""

    # Build comparison/data table
    table = f"""
## Quick Facts & Comparison

| Aspect | Current State | Projected Growth |
|--------|--------------|-----------------|
| Adoption Rate | High and accelerating | +35-50% by end of {year} |
| Accessibility | Increasingly mainstream | Universal access trending |
| Investment | Billions in funding | Continued strong growth |
| Job Opportunities | Rapidly expanding | Top skill demand area |
| Community | Thriving and global | Growing international reach |

---
"""

    # Key takeaways
    takeaways = f"""
## Key Takeaways

- **{subject}** is one of the most impactful areas in {category.lower()} right now
- Getting started is more accessible than ever — don't wait for the "perfect" time
- Consistency and continuous learning are the keys to success
- Community engagement accelerates growth and opens doors to opportunities
- The intersection of {category.lower()} and other domains creates unique value

## What's Next?

Stay tuned for more deep dives into {category.lower()} topics. We publish new articles daily covering the latest trends, practical guides, and expert insights.

---

*Did you find this article helpful? Share it with your network and help others stay informed about the latest in {category.lower()}!*
"""

    # Assemble full content
    full_content = intro + "\n".join(content_sections) + table + takeaways

    # Build front matter
    slug = slugify(title)
    filename = f"{post_date.strftime('%Y-%m-%d')}-{slug}.md"

    front_matter = f"""---
layout: post
title: "{title}"
description: "{description}"
date: {post_date.strftime('%Y-%m-%d')}
category: {category}
keywords: [{', '.join(keywords)}]
author: "TrendPulse Team"
reading_time: {random.choice([5, 6, 7, 8, 9, 10])}
---
"""

    return {
        "filename": filename,
        "content": front_matter + full_content,
        "title": title,
        "category": category,
        "date": post_date.strftime('%Y-%m-%d'),
    }


def write_post(post: dict, dry_run: bool = False) -> str:
    """Write a post to the _posts directory."""
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    filepath = POSTS_DIR / post["filename"]

    if filepath.exists():
        print(f"  ⚠️  Skipped (already exists): {post['filename']}")
        return None

    if dry_run:
        print(f"  🔍 [DRY RUN] Would create: {post['filename']}")
        print(f"     Title: {post['title']}")
        print(f"     Category: {post['category']}")
        print(f"     Date: {post['date']}")
        return None

    filepath.write_text(post["content"], encoding="utf-8")
    print(f"  ✅ Created: {post['filename']}")
    return str(filepath)


def get_existing_posts() -> set:
    """Get set of existing post filenames to avoid duplicates."""
    if not POSTS_DIR.exists():
        return set()
    return {f.name for f in POSTS_DIR.glob("*.md")}


def main():
    parser = argparse.ArgumentParser(description="TrendPulse Daily Blog Post Generator")
    parser.add_argument("--count", type=int, default=1, help="Number of posts to generate (default: 1)")
    parser.add_argument("--category", type=str, default=None,
                        help=f"Specific category: {', '.join(CATEGORIES.keys())}")
    parser.add_argument("--dry-run", action="store_true", help="Preview posts without creating files")
    parser.add_argument("--backfill", type=int, default=0,
                        help="Generate posts for the past N days (one per day)")
    args = parser.parse_args()

    print("=" * 60)
    print("🤖 TrendPulse Daily - Auto Blog Generator")
    print("=" * 60)

    existing = get_existing_posts()
    created_files = []

    if args.backfill > 0:
        print(f"\n📅 Backfilling {args.backfill} days of posts...\n")
        for i in range(args.backfill, 0, -1):
            post_date = datetime.now() - timedelta(days=i)
            # Cycle through categories
            categories = list(CATEGORIES.keys())
            cat = categories[i % len(categories)]
            post = generate_post(category=cat, post_date=post_date)
            if post["filename"] not in existing:
                result = write_post(post, dry_run=args.dry_run)
                if result:
                    created_files.append(result)
                existing.add(post["filename"])
    else:
        print(f"\n📝 Generating {args.count} post(s)...\n")
        for i in range(args.count):
            # Stagger dates if generating multiple posts on same day
            post_date = datetime.now() - timedelta(days=i)
            post = generate_post(category=args.category, post_date=post_date)

            # Regenerate if filename collision
            attempts = 0
            while post["filename"] in existing and attempts < 10:
                post = generate_post(category=args.category, post_date=post_date)
                attempts += 1

            if post["filename"] not in existing:
                result = write_post(post, dry_run=args.dry_run)
                if result:
                    created_files.append(result)
                existing.add(post["filename"])
            else:
                print(f"  ⚠️  Could not generate unique post for {post_date.strftime('%Y-%m-%d')}")

    print(f"\n{'=' * 60}")
    print(f"📊 Summary: {len(created_files)} post(s) created")
    if args.dry_run:
        print("   (Dry run - no files were written)")
    print(f"{'=' * 60}\n")

    return created_files


if __name__ == "__main__":
    main()
