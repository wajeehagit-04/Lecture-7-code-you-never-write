import os
import sys
import webbrowser

print("=" * 60)
print("             BIRYANI & MATCH LEDGER RECONCILIATION TOOL        ")
print("=" * 60)

# This automatically grabs the exact folder where this python file lives
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    script_dir = os.getcwd()

# Dynamically pointing to your txt files in the same repository folder
residents_file = os.path.join(script_dir, "residents.txt")
ledger_file = os.path.join(script_dir, "ledger.txt")
output_file = os.path.join(script_dir, "index.html")

# Path Safety Check to prevent sudden window closures
if not os.path.exists(residents_file) or not os.path.exists(ledger_file):
    print("\n❌ [CRITICAL PATH ERROR]: Could not find the text files!")
    print(f"Looking inside folder: {script_dir}")
    print("\nPlease verify:")
    print("1. Both 'residents.txt' and 'ledger.txt' are inside that exact folder.")
    print("2. They are not named 'residents.txt.txt' by mistake.")
    print("\n" + "="*60)
    input("Press ENTER to close and check your folder layout...")
    sys.exit()

# 1. Parse Baseline Residents Profile Datastream
residents = {}
expected_total = 0

with open(residents_file, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line: continue
        flat, name, expected = line.split(",")
        expected = int(expected)
        residents[flat] = {
            "name": name,
            "expected": expected,
            "paid": 0
        }
        expected_total += expected

# 2. Track Audit Logs & Process Payments Realtime
audit_trail_html = ""
actual_collected = 0

with open(ledger_file, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line: continue
        txid, source, mapped, memo, amt = line.split("|")
        amt_val = int(amt)
        actual_collected += amt_val
        
        # Append rows dynamically onto audit table log stream
        audit_trail_html += f"""
        <tr>
            <td style="font-family: monospace;">{txid}</td>
            <td>{source}</td>
            <td>{mapped}</td>
            <td><i>{memo}</i></td>
            <td style="text-align: right;">{amt_val:,} PKR</td>
        </tr>"""
        
        # Smart Map Account Processing Logic (Parsing the split block manually)
        if "401 and 402" in memo:
            split_amt = amt_val // 2
            residents["401"]["paid"] += split_amt
            residents["402"]["paid"] += split_amt
        else:
            # Map standard payments via unique string pattern detection
            for flat in residents:
                if f"Flat {flat}" in mapped or f"({flat})" in mapped:
                    residents[flat]["paid"] += amt_val
                    break

total_deficit = expected_total - actual_collected

# 3. Build Ledger Status Tables Stream
ledger_rows_html = ""
actions_html = ""

for flat, data in sorted(residents.items()):
    variance = data["paid"] - data["expected"]
    
    if data["paid"] == data["expected"]:
        badge = '<span class="badge-success">FULLY PAID</span>'
        var_style = "0"
    elif data["paid"] > 0:
        badge = '<span class="badge-warning">PARTIAL</span>'
        var_style = f'<td style="color: #b91c1c;">{variance:,}</td>'
        actions_html += f'<div style="margin-bottom: 8px; padding-bottom: 8px; border-bottom: 1px dashed #fcd34d;"><strong>⚠️ Flat {flat} - {data["name"]}:</strong> Shortfall of <strong>PKR {abs(variance):,}</strong>. Follow up to collect balance.</div>\n'
    else:
        badge = '<span class="badge-danger">UNPAID</span>'
        var_style = f'<td style="color: #b91c1c;">{variance:,}</td>'
        actions_html += f'<div style="margin-bottom: 8px; padding-bottom: 8px; border-bottom: 1px dashed #fcd34d;"><strong>❌ Flat {flat} - {data["name"]}:</strong> Missing full payment of <strong>PKR {data["expected"]:,}</strong>. No digital record found.</div>\n'
        
    if var_style == "0":
        var_style = f'<td>0</td>'

    ledger_rows_html += f"""
    <tr>
        <td>{flat}</td>
        <td>{data['name']}</td>
        <td>{data['expected']:,}</td>
        <td>{data['paid']:,}</td>
        {var_style}
        <td>{badge}</td>
    </tr>"""

# 4. Generate Final Styled HTML Output
html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Financial Reconciliation Report</title>
    <style>
        body {{ font-family: 'Helvetica Neue', Arial, sans-serif; color: #1e293b; background-color: #f8fafc; padding: 40px; max-width: 900px; margin: 0 auto; }}
        .header {{ border-bottom: 3px solid #0f172a; padding-bottom: 12px; margin-bottom: 24px; }}
        .cards {{ display: flex; gap: 16px; margin-bottom: 24px; }}
        .card {{ flex: 1; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px; padding: 20px; text-align: center; }}
        .card-val {{ font-size: 18pt; font-weight: bold; margin-top: 4px; }}
        table {{ width: 100%; border-collapse: collapse; background: #ffffff; border: 1px solid #e2e8f0; margin-bottom: 30px; border-radius: 6px; overflow: hidden; }}
        th {{ background-color: #1e293b; color: #ffffff; padding: 12px; text-align: left; font-size: 9.5pt; text-transform: uppercase; }}
        td {{ padding: 12px; border-bottom: 1px solid #e2e8f0; font-size: 10pt; }}
        tr:nth-child(even) {{ background-color: #f8fafc; }}
        .box {{ background-color: #fffbeb; border: 1px solid #fde68a; border-radius: 6px; padding: 16px; }}
        .badge-success {{ background-color: #dcfce7; color: #15803d; padding: 2px 6px; font-size: 8pt; font-weight: bold; border-radius: 4px; }}
        .badge-warning {{ background-color: #fef9c3; color: #a16207; padding: 2px 6px; font-size: 8pt; font-weight: bold; border-radius: 4px; }}
        .badge-danger {{ background-color: #fee2e2; color: #b91c1c; padding: 2px 6px; font-size: 8pt; font-weight: bold; border-radius: 4px; }}
        
        .nav-menu {{ background: #0f172a; padding: 14px; border-radius: 6px; text-align: center; margin-bottom: 25px; }}
        .nav-menu a {{ color: #94a3b8; text-decoration: none; margin: 0 15px; font-weight: bold; font-size: 14px; transition: color 0.2s; }}
        .nav-menu a:hover {{ color: white; }}
    </style>
</head>
<body>
    <div class="nav-menu">
        <a href="../my-grade/index.html">Grade Report</a>
        <a href="../money-detective/index.html">Transaction Audit</a>
        <a href="index.html" style="color: #f59e0b;">Books Reconciliation</a>
    </div>

    <div class="header">
        <h1 style="margin:0;">Reconciled Set of Books</h1>
        <div style="color: #475569;">Match Screening & Biryani Night Fund Ledger</div>
    </div>

    <div class="cards">
        <div class="card"><div>Expected Total</div><div class="card-val">PKR {expected_total:,}</div></div>
        <div class="card"><div>Actual Collected</div><div class="card-val" style="color: #2563eb;">PKR {actual_collected:,}</div></div>
        <div class="card" style="background-color: #fff1f2; border-color: #fecdd3;"><div>Total Deficit</div><div class="card-val" style="color: #be123c;">PKR {total_deficit:,}</div></div>
    </div>

    <h2>1. Household Ledger Status</h2>
    <table>
        <thead><tr><th>Flat</th><th>Resident Name</th><th>Expected (PKR)</th><th>Paid (PKR)</th><th>Variance (PKR)</th><th>Status</th></tr></thead>
        <tbody>
            {ledger_rows_html}
        </tbody>
    </table>

    <h2>2. Audit Trail (Processed App Statements)</h2>
    <table>
        <thead><tr><th>TXN ID</th><th>Source Name</th><th>Mapped Resident</th><th>Memo Context</th><th style="text-align: right;">Amount</th></tr></thead>
        <tbody>
            {audit_trail_html}
        </tbody>
    </table>

    <h2>3. Required Actions & Follow-Ups</h2>
    <div class="box">
        {actions_html}
    </div>
</body>
</html>"""

try:
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"\n🎉 SUCCESS! Verified HTML index report rendered completely at:")
    print(f"   👉 {output_file}")
    webbrowser.open('file://' + os.path.realpath(output_file))
except Exception as e:
    print(f"\n❌ [CRITICAL RUNTIME ERROR]: File generation failure: {e}")

print("\n" + "="*60)
input("Processing complete. Press ENTER to exit safely...")