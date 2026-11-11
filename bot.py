
import os
import requests
import feedparser
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@dailybankingdose")

RSS_URL = (
    "https://news.google.com/rss/search?"
    "q=RBI+OR+banking+India&hl=en-IN&gl=IN&ceid=IN:en"
)

def get_news():
    feed = feedparser.parse(RSS_URL)
    articles = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

    for item in feed.entries:
        try:
            published = parsedate_to_datetime(item.published)
            if published < cutoff:
                continue

            articles.append({
                "title": item.title,
                "link": item.link
            })
        except Exception:
            continue

    return articles[:5]

def send_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": CHANNEL_ID,
            "text": message,
            "disable_web_page_preview": True
        },
        timeout=30
    )
    response.raise_for_status()

def main():
    articles = get_news()

    if not articles:
        send_message(
            "📰 Daily Banking Dose\n\n"
            "Aaj koi verified recent news article nahi mila. "
            "Please check again later."
        )
        return

    message = "🏦 DAILY BANKING DOSE\n"
    message += "📅 " + datetime.now().strftime("%d-%m-%Y") + "\n"
    message += "━━━━━━━━━━━━━━\n\n"

    for i, article in enumerate(articles, 1):
        message += f"{i}. {article['title']}\n"
        message += f"🔗 {article['link']}\n\n"

    message += "━━━━━━━━━━━━━━\n"
    message += "Follow @dailybankingdose"

    send_message(message)
    print("Banking news successfully posted!")

if __name__ == "__main__":
    main()
  
