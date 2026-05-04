from pathlib import Path

from pydantic import ValidationError

from app.providers.base import PalmAnalysisProvider
from app.schemas import PalmReadingResult

HEALTH_DISCLAIMER_KEYWORDS = ("娱乐参考", "医学诊断")


class PalmAnalysisService:
    """Runs provider analysis and validates the stable report schema."""

    def __init__(self, provider: PalmAnalysisProvider) -> None:
        self.provider = provider

    async def analyze_with_retry(self, image_path: Path) -> PalmReadingResult:
        last_error: Exception | None = None
        for _ in range(2):
            try:
                result = PalmReadingResult.model_validate(
                    await self.provider.analyze(image_path)
                )
                self._ensure_health_boundary(result)
                return result
            except (ValidationError, ValueError) as exc:
                last_error = exc
        raise ValueError(f"AI 输出结构校验失败：{last_error}") from last_error

    def _ensure_health_boundary(self, result: PalmReadingResult) -> None:
        health = next((aspect for aspect in result.aspects if aspect.key == "health"), None)
        if health is None:
            raise ValueError("缺少健康解读")
        combined_text = f"{health.body} {' '.join(health.points)} {result.disclaimer}"
        if not all(keyword in combined_text for keyword in HEALTH_DISCLAIMER_KEYWORDS):
            raise ValueError("健康解读缺少娱乐参考或非医学诊断边界")
