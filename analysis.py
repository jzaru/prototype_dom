import json
import math
from collections import defaultdict
from statistics import mean

from config import ANALYSIS_JSON
from exam import load_exams, load_results
from questions import load_questions


# Prototype thresholds only; they are not institutional standards.
RETAIN_DIFFICULTY_MIN = 0.30
RETAIN_DIFFICULTY_MAX = 0.90
RETAIN_DISCRIMINATION_MIN = 0.20


def _student_totals(results):
    totals = defaultdict(int)
    for response in results:
        if response.get("is_correct"):
            totals[response["result_id"]] += 1
    return totals


def cronbach_alpha(matrix):
    """Cronbach's alpha = k/(k-1) * (1 - sum(item variances)/variance(total scores))."""
    if len(matrix) < 2 or len(matrix[0]) < 2:
        return None

    k = len(matrix[0])
    if k < 2:
        return None

    item_variances = []
    for col in range(k):
        values = [row[col] for row in matrix]
        item_variances.append(_sample_variance(values))

    total_scores = [sum(row) for row in matrix]
    total_variance = _sample_variance(total_scores)

    if total_variance == 0:
        return None

    return (k / (k - 1)) * (1 - sum(item_variances) / total_variance)


def _sample_variance(values):
    if len(values) < 2:
        return 0.0
    avg = mean(values)
    return sum((value - avg) ** 2 for value in values) / (len(values) - 1)


def discrimination_index(item_responses, student_totals, total_students):
    """Upper/lower 27% groups, using the standard 27% prototype convention.

    With fewer than 4 students, returns None. For 4+ students, group size is
    max(1, floor(0.27 * N)), capped so the upper and lower groups do not overlap.
    """
    if total_students < 4:
        return None

    ranked = sorted(student_totals.items(), key=lambda pair: pair[1], reverse=True)
    group_size = max(1, math.floor(0.27 * total_students))
    group_size = min(group_size, total_students // 2)

    upper_ids = {student_id for student_id, _ in ranked[:group_size]}
    lower_ids = {student_id for student_id, _ in ranked[-group_size:]}

    upper = [
        correct
        for student_id, correct in item_responses.items()
        if student_id in upper_ids
    ]
    lower = [
        correct
        for student_id, correct in item_responses.items()
        if student_id in lower_ids
    ]

    if not upper or not lower:
        return None

    return (sum(upper) / len(upper)) - (sum(lower) / len(lower))


def recommendation(difficulty, discrimination):
    if discrimination is None:
        return "Review"

    if (
        RETAIN_DIFFICULTY_MIN <= difficulty <= RETAIN_DIFFICULTY_MAX
        and discrimination >= RETAIN_DISCRIMINATION_MIN
    ):
        return "Retain"

    if discrimination < 0 or difficulty < RETAIN_DIFFICULTY_MIN or difficulty > RETAIN_DIFFICULTY_MAX:
        return "Revise"

    return "Review"


def _student_name_and_score_by_result(results):
    summary = {}
    for response in results:
        result_id = response.get("result_id")
        if not result_id:
            continue
        if result_id not in summary:
            summary[result_id] = {
                "student_name": response.get("student_name", "Unknown"),
                "score": response.get("score", 0),
                "total_questions": response.get("total_questions", 0),
                "percentage": response.get("percentage", 0.0),
                "timestamp": response.get("timestamp"),
            }
    return summary


def analyze_exam(exam_id=None):
    exams = load_exams()
    results = load_results()

    if not results:
        return None

    if exam_id:
        exam = next((e for e in exams if e["id"] == exam_id), None)
    else:
        exam = next((e for e in exams if any(r["exam_id"] == e["id"] for r in results)), None)

    if exam is None:
        return None

    exam_results = [r for r in results if r["exam_id"] == exam["id"]]
    if not exam_results:
        return None

    result_ids = list(dict.fromkeys(r["result_id"] for r in exam_results))
    by_student = defaultdict(dict)
    for response in exam_results:
        by_student[response["result_id"]][response["question_id"]] = int(response["is_correct"])

    student_totals = {
        result_id: sum(item_values.values())
        for result_id, item_values in by_student.items()
    }

    student_score_map = _student_name_and_score_by_result(exam_results)
    student_results = []
    for result_id in result_ids:
        summary = student_score_map.get(result_id, {})
        student_results.append({
            "student_name": summary.get("student_name", "Unknown"),
            "score": summary.get("score", 0),
            "total_questions": summary.get("total_questions", 0),
            "percentage": float(summary.get("percentage", 0.0)),
            "timestamp": summary.get("timestamp"),
        })
    student_results.sort(key=lambda item: (-item["score"], item["student_name"]))

    question_map = {q["id"]: q for q in load_questions()}
    question_ids = exam["question_ids"]
    items = []

    for question_id in question_ids:
        item_responses = [r for r in exam_results if r["question_id"] == question_id]
        total = len(item_responses)
        number_correct = sum(1 for r in item_responses if r.get("is_correct") is True)
        number_wrong = total - number_correct
        difficulty = number_correct / total if total else None
        discrimination = discrimination_index(
            {result_id: by_student.get(result_id, {}).get(question_id, 0) for result_id in result_ids},
            student_totals,
            len(result_ids),
        )

        wrong_students = []
        for response in item_responses:
            if response.get("is_correct"):
                continue
            student_summary = student_score_map.get(response.get("result_id"), {})
            wrong_students.append({
                "student_name": response.get("student_name", "Unknown"),
                "student_answer": response.get("student_answer", ""),
                "score": student_summary.get("score", 0),
                "total_questions": student_summary.get("total_questions", 0),
                "percentage": float(student_summary.get("percentage", 0.0)),
            })

        question = question_map.get(question_id, {})
        items.append({
            "question_id": question_id,
            "question": question.get("question", ""),
            "module": question.get("module", ""),
            "question_type": question.get("type", ""),
            "correct_answer": question.get("answer", ""),
            "total_responses": total,
            "number_correct": number_correct,
            "number_wrong": number_wrong,
            "difficulty_index": round(difficulty, 4) if difficulty is not None else None,
            "discrimination_index": round(discrimination, 4) if discrimination is not None else None,
            "students_wrong": wrong_students,
            "recommendation": recommendation(difficulty, discrimination) if difficulty is not None else "Review",
        })

    matrix = [
        [by_student[result_id].get(question_id, 0) for question_id in question_ids]
        for result_id in result_ids
    ]
    reliability = cronbach_alpha(matrix)

    analysis = {
        "exam_id": exam["id"],
        "exam": exam["name"],
        "module": exam["module"],
        "students": len(result_ids),
        "questions": len(question_ids),
        "reliability": round(reliability, 4) if reliability is not None else None,
        "recommendation_note": (
            "Prototype recommendation only. Final item decisions remain with the teacher. "
            "Thresholds are defined in analysis.py and are not institutional standards."
        ),
        "student_results": student_results,
        "items": items,
    }

    ANALYSIS_JSON.write_text(
        json.dumps(analysis, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )
    return analysis
