import os
import sys
import webbrowser

try:
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        script_dir = os.getcwd()

    residents_file = os.path.join(script_dir, "residents.txt")
    ledger_file = os.path.join(script_dir, "ledger.txt")
    output_file = os.path.join(script_dir, "index.html")

    if not os.path.exists(residents_file) or not os.path.exists(ledger_file):
        print("Missing residents.txt or ledger.txt in this folder!")
        input()
        sys.exit()

    residents = {}
    with open(residents_file, "r") as f:
        for line in f:
            if line.strip() and "," in line:
                name, amt = line.strip().split(",", 1)
                residents[name.strip().lower()] = {"name": name.strip(), "expected": float(amt), "paid": 0.0}

    with open(ledger_file, "r") as f:
        for line in f:
            if line.strip() and "," in line:
                name, amt = line.strip().split(",", 1)
                norm_name = name.strip().lower()
                if norm_name in residents:
                    residents[norm_name]["paid"] += float(amt)

    table_rows = ""
    for item in residents.values():
        diff = item["paid"] - item["expected"]
        status = "Matched" if diff == 0 else ("Overpaid" if diff > 0 else "Shortfall")
        color = "#2ecc71" if diff == 0 else ("#3498db" if diff > 0 else "#e74c3c")

        table_rows += f"""
        <tr>
            <td><b>{item['name']}</b></td>
            <td>${item['expected']:.2f}</td>
            <td>${item['paid']:.2f}</td>
            <td><span class="badge" style="background-color: {color};">{status}</span></td>
            <td>{diff:.2f}</td>
        </tr>
        """

    html_content = f"""<!DOCTYPE html>
    <html>
    <head>
        <title>Ledger Reconciliation Audit</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 40px auto; max-width: 950px; background-color: #f8f9fa; color: #333; }}
            h2 {{ text-align: center; color: #2c3e50; margin-bottom: 30px; }}
            .card {{ background: white; padding: 25px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 25px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #eef2f3; }}
            .badge {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; color: white; }}
            .btn-back {{ display: inline-block; margin-bottom: 20px; color: #e67e22; text-decoration: none; font-weight: bold; }}
        </style>
    </head>
    <body>
        <a href="../index.html" class="btn-back">← Back to Dashboard</a>
        <h2>Dual-Ledger Reconciliation & Discrepancy Audit</h2>
        <div class="card">
            <table>
                <thead><tr><th>Account Entity</th><th>Expected</th><th>Actual Paid</th><th>Status</th><th>Variance</th></tr></thead>
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