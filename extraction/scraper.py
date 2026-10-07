import logging
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_article_content(url, timeout=10):
    """
    Fetch and extract the main text content from a given URL.
    Returns the extracted text, or None if extraction fails.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
    try:
        logging.info(f"Extracting content from: {url}")
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.decompose()
            
        # Extract text from paragraphs
        paragraphs = soup.find_all('p')
        content = "\n".join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])
        
        if not content:
            # Fallback: get all text
            content = soup.get_text(separator='\n', strip=True)
            
        # Truncate content to avoid exceeding LLM token limits (e.g. max 5000 chars)
        return content[:5000]
        
    except requests.exceptions.RequestException as e:
        logging.warning(f"Failed to fetch {url}: {e}")
        return None
    except Exception as e:
        logging.warning(f"Error extracting content from {url}: {e}")
        return None
