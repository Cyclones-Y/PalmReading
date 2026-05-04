from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


ReadingStatus = Literal["processing", "succeeded", "failed"]


class HandInfo(BaseModel):
    handSide: str = Field(..., description="左右手识别结果")
    handType: str = Field(..., description="手型判断")
    element: str = Field(..., description="元素倾向")
    typeLabel: str = Field(..., description="整体类型标签")

    @field_validator("handSide")
    @classmethod
    def normalize_hand_side(cls, value: str) -> str:
        normalized = value.strip()
        if normalized in {"左手", "右手", "无法判断"}:
            return normalized
        return "无法判断"


class Trait(BaseModel):
    title: str
    description: str


class MajorLine(BaseModel):
    key: Literal["heartLine", "headLine", "lifeLine", "fateLine"]
    name: str
    summary: str
    meaning: str


class Aspect(BaseModel):
    key: Literal["career", "love", "health"]
    title: str
    body: str
    points: list[str] = Field(default_factory=list)


class Illustration(BaseModel):
    viewBox: str = "0 0 420 520"
    heartLine: str
    headLine: str
    lifeLine: str
    fateLine: str
    minorLines: list[str] = Field(default_factory=list)


class PalmReadingResult(BaseModel):
    templateVersion: str = "palm_vintage_bw_v1"
    handInfo: HandInfo
    overview: str
    traits: list[Trait] = Field(min_length=3, max_length=5)
    majorLines: list[MajorLine] = Field(min_length=4, max_length=4)
    aspects: list[Aspect] = Field(min_length=3, max_length=3)
    guidingEnergy: str
    illustration: Illustration | None = None
    disclaimer: str


class ReadingRecord(BaseModel):
    readingId: str
    shareToken: str
    status: ReadingStatus
    createdAt: datetime
    expiresAt: datetime
    tier: str = "free"
    paymentStatus: str = "free"
    imageObjectKey: str | None = None
    resultJson: PalmReadingResult | None = None
    errorMessage: str | None = None


class CreateReadingResponse(BaseModel):
    readingId: str
    shareToken: str
    status: ReadingStatus
    expiresAt: datetime


class ReadingResponse(BaseModel):
    readingId: str
    shareToken: str
    status: ReadingStatus
    createdAt: datetime
    expiresAt: datetime
    tier: str
    paymentStatus: str
    result: PalmReadingResult | None = None
    errorMessage: str | None = None


class PublicReadingResponse(BaseModel):
    shareToken: str
    status: ReadingStatus
    createdAt: datetime
    expiresAt: datetime
    result: PalmReadingResult | None = None
    errorMessage: str | None = None
