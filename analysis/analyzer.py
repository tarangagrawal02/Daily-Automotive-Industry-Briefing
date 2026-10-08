import os
import json
import logging
from config.settings import config
from storage.database import Database
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_gemini():
    api_key = config.GEMINI_API_KEY
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")

def batch_analyze_articles(articles):
    """
    Use Gemini to verify claims, extract facts, analysis, inference, 
    and output a JSON array of structured responses for multiple articles in one call.
    """
    if not articles:
        return {}
        
    api_key = config.GEMINI_API_KEY
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={api_key}"
    
    articles_text = ""
    for article in articles:
        articles_text += f"\n--- ARTICLE {article['id']} ---\nTitle: {article['title']}\nContent:\n{article['content']}\n"
    
    prompt = f"""
    You are an expert automotive industry analyst. 
    Review the following articles.
    
    {articles_text}
    
    Provide your analysis as a JSON array of objects strictly. The array must contain exactly {len(articles)} objects, corresponding to the articles by ID. Do not include markdown code block wrappers (like ```json), just output the raw JSON array.
    
    Format for each object:
    {{
        "id": <integer ID matching the ARTICLE ID>,
        "is_relevant": true/false, 
        "relevance_reason": "Why it's relevant or not based on high-impact strategic significance",
        "key_facts": ["fact 1", "fact 2"],
        "analysis": "Reasonable interpretation based on facts",
        "inference": "A possible strategic implication derived from facts. Use words like 'could', 'may'.",
        "company": "Primary company involved (if any)",
        "geography": "India or Global",
        "topic": "e.g., M&A, EV Strategy, Capacity expansion",
        "mba_lens": {{
            "concept": "Relevant MBA concept (e.g. Economies of scale, Vertical integration)",
            "explanation": "How the concept applies to this news"
        }},
        "meaningful_numbers": [
             {{"metric": "Sales volume", "value": "25,000", "context": "Domestic sales in August"}}
        ]
    }}
    
    Guidelines:
    - Only set "is_relevant" to true if the article is of high strategic importance (investments, M&A, major product shifts).
    - If the article is rumors/speculation, flag it in analysis but if unverified and low impact, set is_relevant to false.
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    import time
    for attempt in range(4):
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            text_response = data['candidates'][0]['content']['parts'][0]['text']
            
            if text_response.startswith("```json"):
                text_response = text_response[7:-3]
            elif text_response.startswith("```"):
                text_response = text_response[3:-3]
                
            results = json.loads(text_response.strip())
            
            # Map back to a dictionary by id
            mapped_results = {item['id']: item for item in results}
            return mapped_results
        except requests.exceptions.HTTPError as e:
            if response.status_code in [429, 503] and attempt < 3:
                try:
                    err_json = response.json()
                    details = err_json.get('error', {}).get('details', [])
                    
                    is_daily_quota = False
                    retry_delay = None
                    
                    for detail in details:
                        if detail.get('@type') == 'type.googleapis.com/google.rpc.QuotaFailure':
                            for violation in detail.get('violations', []):
                                if 'PerDay' in violation.get('quotaId', ''):
                                    is_daily_quota = True
                        if detail.get('@type') == 'type.googleapis.com/google.rpc.RetryInfo':
                            delay_str = detail.get('retryDelay', '')
                            if delay_str.endswith('s'):
                                retry_delay = float(delay_str[:-1])
                                
                    if is_daily_quota:
                        logging.error("Daily quota exhausted. Aborting retries for batch analysis.")
                        return {}
                        
                    wait_time = retry_delay + 2 if retry_delay else 2 ** attempt * 15
                    logging.warning(f"Got {response.status_code}, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                except Exception as parse_e:
                    wait_time = 2 ** attempt * 15
                    logging.warning(f"Got {response.status_code}, retrying in {wait_time}s...")
                    time.sleep(wait_time)
            else:
                logging.error(f"Error analyzing batch: {e}")
                return {}
        except Exception as e:
            logging.error(f"Error analyzing batch: {e}")
            return {}

def deduplicate_and_filter(analyzed_articles, db: Database):
    """
    Filter low relevance and deduplicate using database history.
    """
    filtered = []
    seen_headlines = set()
    
    recent_stories = db.get_recent_stories(days=2)
    recent_headlines = [s['headline'].lower() for s in recent_stories]
    
    for item in analyzed_articles:
        data = item['analysis_data']
        if not data or not data.get('is_relevant'):
            continue
            
        headline = item['title'].lower()
        
        # Simple string matching for deduplication (can be improved with embeddings if needed)
        # Check against current batch
        is_duplicate = False
        for seen in seen_headlines:
            if seen in headline or headline in seen:
                is_duplicate = True
                break
                
        # Check against DB
        for db_headline in recent_headlines:
            if db_headline in headline or headline in db_headline:
                is_duplicate = True
                break
                
        if not is_duplicate:
            seen_headlines.add(headline)
            filtered.append(item)
            
    # Sort by importance or just return top N
    return filtered[:config.MAX_STORIES]
