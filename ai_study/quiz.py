import html
import random
from dataclasses import dataclass
from typing import List, Sequence

from .summarizer import STOPWORDS, split_into_sentences, tokenize


@dataclass
class Question:
    prompt: str
    options: List[str]
    answer_index: int


_RANDOM = random.Random(42)


def _keyword_candidates(text: str, min_length: int = 5, max_keywords: int = 50) -> List[str]:
    words = [word for word in tokenize(text) if len(word) >= min_length and word not in STOPWORDS]
    unique_words = []
    for word in words:
        if word not in unique_words:
            unique_words.append(word)
    return unique_words[:max_keywords]


def _pick_distractors(answer: str, keywords: Sequence[str], count: int = 3) -> List[str]:
    distractors = [word for word in keywords if word != answer]
    _RANDOM.shuffle(distractors)
    result = distractors[:count]
    while len(result) < count:
        filler = f"Option {_RANDOM.randint(1, 99)}"
        if filler not in result and filler != answer:
            result.append(filler)
    return result


def generate_mcqs(text: str, amount: int = 5) -> List[Question]:
    sentences = split_into_sentences(text)
    keywords = _keyword_candidates(text)
    if not sentences or not keywords:
        return []

    questions: List[Question] = []
    keyword_cycle = keywords.copy()
    for sentence in sentences:
        if len(questions) >= amount:
            break
        sentence_words = tokenize(sentence)
        replacement_word = next((word for word in sentence_words if word in keywords), None)
        if not replacement_word:
            continue
        gap_sentence = sentence.replace(replacement_word, "____", 1)
        distractors = _pick_distractors(replacement_word, keywords)
        options = distractors + [replacement_word]
        _RANDOM.shuffle(options)
        answer_index = options.index(replacement_word)
        questions.append(
            Question(
                prompt=gap_sentence,
                options=options,
                answer_index=answer_index,
            )
        )
        keyword_cycle.append(replacement_word)

    while len(questions) < amount and keyword_cycle:
        answer = keyword_cycle.pop(0)
        prompt = f"Which keyword fits best with the material?"
        distractors = _pick_distractors(answer, keywords)
        options = distractors + [answer]
        _RANDOM.shuffle(options)
        answer_index = options.index(answer)
        questions.append(Question(prompt=prompt, options=options, answer_index=answer_index))

    return questions[:amount]


def build_quiz_html(questions: List[Question], summary: str, output_path: str) -> str:
    question_blocks = []
    for idx, question in enumerate(questions, start=1):
        options_html = "".join(
            f"<label><input type='radio' name='q{idx}' value='{i}'> {html.escape(option)}</label><br>"
            for i, option in enumerate(question.options)
        )
        block = f"""
        <div class='question'>
            <h3>Question {idx}</h3>
            <p>{html.escape(question.prompt)}</p>
            {options_html}
        </div>
        """
        question_blocks.append(block)

    quiz_html = "\n".join(question_blocks)
    page = f"""
    <!DOCTYPE html>
    <html lang='en'>
    <head>
        <meta charset='UTF-8'>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <title>Study Helper Quiz</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 2rem auto; padding: 1rem; }}
            .summary {{ background: #f5f5f5; padding: 1rem; border-radius: 8px; }}
            .question {{ margin: 1rem 0; padding: 1rem; border: 1px solid #e0e0e0; border-radius: 8px; }}
            button {{ padding: 0.7rem 1rem; font-size: 1rem; }}
            #result {{ margin-top: 1rem; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1>AI Study Helper</h1>
        <section class='summary'>
            <h2>Summary</h2>
            <p>{html.escape(summary)}</p>
        </section>
        <section id='quiz'>
            <h2>Quiz</h2>
            {quiz_html}
            <button onclick='gradeQuiz()'>Submit Answers</button>
            <p id='result'></p>
        </section>
        <script>
            const answers = [{','.join(str(q.answer_index) for q in questions)}];
            function gradeQuiz() {{
                let score = 0;
                for (let i = 0; i < answers.length; i++) {{
                    const selected = document.querySelector(`input[name="q${{i+1}}"]:checked`);
                    if (selected && Number(selected.value) === answers[i]) {{
                        score += 1;
                    }}
                }}
                const total = answers.length;
                const percentage = total ? Math.round((score / total) * 100) : 0;
                document.getElementById('result').innerText = `Score: ${{score}} / ${{total}} (${{percentage}}%)`;
            }}
        </script>
    </body>
    </html>
    """
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(page)
    return output_path
