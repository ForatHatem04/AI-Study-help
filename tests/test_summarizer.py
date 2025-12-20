from ai_study.summarizer import split_into_sentences, summarize_text


def test_split_into_sentences():
    text = "First sentence. Second sentence! Third?"
    sentences = split_into_sentences(text)
    assert sentences == ["First sentence.", "Second sentence!", "Third?"]


def test_summarize_text_limits_sentence_count():
    text = "One. Two. Three. Four."
    summary = summarize_text(text, max_sentences=2)
    assert len(summary.split(".")) - 1 <= 2
