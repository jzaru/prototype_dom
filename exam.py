import json
import random
from datetime import datetime, timezone
from pathlib import Path

from config import EXAMS_JSON, MCQ_TYPES, RESULTS_JSON


def load_exams():
    if not EXAMS_JSON.exists():
        return []
    try:
        return json.loads(EXAMS_JSON.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def save_exams(exams):
    EXAMS_JSON.write_text(
        json.dumps(exams, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )


def load_results():
    if not RESULTS_JSON.exists():
        return []
    try:
        return json.loads(RESULTS_JSON.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def save_results(results):
    RESULTS_JSON.write_text(
        json.dumps(results, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )


def create_exam(title, module, number_of_questions, randomize, questions):
    if not title.strip():
        raise ValueError("Exam title cannot be blank.")

    available = (
        questions
        if module.lower() == "all"
        else [q for q in questions if q["module"].lower() == module.lower()]
    )

    if number_of_questions <= 0:
        raise ValueError("Number of questions must be greater than zero.")
    if number_of_questions > len(available):
        raise ValueError(
            f"Only {len(available)} question(s) are available for module '{module}'."
        )

    selected = random.sample(available, number_of_questions)

    exams = load_exams()
    exam_id = f"EXAM{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"

    exam = {
        "id": exam_id,
        "name": title.strip(),
        "module": module,
        "question_ids": [q["id"] for q in selected],
        "randomize": bool(randomize),
        "active": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    exams.append(exam)
    save_exams(exams)
    return exam


def activate_exam(exam_id):
    exams = load_exams()
    found = None
    for exam in exams:
        if exam["id"] == exam_id:
            found = exam
            break

    if found is None:
        raise ValueError("Examination not found.")

    for exam in exams:
        exam["active"] = exam["id"] == exam_id

    save_exams(exams)
    return found


def inactivate_exam(exam_id):
    exams = load_exams()
    found = None
    for exam in exams:
        if exam["id"] == exam_id:
            found = exam
            break

    if found is None:
        raise ValueError("Examination not found.")

    for exam in exams:
        if exam["id"] == exam_id:
            exam["active"] = False
            break

    save_exams(exams)
    return found


def get_active_exam():
    for exam in load_exams():
        if exam.get("active"):
            return exam
    return None


def get_questions_for_exam(exam, questions):
    question_map = {q["id"]: q for q in questions}
    selected = [question_map[qid] for qid in exam["question_ids"] if qid in question_map]

    if len(selected) != len(exam["question_ids"]):
        missing = set(exam["question_ids"]) - set(question_map)
        raise ValueError("The active exam references missing question IDs: " + ", ".join(sorted(missing)))

    if exam.get("randomize"):
        selected = selected.copy()
        random.shuffle(selected)
    return selected


def answer_is_correct(question, student_answer):
    submitted = student_answer.strip()
    expected = question["answer"].strip()

    if question["type"] in MCQ_TYPES:
        return submitted.upper() == expected.upper()

    return submitted.casefold() == expected.casefold()


def take_exam(exam, questions, student_name):
    exam_questions = get_questions_for_exam(exam, questions)
    responses = []

    print("\nLoading examination...")
    print(f"Exam: {exam['name']}")
    print(f"Module: {exam['module']}")
    print(f"Number of Questions: {len(exam_questions)}")
    print(f"Randomization: {'Enabled' if exam.get('randomize') else 'Disabled'}")

    for index, question in enumerate(exam_questions, start=1):
        print("\n" + "=" * 40)
        print(f"Question {index} of {len(exam_questions)}")
        print("=" * 40)

        image = question.get("image", "")
        if image:
            image_path = Path(image)
            if not image_path.is_absolute():
                image_path = Path(__file__).resolve().parent / image
            if image_path.exists():
                print(f"[IMAGE: {image_path}]")
            else:
                print("[Image unavailable]")

        print(question["question"])

        if question["type"] in MCQ_TYPES:
            print(f"A. {question['choice_a']}")
            print(f"B. {question['choice_b']}")
            print(f"C. {question['choice_c']}")
            print(f"D. {question['choice_d']}")
            valid = {"A", "B", "C", "D"}
            while True:
                answer = input("Answer: ").strip().upper()
                if answer in valid:
                    break
                print("✗ Please enter A, B, C, or D.")
        else:
            answer = input("Answer: ").strip()

        responses.append({
            "question_id": question["id"],
            "student_answer": answer,
            "correct_answer": question["answer"],
            "is_correct": answer_is_correct(question, answer),
        })

    correct_count = sum(response["is_correct"] for response in responses)
    total = len(responses)
    percentage = (correct_count / total * 100) if total else 0.0

    timestamp = datetime.now(timezone.utc).isoformat()
    result_id = f"RES{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"

    for response in responses:
        response.update({
            "result_id": result_id,
            "student_name": student_name.strip(),
            "exam_id": exam["id"],
            "exam_name": exam["name"],
            "timestamp": timestamp,
            "score": correct_count,
            "total_questions": total,
            "percentage": percentage,
        })

    results = load_results()
    results.extend(responses)
    save_results(results)

    print("\n" + "=" * 40)
    print("          EXAM COMPLETE")
    print("=" * 40)
    print(f"Student: {student_name}")
    print(f"Score: {correct_count} / {total}")
    print(f"Percentage: {percentage:.2f}%")
    input("\nPress ENTER to return.")
