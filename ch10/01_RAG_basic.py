# 引入套件
from openai import OpenAI
import os
import fitz  # PyMuPDF
from dotenv import load_dotenv

# 載入組態檔，取得模型代碼
load_dotenv()
MODEL_ID = os.getenv('MODEL_ID')
# print(MODEL_ID)

# 建立OpenAI用戶端物件
client = OpenAI()

# 詢問最新的時事
prompt = "台灣對等關稅是多少%?"
response = client.responses.create(
    model=MODEL_ID,
    input=prompt
)
print(response.output_text)

# 定義函數，萃取PDF檔案內容，並轉成文字
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text

# 定義函數，提供上下文(Context)，並呼叫 OpenAI API
def generate_augmented_response(query, context):
    # 提示範本
    prompt_prefix = "Answer the question based only on the following context, " 
    prompt = prompt_prefix + f"Context: {context}\n\nQuestion: {query}\n\nAnswer:"
    response = client.responses.create(
        model=MODEL_ID,
        input=prompt
    )
    return response.output_text

# 萃取PDF檔案內容，並轉成文字
file_path = "./pdf/台灣關稅 2025.08.01.pdf"
pdf_text = extract_text_from_pdf(file_path)
print(f'台灣關稅 2025.08.01.pdf 內容:\n{pdf_text[:500]}')
    
# 測試 1
context = pdf_text[:500]
query = "日本對等關稅是多少%?"
print(query, ':\n', generate_augmented_response(query, context))

# 測試 2
query = "韓國對等關稅是多少%?"
print(query, ':\n', generate_augmented_response(query, context))

# 測試 3
query = "台灣對等關稅是多少%?"
print(query, ':\n', generate_augmented_response(query, context))

# 萃取PDF檔案內容，並轉成文字
file_path = "./pdf/台灣關稅 2026.07.19.pdf"
pdf_text = extract_text_from_pdf(file_path)
print(f'台灣關稅 2025.08.01.pdf 內容:\n{pdf_text[:500]}')
    
# 測試 4
context = pdf_text[:500]
query = "台灣對等關稅是多少%?"
print(query, ':\n', generate_augmented_response(query, context))


