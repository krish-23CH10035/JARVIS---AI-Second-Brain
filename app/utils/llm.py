"""Central LLM factory — single source of truth for all LLM clients."""

from __future__ import annotations

import os
from typing import Optional

from app.utils.logger import get_logger

logger = get_logger("llm")

# ── Cached singleton ────────────────────────────────────────────────────────

_openai_client = None


def get_openai_client():
    """Return a shared OpenAI client (pointing to Groq) for structured JSON calls."""
    global _openai_client
    if _openai_client is not None:
        return _openai_client

    try:
        from openai import OpenAI
        from app.utils.config import settings

        api_key = settings.groq.api_key or os.getenv("GROQ_API_KEY", "")

        if not api_key:
            logger.warning("Groq credentials not configured — SDK client unavailable")
            return None

        _openai_client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key,
        )

        logger.info("Groq OpenAI SDK client created", event_type="llm_factory")
        return _openai_client

    except ImportError:
        logger.warning("openai SDK not installed")
        return None
    except Exception as e:
        logger.error(f"Failed to create Groq client: {e}", exc_info=True)
        return None
