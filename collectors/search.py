import logging
from duckduckgo_search import DDGS
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def search_news(query, max_results=20, max_age_days=2):
    """
    Search for recent news using DuckDuckGo.
    """
    logging.info(f"Searching for: {query}")
    results = []
    
    try:
        with DDGS() as ddgs:
            ddgs_news = ddgs.news(query, max_results=max_results)
            if not ddgs_news:
                return results
                
            for item in ddgs_news:
                # date format from DDG news: usually '2023-11-20T14:48:00+00:00'
                pub_date_str = item.get("date")
                
                try:
                    # Clean up the string to standard ISO format without Z if needed
                    if pub_date_str:
                        pub_date_str = pub_date_str.replace("Z", "+00:00")
                        pub_date = datetime.fromisoformat(pub_date_str)
                        # Remove timezone info for simple comparison
                        pub_date = pub_date.replace(tzinfo=None)
                        
                        if (datetime.utcnow() - pub_date) <= timedelta(days=max_age_days):
                            results.append({
                                'title': item.get('title'),
                                'url': item.get('url'),
                                'source': item.get('source'),
                                'published_at': item.get('date'),
                                'snippet': item.get('body')
                            })
                except Exception as e:
                    logging.warning(f"Error parsing date for '{item.get('title')}': {e}")
                    # If date parsing fails, include it just in case, or we could skip it.
                    # We will skip it to maintain recency strictly.
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
