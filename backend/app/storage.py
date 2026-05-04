from __future__ import annotations

import json
import secrets
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

from app.config import Settings
from app.schemas import PalmReadingResult, ReadingRecord


class LocalStorage:
    """Filesystem storage adapter; production can replace this with object storage."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.records_dir = settings.data_dir / "records"
        self.uploads_dir = settings.data_dir / "uploads"
        self.records_dir.mkdir(parents=True, exist_ok=True)
        self.uploads_dir.mkdir(parents=True, exist_ok=True)

    def new_record(self) -> ReadingRecord:
        now = datetime.now(UTC)
        return ReadingRecord(
            readingId=str(uuid.uuid4()),
            shareToken=secrets.token_urlsafe(18),
            status="processing",
            createdAt=now,
            expiresAt=now + timedelta(days=self.settings.retention_days),
        )

    def save_upload(self, record: ReadingRecord, filename: str, content: bytes) -> str:
        suffix = Path(filename).suffix.lower()
        if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
            suffix = ".jpg"
        day_dir = self.uploads_dir / record.createdAt.strftime("%Y%m%d")
        day_dir.mkdir(parents=True, exist_ok=True)
        image_path = day_dir / f"{record.readingId}{suffix}"
        image_path.write_bytes(content)
        return str(image_path.relative_to(self.settings.data_dir).as_posix())

    def image_path(self, image_object_key: str) -> Path:
        return self.settings.data_dir / image_object_key

    def save_record(self, record: ReadingRecord) -> None:
        path = self._record_path(record.readingId)
        path.write_text(
            record.model_dump_json(indent=2),
            encoding="utf-8",
        )

    def get_record(self, reading_id: str) -> ReadingRecord | None:
        path = self._record_path(reading_id)
        if not path.exists():
            return None
        return ReadingRecord.model_validate_json(path.read_text(encoding="utf-8"))

    def find_by_share_token(self, share_token: str) -> ReadingRecord | None:
        for path in self.records_dir.glob("*.json"):
            payload = json.loads(path.read_text(encoding="utf-8"))
            if payload.get("shareToken") == share_token:
                return ReadingRecord.model_validate(payload)
        return None

    def mark_succeeded(self, reading_id: str, result: PalmReadingResult) -> ReadingRecord:
        record = self._require_record(reading_id)
        record.status = "succeeded"
        record.resultJson = result
        record.errorMessage = None
        self.save_record(record)
        return record

    def mark_failed(self, reading_id: str, message: str) -> ReadingRecord:
        record = self._require_record(reading_id)
        record.status = "failed"
        record.errorMessage = message
        self.save_record(record)
        return record

    def is_expired(self, record: ReadingRecord) -> bool:
        return record.expiresAt <= datetime.now(UTC)

    def _record_path(self, reading_id: str) -> Path:
        return self.records_dir / f"{reading_id}.json"

    def _require_record(self, reading_id: str) -> ReadingRecord:
        record = self.get_record(reading_id)
        if record is None:
            raise FileNotFoundError(reading_id)
        return record
