"""Centralized configuration for the Obsidian Agent."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# Obsidian Vault
# =============================================================================
VAULT_PATH = Path(os.getenv("OBSIDIAN_VAULT_PATH", ""))
REVIEW_FOLDER = "Weekly Reviews"

# =============================================================================
# OpenAI / LLM
# =============================================================================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DEFAULT_MODEL = "openai:gpt-4o"

# =============================================================================
# Email (Resend)
# =============================================================================
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
RESEND_SOURCE_EMAIL = os.getenv("RESEND_SOURCE_EMAIL", "onboarding@resend.dev")
EMAIL_TO = os.getenv("EMAIL_TO", "")

# =============================================================================
# Agent Defaults
# =============================================================================
DEFAULT_DAYS_BACK = 7
