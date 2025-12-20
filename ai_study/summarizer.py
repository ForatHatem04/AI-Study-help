import math
import re
from collections import Counter
from typing import List, Optional

from .llm import summarize_with_llm

STOPWORDS = {
    "the",
    "and",
    "to",
    "of",
    "in",
    "a",
    "for",
    "is",
    "that",
    "on",
    "with",
    "as",
    "by",
    "this",
    "an",
    "be",
    "are",
    "or",
    "from",
    "at",
    "it",
    "we",
    "can",
    "which",
    "these",
    "also",
    "will",
}


def split_into_sentences(text: str) -> List[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    cleaned = [sentence.strip() for sentence in sentences if sentence.strip()]
    return cleaned


def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z']+", text.lower())


def _summarize_locally(text: str, max_sentences: int) -> str:
    sentences = split_into_sentences(text)
    if not sentences:
        return ""
    max_sentences = min(max_sentences, len(sentences))
    words = tokenize(text)
    if not words:
        return " ".join(sentences[:max_sentences])

    frequencies = Counter(word for word in words if word not in STOPWORDS)
    if not frequencies:
        return " ".join(sentences[:max_sentences])

    max_frequency = max(frequencies.values())
    normalized_freq = {word: freq / max_frequency for word, freq in frequencies.items()}

    sentence_scores = {}
    for sentence in sentences:
        sentence_words = tokenize(sentence)
        if not sentence_words:
            continue
        score = sum(normalized_freq.get(word, 0) for word in sentence_words)
        score /= math.sqrt(len(sentence_words))
        sentence_scores[sentence] = score

    ranked_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)
    top_sentences = ranked_sentences[:max_sentences]
    ordered = [sentence for sentence in sentences if sentence in top_sentences]
    return " ".join(ordered)


def summarize_text(text: str, max_sentences: int = 5) -> str:
    """Summarize text with an LLM first, then fall back to extractive scoring."""

    llm_summary: Optional[str] = summarize_with_llm(text, max_sentences=max_sentences)
    if llm_summary:
        return llm_summary.strip()
    return _summarize_locally(text, max_sentences)
