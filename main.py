from analysis import analyze_exam
from config import ANALYSIS_JSON
from exam import (
    activate_exam,
    create_exam,
    get_active_exam,
    inactivate_exam,
    load_exams,
    take_exam,
)
from export import export_analysis_to_excel
from questions import (
    import_questions_from_excel,
    load_questions,
    print_questions,
    summarize_modules,
)


def pause():
    input("\nPress ENTER to return.")


def teacher_view_questions(questions):
    print_questions(questions)
    pause()


def create_exam_menu(questions):
    if not questions:
        print("✗ The question bank is empty. Import questions first.")
        pause()
        return

    modules = sorted({q["module"] for q in questions})
    print("\nSelect Module:")
    print("1. All")
    for index, module in enumerate(modules, 2):
        print(f"{index}. {module}")

    try:
        module_choice = int(input("Choose: ").strip())
        if module_choice == 1:
            module = "All"
        else:
            module = modules[module_choice - 2]
    except (ValueError, IndexError):
        print("✗ Invalid module choice.")
        pause()
        return

    title = input("Exam Title: ").strip()
    try:
        number = int(input("Number of Questions: ").strip())
    except ValueError:
        print("✗ Number of questions must be a whole number.")
        pause()
        return

    print("\nRandomize Questions?")
    print("1. Yes")
    print("2. No")
    random_choice = input("Choose: ").strip()
    if random_choice not in {"1", "2"}:
        print("✗ Invalid randomization choice.")
        pause()
        return

    try:
        exam = create_exam(title, module, number, random_choice == "1", questions)
    except ValueError as exc:
        print(f"✗ {exc}")
        pause()
        return

    print("✓ Examination created successfully.")
    print(f"Exam ID: {exam['id']}")
    pause()


def activate_exam_menu():
    exams = load_exams()
    if not exams:
        print("✗ No examinations have been created.")
        pause()
        return

    print("\nAvailable Examinations:")
    for index, exam in enumerate(exams, 1):
        status = "ACTIVE" if exam.get("active") else "Inactive"
        print(f"{index}. {exam['name']} | {exam['module']} | {status}")

    try:
        selected = int(input("Choose: ").strip())
        exam = exams[selected - 1]
    except (ValueError, IndexError):
        print("✗ Invalid examination choice.")
        pause()
        return

    print("\nActivate this examination?")
    print("1. Yes")
    print("2. No")
    if input("Choose: ").strip() != "1":
        print("Activation cancelled.")
        pause()
        return

    try:
        activate_exam(exam["id"])
    except ValueError as exc:
        print(f"✗ {exc}")
        pause()
        return

    print("✓ Examination activated.")
    print(f"Students can now access: {exam['name']}")
    pause()


def inactivate_exam_menu():
    exam = get_active_exam()
    if not exam:
        print("No examination is currently active.")
        pause()
        return

    print("""
========================================
        INACTIVATE EXAMINATION
========================================
""")
    print(f"Active Examination:\n{exam['name']}")
    print("\nStatus:")
    print("ACTIVE")
    print("\nInactivate this examination?")
    print("1. Yes")
    print("2. No")

    if input("Choose: ").strip() != "1":
        print("Inactivation cancelled.")
        pause()
        return

    try:
        inactivate_exam(exam["id"])
    except ValueError as exc:
        print(f"✗ {exc}")
        pause()
        return

    print("✓ Examination successfully inactivated.")
    pause()


def view_active_exam(questions):
    exam = get_active_exam()
    if not exam:
        print("No examination is currently active.")
        pause()
        return

    print("""
========================================
        ACTIVE EXAMINATION
========================================
""")
    print(f"Exam: {exam['name']}")
    print(f"Module: {exam['module']}")
    print(f"Questions: {len(exam['question_ids'])}")
    print(f"Randomization: {'Enabled' if exam.get('randomize') else 'Disabled'}")
    print("Status: ACTIVE")
    pause()


def _analysis_items_for_display(analysis):
    return analysis.get("items", [])


