from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any

import httpx

from app.config import Settings
from app.providers.base import PalmAnalysisProvider

PALM_ANALYSIS_PROMPT = """
你是精通古今中外手相知识的中文手相解读助手。请基于用户上传的手掌照片，
只输出严格 JSON，不要输出 Markdown、HTML、CSS 或额外解释。

输出必须符合以下结构：
{
  "templateVersion": "palm_vintage_bw_v1",
  "handInfo": {
    "handSide": "左手或右手",
    "handType": "手型判断",
    "element": "元素倾向",
    "typeLabel": "整体类型标签"
  },
  "overview": "掌相总览，中文，80-160字",
  "traits": [
    {"title": "特征标题", "description": "一句解释"}
  ],
  "majorLines": [
    {"key": "heartLine", "name": "感情线", "summary": "可见纹路观察", "meaning": "传统手相解释"},
    {"key": "headLine", "name": "智慧线", "summary": "可见纹路观察", "meaning": "传统手相解释"},
    {"key": "lifeLine", "name": "生命线", "summary": "可见纹路观察", "meaning": "传统手相解释"},
    {"key": "fateLine", "name": "事业线", "summary": "可见纹路观察", "meaning": "传统手相解释"}
  ],
  "aspects": [
    {"key": "career", "title": "事业路径", "body": "事业解读", "points": ["要点1", "要点2", "要点3"]},
    {"key": "love", "title": "情感关系", "body": "情感解读", "points": ["要点1", "要点2", "要点3"]},
    {"key": "health", "title": "健康状态", "body": "健康解读，必须说明传统民俗与娱乐参考，不构成医学诊断", "points": ["要点1", "要点2", "如有持续不适，应以正规医疗检查为准"]}
  ],
  "guidingEnergy": "结语，中文，30-80字",
  "illustration": {
    "viewBox": "0 0 420 520",
    "heartLine": "SVG path d，坐标必须在420x520内",
    "headLine": "SVG path d，坐标必须在420x520内",
    "lifeLine": "SVG path d，坐标必须在420x520内",
    "fateLine": "SVG path d，坐标必须在420x520内",
    "minorLines": ["可选SVG path d"]
  },
  "disclaimer": "手相解读属于传统民俗与娱乐参考，不用于替代现实决策、医疗诊断或专业咨询。"
}

要求：
1. traits 必须 3-5 条。
2. majorLines 必须且只能包含四条主线。
3. aspects 必须包含 career、love、health。
4. 健康内容不能写成医学诊断。
5. 所有文案使用中文。
"""


class OpenAICompatiblePalmAnalysisProvider(PalmAnalysisProvider):
    """Provider for OpenAI-compatible multimodal chat completion APIs."""

    def __init__(self, settings: Settings) -> None:
        if not settings.ai_api_key:
            raise ValueError("PALM_AI_API_KEY 未配置")
        self.settings = settings

    async def analyze(self, image_path: Path) -> dict[str, Any]:
        image_data = _image_to_data_url(image_path)
        payload = {
            "model": self.settings.ai_model,
            "messages": [
                {"role": "system", "content": PALM_ANALYSIS_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "请分析这张手掌照片，并输出指定 JSON。"},
                        {"type": "image_url", "image_url": {"url": image_data}},
                    ],
                },
            ],
            "temperature": 0.4,
            "response_format": {"type": "json_object"},
        }
        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post(
                f"{self.settings.ai_base_url.rstrip('/')}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.settings.ai_api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return json.loads(content)


def _image_to_data_url(image_path: Path) -> str:
    suffix = image_path.suffix.lower()
    mime_type = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }.get(suffix, "image/jpeg")
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"
