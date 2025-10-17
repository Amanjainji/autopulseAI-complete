import os
from typing import Optional

try:
    from anthropic import Anthropic
except Exception:  # SDK optional
    Anthropic = None

from .llm_provider import LLMProvider

_DEFAULT_MODEL = "claude-3-5-sonnet-20241022"

class AnthropicProvider(LLMProvider):
    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None):
        self._model = model or _DEFAULT_MODEL
        self._api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self._client = None
        if Anthropic and self._api_key:
            try:
                self._client = Anthropic(api_key=self._api_key)
            except Exception:
                self._client = None

    def name(self) -> str:
        return f"anthropic/{self._model}"

    def generate(self, prompt: str, system: Optional[str] = None, **kwargs) -> str:
        # If SDK or API key missing, return a graceful fallback
        if not self._client:
            return self._fallback(prompt, system)

        try:
            messages = [
                {"role": "user", "content": prompt}
            ]
            resp = self._client.messages.create(
                model=self._model,
                max_tokens=512,
                temperature=float(kwargs.get("temperature", 0.2)),
                system=system or "You are an expert automotive service assistant. Be concise, professional, and helpful.",
                messages=messages,
            )
            # SDK returns content list
            if getattr(resp, "content", None):
                parts = [p.text for p in resp.content if getattr(p, "text", None)]
                return "\n".join(parts).strip() or "(No response)"
            return "(No response)"
        except Exception:
            return self._fallback(prompt, system)

    def _fallback(self, prompt: str, system: Optional[str]) -> str:
        # Minimal, deterministic fallback if no API
        header = "AI Assistant (offline mode):"
        guidance = "I can't reach Claude right now. Here's a helpful response based on rules:"
        return f"{header}\n{guidance}\n\nUser asked: {prompt[:300]}\n\n- If you're asking about service, I can help book an appointment.\n- If you want vehicle status, check the Dashboard and Predictions.\n- For history, use 'View Service History' in your profile.\n\nPlease try again later for richer AI responses."
