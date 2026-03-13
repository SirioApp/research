from __future__ import annotations

import hmac
import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Literal
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

from .agent import InvestmentResearchAgent
from .ingestion import IngestionError

API_VERSION = "0.2.0"
DEFAULT_API_KEY = "GIT3PRIVATE"
DEFAULT_MODEL = "gpt-4.1-mini"

load_dotenv()


@dataclass(frozen=True, slots=True)
class APISettings:
    host: str
    port: int
    api_key: str
    cors_origins: list[str]


class AnalyzeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str | None = None
    sources: list[str] | None = Field(default=None, min_length=1)
    mode: Literal["auto", "ai", "rules"] = "auto"
    model: str = DEFAULT_MODEL


class AnalyzeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str
    sources: list[str]
    mode: Literal["auto", "ai", "rules"]
    model: str
    result: dict


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    service: str
    version: str


@lru_cache(maxsize=1)
def get_settings() -> APISettings:
    raw_origins = os.getenv("BACKED_API_CORS_ORIGINS", "*")
    origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
    return APISettings(
        host=os.getenv("BACKED_API_HOST", "127.0.0.1"),
        port=int(os.getenv("BACKED_API_PORT", "8000")),
        api_key=os.getenv("BACKED_API_KEY", DEFAULT_API_KEY),
        cors_origins=origins or ["*"],
    )


def _extract_api_key(x_api_key: str | None, authorization: str | None) -> str | None:
    if x_api_key:
        return x_api_key.strip()
    if not authorization:
        return None
    if authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    return None


def authorize_request(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    authorization: str | None = Header(default=None, alias="Authorization"),
    settings: APISettings = Depends(get_settings),
) -> None:
    provided_key = _extract_api_key(x_api_key, authorization)
    expected_key = settings.api_key

    if not provided_key or not hmac.compare_digest(provided_key, expected_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )


def _resolve_sources(payload: AnalyzeRequest) -> list[str]:
    if payload.source and payload.sources:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Use either 'source' or 'sources', not both.",
        )
    if payload.sources:
        return payload.sources
    if payload.source:
        return [payload.source]
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Missing source input. Provide 'source' or 'sources'.",
    )


def _run_analysis(payload: AnalyzeRequest) -> AnalyzeResponse:
    sources = _resolve_sources(payload)
    agent = InvestmentResearchAgent(mode=payload.mode, model=payload.model)

    try:
        result = agent.run(sources)
    except IngestionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Ingestion failed: {exc}",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {exc}",
        ) from exc

    return AnalyzeResponse(
        request_id=str(uuid4()),
        sources=sources,
        mode=payload.mode,
        model=payload.model,
        result=result.to_dict(),
    )


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Backed Research Agent API",
        version=API_VERSION,
        description="HTTP API for analyst-grade web3 due diligence and investment underwriting.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["POST", "GET", "OPTIONS"],
        allow_headers=["*"],
    )

    @app.get("/", response_model=HealthResponse, tags=["system"])
    def home() -> HealthResponse:
        return HealthResponse(
            status="ok",
            service="backed-research-agent-api",
            version=API_VERSION,
        )

    @app.get("/v1/health", response_model=HealthResponse, tags=["system"])
    def health() -> HealthResponse:
        return home()

    @app.post(
        "/",
        response_model=AnalyzeResponse,
        dependencies=[Depends(authorize_request)],
        tags=["analysis"],
    )
    def analyze_root(payload: AnalyzeRequest) -> AnalyzeResponse:
        return _run_analysis(payload)

    @app.post(
        "/v1/analyze",
        response_model=AnalyzeResponse,
        dependencies=[Depends(authorize_request)],
        tags=["analysis"],
    )
    def analyze_v1(payload: AnalyzeRequest) -> AnalyzeResponse:
        return _run_analysis(payload)

    return app


app = create_app()


def run() -> None:
    import uvicorn

    settings = get_settings()
    uvicorn.run(app, host=settings.host, port=settings.port, reload=False)


if __name__ == "__main__":
    run()
