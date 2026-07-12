import os
import re
import sys
import webbrowser

try:
    # Scale details based on your teacher's rules
    GRADING_SCALE = [
        {"grade": "A", "min": 90.0, "max": 100.0, "desc": "Excellent", "color": "#2ecc71"},
        {"grade": "B", "min": 80.0, "max": 89.9, "desc": "Good", "color": "#3498db"},
        {"grade": "C", "min": 70.0, "max": 79.9, "desc": "Satisfactory", "color": "#f1c40f"},
        {"grade": "D", "min": 60.0, "max": 69.9, "desc": "Passing", "color": "#e67e22"},
        {"grade": "F", "min": 0.0, "max": 59.9, "desc": "Failing", "color": "#e74c3c"}
    ]

    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        script_dir = os.getcwd()

    output_file = os.path.join(script_dir, "index.html")

    def get_letter_grade(percentage):
        for scale in GRADING_SCALE:
            if percentage >= scale["min"]:
                return scale["grade"], scale["desc"], scale["color"]
        return "F", "Failing", "#e74c3c"

    def parse_fraction(text):
        """Parses inputs like '15/20', '42 / 50' into (earned, total)."""
        text = text.strip()
        matches = re.findall(r'\d+(?:\.\d+)?', text)
        if len(matches) >= 2:
            return float(matches[0]), float(matches[1])
        elif len(matches) == 1:
            return float(matches[0]), 100.0
        raise ValueError("Invalid format. Use Earned/Total.")

    # --- CLI INTERFACE ---
    print("=" * 60)
    print("         RAW MARKS GRADE AUDIT & TARGET CALCULATOR      ")
    print("=" * 60)

    quizzes = []
    
    print("\n📝 ENTER QUIZ MARKS")
    print("Enter your quizzes using the format: Earned/Total")
    print("Separate multiple quizzes with commas or spaces.")
    print("Example: 15/20, 18/20, 35/50, 9/10")
    
    while not quizzes:
        quiz_input = input("\nEnter your Quizzes:\n> ").strip()
        raw_pairs = re.findall(r'\d+(?:\.\d+)?\s*/\s*\d+(?:\.\d+)?', quiz_input)
        
        for pair in raw_pairs:
            try:
                earned, total = parse_fraction(pair)
                if total > 0:
                    quizzes.append({"earned": earned, "total": total, "pct": (earned / total) * 100})
            except ValueError:
                continue
                
        if not quizzes:
            print("❌ No valid entries found. Make sure you use slashes like: 15/20, 45/50")

    print("\n📝 ENTER FINAL EXAM")
    print("How many marks is the Final Exam worth in total?")
    final_total = 0.0
    while final_total <= 0:
        total_input = input("Total possible marks for the Final Exam (e.g. 100 or 60):\n> ").strip()
        try:
            final_total = float(re.search(r'\d+(?:\.\d+)?', total_input).group())
        except (ValueError, AttributeError):
            print("❌ Please enter a valid number for the total marks.")

    print(f"\nHave you taken the Final Exam yet? (Out of {final_total})")
    print("👉 Enter your score as Earned/Total (e.g. 80/100 or 45/60)")
    print("👉 Or press ENTER to leave it blank if you haven't taken it.")
    
    final_exam_earned = None
    final_input_loop = True
    while final_input_loop:
        final_input = input("\nYour Final Exam Score:\n> ").strip()
        if not final_input:
            final_exam_earned = None
            final_input_loop = False
        else:
            try:
                earned, total = parse_fraction(final_input)
                final_exam_earned = earned
                final_total = total
                final_input_loop = False
            except ValueError:
                print(f"❌ Please enter it as numbers with a slash (e.g. 40/{final_total}) or leave it blank.")

    # --- DROP LOWEST QUIZ MATH ---
    raw_quizzes = quizzes.copy()
    dropped_quiz = None

    if len(quizzes) >= 2:
        dropped_quiz = min(quizzes, key=lambda x: x["pct"])
        quizzes.remove(dropped_quiz)

    total_quiz_earned = sum(q["earned"] for q in quizzes)
    total_quiz_possible = sum(q["total"] for q in quizzes)
    quiz_average_pct = (total_quiz_earned / total_quiz_possible) * 100

    final_standing_html = ""
    target_forecast_html = ""

    if final_exam_earned is not None:
        final_exam_pct = (final_exam_earned / final_total) * 100
        overall_score = (quiz_average_pct * 0.5) + (final_exam_pct * 0.5)
        letter, desc, color = get_letter_grade(overall_score)
        
        final_standing_html = f"""
        <div class="card" style="border-top: 5px solid {color}; text-align: center;">
            <h3 style="margin-top:0;">Your Overall Class Standing</h3>
            <div style="font-size: 48px; font-weight: bold; color: {color};">{letter}</div>
            <div style="font-size: 20px; font-weight: bold; margin: 10px 0;">{overall_score:.2f}% ({desc})</div>
            <p style="color: #666; font-size: 14px;">
                Quizzes (50% weight): {total_quiz_earned:.1f}/{total_quiz_possible:.1f} ({quiz_average_pct:.1f}%) <br>
                Final Exam (50% weight): {final_exam_earned:.1f}/{final_total:.1f} ({final_exam_pct:.1f}%)
            </p>
        </div>
        """
    else:
        print("\n🎯 DESIRED GRADE PREVIEW")
        print("Which letter grade are you aiming for? (A, B, C, or D)")
        desired_letter = ""
        while desired_letter not in ["A", "B", "C", "D"]:
            desired_letter = input("Enter your target letter grade:\n> ").strip().upper()

        target_scale = next(s for s in GRADING_SCALE if s["grade"] == desired_letter)
        target_min_pct = target_scale["min"]

        needed_final_pct = (target_min_pct - (quiz_average_pct * 0.5)) / 0.5
        needed_marks = (needed_final_pct / 100) * final_total

        if needed_marks <= 0:
            status_message = f"🎉 Good news! You have already locked in a grade of <b>{desired_letter}</b>. You could get a 0 on the final exam and still pass with this grade!"
            accent_color = "#2ecc71"
        elif needed_marks > final_total:
            status_message = f"❌ Mathematically impossible. Even if you get a perfect score ({final_total}/{final_total}) on the final, your quiz scores cannot stretch high enough to reach an {desired_letter}."
            accent_color = "#e74c3c"
        else:
            status_message = f"🎯 To get an <b>{desired_letter}</b>, you must score at least <b>{needed_marks:.1f} out of {final_total:.0f}</b> marks on your final exam (which is {needed_final_pct:.1f}%)."
            accent_color = "#3498db"

        final_standing_html = f"""
        <div class="card" style="border-top: 5px solid {accent_color};">
            <h3 style="margin-top:0; color: #2c3e50;">Desired Target Analysis</h3>
            <p style="font-size: 16px; line-height: 1.5; color: #333;">{status_message}</p>
        </div>
        """

        targets_rows = ""
        for scale in GRADING_SCALE[:-1]:
            req_pct = (scale["min"] - (quiz_average_pct * 0.5)) / 0.5
            req_marks = (req_pct / 100) * final_total
            
            if req_marks <= 0:
                display_text = "Already secured! (0 marks needed)"
                bg = "#e2f0d9"
            elif req_marks > final_total:
                display_text = "Not achievable"
                bg = "#fce4d6"
            else:
                display_text = f"<b>{req_marks:.1f} / {final_total:.0f}</b> marks ({req_pct:.1f}%)"
                bg = "#ffffff"
                
            targets_rows += f"""
            <tr style="background-color: {bg};">
                <td><b>{scale['grade']}</b> ({scale['desc']})</td>
                <td>{scale['min']}%</td>
                <td>{display_text}</td>
            </tr>
            """
            
        target_forecast_html = f"""
        <div class="card">
            <h3 style="margin-top:0;">Complete Final Exam Target Matrix</h3>
            <p style="color: #666; font-size: 14px; margin-bottom: 20px;">Here are the raw scores needed across every bracket out of your {final_total:.0f}-mark exam:</p>
            <table>
                <thead>
                    <tr><th>Target Grade</th><th>Minimum Required %</th><th>Marks Needed on Final Exam</th></tr>
                </thead>
                <tbody>
                    {targets_rows}
                </tbody>
            </table>
        </div>
        """

    # --- BUILD HTML REPORT ---
    # Updated navigation bar layout mapping to link directories accurately
    html_content = f"""<!DOCTYPE html>
    <html>
    <head>
        <title>Grade Audit Report</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 40px auto; max-width: 800px; background-color: #f8f9fa; color: #333; }}
            h2 {{ text-align: center; color: #2c3e50; margin-bottom: 30px; }}
            .card {{ background: white; padding: 25px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 25px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #eef2f3; }}
            th {{ background-color: #fcfcfc; color: #7f8c8d; font-size: 13px; text-transform: uppercase; }}
            .badge {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; color: white; }}
            .metric-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
            .metric {{ background: #fdfefe; border: 1px solid #eef2f3; padding: 15px; border-radius: 6px; text-align: center; }}
            .metric-num {{ font-size: 24px; font-weight: bold; color: #2c3e50; margin-top: 5px; }}
            
            .nav-menu {{ background: #2c3e50; padding: 12px; border-radius: 8px; text-align: center; margin-bottom: 25px; }}
            .nav-menu a {{ color: white; text-decoration: none; margin: 0 15px; font-weight: bold; font-size: 14px; }}
            .nav-menu a:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <div class="nav-menu">
            <a href="index.html" style="color: #f1c40f;">Grade Report</a>
            <a href="../money-detective/index.html">Transaction Audit</a>
            <a href="../books-dont-match/index.html">Books Reconciliation</a>
        </div>

        <h2>Academic Grade Report & Audit</h2>
        
        {final_standing_html}

        <div class="card">
            <h3 style="margin-top:0;">Quiz Breakdown (50% Total Weight)</h3>
            <p style="color: #666; font-size: 14px; margin-bottom: 20px;">The quiz with the worst relative percentage performance is dropped.</p>
            <div class="metric-grid">
                <div class="metric">
                    <div style="color: #7f8c8d; font-size: 13px;">ACTIVE QUIZZES TOTAL</div>
                    <div class="metric-num">{total_quiz_earned:.1f} / {total_quiz_possible:.1f} ({quiz_average_pct:.1f}%)</div>
                </div>
                <div class="metric">
                    <div style="color: #c0392b; font-size: 13px;">DROPPED LOWEST QUIZ</div>
                    <div class="metric-num" style="color: #c0392b;">
                        {f'{dropped_quiz["earned"]:.1f}/{dropped_quiz["total"]:.1f} ({dropped_quiz["pct"]:.1f}%)' if dropped_quiz else "None"}
                    </div>
                </div>
            </div>
            <table style="margin-top: 25px;">
                <thead>
                    <tr><th>Logged Quizzes</th><th>Percentage</th><th>Status</th></tr>
                </thead>
                <tbody>
    """

    for q in raw_quizzes:
        if dropped_quiz and q["earned"] == dropped_quiz["earned"] and q["total"] == dropped_quiz["total"]:
            html_content += f'<tr><td>{q["earned"]}/{q["total"]}</td><td>{q["pct"]:.1f}%</td><td><span class="badge" style="background-color: #e74c3c;">Dropped</span></td></tr>'
            dropped_quiz = None
        else:
            html_content += f'<tr><td>{q["earned"]}/{q["total"]}</td><td>{q["pct"]:.1f}%</td><td><span class="badge" style="background-color: #2ecc71;">Active</span></td></tr>'

    html_content += f"""
                </tbody>
            </table>
        </div>

        {target_forecast_html}
    </body>
    </html>
    """

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print("\n🎉 SUCCESS! Grade report HTML generated successfully!")
    print(f"👉 File saved as: {output_file}")
    webbrowser.open('file://' + os.path.realpath(output_file))

    print("\n" + "="*60)
    input("Execution finished. Press ENTER to close...")

except Exception as major_error:
    print("\n" + "!" * 60)
    print("                 CRITICAL RUNTIME EXCEPTION CAUGHT              ")
    print("!" * 60)
    print(f"\nError Details:\n{major_error}")
    print("\nCheck that your input syntax matches the guidelines.")
    print("=" * 60)
    input("Press ENTER to safely close this window...")