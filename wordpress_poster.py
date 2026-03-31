"""
wordpress_poster.py
WordPress.com REST API를 사용해 포스트를 업로드합니다.
"""

import os
import requests

WORDPRESS_SITE = os.environ["WORDPRESS_SITE"]
WORDPRESS_USERNAME = os.environ["WORDPRESS_USERNAME"]
WORDPRESS_PASSWORD = os.environ["WORDPRESS_PASSWORD"]

API_BASE = f"https://public-api.wordpress.com/wp/v2/sites/{WORDPRESS_SITE}"


def get_auth_token() -> str:
    """WordPress.com OAuth 토큰 발급"""
    res = requests.post(
        "https://public-api.wordpress.com/oauth2/token",
        data={
            "username": WORDPRESS_USERNAME,
            "password": WORDPRESS_PASSWORD,
            "grant_type": "password",
            "client_id": "0",
            "client_secret": "anonymous",
        },
        timeout=15,
    )
    data = res.json()
    token = data.get("access_token")
    if not token:
        raise Exception(f"토큰 발급 실패: {data}")
    return token


def post_article(post: dict) -> str | None:
    """
    워드프레스에 포스트 업로드
    반환값: 성공 시 포스트 URL, 실패 시 None
    """
    try:
        token = get_auth_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        # 태그 문자열을 리스트로 변환
        tags = [t.strip() for t in post.get("tags", "").split(",") if t.strip()]

        payload = {
            "title": post["title"],
            "content": post["content"],
            "status": "publish",       # 바로 공개
            "tags": tags,
            "categories": [],
            "format": "standard",
        }

        res = requests.post(
            f"{API_BASE}/posts",
            headers=headers,
            json=payload,
            timeout=30,
        )

        result = res.json()

        if res.status_code in (200, 201):
            post_url = result.get("link", "")
            print(f"✅ 포스팅 성공: {post_url}")
            return post_url
        else:
            print(f"❌ 워드프레스 응답 오류 ({res.status_code}): {result}")
            return None

    except Exception as e:
        print(f"❌ 포스팅 요청 실패: {e}")
        return None
