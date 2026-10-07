# Daily Automotive Intelligence Briefing

An automated daily email newsletter focusing on the global and Indian automotive industry, specifically designed for an MBA student.

## Features
- **Search & Collect:** Fetches recent high-impact automotive news.
- **Analysis (LLM):** Uses Gemini API to extract facts, perform strategic analysis, and provide MBA insights.
- **Deduplication:** Uses SQLite to store past stories and avoid duplicates.
- **Trend Detection:** Automatically spots structural trends across multiple news items.
- **Automated Email:** Generates a clean HTML newsletter and sends it via SMTP.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a `.env` file in the root directory (you can copy `.env.example`):
   ```bash
   cp .env.example .env
   ```
3. Fill in your API keys and email details in the `.env` file. Do NOT commit the `.env` file to version control.

## Usage

### Test Mode
To run an end-to-end test without sending an actual email (it will save the output to `newsletter_output.html` if SMTP_PASSWORD is not set):
```bash
python main.py --test-mode
```

### Scheduled Mode
To run the script automatically every day at the time specified in `SEND_TIME` (default is 08:00):
```bash
python scheduler/cron.py
```
