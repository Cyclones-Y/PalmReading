from pathlib import Path
from typing import Any

from app.providers.base import PalmAnalysisProvider


class MockPalmAnalysisProvider(PalmAnalysisProvider):
    """Deterministic provider used for the free MVP and local development."""

    async def analyze(self, image_path: Path) -> dict[str, Any]:
        return {
            "templateVersion": "palm_vintage_bw_v1",
            "handInfo": {
                "handSide": "左手",
                "handType": "长掌细指",
                "element": "风型带水感",
                "typeLabel": "敏锐的理想实践者",
            },
            "overview": (
                "你的掌纹整体细、长、分支较多，说明不是粗线条的冲动型，"
                "而是观察敏锐、思考细致、容易把感受和判断慢慢消化的人。"
                "掌心肉感均匀，拇指张角较开，代表行动上并不封闭，具备独立选择与自我推进的能力。"
            ),
            "traits": [
                {"title": "理性中有直觉", "description": "逻辑感不弱，但真正做决定时常参考内心感受。"},
                {"title": "慢热而重承诺", "description": "情感表达含蓄，关系稳定后会投入得很认真。"},
                {"title": "适合长期积累", "description": "更适合用作品、信用和经验沉淀优势。"},
                {"title": "敏感但有韧性", "description": "容易被环境影响，却能在压力后重新整理自己。"},
            ],
            "majorLines": [
                {
                    "key": "heartLine",
                    "name": "感情线",
                    "summary": "上方横纹较细，整体略弯，末端趋向食指与中指之间。",
                    "meaning": "你更在意长期的信任、稳定的回应和彼此价值观是否一致。",
                },
                {
                    "key": "headLine",
                    "name": "智慧线",
                    "summary": "智慧线较长，并向掌心下方斜行。",
                    "meaning": "思考方式兼具分析力和想象力，适合处理人、信息、结构与细节。",
                },
                {
                    "key": "lifeLine",
                    "name": "生命线",
                    "summary": "生命线弧度较开，包围拇指根部，主线连续但深浅有变化。",
                    "meaning": "传统手相会把它理解为恢复力与生活韧性不错，但需要靠节奏管理保持状态。",
                },
                {
                    "key": "fateLine",
                    "name": "事业线",
                    "summary": "掌心中轴可见一条偏细的上升线，中段更明显。",
                    "meaning": "方向往往通过尝试、选择和自我修正逐步稳定，适合走长期主义路线。",
                },
            ],
            "aspects": [
                {
                    "key": "career",
                    "title": "事业路径",
                    "body": "你的事业能量偏内在驱动型，适合需要洞察、表达、规划、审美、研究、沟通或项目推进的工作。",
                    "points": [
                        "优势：学习快、感知细，能把复杂信息整理成体系。",
                        "提醒：目标要阶段化，否则容易在选择太多时分散。",
                        "走势：越到后期越靠专业信用和稳定作品打开局面。",
                    ],
                },
                {
                    "key": "love",
                    "title": "情感关系",
                    "body": "你重视关系质量，不喜欢表面热烈但缺少稳定感的互动，确认值得后会比较认真负责。",
                    "points": [
                        "适合：成熟、坦诚、情绪稳定、愿意沟通的人。",
                        "课题：把需求说清楚，少用沉默测试对方。",
                        "关键词：安全感、信任、精神交流、共同成长。",
                    ],
                },
                {
                    "key": "health",
                    "title": "健康状态",
                    "body": "从传统手相角度看，生命线完整，基础恢复力不弱；掌内细纹较多，则提示你容易被思虑、睡眠节奏和外部压力消耗。本内容属于传统民俗与娱乐参考，不构成医学诊断。",
                    "points": [
                        "注意：规律睡眠、肩颈放松、减少长期熬夜。",
                        "建议：用运动和日程边界释放脑力负荷。",
                        "若有持续不适，应以正规医疗检查为准。",
                    ],
                },
            ],
            "guidingEnergy": "你的掌纹给人的核心印象是：温和、敏锐、能沉淀，也有自我选择的骨架。",
            "illustration": {
                "viewBox": "0 0 420 520",
                "heartLine": "M66 276 C123 250 190 243 277 252",
                "headLine": "M292 286 C238 291 172 320 95 360",
                "lifeLine": "M292 284 C266 315 252 357 250 427",
                "fateLine": "M207 438 C207 390 204 340 213 296 C218 270 223 246 219 222",
                "minorLines": [
                    "M143 300 C122 298 101 307 83 324",
                    "M245 286 C263 303 276 324 286 350",
                    "M167 250 C179 269 192 282 207 294",
                    "M196 363 C209 381 219 402 224 426",
                ],
            },
            "disclaimer": "手相解读属于传统民俗与娱乐参考，不用于替代现实决策、医疗诊断或专业咨询。",
        }
