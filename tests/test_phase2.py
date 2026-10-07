import sys
import os
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from collectors.search import search_news
from extraction.scraper import extract_article_content

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_search_and_extract():
    print("--- TESTING PHASE 2: SEARCH & EXTRACTION ---\n")
    
    # 1. Test Search
    query = "automotive industry"
    print(f"Searching for: '{query}'...")
    articles = search_news(query, max_results=10, max_age_days=2)
    
    if not articles:
        print("No articles found! (DuckDuckGo search might be rate-limited or there is no recent news)")
        return
        
    print(f"\nFound {len(articles)} articles:")
    for i, a in enumerate(articles, 1):
        print(f"{i}. {a['title']} ({a['source']})")
        print(f"   URL: {a['url']}")
        print(f"   Date: {a['published_at']}")
        
    print("\n--- TESTING EXTRACTION ---")
    for a in articles:
        url = a['url']
        print(f"\nExtracting content from: {url}")
        
        content = extract_article_content(url)
        
        if content and len(content) > 100:
            print("\nExtraction Successful! Extracted snippet (first 500 chars):")
            print("-" * 40)
            print(content[:500] + "..." if len(content) > 500 else content)
            print("-" * 40)
            print(f"Total extracted length: {len(content)} characters")
            break
        else:
            print(f"Extraction Failed or returned empty/insufficient content (Length: {len(content) if content else 0}). Trying next...")

if __name__ == "__main__":
    test_search_and_extract()
