import requests
import mysql.connector
from tabulate import tabulate

# --- CONFIG ---
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "pxlksr/defog_sqlcoder-7b-2:Q4_K_M"
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "12345678",  # update your password
    "database": "vertical_ai_db"
}

# --- Your schema in plain English ---
SCHEMA_HINT = """
⚠️ CRITICAL SQL SYNTAX RULES FOR YOUR DATABASE ⚠️

1. Column names contain spaces and capital letters, and MUST be used EXACTLY as written below:
   - `Total Price` (NOT total_price, TotalPrice, or Total_Price)
   - `Due Date` (NOT due_date, DueDate, or Due_Date)
   - `Vendor Name` (NOT vendor_name, VendorName, or Vendor_Name)

2. Table structure - CHECK AVAILABLE COLUMNS CAREFULLY:
   a) `purchase_order`:
      - `PO Number` 
      - `Date`
      - `Vendor Name`
      - `Total Price`
      - `Status`

   b) `invoices_withPO`:
      - `Total Price`
      - `Due Date`  (this is the date column for invoices, NOT `Date`)
      - `Status`

3. ALIASES WITH COLUMNS - MOST CRITICAL ISSUE:
   When using a table alias, you MUST:
   * Put backticks around the column name
   * Use EXACT column name with spaces and capitals
   * The alias does not get backticks
   
   CORRECT:
   - i.`Total Price`
   - i.`Due Date`
   - p.`Vendor Name`
   
   INCORRECT (WILL CAUSE ERRORS):
   - i.total_price  ❌
   - i.due_date     ❌
   - p.vendor_name  ❌

4. MYSQL-SPECIFIC DATE FUNCTIONS - CRITICAL:
   Use only MySQL date functions (not PostgreSQL or SQL Server):
   
   CORRECT (MySQL syntax):
   - Extract month: MONTH(`Date`)
   - Extract year: YEAR(`Date`) 
   - Format date: DATE_FORMAT(`Date`, '%Y-%m')
   - Last N months: WHERE `Date` >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
   - Group by month: GROUP BY YEAR(`Date`), MONTH(`Date`)
   - Group by month/year: GROUP BY DATE_FORMAT(`Date`, '%Y-%m')
   
   INCORRECT (non-MySQL syntax):
   - DATE_TRUNC('month', `Date`)  ❌ (PostgreSQL syntax)
   - DATEPART(month, `Date`)  ❌ (SQL Server syntax)
   - EXTRACT(MONTH FROM `Date`)  ❌ (PostgreSQL/Oracle syntax)
   - ORDER BY x NULLS LAST  ❌ (Not MySQL syntax)

5. Complete correct examples for MySQL:
   - SELECT DATE_FORMAT(p.`Date`, '%Y-%m') AS month, SUM(p.`Total Price`) 
     FROM `purchase_order` AS p 
     WHERE p.`Date` >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
     GROUP BY DATE_FORMAT(p.`Date`, '%Y-%m')
     ORDER BY month;

   - SELECT YEAR(i.`Due Date`) AS year, MONTH(i.`Due Date`) AS month, SUM(i.`Total Price`) 
     FROM `invoices_withPO` i 
     WHERE i.`Due Date` BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 14 DAY)
     GROUP BY YEAR(i.`Due Date`), MONTH(i.`Due Date`)
     ORDER BY year, month;

6. Common errors to avoid:
   - Using lowercase column names
   - Removing spaces from column names
   - Forgetting backticks around column names
   - Using table alias without backticks around column names
   - Using non-MySQL date functions
   - Using `Date` column for `invoices_withPO` (it only has `Due Date`)

⚠️ VERIFY column names match EXACTLY with backticks ⚠️
⚠️ USE MySQL-specific functions like DATE_FORMAT and DATE_SUB ⚠️
⚠️ CHECK that you're using columns that actually exist in each table ⚠️
"""

# --- STEP 1: Generate SQL from natural language ---
def get_sql_from_nl(nl_query):
    prompt = f"""
{SCHEMA_HINT}

Translate the following question into a valid MySQL query.

Question: "{nl_query}"
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }
    )
    response.raise_for_status()
    result = response.json()
    return result['response'].strip('`\n ')

# --- STEP 2: Execute SQL on MySQL ---
def run_sql_query(sql):
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    columns = cursor.column_names
    conn.close()
    return columns, results

# --- MAIN ---
if __name__ == "__main__":
    question = input("💬 Ask your question: ")

    try:
        sql = get_sql_from_nl(question)
        print(f"\n🧠 Generated SQL:\n{sql}")

        columns, results = run_sql_query(sql)
        print("\n📊 Query Result:")
        print(tabulate(results, headers=columns, tablefmt="fancy_grid"))

    except Exception as e:
        print("❌ Error:", e)