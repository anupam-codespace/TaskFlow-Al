"""
app/services/ai_service.py — AI-powered task summarisation and priority suggestion.

Design decisions:
1. Tries OpenAI GPT-4o-mini first (best quality).
2. Falls back to a deterministic heuristic algorithm if no API key or quota exceeded.
   This means the feature ALWAYS works — no hard dependency on a paid service.
3. Results are cached on the Task model (ai_summary column) so repeated calls
   don't hit the API again for the same task content.

This pattern (graceful degradation) is critical for change resilience:
adding a new AI provider only requires adding a new branch here.
"""

import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)

# Priority scoring keywords used in the heuristic fallback
_PRIORITY_KEYWORDS = {
    "critical": ["production", "outage", "security", "breach", "data loss", "critical", "urgent", "blocker"],
    "high": ["deadline", "launch", "customer", "breaking", "regression", "high", "important", "release"],
    "medium": ["feature", "improve", "refactor", "medium", "update", "enhancement"],
    "low": ["nice to have", "chore", "cleanup", "documentation", "doc", "minor", "low"],
}


def summarise_task(title: str, description: str) -> str:
    """
    Generate a one-sentence AI summary of a task.

    Tries OpenAI, falls back to heuristic extraction.

    Args:
        title: The task title.
        description: The task description.

    Returns:
        A concise summary string (max ~120 chars).
    """
    summary = _try_openai_summary(title, description)
    if summary:
        return summary
    return _heuristic_summary(title, description)


def suggest_priority(title: str, description: str) -> str:
    """
    Suggest a priority level based on task content.

    Args:
        title: The task title.
        description: The task description.

    Returns:
        One of: 'low', 'medium', 'high', 'critical'.
    """
    priority = _try_openai_priority(title, description)
    if priority:
        return priority
    return _heuristic_priority(title, description)


# ── OpenAI Integration ────────────────────────────────────────────────────────

def _try_openai_summary(title: str, description: str) -> Optional[str]:
    """Attempt to summarise via OpenAI. Returns None on any failure."""
    try:
        from flask import current_app
        api_key = current_app.config.get("OPENAI_API_KEY", "")
        if not api_key:
            return None

        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        prompt = (
            f"Summarise this software task in one clear sentence (max 120 chars).\n\n"
            f"Title: {title}\nDescription: {description or 'No description provided.'}"
        )
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=60,
            temperature=0.3,
        )
        summary = response.choices[0].message.content.strip()
        logger.info("OpenAI summary generated for task title=%r", title)
        return summary[:150]
    except Exception as exc:
        logger.warning("OpenAI summary failed, using heuristic: %s", exc)
        return None


def _try_openai_priority(title: str, description: str) -> Optional[str]:
    """Attempt to classify priority via OpenAI. Returns None on any failure."""
    try:
        from flask import current_app
        api_key = current_app.config.get("OPENAI_API_KEY", "")
        if not api_key:
            return None

        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        prompt = (
            f"Classify this software task priority as exactly one of: low, medium, high, critical.\n"
            f"Respond with only the priority word, nothing else.\n\n"
            f"Title: {title}\nDescription: {description or 'No description.'}"
        )
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=5,
            temperature=0,
        )
        result = response.choices[0].message.content.strip().lower()
        valid = {"low", "medium", "high", "critical"}
        if result in valid:
            logger.info("OpenAI priority=%r for task title=%r", result, title)
            return result
        return None
    except Exception as exc:
        logger.warning("OpenAI priority failed, using heuristic: %s", exc)
        return None


# ── Heuristic Fallback ────────────────────────────────────────────────────────

def _heuristic_summary(title: str, description: str) -> str:
    """
    Deterministic summary: extract first meaningful sentence from description,
    or fall back to the title.
    """
    if description:
        sentences = re.split(r"(?<=[.!?])\s+", description.strip())
        first = sentences[0].strip() if sentences else ""
        if first and len(first) > 10:
            return first[:150]
    return f"{title} — see description for details."


def _heuristic_priority(title: str, description: str) -> str:
    """
    Score the task text against keyword lists and return the best match.
    Defaults to 'medium' if no strong signal is found.
    """
    combined = f"{title} {description}".lower()
    scores = {"critical": 0, "high": 0, "medium": 0, "low": 0}

    for level, keywords in _PRIORITY_KEYWORDS.items():
        for kw in keywords:
            if kw in combined:
                scores[level] += 1

    best = max(scores, key=lambda k: scores[k])
    return best if scores[best] > 0 else "medium"
