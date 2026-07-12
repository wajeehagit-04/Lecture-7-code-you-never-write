import os
import re
import sys
import webbrowser

try:
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        script_dir = os.getcwd()

    output_file = os.path.join(script_dir, "index.html")

    print("=" * 60)
    print("              MONEY DETECTIVE: TRANSACTION AUDITOR      ")
    print("=" * 60)
    print("\n📝 Enter transactions lines below. Type 'DONE' on a new line when finished:")

    user_lines = []
    while True:
        line = input().strip()
        if line.upper() == "DONE":
            break
        if line:
            user_lines.append(line)

    if not user_lines:
        sys.exit()

    parsed_transactions = []
    total_income = 0.0
    total_expense = 0.0

    for idx, line in enumerate(user_lines, 1):
        amounts = re.findall(r'\$?\d+(?:\.\d+)?', line)
        if not amounts:
            parsed_transactions.append({"id": idx, "raw": line, "amount": 0.0, "type": "Flagged", "color": "#e74c3c", "desc": "No financial numbers detected."})
            continue

        val = float(amounts[0].replace('$', ''))
        lower_line = line.lower()
        if any(w in lower_line for w in ["spent", "paid", "expense", "buy", "bought", "purchase", "cost"]):
            t_type = "Expense"
            color = "#e67e22"
            total_expense += val
        elif any(w in lower_line for w in ["received", "salary", "income", "deposit", "earned"]):
            t_type = "Income"
            color = "#2ecc71"
            total_income += val
        else:
            t_type = "Unclassified"
            color = "#f1c40f"

        parsed_transactions.append({"id": idx, "raw": line, "amount": val, "type": t_type, "color": color, "desc": "Processed successfully."})

    net_savings = total_income - total_expense
    table_rows = ""
    for t in parsed_transactions:
        table_rows += f"""
        <tr>
            <td><b>#{t['id']}</b></td>
            <td>{t['raw']}</td>
            <td><span class="badge" style="background-color: {t['color']};">{t['type']}</span></td>
            <td><b>${t['amount']:.2f}</b></td>
        </tr>
        """

    html_content = f"""<!DOCTYPE html>
    <html>
    <head>
        <title>Transaction Audit Dashboard</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 40px auto; max-width: 900px; background-color: #f8f9fa; color: #333; }}
            h2 {{ text-align: center; color: #2c3e50; margin-bottom: 30px; }}
            .card {{ background: white; padding: 25px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 25px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #eef2f3; }}
            .badge {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; color: white; }}
            .btn-back {{ display: inline-block; margin-bottom: 20px; color: #2ecc71; text-decoration: none; font-weight: bold; }}
        </style>
    </head>
    <body>
        <a href="../index.html" class="btn-back">← Back to Dashboard</a>
        <h2>Transaction Ledger & Flow Auditor</h2>
        <div class="card">
            <h3>Summary Metrics</h3>
            <p>Income: ${total_income:.2f} | Expenses: ${total_expense:.2f} | Net Balance: ${net_savings:.2f}</p>
        </div>
        <div class="card">
            <table>
                <thead><tr><th>Line</th><th>Raw Text</th><th>Classification</th><th>Amount</th></tr></thead>
                <tbody>{table_rows}</tbody>
            </table>
        </div>
    </body>
    </html>
    """

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    webbrowser.open('file://' + os.path.realpath(output_file))
except Exception as e:
    print(e)
    input()