from __future__ import annotations

import logging
from functools import lru_cache

from fastapi import BackgroundTasks, Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import Settings, get_settings
from app.providers import MockPalmAnalysisProvider, OpenAICompatiblePalmAnalysisProvider
from app.schemas import CreateReadingResponse, PublicReadingResponse, ReadingResponse
from app.services import PalmAnalysisService
from app.storage import LocalStorage

logger = logging.getLogger(__name__)

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}
ALLOWED_HAND_SIDES = {"左手", "右手"}


@lru_cache
def get_storage() -> LocalStorage:
    return LocalStorage(get_settings())


@lru_cache
def get_analysis_service() -> PalmAnalysisService:
    settings = get_settings()
    if settings.ai_provider == "openai_compatible":
        return PalmAnalysisService(OpenAICompatiblePalmAnalysisProvider(settings))
    return PalmAnalysisService(MockPalmAnalysisProvider())


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/api/v1/palm-readings", response_model=CreateReadingResponse)
    async def create_palm_reading(
        background_tasks: BackgroundTasks,
        image: UploadFile = File(...),
        handSide: str = Form(...),
        settings: Settings = Depends(get_settings),
        storage: LocalStorage = Depends(get_storage),
        analysis_service: PalmAnalysisService = Depends(get_analysis_service),
    ) -> CreateReadingResponse:
        if not settings.ai_analysis_enabled:
            raise HTTPException(status_code=503, detail="AI 分析服务暂时关闭")
        if image.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(status_code=400, detail="仅支持 JPG、PNG 或 WEBP 图片")
        if handSide not in ALLOWED_HAND_SIDES:
            raise HTTPException(status_code=400, detail="请选择左手或右手")

        content = await _read_upload(image, settings.max_upload_bytes)
        record = storage.new_record()
        record.imageObjectKey = storage.save_upload(record, image.filename or "palm.jpg", content)
        storage.save_record(record)
        logger.info("created palm reading task reading_id=%s", record.readingId)

        background_tasks.add_task(
            _run_analysis_task,
            record.readingId,
            handSide,
            storage,
            analysis_service,
        )
        return CreateReadingResponse(
            readingId=record.readingId,
            shareToken=record.shareToken,
            status=record.status,
            expiresAt=record.expiresAt,
        )

    @app.get("/api/v1/palm-readings/{reading_id}", response_model=ReadingResponse)
    async def get_palm_reading(
        reading_id: str,
        storage: LocalStorage = Depends(get_storage),
    ) -> ReadingResponse:
        record = storage.get_record(reading_id)
        if record is None:
            raise HTTPException(status_code=404, detail="报告不存在")
        if storage.is_expired(record):
            raise HTTPException(status_code=410, detail="报告已过期")
        return _to_reading_response(record)

    @app.get("/api/v1/public-readings/{share_token}", response_model=PublicReadingResponse)
    async def get_public_reading(
        share_token: str,
        storage: LocalStorage = Depends(get_storage),
    ) -> PublicReadingResponse:
        record = storage.find_by_share_token(share_token)
        if record is None:
            raise HTTPException(status_code=404, detail="分享报告不存在")
        if storage.is_expired(record):
            raise HTTPException(status_code=410, detail="报告已过期")
        return PublicReadingResponse(
            shareToken=record.shareToken,
            status=record.status,
            createdAt=record.createdAt,
            expiresAt=record.expiresAt,
            result=record.resultJson,
            errorMessage=record.errorMessage,
        )

    return app


async def _read_upload(image: UploadFile, max_upload_bytes: int) -> bytes:
    content = await image.read(max_upload_bytes + 1)
    if not content:
        raise HTTPException(status_code=400, detail="上传图片不能为空")
    if len(content) > max_upload_bytes:
        raise HTTPException(status_code=413, detail="图片不能超过 10MB")
    return content


async def _run_analysis_task(
    reading_id: str,
    hand_side: str,
    storage: LocalStorage,
    analysis_service: PalmAnalysisService,
) -> None:
    record = storage.get_record(reading_id)
    if record is None or record.imageObjectKey is None:
        return
    try:
        image_path = storage.image_path(record.imageObjectKey)
        result = await analysis_service.analyze_with_retry(image_path)
        result.handInfo.handSide = hand_side
        storage.mark_succeeded(reading_id, result)
        logger.info("palm reading task succeeded reading_id=%s", reading_id)
    except Exception as exc:
        logger.exception("palm reading task failed reading_id=%s", reading_id)
        storage.mark_failed(reading_id, str(exc))


def _to_reading_response(record) -> ReadingResponse:
    return ReadingResponse(
        readingId=record.readingId,
        shareToken=record.shareToken,
        status=record.status,
        createdAt=record.createdAt,
        expiresAt=record.expiresAt,
        tier=record.tier,
        paymentStatus=record.paymentStatus,
        result=record.resultJson,
        errorMessage=record.errorMessage,
    )


app = create_app()


@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc: HTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
