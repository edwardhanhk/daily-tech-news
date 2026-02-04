import os
import feedparser
from datetime import datetime, timezone
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.dom.minidom

def get_hn_entries():
    """获取 Hacker News 条目"""
    try:
        rss = feedparser.parse('https://hnrss.org/frontpage')
        entries = []
        for entry in rss.entries[:5]:
            entries.append({
                'title': f"[HN] {entry.title}",
                'link': entry.link,
                'published': entry.published,
                'summary': ''
            })
        return entries
    except Exception as e:
        print(f"⚠️ HN 抓取失败: {e}")
        return []

def get_reddit_entries(subreddit="technology"):
    """获取 Reddit 条目"""
    try:
        rss = feedparser.parse(f'https://www.reddit.com/r/{subreddit}/top.rss?t=day')
        entries = []
        for entry in rss.entries[:5]:
            title = entry.title.split(': ')[-1] if ': ' in entry.title else entry.title
            entries.append({
                'title': f"[r/{subreddit}] {title}",
                'link': entry.link,
                'published': entry.published,
                'summary': entry.summary if hasattr(entry, 'summary') else ''
            })
        return entries
    except Exception as e:
        print(f"⚠️ Reddit 抓取失败: {e}")
        return []

def create_rss_feed(entries):
    """生成标准 RSS XML"""
    # 创建根元素
    rss = Element('rss', {'version': '2.0'})
    channel = SubElement(rss, 'channel')
    
    # 频道信息
    SubElement(channel, 'title').text = '每日科技热帖'
    SubElement(channel, 'link').text = 'https://github.com/edwardhanhk/daily-tech-news'
    SubElement(channel, 'description').text = '每日自动抓取 Hacker News 和 Reddit 科技热帖'
    SubElement(channel, 'lastBuildDate').text = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S %z')
    SubElement(channel, 'generator').text = 'GitHub Actions + Python'

    # 添加条目
    for item_data in entries:
        item = SubElement(channel, 'item')
        SubElement(item, 'title').text = item_data['title']
        SubElement(item, 'link').text = item_data['link']
        SubElement(item, 'guid', {'isPermaLink': 'true'}).text = item_data['link']
        SubElement(item, 'pubDate').text = item_data['published']
        if item_data['summary']:
            SubElement(item, 'description').text = item_data['summary']

    # 格式化 XML
    rough_string = tostring(rss, 'unicode')
    reparsed = xml.dom.minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def save_rss_file(content, filename='feed.xml'):
    """保存 RSS 文件到 docs 目录（GitHub Pages 默认目录）"""
    os.makedirs('docs', exist_ok=True)
    with open(f'docs/{filename}', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ RSS 文件已保存: docs/{filename}")

if __name__ == "__main__":
    print("📡 开始生成 RSS 订阅源...")
    
    # 获取所有条目
    hn_items = get_hn_entries()
    reddit_items = get_reddit_entries("technology")
    all_items = hn_items + reddit_items
    
    # 按发布时间排序（最新在前）
    all_items.sort(key=lambda x: x['published'], reverse=True)
    
    # 生成并保存 RSS
    rss_content = create_rss_feed(all_items)
    save_rss_file(rss_content)
