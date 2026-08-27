# Examination Management and Item Analysis System — Prototype

A simple, local, console-based Python prototype demonstrating:

Excel question bank → question organization → exam creation → teacher activation → student exam → answer recording → item analysis → JSON → Excel.

## Project structure

```text
exam_prototype/
├── main.py
├── questions.py
├── exam.py
├── analysis.py
├── export.py
├── config.py
├── requirements.txt
├── questions.xlsx
├── data/
│   ├── questions.json
│   ├── exams.json
│   ├── results.json
│   └── images/
└── output/
    ├── analysis.json
    └── item_analysis.xlsx
```

`questions.xlsx` is sample input data. The JSON files and exported output are generated/updated by the program.

## Sample Excel format

Required columns:

| ID | Module | Type | Question | Choice_A | Choice_B | Choice_C | Choice_D | Answer | Image | Difficulty |
|---|---|---|---|---|---|---|---|---|---|---|
| Q001 | HTML | MCQ | What does HTML stand for? | Hyper Text Markup Language | High Text Machine Language | Hyper Tool Multi Language | Home Tool Markup Language | A | | Easy |
| Q002 | Python | FillBlank | Python output function is ______. | | | | | print | | Easy |
| Q003 | Python | Programming | Complete the code: print(______) | | | | | "Hello" | data/images/q003.png | Medium |
| Q004 | CSS | MCQ | Which property changes text color? | color | font-size | background | margin | A | | Easy |
| Q005 | Python | MCQ | Which keyword defines a function? | func | def | function | define | B | | Medium |
| Q006 | JavaScript | FillBlank | The keyword used to declare a constant is ______. | | | | | const | | Easy |
| Q007 | HTML | MCQ | Which tag creates a hyperlink? | link | a | href | url | B | | Easy |
| Q008 | Python | Programming | Complete: x = 10; print(______) | | | | | x | | Easy |
| Q009 | CSS | FillBlank | The CSS property for page background color is ______. | | | | | background-color | | Medium |
| Q010 | JavaScript | MCQ | Which symbol begins a single-line comment? | // | <!-- | ## | ** | A | | Easy |

For FillBlank and Programming rows, choice columns may be blank.

## Creating the sample workbook

The included `questions.xlsx` can be used directly. If creating it manually, create one worksheet named `Questions`, put the column names in row 1, and enter rows using the format above.

An optional image can be placed at `data/images/q003.png`. If it is absent, the prototype prints `[Image unavailable]` rather than crashing.

## Installation

From the project folder:

```bash
python -m pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Complete demonstration flow

1. Choose `2. Teacher`.
2. Choose `1. Import Excel Questions`.
3. Enter `questions.xlsx`.
4. Choose `2. View Question Bank`.
5. Choose `3. Sort / Filter Questions` and demonstrate sorting/filtering.
6. Choose `4. Create Examination`.
7. Select `Python`.
8. Enter `5` questions.
9. Select `Yes` for randomization.
10. Choose `5. Activate Examination`.
11. Return to the main menu.
12. Choose `1. Student`.
13. Enter a student name.
14. Answer the five questions.
15. The score is shown and responses are saved to `data/results.json`.
16. Repeat the student flow with additional students if meaningful item analysis is desired.
17. Return to `2. Teacher`.
18. Choose `7. Extract Item Analysis`.
19. Verify `output/analysis.json`.
20. Choose `8. Export Analysis to Excel`.
21. Verify `output/item_analysis.xlsx`.

## Item analysis method

### Difficulty Index

For each item:

`Difficulty = number correct / total responses`

### Discrimination Index

This prototype sorts students by total examination score and compares the proportion correct in the upper and lower groups. It uses groups containing 27% of students, with a minimum group size of one and no overlap.

With fewer than four students, discrimination is reported as `N/A`.

### Cronbach's Alpha

The prototype uses:

`alpha = k/(k-1) * (1 - sum(item variances) / variance(total scores))`

Reliability is reported as `N/A` when the available response matrix does not permit a meaningful calculation, including when total-score variance is zero.

### Recommendations

The recommendations are explicitly prototype-only. They use thresholds defined in `analysis.py`:

- Retain: difficulty 0.30–0.90 and discrimination ≥ 0.20
- Revise: negative discrimination or difficulty outside that range
- Review: otherwise, including when discrimination is unavailable

These are demonstration thresholds, not institutional standards. Final item decisions remain with the teacher.

## Important prototype limitations

- Console UI displays image paths rather than rendering images inside the console.
- Student identity is only a name; there is no authentication.
- Results are stored in JSON, not a database.
- Only one examination can be active at a time.
- Question order is randomized when enabled; choices are not randomized.
- Answers use exact/case-insensitive matching rather than natural-language grading.
- Programming answers are compared as stored strings; student code is never executed.
- The exam is sampled randomly at creation time from the selected module. The stored exam keeps actual question IDs.
- This is a demonstration prototype, not a production assessment platform.
