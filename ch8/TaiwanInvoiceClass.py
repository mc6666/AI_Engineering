from __future__ import annotations
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, datetime
from pathlib import Path
from typing import Literal
import pandas as pd
from great_tables import GT, html

# ============================================================
# 型別
# ============================================================
InvoiceType = Literal["二聯式", "三聯式"]
TaxType = Literal["應稅", "零稅率", "免稅"]

# ============================================================
# 工具
# ============================================================
def money(value: Decimal | int | float | str) -> Decimal:
    """金額統一使用 Decimal，並四捨五入到元。"""
    return Decimal(str(value)).quantize(
        Decimal("1"),
        rounding=ROUND_HALF_UP,
    )

# ============================================================
# 發票明細
# ============================================================
@dataclass
class InvoiceItem:
    """發票明細。"""
    name: str
    quantity: Decimal | int
    unit_price: Decimal | int | float | str
    description: str = ""
    discount: Decimal | int | float | str = 0

    @property
    def amount(self) -> Decimal:
        """未稅明細金額。"""
        amount = (
            Decimal(str(self.quantity))
            * Decimal(str(self.unit_price))
        )

        amount -= Decimal(str(self.discount))

        return money(amount)

# ============================================================
# 賣方
# ============================================================
@dataclass
class Seller:
    name: str
    tax_id: str
    address: str = ""
    phone: str = ""

# ============================================================
# 買方
# ============================================================
@dataclass
class Buyer:
    name: str
    tax_id: str = ""
    address: str = ""