def _sort_analysis_items(items, field):
    if field == "question_id":
        return sorted(items, key=lambda item: item.get("question_id", ""))
    if field in {"difficulty_index", "discrimination_index"}:
        return sorted(
            items,
            key=lambda item: (item.get(field) is None, -(item.get(field) if item.get(field) is not None else 0)),
        )
    return items


def _filter_analysis_items(items, key, value):
    return [item for item in items if str(item.get(key, "")).lower() == str(value).lower()]


def print_item_analysis(analysis):
    items = _analysis_items_for_display(analysis)
    if not items:
        print("No examination results are available for analysis.")
        return

    print(f"\nExam: {analysis.get('exam', '')}")
    print(f"Students: {analysis.get('students', 0)}")
    print(f"Questions: {analysis.get('questions', 0)}")
    print(f"Reliability: {analysis.get('reliability', 'N/A')}")
    print("-" * 90)
    for item in items:
        print(f"{item['question_id']} | {item.get('question', '')}")
        print(f"Module: {item.get('module', '')} | Type: {item.get('question_type', '')}")
        print(f"Correct Answer: {item.get('correct_answer', '')}")
        print(f"Total Responses: {item.get('total_responses', 0)}")
        print(f"Correct: {item.get('number_correct', 0)} | Wrong: {item.get('number_wrong', 0)}")
        print(f"Difficulty Index: {item.get('difficulty_index', 'N/A')}")
        print(f"Discrimination Index: {item.get('discrimination_index', 'N/A')}")
        print(f"Recommendation: {item.get('recommendation', 'Review')}")
        wrong = item.get("students_wrong", [])
        if wrong:
            print("Students who answered incorrectly:")
            for student in wrong:
                print(
                    f"- {student['student_name']} — Answer: {student['student_answer']} — "
                    f"Score: {student['score']}/{student.get('total_questions', 0)}"
                )
        else:
            print("Students who answered incorrectly:\nNone")
        print("-" * 90)


def print_student_results(analysis):
    students = analysis.get("student_results", [])
    if not students:
        print("No examination results are available for analysis.")
        return

    print("\nSTUDENT RESULTS")
    print("\n## Student Score Percentage")
    for student in students:
        print(
            f"{student['student_name']} {student['score']} / {student['total_questions']} "
            f"{student['percentage']:.2f}%"
        )


def sort_filter_analysis_menu(analysis):
    items = list(_analysis_items_for_display(analysis))
    while True:
        print("""
========================================
         SORT / FILTER ANALYSIS
========================================
1. Sort by Question ID
2. Sort by Difficulty Index
3. Sort by Discrimination Index
4. Filter by Module
5. Filter by Question Type
6. Show All
7. Return
""")
        choice = input("Choose: ").strip()

        if choice == "1":
            print_item_analysis({**analysis, "items": _sort_analysis_items(items, "question_id")})
            pause()
        elif choice == "2":
            print_item_analysis({**analysis, "items": _sort_analysis_items(items, "difficulty_index")})
            pause()
        elif choice == "3":
            print_item_analysis({**analysis, "items": _sort_analysis_items(items, "discrimination_index")})
            pause()
        elif choice == "4":
            modules = sorted({item.get("module", "") for item in items if item.get("module")})
            if not modules:
                print("No modules available in the analysis.")
                pause()
                return
            for index, module in enumerate(modules, 1):
                print(f"{index}. {module}")
            try:
                selected = int(input("Choose module: ").strip())
                module = modules[selected - 1]
            except (ValueError, IndexError):
                print("✗ Invalid module choice.")
                continue
            print_item_analysis({**analysis, "items": _filter_analysis_items(items, "module", module)})
            pause()
        elif choice == "5":
            question_types = sorted({item.get("question_type", "") for item in items if item.get("question_type")})
            if not question_types:
                print("No question types available in the analysis.")
                pause()
                return
            for index, question_type in enumerate(question_types, 1):
                print(f"{index}. {question_type}")
            try:
                selected = int(input("Choose question type: ").strip())
                question_type = question_types[selected - 1]
            except (ValueError, IndexError):
                print("✗ Invalid question type choice.")
                continue
            print_item_analysis({**analysis, "items": _filter_analysis_items(items, "question_type", question_type)})
            pause()
        elif choice == "6":
            print_item_analysis(analysis)
            pause()
        elif choice == "7":
            return
        else:
            print("✗ Invalid menu choice.")


