---
name: purchase-order
description: 
  - 管理完整的採購訂單生命週期，包括請購、供應商選擇、詢價比價、採購訂單建立、收貨、發票處理及採購分析。

version: 1.0

domain:
  - ERP
  - 採購管理

permissions:
  - 採購人員
  - 採購主管
  - 倉庫人員
  - 財務人員
  - 應付帳款人員
---

# 資料實體（Entities）
### 供應商（Supplier）
欄位包括：
- 供應商代號（SupplierID）
- 供應商名稱（SupplierName）
- 付款條件（PaymentTerms）
- 信用額度（CreditLimit）
- 聯絡人（ContactPerson）
- 電子郵件（Email）
- 供應商評等（Rating）

### 採購訂單（Purchase Order）
欄位包括：
- 採購單號（PONumber）
- 供應商代號（SupplierID）
- 訂單日期（OrderDate）
- 預計交貨日（RequiredDate）
- 訂單狀態（Status）
- 訂單總金額（TotalAmount）
- 採購人員（Buyer）

### 採購訂單明細（Purchase Order Item）
欄位包括：
- 商品代號（ItemCode）
- 商品名稱（Description）
- 採購數量（Quantity）
- 單價（UnitPrice）
- 折扣（Discount）
- 收貨倉庫（Warehouse）
- 已收貨數量（ReceivedQty）
- 未收貨數量（RemainingQty）

### 訂單狀態（Order Status）
- 草稿（Draft）
- 已送審（Submitted）
- 已核准（Approved）
- 已送出（Sent）
- 部分收貨（Partially Received）
- 已收貨（Received）
- 已開立發票（Invoiced）
- 已結案（Closed）
- 已取消（Cancelled）

# 核心技能（Core Skills）
1. 建立請購單（Purchase Requisition）
### 功能
- 建立內部採購需求。

### 輸入資料
- 申請人
- 部門
- 商品
- 數量
- 需求日期
- 預算代碼
- 採購原因

### 驗證
- 申請人存在
- 預算可用
- 商品存在
- 數量大於零

### 輸出
- 請購單號
- 狀態：草稿（Draft）

2. 核准請購單
### 驗證：
- 預算核准
- 部門主管核准
- 採購部門核准（必要時）

### 輸出：
- 狀態：已核准
- 可進行詢價

3. 詢價（RFQ，Request for Quotation）
### 功能：
- 選擇供應商
- 發送詢價單
- 設定報價截止日期
- 追蹤供應商回覆

4. 供應商報價比較
### 比較項目：
- 單價
- 總成本
- 交期
- 付款條件
- 保固
- 供應商評等
- 運費
- 前置時間（Lead Time）

### 輸出：
- 建議供應商
- 成本分析
- 比價報告

5. 建立採購訂單
### 輸入：
- 已核准請購單
- 供應商
- 商品清單
- 單價
- 收貨地址
- 付款條件

### 驗證：
- 供應商有效
- 已完成詢價／比價（如適用）
- 必填資料完整

### 輸出：
- 採購單號
- 狀態：草稿（Draft）

6. 修改採購訂單
### 可修改：
- 採購數量
- 單價
- 交貨日期
- 付款條件
- 收貨地址

### 限制：
- 開始收貨後不得修改，除非具有授權。

7. 送出採購訂單
### 狀態變更：
草稿
↓
已送審

### 驗證：
- 供應商存在
- 預算已核准
- 價格正確

8. 核准採購訂單
### 商業規則：
若採購金額超過核准門檻：
    需主管核准
否則：
    自動核准

### 狀態：
已送審
↓
已核准

9. 發送採購訂單
### 支援方式：
- Email
- API 整合

### 輸出：
- 發送日期
- 回覆確認狀態

10. 採購訂單追蹤
### 追蹤：
- 供應商確認
- 出貨狀態
- 預計到貨日
- 延遲交貨
- 分批出貨

11. 收貨管理（Goods Receipt）
### 輸入：
- 採購單號
- 收貨倉庫
- 商品
- 收貨數量

### 驗證：
- 收貨數量不得超過採購數量
- 採購單已核准

### 系統自動：
- 更新庫存
- 建立收貨單（Goods Receipt Note，GRN）

12. 部分收貨
### 支援：
- 分批交貨
- 剩餘數量追蹤
- 缺貨管理

### 狀態：
已核准
↓
部分收貨

13. 品質驗收（Quality Inspection）
### 檢驗項目：
- 數量
- 外觀
- 規格
- 功能測試
- 包裝

### 結果：
- 合格
- 不合格
- 退貨

14. 退貨給供應商
### 退貨原因：
- 商品損壞
- 商品錯誤
- 品質不符
- 超量交貨

### 系統產生：
- 退貨授權單
- 供應商通知

15. 三方比對（Three-Way Matching）
### 比對：
採購訂單
↓
收貨單
↓
供應商發票

### 驗證：
- 數量
- 單價
- 供應商

### 結果：
- 一致（Match）
- 差異（Exception）

