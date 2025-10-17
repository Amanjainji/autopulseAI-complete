import json
import os
from typing import Any, Dict

SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "settings.json")

class Settings:
    def __init__(self):
        self._data: Dict[str, Any] = {
            "llm": {
                "provider": "anthropic",
                "model": "claude-3-5-sonnet-20241022",
                "enabled": True
            }
        }
        self.load()

    def load(self):
        try:
            if os.path.exists(SETTINGS_PATH):
                with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
        except Exception:
            # Keep defaults if file malformed
            pass

    def save(self):
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)

    @property
    def llm_enabled(self) -> bool:
        return bool(self._data.get("llm", {}).get("enabled", False))

    @llm_enabled.setter
    def llm_enabled(self, value: bool):
        self._data.setdefault("llm", {})["enabled"] = bool(value)
        self.save()

    @property
    def llm_provider(self) -> str:
        return str(self._data.get("llm", {}).get("provider", "anthropic"))

    @llm_provider.setter
    def llm_provider(self, value: str):
        self._data.setdefault("llm", {})["provider"] = value
        self.save()

    @property
    def llm_model(self) -> str:
        return str(self._data.get("llm", {}).get("model", "claude-3-5-sonnet-20241022"))

    @llm_model.setter
    def llm_model(self, value: str):
        self._data.setdefault("llm", {})["model"] = value
        self.save()

SETTINGS = Settings()
