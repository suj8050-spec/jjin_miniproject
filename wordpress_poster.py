"""
wordpress_poster.py
WordPress.com 전용 REST API v1.1로 포스트를 업로드합니다.
"""

import os
import requests

WORDPRESS_SITE = os.environ["WORDPRESS_SITE"]
WORDPRESS_USERNAME = os.environ["WORDPRESS_USERNAME"]
WORDPRESS_PASSWORD = os.environ["WORDPRESS_PASSWORD"]

# WordPress.com 전용 API (wp-json 아님!)
API_BASE = f"https://public-api.wordpress.com/rest/v1.1/sites/{WORDPRESS_SITE}"


def get_token() -> str:
    """WordPress.com 계정으로 토큰 발급"""
    res = requests.post(
        "https://public-api.wordpress.com/oauth2/token",
        data={
            "username": WORDPRESS_USERNAME,
            "password": WORDPRESS_PASSWORD,
            "grant_type": "password",
            "client_id": "90674",        # WordPress.com 공식 앱 ID
            "client_secret": "Y53xB9sIqHBM1RIQB1EVo1Ip2MVoJLyNBSSKDg5bH8h4e5XKTmXPAovzDFvEaHdA",
        },
        timeout=15,
    )
    data = res.json()
    token = data.get("access_token")
    if not token:
        raise Exception(f"토큰 발급 실패: {data}")
    return token


def post_article(post: dict) -> str | None:
    """WordPress.com에 포스트 업로드"""
    try:
        token = get_token()

        headers = {"Authorization": f"Bearer {token}"}

        payload = {
            "title": post["title"],
            "content": post["content"],
            "status": "publish",
            "tags": post.get("tags", ""),
            "format": "standard",
        }

        res = requests.post(
            f"{API_BASE}/posts/new",
            headers=headers,
            data=payload,
            timeout=30,
        )

        result = res.json()

        if res.status_code in (200, 201) and result.get("ID"):
            post_url = result.get("URL", "")
            print(f"✅ 포스팅 성공: {post_url}")
            return post_url
        else:
            print(f"❌ 워드프레스 응답 오류 ({res.status_code}): {result}")
            return None

    except Exception as e:
        print(f"❌ 포스팅 요청 실패: {e}")
        return None
