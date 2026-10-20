---
name: inventory-management
description: 
  - 管理多個倉庫的庫存，包括收貨、出貨、庫存調撥、 庫存調整、循環盤點、補貨、存貨成本計算與庫存分析。

version: 1.0

domain:
  - ERP
  - 庫存管理 
  - 倉儲管理

permissions:
- 庫存管理員 
- 倉庫作業員 
- 倉庫主管 
- 庫存經理 
- 採購人員 
- 業務人員 
- 財務人員 
- 系統管理員
---

# 資料實體（Entities）
### 商品（Item）
欄位包括：
- 商品代號（ItemCode）
- 商品名稱（ItemName）
- 商品分類（Category）
- 計量單位（UnitOfMeasure）
- 條碼（Barcode）
- 序號（SerialNumber）
- 批號（LotNumber）
- 標準成本（StandardCost）
- 平均成本（AverageCost）
- 再訂購點（ReorderPoint）
- 安全庫存（SafetyStock）
- 前置時間（LeadTime）

### 倉庫（Warehouse）
欄位包括：
- 倉庫代號（WarehouseID）
- 倉庫名稱（WarehouseName）
- 倉庫位置（Location）
- 儲位（BinLocation）

### 庫存交易（InventoryTransaction）
欄位包括：
- 交易編號（TransactionNo）
- 交易類型（TransactionType）
- 商品代號（ItemCode）
- 倉庫（Warehouse）
- 數量（Quantity）
- 單位成本（UnitCost）
- 交易日期（TransactionDate）
- 來源單據（ReferenceDocument）
- 操作者（User）

### 庫存狀態（Inventory Status）
- 可用（Available）
- 已預留（Reserved）
- 採購中（On Order）
- 運送中（In Transit）
- 損壞（Damaged）
- 隔離（Quarantined）
- 已過期（Expired）

# 核心技能（Core Skills）
1. 商品主檔管理
### 功能
- 建立商品
- 修改商品
- 刪除商品
- 啟用商品
- 停用商品
- 指定商品分類
- 設定計量單位
- 設定條碼
- 設定序號管理
- 設定批號管理

2. 倉庫管理
### 功能
- 建立倉庫
- 修改倉庫
- 刪除倉庫
- 建立儲位（Bin）
- 倉庫容量管理
- 倉庫區域（Zone）管理

3. 庫存查詢
### 可依下列條件查詢：
- 商品
- 倉庫
- 條碼
- 商品分類
- 批號
- 序號
- 儲位

### 顯示：
- 現有庫存（On Hand）
- 可用庫存（Available）
- 已預留數量
- 在途數量
- 待出庫數量
- 平均成本
- 庫存價值

4. 入庫管理（Stock Receipt）
### 支援：
- 採購收貨
- 生產入庫
- 客戶退貨
- 手動入庫

### 驗證：
- 倉庫存在
- 商品存在
- 數量必須大於零

### 系統自動：
- 增加庫存
- 建立收貨單（Goods Receipt）


5. 出庫管理（Stock Issue）
### 支援：
- 銷售出貨
- 生產領料
- 部門領用
- 樣品
- 報廢

### 系統自動：
- 扣減庫存
- 更新交易紀錄

6. 庫存調撥
### 支援：
- 倉庫間調撥
- 儲位調撥
- 地點調撥

### 驗證：
- 可用庫存是否足夠
- 目的地是否存在

7. 庫存預留
### 可預留給：
- 銷售訂單
- 生產工單
- 專案需求

### 系統自動：
- 可用庫存 → 已預留庫存

8. 庫存調整
### 支援：
- 正向調整
- 負向調整
- 損壞
- 遺失
- 過期
- 資料修正

### 需填寫：
- 調整原因
- 核准流程

9. 循環盤點（Cycle Count）
### 可依：
- ABC分類
- 隨機抽盤
- 高價值商品
- 即將過期商品

### 系統自動：
- 比較系統數量
- 輸入實盤數量
- 計算盤差

10. 全面盤點（Physical Inventory）
### 功能：
- 凍結庫存
- 匯入盤點資料
- 盤差分析
- 主管核准
- 自動調整庫存

11. 批號管理（Lot Management）
### 追蹤：
- 批號
- 製造日期
- 到期日
- 供應商
- 數量

### 支援：
- FEFO（先到期先出）
- FIFO（先進先出）

12. 序號管理（Serial Number Management）
### 追蹤：
- 單一設備
- 保固資訊
- 出貨紀錄
- 維修紀錄

13. 條碼管理
### 功能：
- 產生條碼
- 列印條碼
- 掃描條碼
- QR Code 支援

