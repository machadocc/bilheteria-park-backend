import time
import logging

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import OperationalError

from .config import DATABASE_URL

logger = logging.getLogger(__name__)

engine = create_engine(DATABASE_URL, future=True, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def wait_for_db(timeout: int = 60, interval: float = 2.0) -> None:
    start_time = time.monotonic()
    while True:
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return
        except OperationalError as exc:
            elapsed = time.monotonic() - start_time
            if elapsed >= timeout:
                logger.exception("Database did not become available within %s seconds", timeout)
                raise
            logger.warning("Database unavailable, retrying in %.1f seconds: %s", interval, exc)
            time.sleep(interval)


def run_migrations() -> None:
    """Aplica alterações de schema que o create_all não consegue fazer (colunas novas em tabelas existentes)."""
    with engine.connect() as conn:
        # --- Migration 001: purchase_code em sales ---
        result = conn.execute(text(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_name='sales' AND column_name='purchase_code'"
        ))
        if not result.fetchone():
            logger.info("Aplicando migration: adicionando purchase_code em sales")
            conn.execute(text("ALTER TABLE sales ADD COLUMN purchase_code VARCHAR(64)"))
            conn.execute(text(
                "UPDATE sales SET purchase_code = UPPER(SUBSTRING(MD5(RANDOM()::TEXT), 1, 12)) "
                "WHERE purchase_code IS NULL"
            ))
            conn.execute(text("ALTER TABLE sales ALTER COLUMN purchase_code SET NOT NULL"))
            conn.execute(text(
                "CREATE UNIQUE INDEX IF NOT EXISTS ix_sales_purchase_code ON sales(purchase_code)"
            ))
            conn.commit()
            logger.info("Migration purchase_code aplicada com sucesso")


def init_db() -> None:
    from .models import Event, TicketBatch, Customer, Sale, SaleItem, EventHistory  # noqa: F401

    wait_for_db()
    Base.metadata.create_all(bind=engine)
    run_migrations()


if __name__ == "__main__":
    init_db()
    print("Database schema created successfully.")
