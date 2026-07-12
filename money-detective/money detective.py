import os
import sys
import re
import webbrowser

print("=" * 60)
print("             SMART AUTO-DETECT TRANSACTION TOOL        ")
print("=" * 60)

try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    script_dir = os.getcwd()

default_input_file = os.path.join(script_dir, "transactions.txt")

# CHANGED: Changed file output name from transaction_audit.html to index.html
output_file = os.path.join(script_dir, "index.html")

user_input = input("👉 Press ENTER to use default file, or paste a custom file path:\n> ").strip()
input_file = os.path.normpath(user_input.strip('"').strip("'").strip()) if user_input else default_input_file

if not os.path.exists(input_file):
    print(f"\n❌ [CRITICAL ERROR]: The file does not exist at: '{input_file}'")
    input("\nPress ENTER to close...")
    sys.exit()

transactions = []
merchant_counts = {}

print("\n[STEP 3] Analyzing data format and parsing rows...")
try:
    with open(input_file, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, 1):
            line = line.strip()
            if not line or "total" in line.lower() or "description" in line.lower():
                continue # Skip blank lines and headers safely
            
            # Smart Regex: Splits lines by tabs, pipes, or 2+ consecutive spaces
            parts = re.split(r'\t|\||\s{2,}', line)
            parts = [x.strip() for x in parts if x.strip()]
            
            if len(parts) >= 3:
                # Expecting layout: Date, Description, Amount
                date, desc, amt = parts[0], parts[1], parts[2]
                transactions.append({"date": date, "desc": desc, "amt": amt})
                merchant_counts[desc] = merchant_counts.get(desc, 0) + 1
            else:
                # Fallback: If elements are separated by just a single space
                parts_single = line.split(" ")
                if len(parts_single) >= 3:
                    # Try to capture a date pattern YYYY-MM-DD at the front
                    if re.match(r'\d{4}-\d{2}-\d{2}', parts_single[0]):
                        date = parts_single[0]
                        amt = parts_single[-1]
                        desc = " ".join(parts_single[1:-1])
                        transactions.append({"date": date, "desc": desc, "amt": amt})
                        merchant_counts[desc] = merchant_counts.get(desc, 0) + 1

except Exception as e:
    print(f"\n❌ [CRITICAL ERROR]: Failed to read file data: {e}")
    input("\nPress ENTER to close...")
    sys.exit()

print(f"         -> Successfully parsed {len(transactions)} transaction rows.")

if not transactions:
    print("\n❌ [CRITICAL ERROR]: Parsed 0 rows.")
    print("   The script couldn't identify the columns automatically.")
    print("   Please ensure your text file lines start with a date (like 2026-06-01).")
    input("\nPress ENTER to close...")
    sys.exit()

# Compile the HTML page
html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Transaction Audit</title>
    <style>
        body {{ font-family: system-ui, -apple-system, sans-serif; margin: 40px; background-color: #f8f9fa; }}
        h2 {{ color: #333; margin-bottom: 5px; }}
        .legend {{ margin-bottom: 20px; padding: 15px; background: white; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .legend-item {{ display: inline-block; margin-right: 20px; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden; }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background-color: #f1f3f5; color: #495057; }}
        .duplicate {{ background-color: #ffcccc !important; color: #cc0000; font-weight: bold; }}
        .subscription {{ background-color: #fff2cc !important; color: #856404; }}
        .repeated {{ background-color: #d1ecf1 !important; color: #0c5460; }}
        
        /* ADDED: Uniform Navigation Style matching your other assignments */
        .nav-menu {{ background: #2c3e50; padding: 12px; border-radius: 8px; text-align: center; margin-bottom: 25px; }}
        .nav-menu a {{ color: white; text-decoration: none; margin: 0 15px; font-weight: bold; font-size: 14px; }}
        .nav-menu a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <!-- ADDED: Navigation Bar utilizing safe Relative Paths -->
    <div class="nav-menu">
        <a href="../task1/index.html">Task 1</a>
        <a href="../task2/index.html">Task 2</a>
        <a href="../task-grade-report/index.html">Grade Report</a>
        <a href="index.html" style="color: #f1c40f;">Transaction Audit</a>
    </div>

    <h2>Monthly Financial Audit Report</h2>
    <p>Source file processed: <b>{os.path.basename(input_file)}</b></p>
    <div class="legend">
        <span class="legend-item" style="color: #cc0000;">■ Duplicate Charge</span>
        <span class="legend-item" style="color: #856404;">■ Subscription / Fixed Recurring</span>
        <span class="legend-item" style="color: #0c5460;">■ Repeated Spending</span>
    </div>
    <table>
        <tr><th>Date</th><th>Description</th><th>Amount</th></tr>"""

sub_keywords = ['subscription', 'renew', 'premium', 'membership', 'rent', 'light', 'power']

for i, tx in enumerate(transactions):
    row_class = ""
    desc_lower = tx['desc'].lower()
    
    is_duplicate = any(
        (tx['date'] == other['date'] and tx['desc'] == other['desc'] and tx['amt'] == other['amt'] and i != idx)
        for idx, other in enumerate(transactions)
    )
    is_sub = any(kw in desc_lower for kw in sub_keywords)
    
    if is_duplicate: row_class = "duplicate"
    elif is_sub: row_class = "subscription"
    elif merchant_counts[tx['desc']] > 1: row_class = "repeated"
        
    html_content += f'<tr class="{row_class}"><td>{tx["date"]}</td><td>{tx["desc"]}</td><td>{tx["amt"]}</td></tr>'

html_content += "</table></body></html>"

try:
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"\n🎉 SUCCESS! HTML file written successfully to:")
    print(f"   👉 {output_file}")
    webbrowser.open('file://' + os.path.realpath(output_file))
except Exception as e:
    print(f"\n❌ [CRITICAL ERROR]: Could not write file to your hard drive: {e}")

print("\n" + "="*60)
input("Execution finished. Press ENTER to close...")