# MySQL NL2SQL Local

A lightweight tool that converts natural language questions into MySQL queries using a local LLM through Ollama.

## 🌟 Features

- **Natural Language → SQL**: Ask questions in plain English and get MySQL queries
- **Local Execution**: All processing happens on your machine with Ollama
- **Zero Cloud Dependencies**: No API keys or internet connection required
- **MySQL Integration**: Directly connects to your MySQL database
- **Formatted Results**: Clean, tabulated output of query results

## 📋 Requirements

- Python 3.7+
- MySQL Server
- [Ollama](https://github.com/ollama/ollama) with the `pxlksr/defog_sqlcoder-7b-2:Q4_K_M` model

## 🚀 Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/mysql-nl2sql-local.git
cd mysql-nl2sql-local
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Install Ollama**
   
Follow the instructions at [ollama.ai](https://ollama.ai/) to install Ollama on your system.

4. **Pull the SQL model**

```bash
ollama pull pxlksr/defog_sqlcoder-7b-2:Q4_K_M
```

5. **Update database configuration**

Open `main.py` and update the MySQL configuration:

```python
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "your_username",
    "password": "your_password",
    "database": "your_database"
}
```

## 🔧 Usage

Run the tool:

```bash
python main.py
```

Then enter your question when prompted:

```
💬 Ask your question: Show me total invoice amounts by month for the last 6 months
```

The tool will:
1. Generate the SQL query
2. Execute it against your database
3. Display the results in a formatted table

## 📝 Example

Input:
```
💬 Ask your question: What vendors have the highest total purchase orders?
```

Output:
```
🧠 Generated SQL:
SELECT p.`Vendor Name`, SUM(p.`Total Price`) AS total_amount
FROM `purchase_order` p
GROUP BY p.`Vendor Name`
ORDER BY total_amount DESC
LIMIT 10;

📊 Query Result:
+----------------+--------------+
| Vendor Name    | total_amount |
+----------------+--------------+
| Acme Corp      | 78500.00     |
| Globex Supply  | 65200.00     |
| Tech Solutions | 45800.00     |
+----------------+--------------+
```

## 🛠 Customization

### Using a Different Model

You can change the LLM by modifying the `OLLAMA_MODEL` variable:

```python
OLLAMA_MODEL = "your-preferred-model"
```

### Modifying the Schema Hint

If your database schema changes, update the `SCHEMA_HINT` to match your tables and columns.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🙏 Acknowledgements

- [Ollama](https://github.com/ollama/ollama) for the local LLM server
- [Defog.ai](https://defog.ai/) for the SQLCoder model architecture
