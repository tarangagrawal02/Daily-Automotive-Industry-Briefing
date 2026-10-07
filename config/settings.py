import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # Email Settings (Using Resend API)
    RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
    EMAIL_SENDER = os.getenv("EMAIL_SENDER", "onboarding@resend.dev")
    EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT", "your_email@example.com")
    
    # Schedule
    TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")
    SEND_TIME = os.getenv("SEND_TIME", "08:00")
    
    # Database
    DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "history.db")
    
    # Other settings
    MAX_STORIES = 10
    
config = Config()
