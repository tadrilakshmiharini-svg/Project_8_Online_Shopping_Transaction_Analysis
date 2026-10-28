# Project 8: Online Shopping Transaction Analysis System

## Requirements
- Python 3.10 or newer recommended
- pandas, numpy, matplotlib
- MySQL Server (optional for demo mode; required for database mode)

## Run in demo mode
1. Open this folder in VS Code.
2. Open Terminal > New Terminal.
3. Install dependencies:
   `python -m pip install -r requirements.txt`
4. Run:
   `python main.py`
5. Open the `output` folder for CSV reports and PNG charts.

The program uses built-in sample data if MySQL is not reachable/configured.

## Enable MySQL
1. Open MySQL Workbench and connect to your local server.
2. Open `schema.sql` and execute all statements.
3. Configure these environment variables in the terminal before running Python:
   PowerShell:
   `$env:MYSQL_HOST="localhost"`
   `$env:MYSQL_USER="root"`
   `$env:MYSQL_PASSWORD="YOUR_MYSQL_PASSWORD"`
   `$env:MYSQL_DATABASE="online_shopping"`
4. Run `python main.py` again.

## Generated files
- `transaction_summary.csv`
- `order_status_report.csv`
- `payment_method_report.csv`
- `monthly_order_volume.csv`
- `product_quantity_report.csv`
- `order_status_chart.png`
- `payment_method_chart.png`
- `monthly_order_volume.png`
- `product_quantity_chart.png`

## Business rules
- Order value is calculated by summing quantity × unit_price from order_items.
- The unit price stored on each order item is used to preserve the price at the time of purchase.
- Cancelled and Refunded orders are retained in order-level reports but excluded from realized transaction value and average order value.
- Average order value is the mean order value for Processing, Shipped, and Delivered orders in this sample.
- Sample data is fictional and should be replaced with real/approved project data if available.

## Troubleshooting
- If `python` is not recognized, install Python and enable "Add Python to PATH".
- If packages are missing, run `python -m pip install -r requirements.txt`.
- If MySQL connection fails, the script falls back to sample data. Check MySQL service, database name, username, password, and SQL setup.
