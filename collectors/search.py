import logging
import requests
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from datetime import datetime, timedelta
from urllib.parse import quote_plus

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def search_news(query, max_results=20, max_age_days=2):
    """
    Search for recent news using Google News RSS feeds.
    """
    logging.info(f"Searching Google News for: {query}")
    results = []
    
    encoded_query = quote_plus(query)
    # Using the US English edition (works fine globally for news aggregation)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        
        # Google News RSS structure: <rss> -> <channel> -> <item>
        items = root.findall('./channel/item')
        
        for item in items[:max_results]:
            title = item.findtext('title')
            link = item.findtext('link')
            source = item.findtext('source')
            pub_date_str = item.findtext('pubDate')
            description = item.findtext('description') or ""
            
            if pub_date_str:
                try:
                    # Parses standard RFC-2822 dates like 'Thu, 03 Oct 2024 10:15:30 GMT'
                    pub_date = parsedate_to_datetime(pub_date_str)
                    
                    # Make it naive UTC for simple comparison
                    if pub_date.tzinfo:
                        pub_date = pub_date.astimezone(None).replace(tzinfo=None)
                        
                    if (datetime.utcnow() - pub_date) <= timedelta(days=max_age_days):
                        results.append({
                            'title': title,
                            'url': link,
                            'source': source,
                            'published_at': pub_date_str,
                            'snippet': description
                        })
                except Exception as e:
                    logging.warning(f"Error parsing date for '{title}': {e}")
                    pass

    except Exception as e:
        logging.error(f"Search failed for query '{query}': {e}")
        
    return results

def get_candidate_articles():
    """
    Run multiple search queries to get candidate articles for global and India automotive news.
    """
    queries = [
        "Indian automotive industry latest",
        "India EV latest",
        "Indian auto companies investments",
        "global automotive industry latest",
        "global EV industry",
        "automaker investments",
        "automotive M&A"
    ]
    
    all_articles = []
    seen_urls = set()
    
    for query in queries:
        articles = search_news(query, max_results=15, max_age_days=2)
        for article in articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                all_articles.append(article)
                
    logging.info(f"Total unique candidate articles found: {len(all_articles)}")
    return all_articles

if __name__ == "__main__":
    articles = get_candidate_articles()
    for a in articles:
        print(a['title'], "-", a['source'])
