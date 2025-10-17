from abc import ABC, abstractmethod
from typing import Optional, Dict

class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, system: Optional[str] = None, **kwargs) -> str:
        """Generate a completion from the underlying model"""
        raise NotImplementedError

    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError
