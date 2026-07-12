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

    # --- CLI INTERFACE ---
    print("=" * 60)
    print("              MONEY DETECTIVE: TRANSACTION AUDITOR      ")
    print("=" * 60)

    print("\n📝 ENTER TRANSACTION LOGS")
    print("Paste your transaction lines below. Each line should contain an amount.")
    print("Example:\nReceived $2500 from salary\nSpent 45.50 at Grocery Store\nPaid $120 for utilities")
    print("\n👉 Type 'DONE' on a new line and press Enter when finished.")

    user_lines = []
    while True:
        line = input().strip()
        if line.upper() == "DONE":
            break
        if line:
            user_lines.append(line)

    if not user_lines:
        print("❌ No transactions entered. Exiting...")
        sys.exit()

    # --- PROCESSING LOGIC ---
    parsed_transactions = []
    total_income = 0.0
    total_expense = 0.0

    for idx, line in enumerate(user_lines, 1):
        # Look for dollar numbers or raw decimals/integers
        amounts = re.findall(r'\$?\d+(?:\.\d+)?', line)
        
        if not amounts:
            parsed_transactions.append({
                "id": idx, "raw": line, "amount": 0.0, "type": "Flagged", 
                "color": "#e74c3c", "desc": "No financial numbers detected."
            })
            continue

        # Take the first clear number found
        raw_num = amounts[0].replace('$', '')
        val = float(raw_num)

        # Basic text pattern classification
        lower_line = line.lower()
        if any(w in lower_line for w in ["spent", "paid", "expense", "buy", "bought", "purchase", "cost"]):
            t_type = "Expense"
            color = "#e67e22"
            total_expense += val
            desc = "Categorized via expense keywords."
        elif any(w in lower_line for w in ["received", "salary", "income", "deposit", "earned", "gain"]):
            t_type = "Income"
            color = "#2ecc71"
            total_income += val
            desc = "Categorized via income keywords."
        else:
            t_type = "Unclassified"
            color = "#f1c40f"
            desc = "Unclear directional language. Needs manual verification."

        parsed_transactions.append({
            "id": idx, "raw": line, "amount": val, "type": t_type, "color": color, "desc": desc
        })

    net_savings = total_income - total_expense
    savings_color = "#2ecc71" if net_savings >= 0 else "#e74c3c"

    # --- BUILD STANDALONE HTML ---
    table_rows = ""
    for t in parsed_transactions:
        table_rows += f"""
        <tr>
            <td><b>#{t['id']}</b></td>
            <td style="font-family: monospace; font-size: 13px;">{t['raw']}</td>
            <td><span class="badge" style="background-color: {t['color']};">{t['type']}</span></td>
            <td><b>${t['amount']:.2f}</b></td>
            <td style="font-size: 13px; color: #7f8c8d;">{t['desc']}</td>
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
            th {{ background-color: #fcfcfc; color: #7f8c8d; font-size: 13px; text-transform: uppercase; }}
            .badge {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; color: white; }}
            .metric-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }}
            .metric {{ background: #fdfefe; border: 1px solid #eef2f3; padding: 15px; border-radius: 6px; text-align: center; }}
            .metric-num {{ font-size: 24px; font-weight: bold; margin-top: 5px; }}
        </style>
    </head>
    <body>
        <h2>Transaction Ledger & Flow Auditor</h2>
        
        <div class="card">
            <h3 style="margin-top:0;">Ledger Summary Metrics</h3>
            <div class="metric-grid">
                <div class="metric">
                    <div style="color: #7f8c8d; font-size: 13px;">TOTAL INCOME REVENUE</div>
                    <div class="metric-num" style="color: #2ecc71;">${total_income:.2f}</div>
                </div>
                <div class="metric">
                    <div style="color: #7f8c8d; font-size: 13px;">TOTAL EXPENSE OUTFLOW</div>
                    <div class="metric-num" style="color: #e67e22;">${total_expense:.2f}</div>
                </div>
                <div class="metric">
                    <div style="color: #7f8c8d; font-size: 13px;">NET RESIDUAL SURPLUS</div>
                    <div class="metric-num" style="color: {savings_color};">${net_savings:.2f}</div>
                </div>
            </div>
        </div>

        <div class="card">
            <h3 style="margin-top:0;">Detailed Line-Item Audit</h3>
            <table>
                <thead>
                    <tr>
                        <th style="width: 8%;">Line</th>
                        <th style="width: 40%;">Raw Transaction Text</th>
                        <th style="width: 15%;">Classification</th>
                        <th style="width: 15%;">Extracted Amount</th>
                        <th style="width: 22%;">Audit Analysis Flag</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print("\n🎉 SUCCESS! Money Detective HTML generated successfully!")
    print(f"👉 File saved as: {output_file}")
    webbrowser.open('file://' + os.path.realpath(output_file))

    print("\n" + "="*60)
    input("Execution finished. Press ENTER to close...")

except Exception as major_error:
    print(f"\n❌ A critical error occurred: {major_error}")
    input("Press ENTER to close...")