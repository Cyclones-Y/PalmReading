from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class PalmAnalysisProvider(ABC):
    """Model-agnostic contract for palm image analysis providers."""

    @abstractmethod
    async def analyze(self, image_path: Path) -> dict[str, Any]:
        """Return a JSON-like palm reading payload; never return HTML or CSS."""
