
import os
import feedparser
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
POSTED_LOG = "posted.log"

FEED_URLS = [
    "https://telegraph.md/category/actual/feed/",
    "https://telegraph.md/category/social/feed/",
    "https://telegraph.md/category/economic/feed/",
    "https://telegraph.md/category/externe/feed/",
    "https://telegraph.md/category/lifestyle/feed/",
    "https://telegraph.md/category/comunicate/feed/",
    "https://telegraph.md/category/opinii/feed/",
    "https://telegraph.md/category/parteneriate-media/feed/",
    "https://telegraph.md/category/publicitate/feed/",
]

def load_posted():
    if not os.path.exists(POSTED_LOG):
        return set()
    with open(POSTED_LOG, "r") as f:
        return set(line.strip() for line in f)

def save_posted(link):
    with open(POSTED_LOG, "a") as f:
        f.write(link + "\n")

def send_to_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    response = requests.post(url, data=data)
    return response.status_code == 200

def format_entry(entry):
    title = entry.get("title", "")
    link = entry.get("link", "")
    return f"<b>{title}</b>\n<a href='{link}'>Citește mai mult</a>"

def main():
    posted = load_posted()
    for feed_url in FEED_URLS:
        parsed = feedparser.parse(feed_url)
        for entry in parsed.entries:
            link = entry.link
            if link not in posted:
                msg = format_entry(entry)
                if send_to_telegram(msg):
                    save_posted(link)

if __name__ == "__main__":
    main()
