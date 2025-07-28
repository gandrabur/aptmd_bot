import os
import feedparser
import html
import asyncio
from datetime import datetime, timedelta, timezone
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
    "publicitate": "https://telegraph.md/category/publicitate/feed/",
    "politic": "https://telegraph.md/category/politic/feed/"
}

MAX_LENGTH = 4000
RECENT_FILE = "recent_articles.txt"
RECENT_WINDOW = timedelta(minutes=60)

def load_recent_links():
    recent_links = set()
    now = datetime.now(timezone.utc)

    if os.path.exists(RECENT_FILE):
        with open(RECENT_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    timestamp_str, link = line.strip().split(" ", 1)
                    timestamp = datetime.fromisoformat(timestamp_str)
                    if now - timestamp <= RECENT_WINDOW:
                        recent_links.add(link)
                except Exception:
                    continue
    return recent_links

def save_new_links(links):
    now = datetime.now(timezone.utc)
    lines = []

    # Păstrăm doar linkurile valabile (nu mai vechi de 60 min)
    if os.path.exists(RECENT_FILE):
        with open(RECENT_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    timestamp_str, link = line.strip().split(" ", 1)
                    timestamp = datetime.fromisoformat(timestamp_str)
                    if now - timestamp <= RECENT_WINDOW:
                        lines.append(f"{timestamp_str} {link}")
                except Exception:
                    continue

    # Adăugăm linkurile noi
    for link in links:
        lines.append(f"{now.isoformat()} {link}")

    with open(RECENT_FILE, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")

def fetch_recent_articles():
    articles = []
    new_links = []
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=30)
    recent_links = load_recent_links()

    for url in RSS_FEEDS.values():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if hasattr(entry, "tags"):
                tag_list = [tag.term.lower() for tag in entry.tags if hasattr(tag, "term")]
                if "teloff" in tag_list:
                    continue

            if hasattr(entry, 'published_parsed'):
                published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                if published > cutoff:
                    link = entry.link.strip()
                    if link in recent_links:
                        continue
                    title = html.escape(entry.title.strip())
                    articles.append(f"◉ <b><a href='{link}'>{title}</a></b>")
                    new_links.append(link)

    return articles, new_links

async def send_to_telegram(text: str):
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )

async def main():
    items, new_links = fetch_recent_articles()
    if not items:
        return

    header = "🕧 <b>Știrile din ultima jumătate de oră</b>\n\n"
    divider = "\n──\n"
    message = header

    for item in items:
        chunk = item + divider
        if len(message) + len(chunk) > MAX_LENGTH:
            break
        message += chunk

    message = message.rstrip(divider)

    footer = "\n\n<i>Pentru detalii, accesați <a href='https://telegraph.md'>telegraph.md</a></i>"
    if len(message) + len(footer) <= MAX_LENGTH:
        message += footer

    await send_to_telegram(message.strip())
    save_new_links(new_links)

if __name__ == "__main__":
    asyncio.run(main())
