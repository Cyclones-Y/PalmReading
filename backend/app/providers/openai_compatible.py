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

在正式解读前，必须先根据图片判断左右手，并把判断结果写入 handInfo.handSide：
1. 只根据图片中真实可见的手掌结构判断，不要默认猜测，不要因为常见习惯而假设为某一只手。
2. 优先观察拇指所在方向：如果是掌心朝向镜头，且拇指位于画面左侧，通常判断为左手；如果拇指位于画面右侧，通常判断为右手。
3. 如果图片经过镜像自拍、手背朝向镜头、手掌严重旋转、拇指被裁切、双手同时入镜或掌心不可见，无法可靠判断时，handSide 必须输出“无法判断”。
4. 不要把生命线、感情线或智慧线的弯曲方向当成唯一依据；左右手判断必须以拇指位置、掌心朝向、手指排列和腕部方向综合判断。
5. handInfo.handSide 只能输出以下三个值之一：“左手”、“右手”、“无法判断”。
6. 后续解读要与 handSide 保持一致；如果 handSide 为“无法判断”，文案中不要强行写“左手代表……”或“右手代表……”。

输出必须符合以下结构：
{
  "templateVersion": "palm_vintage_bw_v1",
  "handInfo": {
    "handSide": "左手、右手或无法判断",
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
                        {
                            "type": "text",
                            "text": (
                                "请分析这张手掌照片，并输出指定 JSON。"
                                "先判断图片中是左手、右手还是无法判断，再进行手相解读。"
                            ),
                        },
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
