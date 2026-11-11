
import os
import requests
import yfinance as yf
from datetime import datetime

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = "@dailybankingdose"

def get_quote(symbol):
    try:
        data = yf.Ticker(symbol).history(
            period="5d",
            interval="1d"
        )
        data = data.dropna(subset=["Close"])

        if len(data) < 1:
            return None

        latest = float(data["Close"].iloc[-1])
        previous = (
            float(data["Close"].iloc[-2])
            if len(data) > 1 else latest
        )

        change = (
            (latest - previous) / previous * 100
            if previous else 0
        )

        date = data.index[-1].strftime("%d-%m-%Y")

        return {
            "price": latest,
            "change": change,
            "date": date
        }

    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

def format_price(data, decimals=2):
    if data is None:
        return "Data unavailable"

    arrow = "🟢" if data["change"] >= 0 else "🔴"

    return (
        f"₹{data['price']:,.{decimals}f} "
        f"{arrow} {data['change']:+.2f}%"
    )

def main():

    gold = get_quote("GC=F")
    dollar = get_quote("USDINR=X")
    ujjivan = get_quote("UJJIVANSFB.NS")
    nifty = get_quote("^NSEI")
    sensex = get_quote("^BSESN")

    message = (
        "🏦 DAILY BANKING DOSE\n"
        "📅 " + datetime.now().strftime("%d-%m-%Y") +
        "\n━━━━━━━━━━━━━━━━━━\n\n"
        "🥇 GOLD PRICE (24K)\n"
    )

    if gold and dollar:
        gold_inr = gold["price"] * dollar["price"] * 10 / 31.1034768
        message += f"₹{gold_inr:,.0f} / 10 gram (approx.)\n"
    else:
        message += "Data unavailable\n"

    message += (
        "\n🏦 UJJIVAN SMALL FINANCE BANK\n"
        + format_price(ujjivan) +
        "\n\n"
        "📊 NIFTY 50\n"
        + format_price(nifty) +
        "\n\n"
        "📈 SENSEX\n"
        + format_price(sensex) +
        "\n\n"
        "💵 USD / INR\n"
        + (
            f"₹{dollar['price']:.2f}"
            if dollar else "Data unavailable"
        )
        + "\n\n━━━━━━━━━━━━━━━━━━\n"
        "📌 Prices: Latest available daily closing data\n"
        "🥇 Gold: Indicative international rate, not retail quote\n"
        "📚 Stay updated with Daily Banking Dose"
    )

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
    print("Daily market update posted successfully!")

if __name__ == "__main__":
    main()
    
