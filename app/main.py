from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import admin, auth, events, sales
from .database import init_db
from .middleware import AdminAuthMiddleware
from .observability import setup_logging, setup_metrics
from .config import IPS_VALIDS, ENVIRONMENT

app = FastAPI(
    title="Bilheteria Park API",
    description="API backend para sistema de bilheteria com foco em integração futura e observabilidade.",
    version="0.1.0",
)

app.add_middleware(AdminAuthMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if ENVIRONMENT == "development" else IPS_VALIDS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas públicas
app.include_router(auth.router)       # POST /auth/login
app.include_router(events.router)     # GET  /eventos/, GET /eventos/{id}
app.include_router(sales.router)      # POST /compras

# Rotas de admin (todas protegidas por JWT via AdminAuthMiddleware)
app.include_router(admin.router)      # /admin/*

setup_logging()
setup_metrics(app)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "service": "bilheteria-park-backend"}
