import os
import feedparser
import html
from datetime import datetime, timedelta
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

FEEDS = [
    "https://telegraph.md/category/actual/feed/",
    "https://telegraph.md/category/social/feed/",
    "https://telegraph.md/category/economic/feed/",
    "https://telegraph.md/category/externe/feed/",
    "https://telegraph.md/category/lifestyle/feed/",
    "https://telegraph.md/category/comunicate/feed/",
    "https://telegraph.md/category/opinii/feed/",
    "https://telegraph.md/category/parteneriate-media/feed/",
    "https://telegraph.md/category/publicitate/feed/"
]

MAX_LENGTH = 4000

def fetch_recent_articles():
    articles = []
    cutoff = datetime.now() - timedelta(minutes=15)
    for url in FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if hasattr(entry, 'published_parsed'):
                published = datetime(*entry.published_parsed[:6])
                if published > cutoff:
                    title = html.escape(entry.title.strip())
                    link = entry.link.strip()
                    article_line = f"• <b><a href='{link}'>{title}</a></b>"
                    articles.append(article_line)
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

    header = "🕒 <b>Știrile din ultimul sfert de oră</b>\n\n"
    message = header
    for item in items:
        # Check before adding the next item to stay under the character limit
        if len(message) + len(item) + 1 > MAX_LENGTH:
            break
        message += item + "\n"

    send_to_telegram(message.strip())

if __name__ == "__main__":
    main()
