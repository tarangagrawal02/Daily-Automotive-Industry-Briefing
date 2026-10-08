import logging
import json
from config.settings import config
from storage.database import Database
from google import genai
from google.genai.errors import APIError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def detect_trend(recent_stories, today_stories):
    """
    Use Gemini to detect a macro trend based on recent and today's stories.
    """
    api_key = config.GEMINI_API_KEY
    if not api_key:
        return None
        
    client = genai.Client(api_key=api_key)
    
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
    
    import time
    for attempt in range(4):
        try:
            interaction = client.interactions.create(
                model="gemini-3.8-flash",
                input=prompt
            )
            
            text_response = interaction.output_text
            
            if text_response.startswith("```json"):
                text_response = text_response[7:-3]
            elif text_response.startswith("```"):
                text_response = text_response[3:-3]
                
            result = json.loads(text_response.strip())
            return result if result.get("trend_name") else None
            
        except APIError as e:
            if e.code in [429, 503] and attempt < 3:
                wait_time = 2 ** attempt * 15
                logging.warning(f"Got API error {e.code}, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                logging.error(f"Error detecting trend: {e}")
                return None
        except Exception as e:
            logging.error(f"Error detecting trend: {e}")
            return None

    return None
