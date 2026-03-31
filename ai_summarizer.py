"""
ai_summarizer.py
Claude API를 사용해 뉴스를 한국어 블로그 포스트로 변환합니다.
"""

import json
import re
import anthropic

client = anthropic.Anthropic()  # ANTHROPIC_API_KEY 환경변수 자동 사용


BLOG_POST_PROMPT = """
당신은 IT/AI 전문 블로거입니다. 아래 영문 뉴스를 바탕으로 한국 독자를 위한 블로그 포스트를 작성하세요.

[원문 정보]
제목: {title}
내용: {content}
출처: {source}
원문 링크: {url}

[작성 요구사항]
1. **제목**: SEO를 고려한 한국어 제목 (30자 내외, 핵심 키워드 포함)
2. **본문 구성** (HTML 형식, 총 800~1200자):
   - 🔍 핵심 요약: 3~4문장으로 이 뉴스가 무엇인지 설명
   - 📌 주요 내용: 3~5개 bullet point로 세부 내용 정리
   - 💡 AI 전문가 코멘트: 이 뉴스가 업계/사용자에게 미치는 영향 분석 (2~3문장)
   - 🔗 원문 보기 링크 포함
3. **말투**: 친근하고 전문적인 IT 블로거 스타일 (~했습니다 체)
4. **태그**: 관련 한국어 키워드 5~7개 (쉼표 구분)
5. **카테고리**: IT뉴스 / AI / 테크 중 가장 적합한 것

반드시 아래 JSON 형식으로만 응답하세요 (다른 텍스트 없이):
{{
  "title": "한국어 SEO 제목",
  "content": "<div class=\\"post-content\\">...HTML 본문...</div>",
  "tags": "AI, 인공지능, 키워드1, 키워드2, 키워드3",
  "category": "AI"
}}
"""


def generate_post(article: dict) -> dict | None:
    """Claude API로 블로그 포스트 생성"""
    prompt = BLOG_POST_PROMPT.format(
        title=article["title"],
        content=article["content"][:1000],  # 토큰 절약
        source=article["source"],
        url=article["url"],
    )

    try:
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=2500,
            messages=[{"role": "user", "content": prompt}],
        )

        raw = response.content[0].text.strip()

        # JSON 파싱 (마크다운 코드블록 제거)
        raw = re.sub(r"```json\s*|\s*```", "", raw).strip()
        post = json.loads(raw)

        # 원문 링크와 출처 정보 본문에 추가
        source_block = f"""
<hr>
<p style="font-size:0.85em; color:#666;">
  📡 출처: <strong>{article['source']}</strong> | 
  <a href="{article['url']}" target="_blank" rel="noopener">원문 보기 →</a>
  <br>원문 발행일: {article['published_at'][:10]}
</p>
"""
        post["content"] += source_block
        post["original_url"] = article["url"]
        return post

    except json.JSONDecodeError as e:
        print(f"❌ JSON 파싱 실패: {e}\n원본 응답: {raw[:200]}")
        return None
    except Exception as e:
        print(f"❌ AI 생성 실패: {e}")
        return None
