# 引入套件
import re
from openai import OpenAI
import sqlite3

# 資料庫名稱
db = "northwind_ORM.db"

# 取得資料庫定義(Schema)的函數
def get_schema(db):
    # Connect to your database
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    # Query the master schema table
    cursor.execute("SELECT type, name, sql FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    schema = ''
    for table_type, name, sql in tables:
        # print(f"Table Name: {name}")
        # print(f"Schema:\n{sql}\n" + "-"*40)
        schema += f"{sql}\n\n"
    conn.close()
    return schema
    
# 定義執行SQL的函數
def execute_sql(db, SQL):
    # Connect to your database
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    # Query the master schema table
    cursor.execute(SQL)
    rows = cursor.fetchall()

    for row in rows:
        for item in row:
            print(str(item), end='\t')
        print('\n')
        
    conn.close()

    
# 建立用戶端物件
client = OpenAI()

# 取得資料庫定義(Schema)
database_schema = get_schema(db)

# 呼叫 API
response = client.responses.create(
    model="gpt-5.6-luna",
        input = [
        {"role": "system", "content": f"你是資料庫專家\nDatabase Schema:\n{database_schema}"},
        {
            "role": "user",
            "content": "get top 3 employees with the highest total sales amounts",
        },
    ],
)

# 顯示回應
print(response.output_text+"\n\n")

# 截取 SQL
code_blocks = re.findall(r"```[a-zA-Z]*\n([\s\S]*?)\n```", response.output_text)

# 執行 SQL
execute_sql(db, code_blocks[0])    