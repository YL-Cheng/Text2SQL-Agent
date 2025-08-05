import pandas as pd


def create_schema() -> pd.DataFrame:
    """
    Generates a DataFrame containing the schema definition for the e-commerce database.

    Returns:
        pd.DataFrame: A DataFrame with columns: table_name, column_name, column_name_zh, definition, data_type.
    """
    column_definitions = {
        "members": [
            ("member_id", "會員編號", "Unique identifier for each member", "Integer"),
            ("member_name", "姓名", "Member's full name", "String"),
            ("email", "電子郵件", "Member's email address", "String"),
            ("join_date", "加入日期", "Date the member registered", "DateTime"),
            ("member_level", "會員等級", "Membership level (e.g., Silver, Gold, Platinum)", "String"),
            ("referrer_id", "推薦人", "ID of the member who referred this member", "Integer (nullable)"),
            ("gender", "性別", "Member's gender (Male, Female, Unknown)", "String"),
            ("birth_year", "出生年份", "Year the member was born", "Integer"),
            ("country", "國家", "Country the member belongs to", "String"),
            ("is_active", "是否啟用", "Whether the member's account is active", "Boolean"),
        ],
        "items": [
            ("item_id", "商品編號", "Unique identifier for each item", "Integer"),
            ("item_name", "商品名稱", "Name of the item", "String"),
            ("category", "分類", "Primary category of the item", "String"),
            ("subcategory", "子分類", "Subcategory of the item", "String"),
            ("brand", "品牌", "Brand of the item (e.g., Apple, Samsung, Nike, Adidas)", "String"),
            ("price", "價格", "Original price of the item", "Float"),
            ("stock_quantity", "庫存量", "Number of items available for sale", "Integer"),
            ("rating", "評分", "Average user rating", "Float"),
            ("is_active", "是否上架", "Whether the item is currently listed for sale", "Boolean"),
            ("created_at", "上架時間", "Time the item was listed", "DateTime"),
        ],
        "campaigns": [
            ("campaign_id", "活動編號", "Unique identifier for each marketing campaign", "Integer"),
            ("campaign_name", "活動名稱", "Name of the marketing campaign", "String"),
            ("start_date", "開始日期", "Start date of the campaign", "DateTime"),
            ("end_date", "結束日期", "End date of the campaign", "DateTime"),
            ("discount_rate", "折扣比例", "Discount rate offered in the campaign", "Float"),
            ("channel", "推廣渠道", "Promotion channel (e.g., App, Website, Email, Social Media)", "String"),
            ("description", "活動說明", "Detailed description of the campaign", "String"),
        ],
        "transactions": [
            ("transaction_id", "交易編號", "Unique identifier for each transaction", "Integer"),
            ("member_id", "會員編號", "Unique ID of the member making the transaction", "Integer"),
            ("campaign_id", "活動編號", "Associated marketing campaign for this transaction", "Integer (nullable)"),
            ("discount_rate", "折扣比例", "Discount rate used in this transaction (0–100%)", "Float"),
            ("final_price", "成交價格", "Final price after applying discount", "Float"),
            ("payment_method", "付款方式", "Payment method used (e.g., CreditCard, PayPal, ATM, LinePay)", "String"),
            ("transaction_time", "交易時間", "Time the transaction occurred", "DateTime"),
        ],
        "transaction_items": [
            ("transaction_id", "交易編號", "Unique ID of the related main transaction", "Integer"),
            ("item_id", "商品編號", "Unique ID of the purchased item", "Integer"),
            ("quantity", "數量", "Quantity of the purchased item", "Integer"),
            ("unit_price", "單價", "Unit price of the item", "Float"),
        ]
    }

    table_definitions = {
        "members": "Table that stores information about registered members.",
        "items": "Table containing details of all items available for sale.",
        "campaigns": "Table listing all marketing campaigns and related information.",
        "transactions": "Table recording each transaction made by members.",
        "transaction_items": "Table listing the specific items purchased in each transaction.",
    }

    rows = []
    for table, fields in column_definitions.items():
        # Add table definition as a row
        rows.append({
            "table_name": table,
            "column_name": "__table__",
            "definition": table_definitions[table],
            "data_type": "TABLE",
        })
        
        # Add column definitions
        for field in fields:
            rows.append({
                "table_name": table,
                "column_name": field[0],
                "definition": field[2],
                "data_type": field[3],
            })

    df_schema = pd.DataFrame(rows)
    return df_schema


if __name__ == "__main__":
    df_schema = create_schema()
    print(df_schema)