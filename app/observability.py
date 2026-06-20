import logging
import time

from fastapi import FastAPI, Request
from starlette.responses import PlainTextResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

request_counter = Counter(
    "http_requests_total",
    "Total de requisições HTTP",
    ["method", "path", "status_code"],
)
request_latency = Histogram(
    "http_request_duration_seconds",
    "Duração das requisições HTTP",
    ["method", "path"],
)


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def setup_metrics(app: FastAPI) -> None:
    @app.middleware("http")
    async def prometheus_middleware(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        request_counter.labels(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
        ).inc()
        request_latency.labels(method=request.method, path=request.url.path).observe(duration)
        return response

    @app.get("/metrics", include_in_schema=False)
    async def metrics() -> PlainTextResponse:
        payload = generate_latest()
        return PlainTextResponse(payload, media_type=CONTENT_TYPE_LATEST)
