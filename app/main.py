from fastapi import FastAPI

from .api import batches, customers, dashboard, events, sales
from .database import init_db
from .observability import setup_logging, setup_metrics

app = FastAPI(
    title="Bilheteria Park API",
    description="API backend para sistema de bilheteria com foco em integração futura e observabilidade.",
    version="0.1.0",
)

app.include_router(events.router)
app.include_router(batches.router)
app.include_router(customers.router)
app.include_router(sales.router)
app.include_router(dashboard.router)

setup_logging()
setup_metrics(app)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "service": "bilheteria-park-backend"}
