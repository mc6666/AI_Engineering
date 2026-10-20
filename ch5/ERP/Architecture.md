# Project
ERP: Include Purchase Order、Sales Order and Inventory Management Modules.

# Goal
Develop a professional web application for general enterprises.
The entire project shall be written in Python Django and Javascript.

# Technology Stack
Python 3.12+
Django 6.0+
Pure Javascript (ES6)
AdminLTE CSS and Javascript

# Project Architecture
## 系統提供前台及後台，以不同的URL分開處理
- 前台提供Purchase Order、Sales Order and Inventory Management Modules的應用功能. 
- 後台管理設定權限控管. 


## Page layout
- 前台及後台畫面均包含sidebar及content
- 前台sidebar:採樹狀結構顯示應用功能，以JSON File儲存
- 前台content:為應用功能操作畫面
- 後台sidebar:採樹狀結構顯示權限控管功能，以JSON File儲存
- 後台content:為權限控管功能操作畫面
- 畫面採用 **AdminLTE** CSS and Javascript.
- **AdminLTE** installation: include following CSS and Javascripts in base.html.
```
<!-- In <head> -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/bootstrap-icons.min.css" />
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/overlayscrollbars@2.11.0/styles/overlayscrollbars.min.css" />
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/admin-lte@4.0.0/dist/css/adminlte.min.css" />

<!-- Before </body> -->
<script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.8/dist/umd/popper.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/overlayscrollbars@2.11.0/browser/overlayscrollbars.browser.es6.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/admin-lte@4.0.0/dist/js/adminlte.min.js"></script>
```

## Security
- 權限控管: 定義 user、role and function，再以 user-role、role-function 設定使用權限
- Authentication: provide Registry、 Change password、 Login check with database.
- Authorization: permission right defined by roles.
- Login後，Sidebar只會出現有使用權限的選單.
- 系統提供後台管理設定權限控管.

## Database
- 使用SQLite資料庫.









