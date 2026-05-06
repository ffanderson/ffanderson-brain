#!/usr/bin/env python3
"""
LLMClient — a thin, swappable wrapper around an LLM provider.

Default provider: Anthropic Claude via the official Python SDK.

Set `LLM_MOCK=1` in the environment to bypass the network and return
deterministic stub responses. This is useful for offline tests, dry-runs,
and CI.

Swapping providers is intended to be a one-file change: add a new
`_call_<provider>` method, route in `complete()`.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Optional


DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_MAX_TOKENS = 4096
# Hard wall on individual API calls. Without this, the SDK's internal retry/
# backoff loop can sit on a stuck connection indefinitely; observed in the
# 2026-05-05 backfill on long transcripts.
DEFAULT_TIMEOUT_S = 180.0


@dataclass
class LLMResponse:
    """Container for an LLM call's result."""

    text: str
    model: str
    provider: str

    def as_json(self) -> dict:
        """Parse `text` as JSON. Tolerates fenced ```json blocks."""
        cleaned = self.text.strip()
        if cleaned.startswith("```"):
            # Strip code fences; first line is the fence, last line is the fence.
            lines = cleaned.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            cleaned = "\n".join(lines)
        return json.loads(cleaned)


class LLMClient:
    """Provider-neutral wrapper. Today: Anthropic. Tomorrow: pluggable."""

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        mock: Optional[bool] = None,
    ):
        self.model = model
        self.max_tokens = max_tokens
        self.mock = mock if mock is not None else os.getenv("LLM_MOCK") == "1"
        self._client = None  # lazy-init the SDK

    def complete(
        self,
        prompt: str,
        system: Optional[str] = None,
        response_format: Optional[str] = None,  # "json" hints downstream parsing
    ) -> LLMResponse:
        if self.mock:
            return self._mock_response(prompt, response_format)
        return self._call_anthropic(prompt, system, response_format)

    def _mock_response(self, prompt: str, response_format: Optional[str]) -> LLMResponse:
        """Deterministic stub responses for offline use."""
        if response_format == "json":
            text = json.dumps(
                {
                    "_mock": True,
                    "_note": "LLM_MOCK=1; replace with real call to populate.",
                }
            )
        else:
            text = "[mock response — set ANTHROPIC_API_KEY and unset LLM_MOCK to enable]"
        return LLMResponse(text=text, model=self.model, provider="mock")

    def _call_anthropic(
        self,
        prompt: str,
        system: Optional[str],
        response_format: Optional[str],
    ) -> LLMResponse:
        if self._client is None:
            try:
                import anthropic  # type: ignore
            except ImportError as e:
                raise RuntimeError(
                    "anthropic package not installed. Run "
                    "`pip install -r scripts/requirements.txt`."
                ) from e
            self._client = anthropic.Anthropic(timeout=DEFAULT_TIMEOUT_S)

        kwargs: dict = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            kwargs["system"] = system

        msg = self._client.messages.create(**kwargs)
        # `msg.content` is a list of content blocks; join their text.
        text_parts = [
            block.text
            for block in msg.content
            if getattr(block, "type", None) == "text"
        ]
        return LLMResponse(
            text="".join(text_parts).strip(),
            model=self.model,
            provider="anthropic",
        )
