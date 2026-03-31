# 🤖 티스토리 IT/AI 뉴스 자동 포스팅 봇

NewsAPI로 최신 뉴스를 수집하고, Claude AI가 한국어 블로그 포스트로 변환해 티스토리에 자동 업로드합니다.  
GitHub Actions를 통해 **매일 오전 9시** 자동 실행됩니다.

---

## 📁 파일 구조

```
tistory-auto-post/
├── .github/
│   └── workflows/
│       └── auto_post.yml     # GitHub Actions 스케줄
├── main.py                   # 메인 실행 파일
├── news_collector.py         # NewsAPI 뉴스 수집
├── ai_summarizer.py          # Claude AI 블로그 포스트 생성
├── tistory_poster.py         # 티스토리 API 업로드
├── requirements.txt          # Python 의존성
└── posted_urls.json          # 중복 방지 기록 (자동 생성)
```

---

## ⚙️ 초기 설정 (3단계)

### 1단계: API 키 발급

| 서비스 | 발급 URL | 무료 한도 |
|--------|----------|-----------|
| **NewsAPI** | https://newsapi.org/register | 100 req/day |
| **Anthropic (Claude)** | https://console.anthropic.com | 유료 (저렴) |
| **티스토리** | https://www.tistory.com/guide/api/manage/register | 무료 |

### 2단계: 티스토리 Access Token 발급

1. 티스토리 앱 등록 후 `App ID`와 `Secret Key` 확인
2. 브라우저에서 아래 URL 접속 (앱 ID 교체):
```
https://www.tistory.com/oauth/authorize?client_id=YOUR_APP_ID&redirect_uri=https://localhost&response_type=code
```
3. 로그인 후 리다이렉트된 URL에서 `code=` 값 복사
4. 아래 Python 코드로 Access Token 교환:

```python
import requests
res = requests.get("https://www.tistory.com/oauth/access_token", params={
    "client_id": "YOUR_APP_ID",
    "client_secret": "YOUR_SECRET_KEY",
    "redirect_uri": "https://localhost",
    "code": "복사한_CODE",
    "grant_type": "authorization_code"
})
print(res.text)  # access_token=xxxxxxxxxxxx 출력됨
```

### 3단계: GitHub Secrets 등록

레포지토리 → **Settings → Secrets and variables → Actions → New repository secret**

| Secret 이름 | 값 |
|-------------|-----|
| `NEWS_API_KEY` | NewsAPI 키 |
| `ANTHROPIC_API_KEY` | Anthropic API 키 |
| `TISTORY_ACCESS_TOKEN` | 위에서 발급한 토큰 |
| `TISTORY_BLOG_NAME` | 블로그 이름 (`xxx.tistory.com` → `xxx`) |

---

## 🚀 실행 방법

### 자동 실행
GitHub Actions가 **매일 오전 9시(KST)** 자동으로 실행합니다.

### 수동 실행 (테스트)
GitHub 레포 → **Actions 탭 → 🤖 Tistory Auto Post → Run workflow**

### 로컬 테스트
```bash
pip install -r requirements.txt

export NEWS_API_KEY="your_key"
export ANTHROPIC_API_KEY="your_key"
export TISTORY_ACCESS_TOKEN="your_token"
export TISTORY_BLOG_NAME="your_blog"

python main.py
```

---

## ⚙️ 커스터마이즈

### 뉴스 키워드 변경 (`news_collector.py`)
```python
SEARCH_QUERIES = [
    "artificial intelligence",
    "AI chatbot LLM",
    # 원하는 키워드 추가
]
```

### 포스팅 시간 변경 (`auto_post.yml`)
```yaml
- cron: '0 0 * * *'   # UTC 00:00 = KST 09:00
- cron: '0 22 * * *'  # UTC 22:00 = KST 07:00 (아침 7시)
```

### 하루 포스팅 수 변경 (`main.py`)
```python
MAX_POSTS_PER_RUN = 3  # 원하는 수로 변경
```

---

## 📊 비용 예상 (월간)

| 항목 | 무료 한도 | 초과 시 |
|------|-----------|---------|
| NewsAPI | 100 req/day (무료) | $449/month |
| Claude API | - | 포스트당 약 $0.01 |
| GitHub Actions | 2,000 min/month (무료) | $0.008/min |

> 💡 **월 3만원 이하**로 운영 가능합니다.
