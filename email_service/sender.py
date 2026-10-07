import requests
import logging
from config.settings import config
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def send_email(html_content, is_test=False):
    """
    Send the generated HTML newsletter via the Resend API.
    """
    api_key = config.RESEND_API_KEY
    sender_email = config.EMAIL_SENDER
    receiver_email = config.EMAIL_RECIPIENT
    
    if not api_key:
        logging.warning("RESEND_API_KEY not set. Cannot send email. Saving to file instead.")
        with open("newsletter_output.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        logging.info("Newsletter saved to newsletter_output.html")
        return False
        
    subject = f"Automotive Intelligence Briefing - {datetime.now().strftime('%b %d, %Y')}"
    if is_test:
        subject = "[TEST] " + subject
        
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "from": f"Automotive Briefing <{sender_email}>",
        "to": [receiver_email],
        "subject": subject,
        "html": html_content
    }
    
    try:
        logging.info("Connecting to Resend API...")
        response = requests.post("https://api.resend.com/emails", json=payload, headers=headers)
        response.raise_for_status()
        logging.info(f"Email sent successfully via Resend to {receiver_email}. Response: {response.json()}")
        return True
    except requests.exceptions.HTTPError as e:
        logging.error(f"Failed to send email via Resend API: {e.response.text}")
        return False
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        return False
