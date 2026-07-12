import os
import re
import sys
import webbrowser

try:
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
        text = text.strip()
        matches = re.findall(r'\d+(?:\.\d+)?', text)
        if len(matches) >= 2:
            return float(matches[0]), float(matches[1])
        elif len(matches) == 1:
            return float(matches[0]), 100.0
        raise ValueError("Invalid format.")

    print("=" * 60)
    print("         RAW MARKS GRADE AUDIT & TARGET CALCULATOR      ")
    print("=" * 60)

    quizzes = []
    print("\n📝 ENTER QUIZ MARKS (e.g., 15/20, 18/20)")
    while not quizzes:
        quiz_input = input("Your Quizzes:\n> ").strip()
        raw_pairs = re.findall(r'\d+(?:\.\d+)?\s*/\s*\d+(?:\.\d+)?', quiz_input)
        for pair in raw_pairs:
            try:
                earned, total = parse_fraction(pair)
                if total > 0:
                    quizzes.append({"earned": earned, "total": total, "pct": (earned / total) * 100})
            except ValueError:
                continue

    print("\n📝 ENTER FINAL EXAM TOTAL MARKS")
    final_total = 100.0
    total_input = input("Total possible marks for the Final Exam:\n> ").strip()
    if total_input:
        try:
            final_total = float(re.search(r'\d+(?:\.\d+)?', total_input).group())
        except:
            pass

    print(f"\nYour Final Exam Score (Earned/{final_total:.0f} or leave blank):")
    final_input = input("> ").strip()
    final_exam_earned = None
    if final_input:
        try:
            earned, total = parse_fraction(final_input)
            final_exam_earned = earned
            final_total = total
        except:
            pass

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
        </div>
        """
    else:
        status_message = f"🎯 Your current active quiz average is <b>{quiz_average_pct:.1f}%</b>. Ready to calculate final exam benchmarks."
        final_standing_html = f"""
        <div class="card" style="border-top: 5px solid #3498db;">
            <h3 style="margin-top:0; color: #2c3e50;">Quiz Status Analysis</h3>
            <p style="font-size: 16px; line-height: 1.5; color: #333;">{status_message}</p>
        </div>
        """

    # --- BUILD CLEAN HTML REPORT ---
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
            .btn-back {{ display: inline-block; margin-bottom: 20px; color: #3498db; text-decoration: none; font-weight: bold; }}
        </style>
    </head>
    <body>
        <a href="../index.html" class="btn-back">← Back to Dashboard</a>
        <h2>Academic Grade Report & Audit</h2>
        
        {final_standing_html}

        <div class="card">
            <h3>Quiz Breakdown (50% Weight)</h3>
            <table>
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
    </body>
    </html>
    """

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"\n🎉 SUCCESS! Clean report saved as: {output_file}")
    webbrowser.open('file://' + os.path.realpath(output_file))

except Exception as e:
    print(f"Error: {e}")
    input()