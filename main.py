"""
main.py
뉴스 수집 → AI 요약 → 티스토리 포스팅 전체 파이프라인
"""

import os
import time
import json
from datetime import datetime

from news_collector import collect_all_news
from ai_summarizer import generate_post
from tistory_poster import post_article

# 중복 포스팅 방지를 위한 파일
POSTED_URLS_FILE = "posted_urls.json"

# 하루 최대 포스팅 수 (NewsAPI 무료 = 100 req/day 제한 고려)
MAX_POSTS_PER_RUN = 3


def load_posted_urls() -> set:
    """이전에 포스팅한 URL 목록 불러오기"""
    try:
        with open(POSTED_URLS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data.get("urls", []))
    except FileNotFoundError:
        return set()


def save_posted_url(url: str):
    """포스팅 완료된 URL 저장"""
    posted = load_posted_urls()
    posted.add(url)

    # 최근 500개만 유지 (파일 비대화 방지)
    urls_list = list(posted)[-500:]

    with open(POSTED_URLS_FILE, "w", encoding="utf-8") as f:
        json.dump({"urls": urls_list, "updated": datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)


def run():
    print(f"\n{'='*50}")
    print(f"🚀 자동 포스팅 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")

    posted_urls = load_posted_urls()
    print(f"📋 기존 포스팅 URL 수: {len(posted_urls)}개")

    # 1. 뉴스 수집
    articles = collect_all_news(max_total=15)
    if not articles:
        print("⚠️ 수집된 기사가 없습니다. 종료합니다.")
        return

    # 2. 중복 필터링
    new_articles = [a for a in articles if a["url"] not in posted_urls]
    print(f"🆕 새로운 기사: {len(new_articles)}개 (전체 {len(articles)}개 중)")

    if not new_articles:
        print("⚠️ 모든 기사가 이미 포스팅됨. 종료합니다.")
        return

    # 3. AI 요약 + 포스팅
    success_count = 0
    for i, article in enumerate(new_articles):
        if success_count >= MAX_POSTS_PER_RUN:
            print(f"\n✅ 오늘의 목표 {MAX_POSTS_PER_RUN}개 달성! 종료합니다.")
            break

        print(f"\n[{i+1}/{len(new_articles)}] 처리 중...")
        print(f"  제목: {article['title'][:60]}...")
        print(f"  출처: {article['source']}")

        # AI 요약 생성
        post = generate_post(article)
        if not post:
            print("  ⚠️ AI 생성 실패, 다음 기사로 넘어갑니다.")
            continue

        print(f"  📝 생성된 제목: {post['title']}")

        # 티스토리 업로드
        result_url = post_article(post)
        if result_url:
            save_posted_url(article["url"])
            success_count += 1
        
        # API 호출 간격 (티스토리 Rate Limit 방지)
        if i < len(new_articles) - 1:
            print("  ⏳ 30초 대기 중...")
            time.sleep(30)

    print(f"\n{'='*50}")
    print(f"🎉 완료! 총 {success_count}개 포스팅 성공")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    run()
