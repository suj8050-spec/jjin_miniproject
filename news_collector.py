"""
news_collector.py
NewsAPI를 사용해 IT/AI 최신 뉴스를 수집합니다.
"""

import os
import requests
from datetime import datetime, timedelta


NEWS_API_KEY = os.environ["NEWS_API_KEY"]
NEWS_API_URL = "https://newsapi.org/v2/everything"

# 수집할 키워드 목록
SEARCH_QUERIES = [
    "artificial intelligence",
    "AI chatbot LLM",
    "machine learning",
    "OpenAI OR Anthropic OR Google AI",
    "반도체 AI",
]


def fetch_articles(query: str, page_size: int = 5) -> list[dict]:
    """NewsAPI로 기사 수집"""
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    params = {
        "q": query,
        "from": yesterday,
        "sortBy": "publishedAt",
        "language": "en",
        "pageSize": page_size,
        "apiKey": NEWS_API_KEY,
    }

    res = requests.get(NEWS_API_URL, params=params, timeout=10)
    res.raise_for_status()
    data = res.json()

    articles = []
    for a in data.get("articles", []):
        # 삭제된 기사 또는 내용 없는 기사 스킵
        if not a.get("title") or a["title"] == "[Removed]":
            continue
        if not a.get("description"):
            continue

        articles.append({
            "title": a["title"],
            "description": a["description"],
            "content": a.get("content", a["description"]),
            "url": a["url"],
            "source": a["source"]["name"],
            "published_at": a["publishedAt"],
            "image_url": a.get("urlToImage", ""),
        })

    return articles


def collect_all_news(max_total: int = 10) -> list[dict]:
    """모든 쿼리에서 뉴스 수집 후 중복 제거"""
    seen_urls = set()
    all_articles = []

    for query in SEARCH_QUERIES:
        try:
            articles = fetch_articles(query, page_size=5)
            for article in articles:
                if article["url"] not in seen_urls:
                    seen_urls.add(article["url"])
                    all_articles.append(article)
        except Exception as e:
            print(f"⚠️ 쿼리 '{query}' 수집 실패: {e}")
            continue

        if len(all_articles) >= max_total:
            break

    print(f"📰 총 {len(all_articles)}개 기사 수집 완료")
    return all_articles[:max_total]
