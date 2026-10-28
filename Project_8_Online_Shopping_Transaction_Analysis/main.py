"""
Project 8: Online Shopping Transaction Analysis System
Reads transactions from MySQL when configured; otherwise uses built-in sample data.
Outputs CSV reports and PNG charts in the output/ folder.
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Optional MySQL settings. Set these environment variables for your own database.
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "online_shopping")

SAMPLE_PRODUCTS = pd.DataFrame([
    {"product_id": 1, "product_name": "Wireless Mouse", "category": "Electronics", "unit_price": 599.00},
    {"product_id": 2, "product_name": "USB Keyboard", "category": "Electronics", "unit_price": 899.00},
    {"product_id": 3, "product_name": "Water Bottle", "category": "Home", "unit_price": 299.00},
    {"product_id": 4, "product_name": "Notebook Pack", "category": "Stationery", "unit_price": 199.00},
    {"product_id": 5, "product_name": "Backpack", "category": "Accessories", "unit_price": 1299.00},
])

SAMPLE_ORDERS = pd.DataFrame([
    {"order_id": 1001, "order_date": "2026-01-05", "payment_method": "UPI", "order_status": "Delivered"},
    {"order_id": 1002, "order_date": "2026-01-11", "payment_method": "Card", "order_status": "Delivered"},
    {"order_id": 1003, "order_date": "2026-02-02", "payment_method": "Cash on Delivery", "order_status": "Cancelled"},
    {"order_id": 1004, "order_date": "2026-02-14", "payment_method": "UPI", "order_status": "Shipped"},
    {"order_id": 1005, "order_date": "2026-03-03", "payment_method": "Net Banking", "order_status": "Delivered"},
    {"order_id": 1006, "order_date": "2026-03-18", "payment_method": "Card", "order_status": "Refunded"},
    {"order_id": 1007, "order_date": "2026-04-09", "payment_method": "UPI", "order_status": "Processing"},
    {"order_id": 1008, "order_date": "2026-04-22", "payment_method": "Cash on Delivery", "order_status": "Delivered"},
    {"order_id": 1009, "order_date": "2026-05-06", "payment_method": "Card", "order_status": "Delivered"},
    {"order_id": 1010, "order_date": "2026-05-21", "payment_method": "UPI", "order_status": "Shipped"},
    {"order_id": 1011, "order_date": "2026-06-12", "payment_method": "Net Banking", "order_status": "Delivered"},
    {"order_id": 1012, "order_date": "2026-06-28", "payment_method": "UPI", "order_status": "Delivered"},
])

SAMPLE_ITEMS = pd.DataFrame([
    {"item_id": 1, "order_id": 1001, "product_id": 1, "quantity": 2, "unit_price": 599.00},
    {"item_id": 2, "order_id": 1001, "product_id": 3, "quantity": 1, "unit_price": 299.00},
    {"item_id": 3, "order_id": 1002, "product_id": 2, "quantity": 1, "unit_price": 899.00},
    {"item_id": 4, "order_id": 1002, "product_id": 4, "quantity": 3, "unit_price": 199.00},
    {"item_id": 5, "order_id": 1003, "product_id": 5, "quantity": 1, "unit_price": 1299.00},
    {"item_id": 6, "order_id": 1004, "product_id": 1, "quantity": 1, "unit_price": 599.00},
    {"item_id": 7, "order_id": 1004, "product_id": 4, "quantity": 2, "unit_price": 199.00},
    {"item_id": 8, "order_id": 1005, "product_id": 5, "quantity": 1, "unit_price": 1299.00},
    {"item_id": 9, "order_id": 1005, "product_id": 3, "quantity": 2, "unit_price": 299.00},
    {"item_id": 10, "order_id": 1006, "product_id": 2, "quantity": 1, "unit_price": 899.00},
    {"item_id": 11, "order_id": 1007, "product_id": 3, "quantity": 2, "unit_price": 299.00},
    {"item_id": 12, "order_id": 1008, "product_id": 4, "quantity": 5, "unit_price": 199.00},
    {"item_id": 13, "order_id": 1009, "product_id": 1, "quantity": 1, "unit_price": 599.00},
    {"item_id": 14, "order_id": 1009, "product_id": 5, "quantity": 1, "unit_price": 1299.00},
    {"item_id": 15, "order_id": 1010, "product_id": 2, "quantity": 2, "unit_price": 899.00},
    {"item_id": 16, "order_id": 1011, "product_id": 4, "quantity": 2, "unit_price": 199.00},
    {"item_id": 17, "order_id": 1012, "product_id": 3, "quantity": 1, "unit_price": 299.00},
    {"item_id": 18, "order_id": 1012, "product_id": 1, "quantity": 1, "unit_price": 599.00},
])

def load_data():
    """Try MySQL first. If connection is not configured, use sample data."""
    try:
        import mysql.connector
        conn = mysql.connector.connect(
            host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE, connection_timeout=3
        )
        products = pd.read_sql("SELECT * FROM products", conn)
        orders = pd.read_sql("SELECT * FROM orders", conn)
        items = pd.read_sql("SELECT * FROM order_items", conn)
        conn.close()
        print("Connected to MySQL database:", MYSQL_DATABASE)
        return products, orders, items
    except Exception as exc:
        print("MySQL connection/data read unavailable; using built-in sample data.")
        print("To use MySQL, run schema.sql and configure MYSQL_HOST, MYSQL_USER,")
        print("MYSQL_PASSWORD, and MYSQL_DATABASE. Details:", str(exc))
        return SAMPLE_PRODUCTS.copy(), SAMPLE_ORDERS.copy(), SAMPLE_ITEMS.copy()

def main():
    products, orders, items = load_data()
    orders["order_date"] = pd.to_datetime(orders["order_date"], errors="coerce")
    orders["order_status"] = orders["order_status"].astype(str).str.strip().str.title()
    orders["payment_method"] = orders["payment_method"].astype(str).str.strip()

    # Calculate line totals from order items, not from product catalog prices.
    items["line_total"] = items["quantity"] * items["unit_price"]
    item_details = items.merge(products[["product_id", "product_name", "category"]],
                                on="product_id", how="left")
    order_totals = items.groupby("order_id", as_index=False).agg(
        order_value=("line_total", "sum"),
        total_units=("quantity", "sum")
    )
    transaction_summary = orders.merge(order_totals, on="order_id", how="left")
    transaction_summary[["order_value", "total_units"]] = transaction_summary[
        ["order_value", "total_units"]].fillna(0)
    transaction_summary["order_value"] = transaction_summary["order_value"].round(2)

    # Cancelled orders are excluded from realized transaction value and average order value.
    # Refunded orders remain visible in the order report but are excluded from realized value.
    valid_statuses = ["Delivered", "Shipped", "Processing"]
    eligible = transaction_summary[transaction_summary["order_status"].isin(valid_statuses)]
    avg_order_value = float(eligible["order_value"].mean()) if len(eligible) else 0.0
    realized_value = float(eligible["order_value"].sum())

    transaction_summary.to_csv(os.path.join(OUTPUT_DIR, "transaction_summary.csv"), index=False)
    transaction_summary.groupby("order_status").agg(
        order_count=("order_id", "count"),
        order_value=("order_value", "sum")
    ).reset_index().to_csv(os.path.join(OUTPUT_DIR, "order_status_report.csv"), index=False)

    payment_report = transaction_summary.groupby("payment_method").size().reset_index(name="order_count")
    payment_report.to_csv(os.path.join(OUTPUT_DIR, "payment_method_report.csv"), index=False)

    monthly = transaction_summary.assign(
        month=transaction_summary["order_date"].dt.to_period("M").astype(str)
    ).groupby("month").size().reset_index(name="order_count")
    monthly.to_csv(os.path.join(OUTPUT_DIR, "monthly_order_volume.csv"), index=False)

    product_report = item_details.groupby(["product_name", "category"], as_index=False).agg(
        units_sold=("quantity", "sum"),
        item_revenue=("line_total", "sum")
    ).sort_values("units_sold", ascending=False)
    product_report.to_csv(os.path.join(OUTPUT_DIR, "product_quantity_report.csv"), index=False)

    # NumPy statistics for eligible order values.
    values = eligible["order_value"].to_numpy(dtype=float)
    median_value = float(np.median(values)) if len(values) else 0.0
    std_value = float(np.std(values)) if len(values) else 0.0

    print("\n=== ONLINE SHOPPING TRANSACTION ANALYSIS ===")
    print(f"Total orders recorded: {len(transaction_summary)}")
    print(f"Orders included in realized value/AOV: {len(eligible)}")
    print(f"Realized transaction value (INR): ₹{realized_value:,.2f}")
    print(f"Average order value (INR): ₹{avg_order_value:,.2f}")
    print(f"Median eligible order value (INR): ₹{median_value:,.2f}")
    print(f"Standard deviation (INR): ₹{std_value:,.2f}")
    print("\nOrder status report:")
    print(transaction_summary["order_status"].value_counts().to_string())
    print("\nPayment method report:")
    print(payment_report.to_string(index=False))
    print("\nProduct units sold:")
    print(product_report[["product_name", "units_sold"]].to_string(index=False))

    # Chart 1: order status distribution
    status_counts = transaction_summary["order_status"].value_counts()
    plt.figure(figsize=(8, 5))
    status_counts.plot(kind="bar")
    plt.title("Order Status Distribution")
    plt.xlabel("Order Status")
    plt.ylabel("Number of Orders")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "order_status_chart.png"), dpi=150)
    plt.close()

    # Chart 2: payment method distribution
    plt.figure(figsize=(7, 5))
    payment_report.set_index("payment_method")["order_count"].plot(kind="pie", autopct="%1.1f%%")
    plt.title("Payment Method Distribution")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "payment_method_chart.png"), dpi=150)
    plt.close()

    # Chart 3: monthly order volume
    plt.figure(figsize=(9, 5))
    plt.plot(monthly["month"], monthly["order_count"], marker="o")
    plt.title("Monthly Order Volume")
    plt.xlabel("Month")
    plt.ylabel("Number of Orders")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "monthly_order_volume.png"), dpi=150)
    plt.close()

    # Chart 4: product quantities sold
    plt.figure(figsize=(9, 5))
    plt.bar(product_report["product_name"], product_report["units_sold"])
    plt.title("Product Units Sold")
    plt.xlabel("Product")
    plt.ylabel("Units Sold")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "product_quantity_chart.png"), dpi=150)
    plt.close()

    print(f"\nReports and charts saved in: {os.path.abspath(OUTPUT_DIR)}")
    print("Note: Cancelled and Refunded orders are shown in reports but excluded from realized value/AOV.")

if __name__ == "__main__":
    main()