14. 庫存成本計算
### 支援成本法：
- FIFO（先進先出）
- LIFO（後進先出）
- 加權平均法
- 標準成本法
- 移動平均法

### 產生：
- 庫存價值
- 成本分析

15. 補貨管理（Reorder Management）
### 自動監控：
- 再訂購點
- 安全庫存
- 前置時間
- 經濟訂購量（EOQ）

### 輸出：
- 建議採購數量

16. 效期管理（Expiration Management）
### 監控：
- 已過期商品
- 即將過期商品
- 保存期限

### 系統自動：
- 發送通知
- 建議報廢

17. 庫存儀表板（Inventory Dashboard）
### 顯示：
- 總庫存價值
- 庫存水位
- 缺貨商品
- 超量庫存
- 暢銷商品
- 滯銷商品
- 呆滯庫存
- 庫存週轉率

# AI 智慧技能（AI Skills）
## AI 庫存助理
### 支援自然語言查詢：
- 顯示所有低庫存商品。
- 哪些商品需要補貨？
- 查詢某商品目前庫存。
- 哪個倉庫還有存貨？
- 顯示各倉庫庫存價值。
- 查詢過期商品。
- 哪些商品庫存過高？
- 查詢損壞庫存。

## 智慧補貨建議
### AI 可建議：
- 建議採購數量
- 建議跨倉調撥
- 最佳安全庫存
- 最佳再訂購點

## 庫存需求預測
### AI 可預測：
- 未來庫存量
- 缺貨風險
- 庫存過剩
- 季節性需求
- 採購需求

## 倉庫最佳化：
### AI 可建議：
- 最佳儲位配置
- 最佳揀貨路徑
- 倉庫空間利用率
- 倉庫整併方案

## 庫存異常偵測
### AI 可偵測：
- 負庫存
- 重複交易
- 異常耗用
- 庫存短少
- 遺失商品
- 異常調整
- 疑似盜竊行為

# 報表（Reports）
### 系統可產生：
- 庫存價值報表
- 庫存狀況報表
- 庫齡分析報表
- ABC 分析
- 滯銷商品報表
- 呆滯庫存報表
- 庫存分類帳
- 庫存異動明細
- 補貨建議報表
- 庫存週轉率報表

# 作業流程（Workflow）
商品主檔 
↓ 
採購收貨 
↓ 
存建立 
↓ 
庫存預留 
↓ 
出庫 
↓ 
倉庫調撥 
↓ 
循環盤點 
↓ 
庫存調整 
↓ 
成本計算 
↓ 
報表分析

# API 功能
createItem() 
updateItem() 
deleteItem() 
createWarehouse() 
updateWarehouse() 
receiveInventory() 
issueInventory() 
transferInventory() 
reserveInventory() 
releaseReservation() 
adjustInventory() 
performCycleCount() 
performPhysicalCount() 
generateBarcode() 
scanBarcode() 
manageLot() 
manageSerialNumber() 
calculateInventoryValue() 
generateReorderSuggestion() 
searchInventory() 
getInventoryDashboard() 
generateInventoryReport() 
forecastInventory() 
detectInventoryAnomalies()

# 商業規則（Business Rules）
規則	    說明
庫存可用性	若可用庫存不足，不允許出庫（除非允許負庫存）。
庫存預留	已預留庫存不得分配給其他訂單，直到解除預留。
倉庫驗證	所有庫存交易必須指定有效倉庫與儲位（若有啟用）。
批號／序號管理	啟用批號或序號管理的商品，每次交易都必須輸入對應資訊。
成本計算	系統依公司設定的成本法（FIFO、LIFO、加權平均、標準成本或移動平均）計算庫存成本。
循環盤點	盤差需經主管核准後，才能更新庫存數量。
全面盤點	盤點期間可凍結指定倉庫或儲位的庫存交易。
補貨	當庫存低於再訂購點時，系統依安全庫存與交期自動產生補貨建議。
效期控管	已過期商品不得出貨或領料，除非經授權。
稽核追蹤	所有庫存交易、調整、核准及成本更新皆保留完整的使用者、時間、來源單據與異動前後紀錄。

# 系統整合（Integration）
模組	整合內容
採購管理（Purchase Order）	採購收貨後自動更新庫存。
銷售管理（Sales Order）	預留與扣減銷售訂單所需庫存。
生產管理（Production）	領用原料並回收入庫成品。
財務管理（Finance）	自動計算存貨成本、存貨價值及銷貨成本（COGS）。
倉儲管理（WMS）	支援儲位、上架、揀貨及倉庫最佳化。
固定資產管理（Asset Management）	管理序號化設備與資產。
品質管理（Quality Management）	支援隔離、檢驗、放行及退貨等品質流程。

本階段只整合採購管理、銷售管理