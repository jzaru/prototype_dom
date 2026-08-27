import json

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font

from config import ANALYSIS_JSON, ANALYSIS_XLSX
from questions import load_questions


def export_analysis_to_excel():
    if not ANALYSIS_JSON.exists():
        raise FileNotFoundError("No analysis.json exists yet. Extract item analysis first.")

    try:
        analysis = json.loads(ANALYSIS_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError("analysis.json is invalid.") from exc

    question_map = {q["id"]: q for q in load_questions()}

    rows = []
    for item in analysis["items"]:
        question = question_map.get(item["question_id"], {})
        rows.append({
            "Question ID": item["question_id"],
            "Question": question.get("question", ""),
            "Module": question.get("module", ""),
            "Question Type": question.get("type", ""),
            "Correct Answer": question.get("answer", ""),
            "Total Responses": analysis["students"],
            "Difficulty Index": item["difficulty_index"],
            "Discrimination Index": item["discrimination_index"],
            "Recommendation": item["recommendation"],
        })

    summary = pd.DataFrame([
        ["Exam", analysis["exam"]],
        ["Number of Students", analysis["students"]],
        ["Number of Questions", analysis["questions"]],
        ["Reliability", analysis["reliability"] if analysis["reliability"] is not None else "N/A"],
    ], columns=["Summary", "Value"])

    items_df = pd.DataFrame(rows)

    with pd.ExcelWriter(ANALYSIS_XLSX, engine="openpyxl") as writer:
        summary.to_excel(writer, sheet_name="Summary", index=False)
        items_df.to_excel(writer, sheet_name="Item Analysis", index=False)

    workbook = load_workbook(ANALYSIS_XLSX)
    for worksheet in workbook.worksheets:
        for cell in worksheet[1]:
            cell.font = Font(bold=True)
        for column_cells in worksheet.columns:
            max_length = max(len(str(cell.value or "")) for cell in column_cells)
            worksheet.column_dimensions[column_cells[0].column_letter].width = min(max_length + 2, 60)
    workbook.save(ANALYSIS_XLSX)

    return ANALYSIS_XLSX
