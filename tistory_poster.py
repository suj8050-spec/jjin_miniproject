"""
tistory_poster.py
티스토리 Open API를 사용해 포스트를 업로드합니다.
"""

import os
import requests

TISTORY_API_BASE = "https://www.tistory.com/apis"
ACCESS_TOKEN = os.environ["TISTORY_ACCESS_TOKEN"]
BLOG_NAME = os.environ["TISTORY_BLOG_NAME"]


def get_category_id(category_name: str) -> str:
    """블로그 카테고리 목록에서 ID 조회"""
    try:
        res = requests.get(
            f"{TISTORY_API_BASE}/category/list",
            params={
                "access_token": ACCESS_TOKEN,
                "output": "json",
                "blogName": BLOG_NAME,
            },
            timeout=10,
        )
        data = res.json()
        categories = data.get("tistory", {}).get("item", {}).get("categories", [])

        for cat in categories:
            if category_name in cat.get("name", ""):
                return cat["id"]
    except Exception as e:
        print(f"⚠️ 카테고리 조회 실패 (기본값 사용): {e}")

    return "0"  # 기본 카테고리


def post_article(post: dict) -> str | None:
    """
    티스토리에 포스트 업로드
    반환값: 성공 시 포스트 URL, 실패 시 None
    """
    category_id = get_category_id(post.get("category", "IT뉴스"))

    params = {
        "access_token": ACCESS_TOKEN,
        "output": "json",
        "blogName": BLOG_NAME,
        "title": post["title"],
        "content": post["content"],
        "visibility": "3",       # 3 = 전체 공개
        "category": category_id,
        "tag": post.get("tags", "IT뉴스,AI,인공지능"),
        "acceptComment": "1",    # 댓글 허용
    }

    try:
        res = requests.post(
            f"{TISTORY_API_BASE}/post/write",
            params=params,
            timeout=15,
        )
        result = res.json()

        tistory = result.get("tistory", {})
        if str(tistory.get("status")) == "200":
            post_url = tistory.get("url", "")
            print(f"✅ 포스팅 성공: {post_url}")
            return post_url
        else:
            print(f"❌ 티스토리 응답 오류: {result}")
            return None

    except Exception as e:
        print(f"❌ 포스팅 요청 실패: {e}")
        return None
