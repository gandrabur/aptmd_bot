import os
import feedparser
import html
import asyncio
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
    cutoff = datetime.now() - timedelta(minutes=15)  # Sau timedelta(hours=3) pentru test
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

async def send_to_telegram(bot: Bot, text):
    if text:
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=text,
            parse_mode="HTML",
            disable_web_page_preview=True
        )

async def main():
    bot = Bot(token=TELEGRAM_TOKEN)
    items = fetch_recent_articles()
    if not items:
        return

    header = "🕒 <b>Știrile din ultimul sfert de oră</b>\n\n"
    message = header
    for item in items:
        if len(message) + len(item) + 1 > MAX_LENGTH:
            break
        message += item + "\n"

    await send_to_telegram(bot, message.strip())

if __name__ == "__main__":
    asyncio.run(main())
