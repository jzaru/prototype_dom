from pathlib import Path

from analysis import analyze_exam
from config import ANALYSIS_JSON, ANALYSIS_XLSX
from exam import (
    activate_exam,
    create_exam,
    get_active_exam,
    load_exams,
    take_exam,
)
from export import export_analysis_to_excel
from questions import (
    filter_by_module,
    filter_by_type,
    load_questions,
    print_questions,
    sort_questions,
    summarize_modules,
    import_questions_from_excel,
)


def pause():
    input("\nPress ENTER to return.")


def teacher_view_questions(questions):
    print_questions(questions)
    pause()


def sort_filter_menu(questions):
    if not questions:
        print("✗ The question bank is empty. Import questions first.")
        pause()
        return

    while True:
        print("""
========================================
        SORT / FILTER QUESTIONS
========================================
1. Sort by ID
2. Sort by Module
3. Sort by Difficulty
4. Filter by Module
5. Filter by Question Type
6. Show All
7. Return
""")
        choice = input("Choose: ").strip()

        if choice == "1":
            print_questions(sort_questions(questions, "id"))
            pause()
        elif choice == "2":
            print_questions(sort_questions(questions, "module"))
            pause()
        elif choice == "3":
            print_questions(sort_questions(questions, "difficulty"))
            pause()
        elif choice == "4":
            modules = sorted({q["module"] for q in questions})
            for i, module in enumerate(modules, 1):
                print(f"{i}. {module}")
            try:
                selected = int(input("Choose module: ").strip())
                module = modules[selected - 1]
            except (ValueError, IndexError):
                print("✗ Invalid module choice.")
                continue
            print_questions(filter_by_module(questions, module))
            pause()
        elif choice == "5":
            types = sorted({q["type"] for q in questions})
            for i, question_type in enumerate(types, 1):
                print(f"{i}. {question_type}")
            try:
                selected = int(input("Choose question type: ").strip())
                question_type = types[selected - 1]
            except (ValueError, IndexError):
                print("✗ Invalid question type choice.")
                continue
            print_questions(filter_by_type(questions, question_type))
            pause()
        elif choice == "6":
            print_questions(questions)
            pause()
        elif choice == "7":
            return
        else:
            print("✗ Invalid menu choice.")


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


def extract_analysis_menu():
    try:
        analysis = analyze_exam()
    except Exception as exc:
        print(f"✗ Analysis failed: {exc}")
        pause()
        return

    if analysis is None:
        print("No examination results are available for analysis.")
        print("At least one student must complete an examination first.")
        pause()
        return

    print("✓ Item analysis extracted.")
    print(f"JSON: {ANALYSIS_JSON}")
    print(f"Students: {analysis['students']}")
    print(f"Questions: {analysis['questions']}")
    print(
        "Reliability: "
        + (str(analysis["reliability"]) if analysis["reliability"] is not None else "N/A")
    )
    print("Prototype recommendation only. Final item decisions remain with the teacher.")
    pause()


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
3. Sort / Filter Questions
4. Create Examination
5. Activate Examination
6. View Active Examination
7. Extract Item Analysis
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
            sort_filter_menu(questions)

        elif choice == "4":
            create_exam_menu(questions)

        elif choice == "5":
            activate_exam_menu()

        elif choice == "6":
            view_active_exam(questions)

        elif choice == "7":
            extract_analysis_menu()

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
        print("Please wait for the teacher to activate an examination.")
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
