import os
import feedparser
import html
import asyncio
from datetime import datetime, timedelta
from telegram import Bot
from telegram.constants import ParseMode
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

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
    cutoff = datetime.utcnow() - timedelta(minutes=30)
    for url in RSS_FEEDS.values():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if hasattr(entry, 'published_parsed'):
                published = datetime(*entry.published_parsed[:6])
                if published > cutoff:
                    title = html.escape(entry.title.strip())
                    link = entry.link.strip()
                    # larger bullet ◉ 
                    articles.append(f"◉ <b><a href='{link}'>{title}</a></b>")
    return articles

async def send_to_telegram(text: str):
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )

async def main():
    items = fetch_recent_articles()
    if not items:
        return

    header = "🕧 <b>Știrile din ultima jumătate de oră</b>\n\n"
    divider = "\n────────────\n"
    message = header

    for item in items:
        chunk = item + divider
        if len(message) + len(chunk) > MAX_LENGTH:
            break
        message += chunk

    # remove trailing divider
    message = message.rstrip(divider)

    # footer in italics with active link
    footer = "\n\n<i>Pentru detalii, accesați <a href='https://telegraph.md'>telegraph.md</a></i>"
    if len(message) + len(footer) <= MAX_LENGTH:
        message += footer

    await send_to_telegram(message.strip())

if __name__ == "__main__":
    asyncio.run(main())
