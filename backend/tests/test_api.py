from datetime import UTC, datetime, timedelta
from pathlib import Path

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app, get_analysis_service, get_storage
from app.providers import MockPalmAnalysisProvider
from app.services import PalmAnalysisService
from app.storage import LocalStorage


def make_client(tmp_path: Path) -> tuple[TestClient, LocalStorage]:
    app = create_app()
    storage = LocalStorage(Settings(data_dir=tmp_path))
    app.dependency_overrides[get_storage] = lambda: storage
    app.dependency_overrides[get_analysis_service] = lambda: PalmAnalysisService(MockPalmAnalysisProvider())
    return TestClient(app), storage


def test_upload_creates_reading_and_result(tmp_path: Path) -> None:
    client, _ = make_client(tmp_path)

    response = client.post(
        "/api/v1/palm-readings",
        data={"handSide": "右手"},
        files={"image": ("palm.jpg", b"fake-image", "image/jpeg")},
    )

    assert response.status_code == 200
    payload = response.json()
    reading_id = payload["readingId"]
    detail = client.get(f"/api/v1/palm-readings/{reading_id}")
    assert detail.status_code == 200
    data = detail.json()
    assert data["status"] == "succeeded"
    assert data["result"]["handInfo"]["handSide"] == "右手"
    assert data["result"]["templateVersion"] == "palm_vintage_bw_v1"
    assert data["result"]["aspects"][2]["key"] == "health"


def test_rejects_non_image(tmp_path: Path) -> None:
    client, _ = make_client(tmp_path)

    response = client.post(
        "/api/v1/palm-readings",
        data={"handSide": "左手"},
        files={"image": ("note.txt", b"hello", "text/plain")},
    )

    assert response.status_code == 400
    assert "JPG" in response.json()["detail"]


def test_public_link_expires(tmp_path: Path) -> None:
    client, storage = make_client(tmp_path)
    upload = client.post(
        "/api/v1/palm-readings",
        data={"handSide": "左手"},
        files={"image": ("palm.jpg", b"fake-image", "image/jpeg")},
    )
    share_token = upload.json()["shareToken"]
    reading_id = upload.json()["readingId"]

    record = storage.get_record(reading_id)
    assert record is not None
    record.expiresAt = datetime.now(UTC) - timedelta(seconds=1)
    storage.save_record(record)

    response = client.get(f"/api/v1/public-readings/{share_token}")
    assert response.status_code == 410
    assert response.json()["detail"] == "报告已过期"


def test_rejects_invalid_hand_side(tmp_path: Path) -> None:
    client, _ = make_client(tmp_path)

    response = client.post(
        "/api/v1/palm-readings",
        data={"handSide": "自动判断"},
        files={"image": ("palm.jpg", b"fake-image", "image/jpeg")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "请选择左手或右手"