# ============================================================
# TaiwanInvoice
# ============================================================
@dataclass
class TaiwanInvoice:
    # --------------------------------------------------------
    # 發票基本資料
    # --------------------------------------------------------
    invoice_type: InvoiceType = "三聯式"
    invoice_no: str = ""
    invoice_date: date = field(default_factory=date.today)

    period: str = ""

    # --------------------------------------------------------
    # 賣方 / 買方
    # --------------------------------------------------------
    seller: Seller = field(
        default_factory=lambda: Seller(
            name="",
            tax_id="",
        )
    )

    buyer: Buyer = field(
        default_factory=lambda: Buyer(
            name="",
            tax_id="",
        )
    )

    # --------------------------------------------------------
    # 明細
    # --------------------------------------------------------
    items: list[InvoiceItem] = field(
        default_factory=list
    )

    # --------------------------------------------------------
    # 稅務
    # --------------------------------------------------------
    tax_type: TaxType = "應稅"
    vat_rate: Decimal = Decimal("0.05")

    # --------------------------------------------------------
    # 備註
    # --------------------------------------------------------
    notes: str = ""

    # ========================================================
    # 新增明細
    # ========================================================
    def add_item(
        self,
        name: str,
        quantity: Decimal | int,
        unit_price: Decimal | int | float | str,
        description: str = "",
        discount: Decimal | int | float | str = 0,
    ) -> InvoiceItem:

        item = InvoiceItem(
            name=name,
            quantity=quantity,
            unit_price=unit_price,
            description=description,
            discount=discount,
        )

        self.items.append(item)

        return item

    # ========================================================
    # 銷售額
    # ========================================================
    @property
    def subtotal(self) -> Decimal:
        return money(
            sum(
                (item.amount for item in self.items),
                Decimal("0"),
            )
        )

    # ========================================================
    # 營業稅
    # ========================================================
    @property
    def vat(self) -> Decimal:
        if self.tax_type != "應稅":
            return Decimal("0")

        return money(
            self.subtotal * self.vat_rate
        )

    # ========================================================
    # 總計
    # ========================================================
    @property
    def total(self) -> Decimal:
        return money(
            self.subtotal + self.vat
        )

    # ========================================================
    # 發票期間
    # ========================================================
    @property
    def invoice_period(self) -> str:
        if self.period:
            return self.period

        if isinstance(self.invoice_date, str):
            self.invoice_date = datetime.strptime(self.invoice_date, "%Y-%m-%d")
        month = self.invoice_date.month
        if month in (1, 2):
            return "01-02月"
        elif month in (3, 4):
            return "03-04月"
        elif month in (5, 6):
            return "05-06月"
        elif month in (7, 8):
            return "07-08月"
        elif month in (9, 10):
            return "09-10月"
        else:
            return "11-12月"

    # ========================================================
    # 明細 DataFrame
    # ========================================================
    def to_dataframe(self) -> pd.DataFrame:
        rows = []
        
        # convert self.items to InvoiceItem list
        item_list = []
        for item in self.items:
            # print(item)
            if isinstance(item, dict):
                item = InvoiceItem(**item)
            item_list.append(item)
        if self.items != []:
            self.items = item_list
        
        for item in self.items:
            rows.append(
                {
                    "品名": item.name,
                    "說明": item.description,
                    "數量": item.quantity,
                    "單價": item.unit_price,
                    "金額": item.amount,
                }
            )

        return pd.DataFrame(
            rows,
            columns=[
                "品名",
                "說明",
                "數量",
                "單價",
                "金額",
            ],
        )

    # ========================================================
    # Great Tables
    # ========================================================
    def create_table(self) -> GT:
        df = self.to_dataframe()
        if isinstance(self.buyer, dict):
            self.buyer = Buyer(**self.buyer)
        if isinstance(self.seller, dict):
            self.seller = Seller(**self.seller)
        
        table = (
            GT(df)
            # ------------------------------------------------
            # 表頭
            # ------------------------------------------------
            .tab_header(
                title=html(
                    """
                    <div class="invoice-title">
                        統 一 發 票
                    </div>
                    """
                ),

                subtitle=html(
                    f"""
                    <div class="invoice-subtitle">
                        {self.invoice_type}
                    </div>
                    """
                ),
            )

            # ------------------------------------------------
            # 欄位
            # ------------------------------------------------
            .cols_label(
                品名="品名",
                說明="說明",
                數量="數量",
                單價="單價",
                金額="金額",
            )

            # ------------------------------------------------
            # 金額格式
            # ------------------------------------------------
            .fmt_currency(
                columns=["單價", "金額"],
                currency="TWD",
                decimals=0,
            )

            # ------------------------------------------------
            # 對齊
            # ------------------------------------------------
            .cols_align(
                align="left",
                columns=["品名", "說明"],
            )

            .cols_align(
                align="center",
                columns=["數量"],
            )

            .cols_align(
                align="right",
                columns=["單價", "金額"],
            )

            # ------------------------------------------------
            # 發票資訊
            # ------------------------------------------------
            .tab_header(
                title=html(
                    f"""
                    <div class="invoice-title">
                        統 一 發 票
                    </div>

                    <div class="invoice-meta">
                        <span>
                            發票期間：
                            <b>{self.invoice_period}</b>
                        </span>

                        <span>
                            發票號碼：
                            <b>{self.invoice_no}</b>
                        </span>

                        <span>
                            開立日期：
                            <b>{self.invoice_date}</b>
                        </span>
                    </div>

                    <div class="invoice-parties">

                        <div>
                            <b>買受人：</b>
                            {self.buyer.name}
                        </div>

                        <div>
                            <b>統一編號：</b>
                            {self.buyer.tax_id or "—"}
                        </div>

                    </div>
                    """
                )
            )

            # ------------------------------------------------
            # Footer
            # ------------------------------------------------
            .tab_source_note(
                source_note=html(
                    self._summary_html()
                )
            )

            # ------------------------------------------------
            # 表格設定
            # ------------------------------------------------
            .tab_options(
                table_width="100%",
                table_font_size="13px",
            )
        )

        return table

    # ========================================================
    # 發票總計 HTML
    # ========================================================
    def _summary_html(self) -> str:
        tax_label = {
            "應稅": f"營業稅（{self.vat_rate * 100:g}%）",
            "零稅率": "營業稅（零稅率）",
            "免稅": "營業稅（免稅）",
        }[self.tax_type]

        return f"""
        <div class="invoice-summary">

            <div class="summary-row">
                <span>銷售額合計</span>
                <strong>
                    NT$ {self.subtotal:,.0f}
                </strong>
            </div>

            <div class="summary-row">
                <span>{tax_label}</span>
                <strong>
                    NT$ {self.vat:,.0f}
                </strong>
            </div>

            <div class="summary-row total">
                <span>總計</span>
                <strong>
                    NT$ {self.total:,.0f}
                </strong>
            </div>

        </div>

        <div class="seller-info">

            <div>
                <b>賣方：</b>
                {self.seller.name}
            </div>

            <div>
                <b>統一編號：</b>
                {self.seller.tax_id}
            </div>

            <div>
                <b>地址：</b>
                {self.seller.address}
            </div>

            <div>
                <b>電話：</b>
                {self.seller.phone}
            </div>

            <div>
                <b>備註：</b>
                {self.notes}
            </div>

        </div>
        """

    # ========================================================
    # CSS
    # ========================================================
    @staticmethod
    def css() -> str:
        return """
        <style>

        body {
            font-family:
                "Microsoft JhengHei",
                "Noto Sans CJK TC",
                "Noto Sans TC",
                sans-serif;

            background: white;
        }

        .invoice-title {
            text-align: center;
            font-size: 28px;
            font-weight: bold;
            letter-spacing: 8px;
            margin-bottom: 10px;
        }

        .invoice-subtitle {
            text-align: center;
            font-size: 16px;
            margin-bottom: 10px;
        }

        .invoice-meta {
            display: flex;
            justify-content: space-between;
            font-size: 13px;
            margin: 10px 0;
        }

        .invoice-parties {
            border: 1px solid #333;
            padding: 10px;
            margin-bottom: 10px;
            font-size: 14px;
        }

        .invoice-parties div {
            margin: 3px 0;
        }

        .invoice-summary {
            margin-top: 15px;
            margin-left: auto;
            width: 45%;
        }

        .summary-row {
            display: flex;
            justify-content: space-between;
            padding: 5px 10px;
            border-bottom: 1px solid #ddd;
        }

        .summary-row.total {
            font-size: 18px;
            font-weight: bold;
            border-top: 2px solid #333;
            border-bottom: 2px solid #333;
            padding: 10px;
        }

        .seller-info {
            margin-top: 20px;
            border-top: 1px solid #333;
            padding-top: 10px;
            font-size: 13px;
            line-height: 1.8;
        }

        </style>
        """

    # ========================================================
    # HTML
    # ========================================================
    def to_html(
        self,
        filename: str | Path = "invoice.html",
    ) -> Path:

        filename = Path(filename)

        table = self.create_table()

        html_content = (
            self.css()
            + table.as_raw_html()
        )

        # ----------------------------------------------------
        # 注意：
        # Great Tables 的 HTML 內容直接輸出，
        # 再由瀏覽器進行列印。
        # ----------------------------------------------------

        full_html = f"""
        <!DOCTYPE html>

        <html lang="zh-Hant">

        <head>

            <meta charset="UTF-8">

            <title>
                統一發票 {self.invoice_no}
            </title>

            {self.css()}

        </head>

        <body>

            {table.as_raw_html()}

        </body>

        </html>
        """

        filename.write_text(
            full_html,
            encoding="utf-8",
        )

        return filename

    # ========================================================
    # PDF
    # ========================================================
    def to_pdf(
        self,
        filename: str | Path = "invoice.html",
    ) -> Path:

        filename = Path(filename)
        table = self.create_table()
        table.gtsave(filename)
        return filename

    # ========================================================
    # 顯示
    # ========================================================
    def show(self):
        self.create_table().show(
            target="browser"
        )

    # ========================================================
    # JSON
    # ========================================================
    def to_dict(self) -> dict:
        return {
            "invoice_type": self.invoice_type,
            "invoice_no": self.invoice_no,
            "invoice_date": self.invoice_date.isoformat(),
            "period": self.invoice_period,

            "seller": {
                "name": self.seller.name,
                "tax_id": self.seller.tax_id,
                "address": self.seller.address,
                "phone": self.seller.phone,
            },

            "buyer": {
                "name": self.buyer.name,
                "tax_id": self.buyer.tax_id,
                "address": self.buyer.address,
            },

            "tax_type": self.tax_type,
            "vat_rate": str(self.vat_rate),

            "items": [
                {
                    "name": item.name,
                    "description": item.description,
                    "quantity": str(item.quantity),
                    "unit_price": str(item.unit_price),
                    "discount": str(item.discount),
                    "amount": str(item.amount),
                }
                for item in self.items
            ],

            "subtotal": str(self.subtotal),
            "vat": str(self.vat),
            "total": str(self.total),

            "notes": self.notes,
        }

