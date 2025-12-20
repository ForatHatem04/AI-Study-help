"""Lightweight helpers for LLM-backed summarization and quiz generation.

This module centralizes OpenAI chat completions usage so both the CLI and GUI can
request richer summaries and multiple-choice questions. If an OpenAI API key is
not provided, callers can fall back to local generation.
"""

from __future__ import annotations

import json
import os
from typing import Any, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - only for type hints
    from openai import OpenAI


def _get_client() -> Optional[OpenAI]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        from openai import OpenAI
    except ImportError:
        return None
    return OpenAI(api_key=api_key)


def api_configured() -> bool:
    """Return True if an OpenAI API key is available."""

    return _get_client() is not None


def summarize_with_llm(text: str, max_sentences: int = 30) -> Optional[str]:
    """Return a high-quality summary using an OpenAI chat model.

    The model is instructed to produce concise, ordered sentences and cap the
    output length to the requested sentence count. If no API key is configured
    or the request fails, ``None`` is returned so callers can choose a fallback.
    """

    client = _get_client()
    if not client:
        return None

    prompt = (
        "You are a study assistant. Read the provided material and return a clear, "
        "cohesive summary composed of complete sentences. Keep the flow logical "
        "and limit the response to the requested number of sentences."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.3,
            messages=[
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": f"Summarize this in no more than {max_sentences} sentences:\n{text}",
                },
            ],
        )
    except Exception:
        return None

    return response.choices[0].message.content if response.choices else None


def mcqs_with_llm(text: str, amount: int = 10) -> Optional[List[dict[str, Any]]]:
    """Generate multiple-choice questions using an OpenAI chat model.

    The LLM returns JSON-structured questions to simplify parsing. If the API is
    unavailable or the response cannot be parsed, ``None`` is returned.
    """

    client = _get_client()
    if not client:
        return None

    system_prompt = (
        "You create study-ready multiple choice questions. Use the source text to "
        "write questions that test key concepts and include plausible distractors. "
        "Return strictly JSON with a list of objects containing 'prompt', 'options', "
        "and 'answer_index' (0-based)."
    )
    user_prompt = (
        f"Create {amount} high-quality MCQs from this material. Return JSON only with the "
        "fields 'prompt', 'options', and 'answer_index'. Make exactly one correct answer per question.\n\n"
        f"Content:\n{text}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.4,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        )
        message = response.choices[0].message.content if response.choices else None
        if not message:
            return None
        return json.loads(message)
    except Exception:
        return None
