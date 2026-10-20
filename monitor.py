import os
import requests
import feedparser
import json

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
STATE_FILE = "seen_posts.json"

RSS_URL = "https://slickdeals.net/newsearch.php?rss=1&searcharea=deals&searchin=first&q=amazon&rpp=20"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "disable_web_page_preview": False})

def load_seen():
    try:
        with open(STATE_FILE, "r") as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()

def save_seen(seen):
    with open(STATE_FILE, "w") as f:
        json.dump(list(seen), f)

def main():
    feed = feedparser.parse(RSS_URL)
    seen = load_seen()
    new_posts = 0

    for entry in feed.entries:
        if entry.id not in seen:
            title = entry.title.lower()
            if any(k in title for k in ["error", "glitch", "price mistake", "ymmv", "free"]):
                msg = f"🚨 **GLITCH?** 🚨\n\n{entry.title}\n\n{entry.link}"
                send_telegram(msg)
                new_posts += 1
            
            seen.add(entry.id)
    
    if new_posts > 0:
        save_seen(seen)
        print(f"Sent {new_posts} alerts.")
    else:
        print("No new glitches found.")

if __name__ == "__main__":
    main()
