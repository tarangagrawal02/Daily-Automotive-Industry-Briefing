import logging
import argparse
import sys
from datetime import datetime
import json

from config.settings import config
from collectors.search import get_candidate_articles
from extraction.scraper import extract_article_content
from analysis.analyzer import setup_gemini, batch_analyze_articles, deduplicate_and_filter
from trend_detection.trends import detect_trend
from newsletter.generator import generate_newsletter_html
from email_service.sender import send_email
from storage.database import Database

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_pipeline(is_test=False):
    logging.info("Starting Daily Automotive Intelligence Briefing Pipeline")
    
    try:
        setup_gemini()
    except Exception as e:
        logging.error(f"Failed to setup Gemini API: {e}")
        return
        
    db = Database(config.DB_PATH)
    
    # 1. Search and Collect Candidate Articles
    candidates = get_candidate_articles()
    if not candidates:
        logging.error("No candidate articles found. DuckDuckGo may have rate-limited the IP. Aborting run.")
        sys.exit(1)
        
    # 2. Extract and Prepare for Analysis
    articles_to_analyze = []
    
    for idx, article in enumerate(candidates):
        if db.is_url_processed(article['url']):
            logging.info(f"Skipping already processed URL: {article['url']}")
            continue
            
        content = extract_article_content(article['url'])
        if not content:
            continue
            
        articles_to_analyze.append({
            "id": idx,
            "title": article['title'],
            "content": content,
            "original_article": article
        })
        
    analyzed_articles = []
    if articles_to_analyze:
        logging.info(f"Batch analyzing {len(articles_to_analyze)} articles...")
        # Since we might have 15-20 articles, chunk them in groups of 4 to prevent JSON output truncation from exceeding model output limits
        chunk_size = 4
        for i in range(0, len(articles_to_analyze), chunk_size):
            chunk = articles_to_analyze[i:i+chunk_size]
            batch_results = batch_analyze_articles(chunk)
            
            for idx, item in enumerate(chunk):
                analysis_data = batch_results.get(item['id'])
                if analysis_data:
                    orig_article = item['original_article']
                    orig_article['analysis_data'] = analysis_data
                    analyzed_articles.append(orig_article)
            
    if not analyzed_articles:
        logging.error("No new articles could be analyzed. Aborting run.")
        sys.exit(1)
        
    # 3. Filter and Deduplicate
    final_stories = deduplicate_and_filter(analyzed_articles, db)
    
    MIN_STORIES = 2
    if len(final_stories) < MIN_STORIES:
        logging.error(f"Only {len(final_stories)} usable stories found. Minimum required is {MIN_STORIES}. Aborting run.")
        sys.exit(1)
        
    logging.info(f"Selected {len(final_stories)} high-impact stories.")
    
    # 4. Save to Database
    for story in final_stories:
        data = story['analysis_data']
        # Convert key_facts list to JSON string for storage
        key_facts_str = json.dumps(data.get('key_facts', []))
        
        db.insert_story(
            date=datetime.utcnow().isoformat(),
            headline=story['title'],
            company=data.get('company', ''),
            topic=data.get('topic', ''),
            geography=data.get('geography', ''),
            source=story['source'],
            url=story['url'],
            key_facts=key_facts_str,
            strategic_theme=data.get('inference', '')
        )
        
    # 5. Trend Detection
    recent_stories_db = db.get_recent_stories(days=7)
    trend_data = detect_trend(recent_stories_db, final_stories)
    if trend_data:
        logging.info(f"Detected trend: {trend_data.get('trend_name')}")
        
    # 6. Generate Newsletter
    html_content = generate_newsletter_html(final_stories, trend_data)
    
    # 7. Send Email
    success = send_email(html_content, is_test=is_test)
    if success:
        logging.info("Pipeline completed successfully.")
    else:
        logging.error("Failed to send email via Resend. Aborting workflow.")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automotive Intelligence Briefing")
    parser.add_argument("--test-mode", action="store_true", help="Run in test mode (does not send real emails if not configured)")
    args = parser.parse_args()
    
    run_pipeline(is_test=args.test_mode)
