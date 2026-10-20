# 實施計劃 

1. 使用 Drizzle 定義一個 `expenses` 資料表（包含 id、amount、description 和 date 四個欄位）。 
2. 建立 SQLite 資料庫和一個資料庫客戶端。 
3. 新增 POST /expenses 請求以建立費用記錄，使用 Zod 驗證請求。
4. 新增 GET /expenses 請求，傳回所有按日期降冪排列的費用。 
5. 在 src/index.ts 檔案中配置 Hono 應用。

## 需要修改的文件 
- src/schema.ts 
- src/db.ts 
- src/index.ts

