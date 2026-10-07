import logging
import json
import google.generativeai as genai
from config.settings import config
from storage.database import Database

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

import requests

def detect_trend(recent_stories, today_stories):
    """
    Use Gemini to detect a macro trend based on recent and today's stories.
    """
    api_key = config.GEMINI_API_KEY
    if not api_key:
        return None
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={api_key}"
    
    # Combine titles and themes
    all_context = []
    for s in today_stories:
        all_context.append(f"- [TODAY] {s['title']} ({s['analysis_data'].get('topic', '')})")
    for s in recent_stories:
        all_context.append(f"- [RECENT] {s['headline']} ({s['topic']})")
        
    context_str = "\n".join(all_context)
    
    prompt = f"""
    You are an expert automotive industry strategist.
    Based on the following recent news events, identify ONE significant structural trend emerging.
    
    Events:
    {context_str}
    
    Provide your response in the following JSON format strictly:
    {{
        "trend_name": "Name of the trend",
        "what_is_changing": "2-4 sentences explaining what is changing",
        "evidence": ["Example 1 from events", "Example 2 from events"],
        "strategic_significance": "Why this matters to automotive companies",
        "mba_connection": "Relevant strategy/business concept"
    }}
    
    If there is not enough evidence to support a macro trend, return an empty JSON object: {{}}
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
                
            result = json.loads(text_response.strip())
            return result if result.get("trend_name") else None
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
                        logging.error("Daily quota exhausted. Aborting retries for trend detection.")
                        return None
                        
                    wait_time = retry_delay + 2 if retry_delay else 2 ** attempt * 15
                    logging.warning(f"Got {response.status_code}, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                except Exception as parse_e:
                    wait_time = 2 ** attempt * 15
                    logging.warning(f"Got {response.status_code}, retrying in {wait_time}s...")
                    time.sleep(wait_time)
            else:
                logging.error(f"Error detecting trend: {e}")
                return None
        except Exception as e:
            logging.error(f"Error detecting trend: {e}")
            return None
