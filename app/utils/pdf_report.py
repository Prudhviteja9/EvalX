# ============================================================
# PDF REPORT GENERATOR
# ============================================================
#
# Creates a professional PDF report from evaluation results.
#
# Real life:
#   Like a teacher creating a printed report card:
#   - Student name, scores, grade, comments
#   - Professional format, easy to read
#
# We use fpdf2 library to create PDFs with Python.

from fpdf import FPDF
from datetime import datetime
from app.schemas.evaluation import EvaluationReport


def generate_pdf_report(report: EvaluationReport, output_path: str) -> str:
    """
    Generate a PDF report from evaluation results.

    Parameters:
        report: The evaluation report data
        output_path: Where to save the PDF file

    Returns:
        Path to the generated PDF file
    """

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # ===== PAGE 1: TITLE + SUMMARY =====
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 24)
    pdf.cell(0, 15, "EvalX Evaluation Report", new_x="LMARGIN", new_y="NEXT", align="C")

    # Subtitle
    pdf.set_font("Helvetica", "", 14)
    pdf.cell(0, 10, report.name, new_x="LMARGIN", new_y="NEXT", align="C")

    # Date
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 8, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_text_color(0, 0, 0)

    pdf.ln(10)

    # Summary box
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Summary", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, f"Total Test Cases: {report.total_test_cases}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"Models Tested: {len(report.model_reports)}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"Best Model: {report.best_model}", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(10)

    # ===== MODEL COMPARISON TABLE =====
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Model Comparison", new_x="LMARGIN", new_y="NEXT")

    # Table header
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(41, 128, 185)  # Blue header
    pdf.set_text_color(255, 255, 255)  # White text

    col_widths = [40, 25, 25, 30, 25, 25]
    headers = ["Model", "Accuracy", "Correct", "Avg Latency", "Tokens", "Cost"]

    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 8, header, border=1, fill=True, align="C")
    pdf.ln()

    # Table rows
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)

    for mr in report.model_reports:
        is_winner = mr.model_name == report.best_model
        if is_winner:
            pdf.set_fill_color(220, 255, 220)  # Light green for winner
        else:
            pdf.set_fill_color(255, 255, 255)  # White for others

        row_data = [
            mr.model_name,
            f"{mr.accuracy:.0%}",
            f"{mr.correct_answers}/{mr.total_questions}",
            f"{mr.avg_latency_ms:.0f}ms",
            str(mr.total_tokens),
            f"${mr.estimated_cost:.6f}",
        ]

        for i, data in enumerate(row_data):
            pdf.cell(col_widths[i], 7, data, border=1, fill=is_winner, align="C")
        pdf.ln()

    pdf.ln(10)

    # ===== DETAILED RESULTS PER MODEL =====
    for mr in report.model_reports:
        # Check if we need a new page
        if pdf.get_y() > 200:
            pdf.add_page()

        pdf.set_font("Helvetica", "B", 14)
        winner_tag = " (WINNER)" if mr.model_name == report.best_model else ""
        pdf.cell(0, 10, f"{mr.model_name}{winner_tag} - Detailed Results", new_x="LMARGIN", new_y="NEXT")

        # Per-question table
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(41, 128, 185)
        pdf.set_text_color(255, 255, 255)

        q_col_widths = [60, 30, 60, 18, 18]
        q_headers = ["Question", "Expected", "Model Answer", "Result", "Time"]

        for i, header in enumerate(q_headers):
            pdf.cell(q_col_widths[i], 7, header, border=1, fill=True, align="C")
        pdf.ln()

        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(0, 0, 0)

        for r in mr.results:
            if pdf.get_y() > 270:
                pdf.add_page()

            # Truncate long text to fit in cells
            q_text = r.question[:35] + "..." if len(r.question) > 35 else r.question
            e_text = r.expected_answer[:18] if len(r.expected_answer) > 18 else r.expected_answer
            a_text = r.model_answer[:35] + "..." if len(r.model_answer) > 35 else r.model_answer
            status = "PASS" if r.is_correct else "FAIL"

            if r.is_correct:
                pdf.set_fill_color(220, 255, 220)
            else:
                pdf.set_fill_color(255, 220, 220)

            row = [q_text, e_text, a_text, status, f"{r.latency_ms:.0f}ms"]
            for i, data in enumerate(row):
                pdf.cell(q_col_widths[i], 6, data, border=1, fill=True, align="C")
            pdf.ln()

        pdf.ln(8)

    # ===== FOOTER =====
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 10, "Generated by EvalX - LLM Evaluation Framework | github.com/Prudhviteja9/EvalX", new_x="LMARGIN", new_y="NEXT", align="C")

    # Save the PDF
    pdf.output(output_path)
    return output_path