def item_analysis_menu():
    try:
        analysis = analyze_exam()
    except Exception as exc:
        print(f"✗ Analysis failed: {exc}")
        pause()
        return

    if analysis is None:
        print("No examination results are available for analysis.")
        print("At least one student must complete an examination before analysis can be performed.")
        pause()
        return

    while True:
        print("""
========================================
             ITEM ANALYSIS
========================================
1. View Item Analysis
2. View Student Results
3. Sort / Filter Analysis
4. Generate JSON Analysis
5. Return
""")
        choice = input("Choose: ").strip()

        if choice == "1":
            print_item_analysis(analysis)
            pause()
        elif choice == "2":
            print_student_results(analysis)
            pause()
        elif choice == "3":
            sort_filter_analysis_menu(analysis)
        elif choice == "4":
            analysis = analyze_exam()
            if analysis is None:
                print("No examination results are available for analysis.")
                print("At least one student must complete an examination before analysis can be performed.")
                pause()
                return
            print("✓ Item analysis generated.")
            print(f"JSON: {ANALYSIS_JSON}")
            print(f"Students: {analysis['students']}")
            print(f"Questions: {analysis['questions']}")
            pause()
        elif choice == "5":
            return
        else:
            print("✗ Invalid menu choice.")


def export_analysis_menu():
    try:
        path = export_analysis_to_excel()
    except (FileNotFoundError, ValueError) as exc:
        print(f"✗ {exc}")
        pause()
        return
    except Exception as exc:
        print(f"✗ Excel export failed: {exc}")
        pause()
        return

    print(f"✓ Analysis exported successfully: {path}")
    pause()


def teacher_menu():
    questions = load_questions()

    while True:
        print("""
========================================
              TEACHER
========================================
1. Import Excel Questions
2. View Question Bank
3. Create Examination
4. Activate Examination
5. Inactivate Examination
6. View Active Examination
7. Item Analysis
8. Export Analysis to Excel
9. Return
""")
        choice = input("Choose: ").strip()

        if choice == "1":
            file_path = input("Excel file path: ").strip()
            try:
                questions = import_questions_from_excel(file_path)
            except (FileNotFoundError, ValueError) as exc:
                print(f"✗ {exc}")
                pause()
                continue

            print("✓ Questions imported successfully.")
            print(f"Total Questions: {len(questions)}")
            print("Modules:")
            for module, count in sorted(summarize_modules(questions).items()):
                print(f"{module}: {count}")
            pause()

        elif choice == "2":
            teacher_view_questions(questions)

        elif choice == "3":
            create_exam_menu(questions)

        elif choice == "4":
            activate_exam_menu()

        elif choice == "5":
            inactivate_exam_menu()

        elif choice == "6":
            view_active_exam(questions)

        elif choice == "7":
            item_analysis_menu()

        elif choice == "8":
            export_analysis_menu()

        elif choice == "9":
            return

        else:
            print("✗ Invalid menu choice.")


def student_menu():
    exam = get_active_exam()

    print("""
========================================
              STUDENT
========================================
""")

    if not exam:
        print("No examination is currently active.")
        print("Please wait for the teacher to activate")
        print("an examination.")
        pause()
        return

    print(f"Active Examination: {exam['name']}")
    student_name = input("\nEnter your name: ").strip()
    if not student_name:
        print("✗ Student name cannot be blank.")
        pause()
        return

    questions = load_questions()
    try:
        take_exam(exam, questions, student_name)
    except ValueError as exc:
        print(f"✗ Could not load the examination: {exc}")
        pause()


def main():
    while True:
        print("""
========================================
       EXAMINATION SYSTEM PROTOTYPE
========================================

1. Student
2. Teacher
3. Exit
""")
        choice = input("Choose: ").strip()

        if choice == "1":
            student_menu()
        elif choice == "2":
            teacher_menu()
        elif choice == "3":
            print("Goodbye.")
            break
        else:
            print("✗ Invalid menu choice.")


if __name__ == "__main__":
    main()
