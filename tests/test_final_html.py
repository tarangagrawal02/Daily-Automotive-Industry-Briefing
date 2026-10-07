import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import config
from analysis.analyzer import verify_and_analyze_article
from newsletter.generator import generate_newsletter_html
import json

article_content = """
Tesla today announced a massive $2 billion investment to build a new Gigafactory in Gujarat, India. 
The factory will produce a new low-cost EV model aimed at the Indian and Southeast Asian markets, 
with a planned capacity of 500,000 vehicles per year. This marks a major shift in Tesla's global 
expansion strategy and intensifies competition for local players like Tata Motors.
"""

title = "Tesla Announces $2 Billion Investment in New Factory in India"

print("Mocking analysis with Gemini...")
analysis = {
    "is_relevant": True,
    "relevance_reason": "Massive investment in an emerging market indicating a strategic shift.",
    "key_facts": ["$2 billion investment", "New Gigafactory in Gujarat, India", "Production capacity of 500,000 vehicles/year", "Aimed at Indian and Southeast Asian markets"],
    "analysis": "Tesla is moving aggressively to capture the low-cost EV market while diversifying its supply chain away from China.",
    "inference": "This could spark a price war in the Indian EV market and force local incumbents like Tata and Mahindra to accelerate their own EV roadmaps.",
    "company": "Tesla",
    "geography": "India",
    "topic": "Capacity expansion",
    "mba_lens": {
        "concept": "Foreign Direct Investment (FDI) & Localization",
        "explanation": "By investing locally, Tesla reduces tariff burdens, taps into cheaper manufacturing, and tailors products closer to the end consumer."
    },
    "meaningful_numbers": [
         {"metric": "Investment size", "value": "$2 Billion", "context": "Initial capital expenditure for the factory"},
         {"metric": "Production capacity", "value": "500,000", "context": "Annual vehicle production target"}
    ]
}
print(json.dumps(analysis, indent=2))

if analysis:
    mock_story = {
        "title": title,
        "url": "https://example.com/tesla",
        "source": "Reuters",
        "analysis_data": analysis
    }
    
    trend_data = {
        "trend_name": "Shift to Emerging Market Manufacturing",
        "what_is_changing": "Global automakers are moving major production capacity to India to serve both local demand and export to Southeast Asia.",
        "evidence": ["Tesla's $2B Gujarat factory", "Recent expansions by Hyundai"],
        "strategic_significance": "Reduces reliance on China and taps into high-growth markets.",
        "mba_connection": "Foreign Direct Investment and Market Entry Strategy"
    }
    
    html = generate_newsletter_html([mock_story], trend_data)
    with open("newsletter_output.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Generated newsletter_output.html!")
else:
    print("Failed to analyze.")
