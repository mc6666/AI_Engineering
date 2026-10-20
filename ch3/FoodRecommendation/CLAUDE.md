# YouTuber 美食推薦系統 — Django 實作計畫

## Context
第3章 SDD 書籍範例：使用 Claude AI 根據 YouTuber 風格推薦台灣美食。
多人使用 = 無需登入，任何人皆可直接使用（匿名、無狀態）。

---

## 專案規格
- Stack: Django 6.0.3、anthropic SDK、python-dotenv、SQLite
- Model: `claude-haiku-4-5-20251001`
- Locale: `zh-hant`、時區 `Asia/Taipei`
- 6 位預設台灣美食 YouTuber：愛莉莎莎、台客劇場、喜翔、蔡阿嘎、滴妹、Edwin 吃什麼
- UI: Bootstrap 5 CDN（無需 collectstatic）

---

## 資料夾結構

```
FoodRecommendation/
├── manage.py
├── requirements.txt
├── .env                         ← ANTHROPIC_API_KEY、SECRET_KEY
├── food_recommendation/         ← 專案 package
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── recommender/                 ← 唯一應用程式（單 app，簡潔為主）
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── services.py              ← Claude API 呼叫（thin views 原則）
│   ├── urls.py
│   ├── views.py
│   ├── management/
│   │   └── commands/
│   │       └── seed_youtubers.py  ← 預填 6 位 YouTuber 資料
│   └── templates/
│       └── recommender/
│           ├── base.html        ← Bootstrap 5 CDN navbar + footer
│           ├── index.html       ← 首頁：選 YouTuber + 輸入需求
│           └── result.html      ← Claude 回應結果
└── db.sqlite3                   ← 自動產生
```

---

## 資料模型（`recommender/models.py`）

```python
class YouTuber(models.Model):
    name            = models.CharField(max_length=100)        # 顯示名稱
    channel_name    = models.CharField(max_length=200)        # 頻道名
    youtube_url     = models.URLField(blank=True)
    description     = models.TextField()                      # 風格描述（餵給 Claude）
    style_keywords  = models.CharField(max_length=300)        # 逗號分隔關鍵字

class FoodSuggestion(models.Model):
    session_key     = models.CharField(max_length=40)         # 匿名多人識別
    youtubers       = models.ManyToManyField(YouTuber)
    user_query      = models.TextField()                      # 使用者輸入需求
    ai_response     = models.TextField()                      # Claude 回應
    created_at      = models.DateTimeField(auto_now_add=True)
```

`FoodSuggestion` 以 `session_key`（Django 匿名 session）識別不同使用者，不需帳號系統。

---

## URL 設計（`recommender/urls.py`）

| 路徑 | View | 說明 |
|------|------|------|
| `/` | `IndexView` | GET：首頁（YouTuber 選單 + 查詢表單） |
| `/suggest/` | `SuggestView` | POST：呼叫 Claude，回傳結果 |
| `/history/` | `HistoryView` | GET：顯示本 session 的查詢記錄 |

---

## Views（`recommender/views.py`）

- **`IndexView(TemplateView)`**：`get_context_data` 注入全部 YouTuber 供 checkbox 選擇
- **`SuggestView(View)`**：
  1. POST 取得 `youtuber_ids[]` 與 `user_query`
  2. 呼叫 `services.get_suggestions(youtubers, query)` → 取得 Claude 回應
  3. 將結果存入 `FoodSuggestion`（含 `request.session.session_key`）
  4. redirect 到 `result.html` 顯示回應
- **`HistoryView(ListView)`**：過濾 `FoodSuggestion.session_key == request.session.session_key`

---

## Claude AI 整合（`recommender/services.py`）

```python
import anthropic
from django.conf import settings

def get_suggestions(youtubers: list, user_query: str) -> str:
    yt_context = "\n".join(
        f"- {yt.name}（{yt.channel_name}）：{yt.description}  關鍵字：{yt.style_keywords}"
        for yt in youtubers
    )
    prompt = f"""你是一位熟悉台灣美食的推薦助理。
以下是使用者選擇的 YouTuber 風格資訊：
{yt_context}

使用者需求：{user_query}

請根據上述 YouTuber 的推薦風格，提供 3~5 道具體的台灣美食建議，
包含：食物名稱、建議餐廳或地點、為何符合該 YouTuber 風格。
請用繁體中文回答。"""

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return next(b.text for b in response.content if b.type == "text")
```

---

## 預填資料（`seed_youtubers` 管理命令）

執行 `python manage.py seed_youtubers` 一次性插入 6 位 YouTuber：

| name | style_keywords 範例 |
|------|---------------------|
| 愛莉莎莎 | 網紅打卡、外觀精緻、甜點 |
| 台客劇場 | 在地小吃、古早味、平價 |
| 喜翔 | 海鮮、台南、在地人推薦 |
| 蔡阿嘎 | 搞笑、台式、巷弄小店 |
| 滴妹 | 日系、飲料、文青風格 |
| Edwin 吃什麼 | 燒肉、火鍋、高單價 |

---

## requirements.txt

```
Django==6.0.3
anthropic==0.50.0
python-dotenv==1.1.0
```

---

## settings.py 重點設定

```python
from dotenv import load_dotenv
load_dotenv()

LANGUAGE_CODE = 'zh-hant'
TIME_ZONE = 'Asia/Taipei'
ANTHROPIC_API_KEY = os.environ['ANTHROPIC_API_KEY']
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # 匿名 session 存 DB
```

---

## 驗證方式

1. `pip install -r requirements.txt`
2. 建立 `.env`（含 `SECRET_KEY` 與 `ANTHROPIC_API_KEY`）
3. `python manage.py migrate`
4. `python manage.py seed_youtubers`
5. `python manage.py runserver` → http://127.0.0.1:8000/
6. 勾選 2~3 位 YouTuber，輸入「想吃點什麼」，驗證 Claude 回應是否符合 YouTuber 風格
7. 開不同瀏覽器（或無痕模式），確認 `/history/` 只顯示各自的查詢記錄（session 隔離）
