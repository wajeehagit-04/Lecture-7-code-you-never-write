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

    # Path Safety Check
    if not os.path.exists(residents_file) or not os.path.exists(ledger_file):
        print("\n❌ [CRITICAL PATH ERROR]: Missing required data files!")
        print(f"Ensure 'residents.txt' and 'ledger.txt' are inside: {script_dir}")
        input("\nPress ENTER to close...")
        sys.exit()

    # --- PARSE TEXT FILES ---
    residents = {}
    expected_total = 0.0

    with open(residents_file, "r") as f:
        for line in f:
            if line.strip() and "," in line:
                name, amt = line.strip().split(",", 1)
                try:
                    val = float(amt)
                    residents[name.strip().lower()] = {"name": name.strip(), "expected": val, "paid": 0.0}
                    expected_total += val
                except ValueError:
                    continue

    actual_total = 0.0
    with open(ledger_file, "r") as f:
        for line in f:
            if line.strip() and "," in line:
                name, amt = line.strip().split(",", 1)
                try:
                    val = float(amt)
                    norm_name = name.strip().lower()
                    if norm_name in residents:
                        residents[norm_name]["paid"] += val
                    else:
                        residents[norm_name] = {"name": name.strip() + " (Unregistered)", "expected": 0.0, "paid": val}
                    actual_total += val
                except ValueError:
                    continue

    # --- PROCESS CORRELATION ---
    discrepancy_count = 0
    table_rows = ""

    for item in residents.values():
        diff = item["paid"] - item["expected"]
        
        if diff == 0:
            status = "Matched"
            color = "#2ecc71"
            comment = "Account balances perfectly."
        elif diff > 0:
            status = "Overpaid"
            color = "#3498db"
            comment = f"Paid a surplus variance of +${abs(diff):.2f}."
            discrepancy_count += 1
        else:
            status = "Shortfall"
            color = "#e74c3c"
            comment = f"Owes a outstanding deficiency of -${abs(diff):.2f}."
            discrepancy_count += 1

        table_rows += f"""
        <tr>
            <td><b>{item['name']}</b></td>
            <td>${item['expected']:.2f}</td>
            <td>${item['paid']:.2f}</td>
            <td><span class="badge" style="background-color: {color};">{status}</span></td>
            <td style="font-family: monospace; color: {color if diff != 0 else '#7f8c8d'};">
                {'+' if diff > 0 else ''}{diff:.2f}
            </td>
            <td style="font-size: 13px; color: #7f8c8d;">{comment}</td>
        </tr>
        """

    variance_total = actual_total - expected_total
    variance_color = "#2ecc71" if variance_total == 0 else ("#3498db" if variance_total > 0 else "#e74c3c")

    # --- BUILD STANDALONE HTML ---
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
            th {{ background-color: #fcfcfc; color: #7f8c8d; font-size: 13px; text-transform: uppercase; }}
            .badge {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; color: white; }}
            .metric-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; }}
            .metric {{ background: #fdfefe; border: 1px solid #eef2f3; padding: 15px; border-radius: 6px; text-align: center; }}
            .metric-num {{ font-size: 20px; font-weight: bold; margin-top: 5px; color: #2c3e50; }}
        </style>
    </head>
    <body>
        <h2>Dual-Ledger Reconciliation & Discrepancy Audit</h2>
        
        <div class="card">
            <h3 style="margin-top:0;">Global Balanced Metrics</h3>
            <div class="metric-grid">
                <div class="metric">
                    <div style="color: #7f8c8d; font-size: 12px;">EXPECTED ACCRUAL</div>
                    <div class="metric-num">${expected_total:.2f}</div>
                </div>
                <div class="metric">
                    <div style="color: #7f8c8d; font-size: 12px;">ACTUAL COLLECTED</div>
                    <div class="metric-num">${actual_total:.2f}</div>
                </div>
                <div class="metric">
                    <div style="color: #7f8c8d; font-size: 12px;">NET VARIANCE GAP</div>
                    <div class="metric-num" style="color: {variance_color};">${variance_total:.2f}</div>
                </div>
                <div class="metric">
                    <div style="color: #7f8c8d; font-size: 12px;">FLAGGED ACCOUNTS</div>
                    <div class="metric-num" style="color: {'#e74c3c' if discrepancy_count > 0 else '#2ecc71'};">{discrepancy_count}</div>
                </div>
            </div>
        </div>

        <div class="card">
            <h3 style="margin-top:0;">Account Cross-Examination Register</h3>
            <table>
                <thead>
                    <tr>
                        <th>Account Entity</th>
                        <th>Expected Target</th>
                        <th>Actual Deposited</th>
                        <th>Status Flag</th>
                        <th>Variance</th>
                        <th>Audit Conclusion Notes</th>
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
    print("\n🎉 SUCCESS! Reconciliation HTML generated successfully!")
    print(f"👉 File saved as: {output_file}")
    webbrowser.open('file://' + os.path.realpath(output_file))

    print("\n" + "="*60)
    input("Execution finished. Press ENTER to close...")

except Exception as major_error:
    print(f"\n❌ A critical error occurred: {major_error}")
    input("Press ENTER to close...")