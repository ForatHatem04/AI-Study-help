from ai_study.quiz import build_quiz_html, generate_mcqs


def test_generate_mcqs_creates_requested_amount(tmp_path):
    text = "Python enables rapid development. Python supports multiple paradigms."
    questions = generate_mcqs(text, amount=3)
    assert len(questions) == 3


def test_build_quiz_html_writes_file(tmp_path):
    text = "Data science uses python heavily. Data science relies on statistics."
    questions = generate_mcqs(text, amount=2)
    output_file = tmp_path / "quiz.html"
    build_quiz_html(questions, "Summary text", output_file)
    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert "Summary text" in content
    assert "Question 1" in content