16. 處理供應商發票
### 輸入：
- 發票號碼
- 發票日期
- 金額
- 付款條件

### 驗證：
- 已完成三方比對

### 系統自動：
- 建立應付帳款（Accounts Payable）

17. 安排付款
### 計算：
- 到期日
- 提前付款折扣
- 現金需求

### 輸出：
- 付款排程

18. 結案
### 條件：
- 全部收貨完成
- 發票完成處理
- 無未結餘額

### 狀態：
- 已結案（Closed）

19. 取消採購訂單
### 允許：
- 尚未出貨

### 系統自動：
- 解除預算承諾
- 通知供應商

20. 採購訂單查詢
### 可依：
- 採購單號
- 供應商
- 採購人員
- 商品
- 日期
- 狀態

### 顯示：
- 訂單摘要
- 收貨紀錄
- 發票狀態
- 付款狀態
- 庫存管理技能（Inventory Skills）

### 庫存查詢
顯示：
- 現有庫存
- 已預留
- 在途庫存
- 安全庫存
- 再訂購點
- 自動補貨建議

依據：
- 現有庫存
- 前置時間
- 銷售預測
- 安全庫存
- 經濟訂購量（EOQ）

### 輸出：
- 建議採購數量
- 供應商績效評估

### 計算：
- 準時交貨率
- 品質合格率
- 平均交期
- 採購金額
- 退貨率

### 產生：
- 供應商績效評分卡
- AI 智慧技能（AI Skills）
- AI 採購助理

### 支援自然語言查詢：
- 哪一家供應商價格最低？
- 推薦最佳供應商。
- 哪些採購單已逾期？
- 顯示延遲交貨清單。
- 哪家供應商品質最好？
- 今日有哪些收貨安排？
- 哪些供應商發票尚未付款？
- 哪些採購單等待核准？
- AI 智慧建議

### 提供：
- 最佳供應商推薦
- 替代供應商
- 成本較低商品
- 更佳付款條件
- 大量採購折扣
- 合約價格建議
- 合併採購建議
- AI 採購預測

### 預測：
- 物料需求
- 採購成本
- 供應商交期
- 缺料風險
- 預算使用率
- 季節性採購需求
- AI 異常偵測

### 偵測：
- 延遲交貨
- 重複採購單
- 重複發票
- 價格異常上漲
- 預算超支
- 供應短缺
- 單一供應商依賴風險
- 疑似採購舞弊

### 作業流程（Workflow）
建立請購單
    ↓
請購核准
    ↓
詢價（RFQ）
    ↓
比價分析
    ↓
供應商選擇
    ↓
建立採購訂單
    ↓
採購核准
    ↓
發送採購單
    ↓
供應商確認
    ↓
收貨
    ↓
品質驗收
    ↓
三方比對
    ↓
供應商發票
    ↓
付款
    ↓
結案

# API 功能
createPurchaseRequisition()
approvePurchaseRequisition()
createRFQ()
sendRFQ()
compareQuotations()
recommendSupplier()
createPurchaseOrder()
updatePurchaseOrder()
submitPurchaseOrder()
approvePurchaseOrder()
sendPurchaseOrder()
trackPurchaseOrder()
receiveGoods()
processPartialReceipt()
qualityInspection()
returnToSupplier()
threeWayMatch()
processSupplierInvoice()
schedulePayment()
closePurchaseOrder()
cancelPurchaseOrder()
searchPurchaseOrders()
generateSupplierScorecard()
checkInventory()
generateReorderSuggestion()
getProcurementDashboard()

# 商業規則（Business Rules）
規則	    說明
預算控管	請購單與採購訂單不得超過核准預算，除非取得授權。
供應商驗證	僅能向有效且已核准的供應商建立採購訂單。
核准流程	超過設定金額的採購訂單須經主管核准。
收貨控制	收貨數量不得超過採購數量，除非允許超收。
三方比對	採購訂單、收貨單與供應商發票三方比對一致後，方可付款。
庫存更新	驗收合格商品立即更新庫存；不合格商品進入隔離或退貨流程。
付款管理	依付款條件安排付款，並支援提前付款折扣。
稽核追蹤	所有建立、修改、核准、收貨、退貨、發票及付款作業皆保留完整的使用者、時間及異動紀錄。
供應商績效	系統依交期、品質、價格及服務表現定期更新供應商績效評分。
法規遵循	採購流程須符合企業採購政策、合約條款及相關法規要求。

# 系統整合（Integration）
模組	整合內容
庫存管理（Inventory）	收貨後自動更新庫存，並提供補貨需求。
銷售管理（Sales Order）	根據銷售需求觸發採購或補貨。
財務管理（Finance）	建立應付帳款、付款及採購成本。
倉儲管理（WMS）	支援收貨、上架、驗收及倉庫管理。
品質管理（Quality Management）	執行收貨檢驗、隔離及退貨流程。
商業智慧（BI）	提供採購分析、供應商績效及成本趨勢分析。

本階段只整合庫存管理、銷售管理