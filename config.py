from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
IMAGES_DIR = DATA_DIR / "images"

QUESTIONS_JSON = DATA_DIR / "questions.json"
EXAMS_JSON = DATA_DIR / "exams.json"
RESULTS_JSON = DATA_DIR / "results.json"
ANALYSIS_JSON = OUTPUT_DIR / "analysis.json"
ANALYSIS_XLSX = OUTPUT_DIR / "item_analysis.xlsx"

REQUIRED_COLUMNS = ["ID", "Module", "Type", "Question", "Answer"]
MCQ_TYPES = {"MCQ", "Multiple Choice", "MultipleChoice"}
SUPPORTED_TYPES = MCQ_TYPES | {"FillBlank", "Fill in the Blank", "Programming", "Programming FillBlank"}

for directory in (DATA_DIR, OUTPUT_DIR, IMAGES_DIR):
    directory.mkdir(parents=True, exist_ok=True)
