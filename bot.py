
import os
import re
import html
import requests
import feedparser
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@dailybankingdose")

RSS_URL = (
    "https://news.google.com/rss/search?"
    "q=RBI+OR+Indian+banking+OR+digital+banking"
    "&hl=en-IN&gl=IN&ceid=IN:en"
)

def clean_text(raw):
    text = html.unescape(raw or "")
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def get_news():
    feed = feedparser.parse(RSS_URL)
    articles = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

    for item in feed.entries:
        try:
            published = parsedate_to_datetime(item.published)

            if published < cutoff:
                continue

            summary = clean_text(
                item.get("summary", "") or
                item.get("description", "")
            )

            source = item.get("source", {}).get(
                "title", "News source"
            )

            articles.append({
                "title": item.title,
                "summary": summary,
                "source": source
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
            "🏦 DAILY BANKING DOSE\n\n"
            "Aaj koi recent news feed mein available nahi hai."
        )
        return

    message = (
        "🏦 DAILY BANKING DOSE\n"
        "📅 " + datetime.now().strftime("%d-%m-%Y") +
        "\n━━━━━━━━━━━━━━━━━━\n\n"
    )

    for i, article in enumerate(articles, 1):

        message += f"📰 NEWS {i}\n\n"
        message += f"📌 {article['title']}\n\n"

        if article["summary"]:
            message += (
                "📖 NEWS SUMMARY:\n"
                + article["summary"][:650]
                + "\n\n"
            )
        else:
            message += (
                "📖 Detailed summary feed mein available nahi hai.\n\n"
            )

        message += f"🏢 Source: {article['source']}\n"
        message += "━━━━━━━━━━━━━━━━━━\n\n"

    message += (
        "🎓 DAILY BANKING DOSE\n"
        "Banking Knowledge | RBI | Current Affairs"
    )

    send_message(message)
    print("Detailed news digest posted successfully!")

if __name__ == "__main__":
    main()
    
