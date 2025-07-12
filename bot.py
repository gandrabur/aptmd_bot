import os
import feedparser
import html
from datetime import datetime, timedelta
from telegram import Bot
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Allowed RSS feeds (politic is excluded)
RSS_FEEDS = {
    "actual": "https://telegraph.md/category/actual/feed/",
    "social": "https://telegraph.md/category/social/feed/",
    "economic": "https://telegraph.md/category/economic/feed/",
    "externe": "https://telegraph.md/category/externe/feed/",
    "lifestyle": "https://telegraph.md/category/lifestyle/feed/",
    "comunicate": "https://telegraph.md/category/comunicate/feed/",
    "opinii": "https://telegraph.md/category/opinii/feed/",
    "parteneriate-media": "https://telegraph.md/category/parteneriate-media/feed/",
    "publicitate": "https://telegraph.md/category/publicitate/feed/"
}

MAX_LENGTH = 4000

def fetch_recent_articles():
    articles = []
    cutoff = datetime.now() - timedelta(minutes=15)
    for category, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if hasattr(entry, 'published_parsed'):
                published = datetime(*entry.published_parsed[:6])
                if published > cutoff:
                    title = html.escape(entry.title.strip())
                    link = entry.link.strip()
                    line = f"• <b><a href='{link}'>{title}</a></b>"
                    articles.append(line)
    return articles

def send_to_telegram(text):
    if text:
        Bot(token=TELEGRAM_TOKEN).send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=text,
            parse_mode="HTML",
            disable_web_page_preview=True
        )

def main():
    items = fetch_recent_articles()
    if not items:
        return

    header = "🗞️ <b>Știrile din ultimul sfert de oră</b>

"
    message = header
    divider = "\n────────────\n"

    for item in items:
        next_piece = item + divider
        if len(message) + len(next_piece) > MAX_LENGTH:
            break
        message += next_piece

    message = message.rstrip(divider)
    send_to_telegram(message.strip())

if __name__ == "__main__":
    main()
