import schedule
import time
import logging
import sys
import os

# Add parent directory to path so we can import from other modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.settings import config
from main import run_pipeline

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def job():
    logging.info("Scheduled job started")
    run_pipeline(is_test=False)
    logging.info("Scheduled job finished")

if __name__ == "__main__":
    send_time = config.SEND_TIME
    logging.info(f"Scheduling Daily Automotive Intelligence Briefing at {send_time} every day (Timezone: {config.TIMEZONE})")
    
    # Simple schedule, relies on the machine's local time matching the desired timezone
    schedule.every().day.at(send_time).do(job)
    
    while True:
        schedule.run_pending()
        time.sleep(60)
