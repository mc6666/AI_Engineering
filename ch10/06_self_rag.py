# 引入套件
import os
from openai import OpenAI
from dotenv import load_dotenv

# 載入組態檔，取得模型代碼
load_dotenv()
MODEL_ID = os.getenv('MODEL_ID')

# 建立OpenAI用戶端物件
client = OpenAI()

# 呼叫API判斷是否需要搜尋上下文
def determine_if_retrieval_needed(query):
    system_prompt = """You are an AI assistant that determines if retrieval is necessary to answer a query.
    For factual questions, specific information requests, or questions about events, people, or concepts, answer "Yes".
    For opinions, hypothetical scenarios, or simple queries with common knowledge, answer "No".
    Answer with ONLY "Yes" or "No"."""

    user_prompt = f"Query: {query}\n\nIs retrieval necessary to answer this query accurately?"

    response = client.responses.create(
        model=MODEL_ID,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
    )
    print('上下文：', response.output_text)
    answer = response.output_text.strip().lower()
    return "yes" in answer

# 呼叫API判斷上下文是否適當
def evaluate_relevance(query, context):
    system_prompt = """You are an AI assistant. Determine if a document is relevant to a query.
    Answer with ONLY "Relevant" or "Irrelevant"."""

    user_prompt = f"""Query: {query}
    Document content:
    {context[:500]}... [truncated]

    Is this document relevant to the query? Answer with ONLY "Relevant" or "Irrelevant".
    """

    response = client.responses.create(
        model=MODEL_ID,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
    )
    answer = response.output_text.strip().lower()
    return answer


# 測試
if __name__ == "__main__":
    # 測試是否需要搜尋上下文
    prompt = "明天氣象"
    print('否需要搜尋上下文:', determine_if_retrieval_needed(prompt))

    # 判斷上下文是否適當
    context = "The weather forecast for tomorrow is cloudy and overcast, with a high of 62 degrees."
    print('判斷上下文是否適當:', evaluate_relevance(prompt, context))    

