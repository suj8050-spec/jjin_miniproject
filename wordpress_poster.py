"""
wordpress_poster.py
WordPress.com REST API를 Basic Auth로 포스트를 업로드합니다.
"""

import os
import requests
from requests.auth import HTTPBasicAuth

WORDPRESS_SITE = os.environ["WORDPRESS_SITE"]
WORDPRESS_USERNAME = os.environ["WORDPRESS_USERNAME"]
WORDPRESS_PASSWORD = os.environ["WORDPRESS_PASSWORD"]

API_BASE = f"https://{WORDPRESS_SITE}/wp-json/wp/v2"


def post_article(post: dict) -> str | None:
    try:
        auth = HTTPBasicAuth(WORDPRESS_USERNAME, WORDPRESS_PASSWORD)

        tags_str = post.get("tags", "")
        tag_names = [t.strip() for t in tags_str.split(",") if t.strip()]

        tag_ids = []
        for tag_name in tag_names:
            res = requests.get(
                f"{API_BASE}/tags",
                params={"search": tag_name},
                auth=auth,
                timeout=10,
            )
            tags_data = res.json()
            if tags_data:
                tag_ids.append(tags_data[0]["id"])
            else:
                res = requests.post(
                    f"{API_BASE}/tags",
                    json={"name": tag_name},
                    auth=auth,
                    timeout=10,
                )
                if res.status_code in (200, 201):
                    tag_ids.append(res.json()["id"])

        payload = {
            "title": post["title"],
            "content": post["content"],
            "status": "publish",
            "tags": tag_ids,
            "format": "standard",
        }

        res = requests.post(
            f"{API_BASE}/posts",
            json=payload,
            auth=auth,
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
