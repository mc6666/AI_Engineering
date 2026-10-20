from openai import OpenAI
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

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
