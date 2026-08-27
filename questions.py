import json
from collections import Counter
from pathlib import Path

import pandas as pd

from config import QUESTIONS_JSON, REQUIRED_COLUMNS, MCQ_TYPES


def normalize_question_type(value):
    return str(value).strip()


def load_questions():
    if not QUESTIONS_JSON.exists():
        return []
    try:
        return json.loads(QUESTIONS_JSON.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def save_questions(questions):
    QUESTIONS_JSON.write_text(
        json.dumps(questions, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )


def import_questions_from_excel(file_path):
    path = Path(file_path.strip().strip('"'))
    if not path.exists():
        raise FileNotFoundError(f"Excel file not found: {path}")
    if path.suffix.lower() not in {".xlsx", ".xlsm", ".xltx", ".xltm"}:
        raise ValueError("Please provide an Excel workbook (.xlsx, .xlsm, .xltx, or .xltm).")

    try:
        df = pd.read_excel(path)
    except Exception as exc:
        raise ValueError(f"Could not read the Excel file: {exc}") from exc

    df.columns = [str(column).strip() for column in df.columns]
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))

    questions = []
    seen_ids = set()

    for row_number, row in df.iterrows():
        excel_row = row_number + 2

        def cell(name):
            value = row.get(name, "")
            return "" if pd.isna(value) else str(value).strip()

        question_id = cell("ID")
        module = cell("Module")
        question_type = normalize_question_type(cell("Type"))
        question_text = cell("Question")
        answer = cell("Answer")

        if not question_id or not module or not question_type or not question_text or not answer:
            raise ValueError(
                f"Row {excel_row}: ID, Module, Type, Question, and Answer must not be blank."
            )

        if question_id in seen_ids:
            raise ValueError(f"Row {excel_row}: duplicate question ID '{question_id}'.")
        seen_ids.add(question_id)

        if question_type in MCQ_TYPES:
            for choice in ("Choice_A", "Choice_B", "Choice_C", "Choice_D"):
                if choice not in df.columns:
                    raise ValueError(f"MCQ row {excel_row} requires column '{choice}'.")
                if not cell(choice):
                    raise ValueError(f"Row {excel_row}: MCQ choice '{choice}' is blank.")
            if answer.upper() not in {"A", "B", "C", "D"}:
                raise ValueError(f"Row {excel_row}: MCQ Answer must be A, B, C, or D.")

        questions.append({
            "id": question_id,
            "module": module,
            "type": question_type,
            "question": question_text,
            "choice_a": cell("Choice_A"),
            "choice_b": cell("Choice_B"),
            "choice_c": cell("Choice_C"),
            "choice_d": cell("Choice_D"),
            "answer": answer,
            "image": cell("Image"),
            "difficulty": cell("Difficulty"),
        })

    save_questions(questions)
    return questions


def summarize_modules(questions):
    return Counter(question["module"] for question in questions)


def sort_questions(questions, field):
    return sorted(questions, key=lambda q: q.get(field, "").lower())


def filter_by_module(questions, module):
    return [q for q in questions if q["module"].lower() == module.lower()]


def filter_by_type(questions, question_type):
    return [q for q in questions if q["type"].lower() == question_type.lower()]


def print_questions(questions):
    if not questions:
        print("No questions to display.")
        return

    print(f"\nTotal Questions: {len(questions)}")
    print("-" * 90)
    for q in questions:
        print(
            f'{q["id"]} | {q["module"]} | {q["type"]} | '
            f'Difficulty: {q.get("difficulty", "")}'
        )
        print(f'  {q["question"]}')
    print("-" * 90)
