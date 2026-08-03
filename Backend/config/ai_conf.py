"""Gemini settings.

The key lives in Backend/.env (gitignored) and never reaches the browser —
the frontend talks to our own /api/ai/chat, which proxies to Google.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Google exposes an OpenAI-compatible surface, so the request/response shape
# matches what the chat page already speaks.
GEMINI_BASE_URL = os.getenv(
    "GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai"
)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest")

CHAT_COMPLETIONS_URL = f"{GEMINI_BASE_URL.rstrip('/')}/chat/completions"


def is_configured() -> bool:
    return bool(GEMINI_API_KEY)
