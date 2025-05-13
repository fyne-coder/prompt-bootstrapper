"""
Configuration constants for OpenAI integration.
"""
import os

# Default model for LLM nodes, configurable via environment variable.
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini-2025-04-14")