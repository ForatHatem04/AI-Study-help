# AI Study Helper

Generate concise summaries and multiple-choice quizzes (MCQs) from PDF, Word, and PowerPoint files.

## Features
- Extract text from `.pdf`, `.docx/.doc`, and `.pptx/.ppt` files.
- Summarize the content into a configurable number of sentences.
- Generate MCQs and an interactive HTML quiz.
- Save summary to a text file and quiz to a standalone HTML page.

## Setup
1. Create a virtual environment (recommended) and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

## Usage
### GUI (no terminal required)
Run the GUI helper and use the buttons to pick documents and choose where to save
the outputs:
```bash
python gui.py
```

The window shows your selected files, lets you set how many summary sentences and
questions to generate, and writes the results to the chosen text and HTML files.
### Command line
Run the CLI with one or more documents:
```bash
python main.py path/to/file1.pdf path/to/file2.docx --summary-length 4 --questions 6 --html-output quiz.html --summary-output summary.txt
```

Outputs:
- `summary.txt` contains the generated summary.
- `quiz.html` contains the interactive quiz; open it in a browser to practice.

## Project Structure
- `ai_study/extractors.py`: Text extraction from supported document formats.
- `ai_study/summarizer.py`: Frequency-based summarizer.
- `ai_study/quiz.py`: MCQ generation and HTML quiz builder.
- `main.py`: Command-line entry point tying everything together.

## Extending
- Adjust `STOPWORDS` in `summarizer.py` to fine-tune keyword emphasis.
- Enhance `generate_mcqs` in `quiz.py` with advanced NLP if desired.