# ============================================================
# Function Calling
# ============================================================
def generate_invoice(
    invoice_type: str, 
    invoice_no: str, 
    invoice_date: datetime,
    seller: Seller,
    buyer: Buyer,
    tax_type: str,
    notes: str,
    items = list[InvoiceItem]
    ):
    
    invoice = TaiwanInvoice(
        invoice_type=invoice_type,
        invoice_no=invoice_no,
        invoice_date=invoice_date,
        seller=seller,
        buyer=buyer,
        tax_type="應稅",
        notes="感謝您的惠顧。",
    )

    # --------------------------------------------------------
    # 新增商品
    # --------------------------------------------------------
    for item in items:
        # print(item)
        if isinstance(item, dict):
            invoice.add_item(**item)
        else:
            invoice.items = items
    
    # --------------------------------------------------------
    # 顯示計算結果
    # --------------------------------------------------------
    print("================================")
    print("統一發票")
    print("================================")
    print(f"銷售額：NT$ {invoice.subtotal:,.0f}")
    print(f"營業稅：NT$ {invoice.vat:,.0f}")
    print(f"總計：  NT$ {invoice.total:,.0f}")
    print("================================")

    # --------------------------------------------------------
    # 輸出 HTML
    # --------------------------------------------------------
    path = invoice.to_html(
        "output/invoice.html"
    )
    return path

# ============================================================
# Demo
# ============================================================
if __name__ == "__main__":
    # --------------------------------------------------------
    # 新增商品
    # --------------------------------------------------------
    items = []
    items.append(InvoiceItem(
        name="筆記型電腦",
        description="商務型筆記型電腦",
        quantity=2,
        unit_price=35000,
    ))

    items.append(InvoiceItem(
        name="4K 螢幕",
        description="27 吋 4K 顯示器",
        quantity=3,
        unit_price=12000,
    ))

    items.append(InvoiceItem(
        name="軟體授權",
        description="年度軟體授權",
        quantity=5,
        unit_price=8000,
    ))

    path = generate_invoice(
        invoice_type="三聯式",
        invoice_no="AB-12345678",
        invoice_date=date(2026, 8, 31),

        seller=Seller(
            name="ABC 科技股份有限公司",
            tax_id="12345678",
            address="台北市信義區信義路100號",
            phone="02-1234-5678",
        ),

        buyer=Buyer(
            name="XYZ 股份有限公司",
            tax_id="87654321",
            address="新北市板橋區文化路200號",
        ),

        tax_type="應稅",

        notes="感謝您的惠顧。",
        items=items
        )

    print(f"HTML：{path}")
