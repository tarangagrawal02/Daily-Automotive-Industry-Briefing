import sys
import os
import logging
import json
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from storage.database import Database
from analysis.analyzer import deduplicate_and_filter
from config.settings import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_storage_and_deduplication():
    print("--- TESTING PHASE 3: STORAGE & DEDUPLICATION ---\n")
    
    test_db_path = "test_history.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
        
    db = Database(test_db_path)
    
    # 1. Test URL Deduplication
    print("1. Testing URL Deduplication...")
    test_url = "https://example.com/auto-news-1"
    
    print(f"Is '{test_url}' processed? {db.is_url_processed(test_url)}")
    
    db.insert_story(
        date=datetime.utcnow().isoformat(),
        headline="Company X announces massive EV investment",
        company="Company X",
        topic="Investments",
        geography="Global",
        source="Test Source",
        url=test_url,
        key_facts='["Fact 1", "Fact 2"]',
        strategic_theme="Aggressive EV Push"
    )
    
    print(f"Inserted story. Is '{test_url}' processed now? {db.is_url_processed(test_url)}")
    
    # 2. Test Content/Headline Deduplication
    print("\n2. Testing Headline Deduplication Logic...")
    
    # Mocking analyzed articles batch
    mock_articles = [
        {
            "title": "Company X Announces massive EV investment", # Exact/case-insensitive match to DB
            "url": "https://example.com/auto-news-syndicated",
            "analysis_data": {"is_relevant": True, "topic": "Investments"}
        },
        {
            "title": "Company Y launches new hybrid model in India", # New story
            "url": "https://example.com/company-y",
            "analysis_data": {"is_relevant": True, "topic": "Product Launch"}
        },
        {
            "title": "Company Y LAUNCHES New Hybrid Model in India", # Duplicate within the same batch
            "url": "https://example.com/company-y-duplicate",
            "analysis_data": {"is_relevant": True, "topic": "Product Launch"}
        },
        {
            "title": "Unimportant CEO gossip", # Not relevant
            "url": "https://example.com/gossip",
            "analysis_data": {"is_relevant": False, "topic": "Gossip"}
        }
    ]
    
    print("Batch of incoming articles:")
    for a in mock_articles:
        print(f" - {a['title']} (Relevant: {a['analysis_data']['is_relevant']})")
        
    filtered_stories = deduplicate_and_filter(mock_articles, db)
    
    print("\nFiltered and Deduplicated Stories:")
    for s in filtered_stories:
        print(f" -> {s['title']}")
        
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

if __name__ == "__main__":
    test_storage_and_deduplication()
