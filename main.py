import argparse
from pathlib import Path

from ai_study.extractors import extract_text_from_files
from ai_study.quiz import build_quiz_html, generate_mcqs
from ai_study.summarizer import summarize_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create summaries and MCQ quizzes from study files.")
    parser.add_argument("files", nargs="+", help="Paths to PDF, Word, or PowerPoint files")
    parser.add_argument("--questions", type=int, default=5, help="Number of MCQs to generate")
    parser.add_argument(
        "--summary-length",
        type=int,
        default=5,
        help="Maximum number of sentences to keep in the summary",
    )
    parser.add_argument(
        "--html-output",
        type=str,
        default="quiz.html",
        help="Path to write the quiz HTML file",
    )
    parser.add_argument(
        "--summary-output",
        type=str,
        default="summary.txt",
        help="Optional path to store the summary text",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    content = extract_text_from_files(args.files)
    summary = summarize_text(content, max_sentences=args.summary_length)
    questions = generate_mcqs(content, amount=args.questions)

    Path(args.summary_output).write_text(summary, encoding="utf-8")
    build_quiz_html(questions, summary, args.html_output)

    print(f"Summary saved to {args.summary_output}")
    print(f"Quiz saved to {args.html_output}")


if __name__ == "__main__":
    main()
