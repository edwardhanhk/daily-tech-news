import os
import requests
import feedparser
from datetime import datetime, timedelta

# 从 GitHub Secrets 读取 Telegram 信息
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def get_hn_top():
    """获取 Hacker News 前 5 条"""
    try:
        rss = feedparser.parse('https://hnrss.org/frontpage')
        items = []
        for i, entry in enumerate(rss.entries[:5]):
            title = entry.title
            link = entry.link
            items.append(f"{i+1}. [{title}]({link})")
        return "\n".join(items)
    except:
        return "❌ Hacker News 抓取失败"

def get_reddit_top(subreddit="technology"):
    """获取 Reddit 某板块前 5 条"""
    try:
        rss = feedparser.parse(f'https://www.reddit.com/r/{subreddit}/top.rss?t=day')
        items = []
        for i, entry in enumerate(rss.entries[:5]):
            # Reddit 标题包含作者信息，需要清理
            title = entry.title.split(': ')[-1] if ': ' in entry.title else entry.title
            link = entry.link
            items.append(f"{i+1}. [{title}]({link})")
        return "\n".join(items)
    except:
        return "❌ Reddit 抓取失败"

def send_telegram_message(text):
    """发送消息到 Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("✅ 消息已发送到 Telegram！")
        else:
            print(f"❌ 发送失败: {response.text}")
    except Exception as e:
        print(f"❌ 发送异常: {e}")

if __name__ == "__main__":
    print("🚀 开始抓取科技热帖...")
    
    hn_news = get_hn_top()
    reddit_news = get_reddit_top("technology")  # 可改为 "programming", "AI" 等
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    message = f"""【每日科技热帖】⏰ {current_time}

🔥 Hacker News Top 5:
{hn_news}

🌐 Reddit r/technology Top 5:
{reddit_news}

---
🤖 由 GitHub Actions 自动推送"""

    send_telegram_message(message)
